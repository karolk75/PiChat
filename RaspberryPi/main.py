import azure.cognitiveservices.speech as speechsdk
import openai
import asyncio
import json
from collections import namedtuple
import tiktoken
import time
import os
import uuid

from azure.iot.device import Message
from azure.iot.device.aio import IoTHubDeviceClient as AsyncIoTHubDeviceClient

EOF = object()

# Load config.json
def load_config():
    try:
        with open('config.json', encoding='utf-8') as f:
            config = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            if not config.AzureCognitiveServices.Key or not config.AzureCognitiveServices.Region:
                raise ValueError("Missing required speech service configuration.")
            
            # Get IoT Hub connection string from environment variable or config
            if hasattr(config, 'AzureIoTHub') and hasattr(config.AzureIoTHub, 'ConnectionString'):
                # Use connection string from config if available
                pass
            else:
                # Use environment variable if not in config
                connection_string = os.environ.get('IOTHUB_DEVICE_CONNECTION_STRING')
                if not connection_string:
                    raise ValueError("Missing IoT Hub connection string. Set IOTHUB_DEVICE_CONNECTION_STRING environment variable.")
                
                # Add IoTHub config if not present
                if not hasattr(config, 'AzureIoTHub'):
                    # Create a new mutable dict to add the IoTHub config
                    config_dict = config._asdict()
                    config_dict['AzureIoTHub'] = {
                        'ConnectionString': connection_string
                    }
                    config = namedtuple('X', config_dict.keys())(*config_dict.values())
                
            return config
    except FileNotFoundError:
        print("Error: config file not found.")
    except Exception as e:
        print(f"Error loading config: {e}")

# If tokens greater than max_tokens, then remove history message
def truncate_conversation(conversation, max_tokens):
    total_tokens = 0
    truncated_conversation = []
    encoding = tiktoken.get_encoding("cl100k_base")

    # Iterate in reverse to keep the most recent messages
    for message in reversed(conversation):
        message_tokens = len(encoding.encode(message['content']))
        if total_tokens + message_tokens > max_tokens - 100: 
            print(f'Token limit reached at {total_tokens}/{max_tokens}. Truncating conversation history.')
            break
        total_tokens += message_tokens
        truncated_conversation.append(message)

    # Replace the original conversation with the truncated one (reversed back to chronological order)
    conversation.clear()
    conversation.extend(reversed(truncated_conversation))
    
    print(f'Conversation has {len(conversation)} messages with approximately {total_tokens} tokens')
    return conversation

# Create IoT Hub client for sending messages and receiving responses
async def create_iot_hub_client(connection_string):
    try:
        # Create instance of the device client using the connection string
        device_client = AsyncIoTHubDeviceClient.create_from_connection_string(connection_string)
        
        # Connect the device client
        await device_client.connect()
        print("IoT Hub device client connected successfully!")
        
        return device_client
    except Exception as e:
        print(f"Error connecting to IoT Hub: {e}")
        raise

# Send message to backend via IoT Hub and receive response
async def send_to_iot_hub_and_receive(device_client, prompt, conversation, queue, ending_punctuations):
    # Capture the current event loop for thread-safe operations
    loop = asyncio.get_running_loop()
    
    # Append user questions to conversation history
    conversation.append({"role": "user", "content": prompt})
    
    truncate_conversation(conversation, 4000)
    
    # Create message payload
    message_payload = {
        "message": prompt,
        "conversation": conversation,
        "timestamp": time.time(),
        "device_id": os.environ.get("DEVICE_ID", "raspberry_pi")
    }
    
    # Create IoT Hub message
    message = Message(json.dumps(message_payload))
    message.content_type = "application/json"
    message.content_encoding = "utf-8"
    
    # Set message-id as a system property
    message.message_id = str(uuid.uuid4())
    
    # Set up response tracking
    response_event = asyncio.Event()
    response_text_container = [None] # Use a list to pass text by reference from handler

    # Define message handler function
    async def message_handler(msg):
        
        try:
            # Parse the response
            response_data = json.loads(msg.data.decode())
            print(f"Response received from cloud: {msg.data.decode()} at {time.time()}")
            
            # Extract the response text
            current_response_text = response_data.get('response', '')
            if not current_response_text:
                print("Warning: Received empty response from backend")
                response_text_container[0] = "" 
                loop.call_soon_threadsafe(response_event.set)
                return
            
            response_text_container[0] = current_response_text
            loop.call_soon_threadsafe(response_event.set)
            
        except json.JSONDecodeError as e:
            print(f"Error decoding response JSON: {e}")
            # In case of error, also set the event to prevent indefinite hang, response_text will be None
            response_text_container[0] = None 
            loop.call_soon_threadsafe(response_event.set)
        except Exception as e:
            print(f"Error handling message from IoT Hub: {e}")
            response_text_container[0] = None
            loop.call_soon_threadsafe(response_event.set)
    
    # Set the message received handler
    device_client.on_message_received = message_handler
    
    # Send the message
    print(f"Sending message to IoT Hub: {prompt}")
    await device_client.send_message(message)
    print("Message sent successfully!")
    
    # Wait for response with timeout
    try:
        print("Waiting for response for 30 seconds...")
        await asyncio.wait_for(response_event.wait(), timeout=30.0)
        retrieved_response_text = response_text_container[0]
        
        if retrieved_response_text:
            # Process the response text to break it into sentences
            full_answer = ""
            current_sentence = ""
            
            # Process character by character to build sentences
            for char_idx, char in enumerate(retrieved_response_text):
                current_sentence += char
                
                if any(current_sentence.endswith(ending) for ending in ending_punctuations if ending):
                    await queue.put(current_sentence)
                    full_answer += current_sentence
                    current_sentence = ""
            
            if current_sentence:
                await queue.put(current_sentence)
                full_answer += current_sentence
            
            # Add assistant response to conversation history
            conversation.append({"role": "assistant", "content": full_answer})
        else:
            print(f"Response_event set, but no valid response_text ('{retrieved_response_text}') to process at {time.time()}")
        
    except asyncio.TimeoutError:
        print("Timeout waiting for response from backend")
        await queue.put("I'm sorry, I didn't receive a response from the backend in time.")
    finally:
        device_client.on_message_received = None 
    
    # Signal end of response
    await queue.put(EOF)

# async read message from queue and synthesized speech
async def text_to_speech_async(speech_synthesizer, queue):
    try:
        loop = asyncio.get_running_loop()
        while True:
            text = await queue.get()
            if text is EOF:
                print("End of response processing")
                break

            text = text.strip()
            if not text:
                continue

            print(f"Speaking: {text}")
            
            def blocking_speak_call():
                return speech_synthesizer.speak_text_async(text).get()

            speech_synthesis_result = await loop.run_in_executor(None, blocking_speak_call)

            if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesized successfully")
            elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = speech_synthesis_result.cancellation_details
                print("Speech synthesis canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))
    except Exception as e:
        print(f"Error in text_to_speech_async: {e}")

# Detect keyword and wakeup
async def detect_keyword(recognizer, model, keyword):
    done = False

    def recognized_cb(evt):
        result = evt.result
        if result.reason == speechsdk.ResultReason.RecognizedKeyword:
            print("RECOGNIZED KEYWORD: {}".format(result.text))
        nonlocal done
        done = True

    def canceled_cb(evt):
        result = evt.result
        if result.reason == speechsdk.ResultReason.Canceled:
            print('CANCELED: {}'.format(result.cancellation_details.reason))
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the keyword recognizer.
    recognizer.recognized.connect(recognized_cb)
    recognizer.canceled.connect(canceled_cb)

    # Start keyword recognition.
    recognizer.start_keyword_recognition(model)
    print('Say something starting with "{}" followed by whatever you want...'.format(keyword))
    while not done:
        await asyncio.sleep(.5)

    recognizer.recognized.disconnect_all()
    recognizer.canceled.disconnect_all()
    recognizer.stop_keyword_recognition()

    # Read result audio (incl. the keyword).
    return done

# Load IoT Hub connection string from config or environment variables
def load_connection_string():
    try:
        # Try to load from config.json first
        with open('config.json', encoding='utf-8') as f:
            config = json.load(f, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            if hasattr(config, 'AzureIoTHub') and hasattr(config.AzureIoTHub, 'ConnectionString'):
                return config.AzureIoTHub.ConnectionString
    except (FileNotFoundError, json.JSONDecodeError, AttributeError):
        print("Config file not found or invalid, checking environment variable...")
    
    # Fallback to environment variable
    connection_string = os.environ.get('IOTHUB_DEVICE_CONNECTION_STRING')
    if not connection_string:
        raise ValueError(
            "No connection string found! Please set the IOTHUB_DEVICE_CONNECTION_STRING environment variable "
            "or add it to config.json"
        )
    
    return connection_string

# Continuously listens for speech input to recognize and send as text to Azure IoT Hub
async def chat_with_backend():
    device_client = None
    try:
        # Load config.json
        config = load_config()
        
        # Get IoT Hub connection string
        connection_string = load_connection_string()
        
        # Create IoT Hub client
        device_client = await create_iot_hub_client(connection_string)
        
        # Create speech config and audio config
        speech_config = speechsdk.SpeechConfig(subscription=config.AzureCognitiveServices.Key, 
                                           region=config.AzureCognitiveServices.Region)
        audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        # Set speech recognition language
        speech_config.speech_recognition_language = config.AzureCognitiveServices.SpeechRecognitionLanguage
        
        ending_punctuations = (".", "?", "!", ";")
        if (speech_config.speech_recognition_language == "zh-CN"):
            ending_punctuations = ("。", "？", "！", "；", "")

        # Set speech synthesis voice name
        speech_config.speech_synthesis_voice_name = config.AzureCognitiveServices.SpeechSynthesisVoiceName
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

        # Set keyword recognition model
        kws_model = speechsdk.KeywordRecognitionModel(config.AzureCognitiveServices.WakePhraseModel)
        conversation = []
        
        print("Smart Speaker is ready! Say '{}' to start.".format(config.AzureCognitiveServices.WakeWord))
        
        while True:
            # Create a fresh speech recognizer for each iteration
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
            
            try:
                # Detect keyword
                if (not await detect_keyword(speech_recognizer, kws_model, config.AzureCognitiveServices.WakeWord)):
                    continue

                # Get audio from the microphone and then send it to the TTS service.
                loop = asyncio.get_running_loop()
                speech_recognition_result = await loop.run_in_executor(None, speech_recognizer.recognize_once_async().get)

                # If speech is recognized, send it to IoT Hub and listen for the response.
                if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    if speech_recognition_result.text == config.AzureCognitiveServices.StopWord: 
                        print("Conversation ended.")
                        break

                    print("Recognized speech: {}".format(speech_recognition_result.text))

                    # Create queue for response messages
                    queue = asyncio.Queue()
                    
                    # Send to IoT Hub and process response
                    await send_to_iot_hub_and_receive(
                        device_client,
                        speech_recognition_result.text,
                        conversation,
                        queue,
                        ending_punctuations
                    )

                    # Speak the response
                    await text_to_speech_async(speech_synthesizer, queue)
                    
                elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                    print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
                elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = speech_recognition_result.cancellation_details
                    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                    if cancellation_details.reason == speechsdk.CancellationReason.Error:
                        print("Error details: {}".format(cancellation_details.error_details))
            except Exception as e:
                print(f"Error in speech recognition loop: {e}")
            finally:
                # Ensure recognizer is properly cleaned up in all cases
                if 'speech_recognizer' in locals():
                    speech_recognizer.recognized.disconnect_all()
                    speech_recognizer.canceled.disconnect_all()
    except Exception as e:
        print(f"Error in chat_with_backend: {e}")
    finally:
        # Disconnect IoT Hub client when done
        if device_client:
            await device_client.disconnect()
            print("Disconnected from IoT Hub")

if __name__ == '__main__':
    try:
        asyncio.run(chat_with_backend())
    except Exception as err:
        print("Encountered exception. {}".format(err))