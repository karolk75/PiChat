# import azure.cognitiveservices.speech as speechsdk
# import logging
# import asyncio
# import os
# import tempfile
# from pathlib import Path
# from ..config import settings

# logger = logging.getLogger(__name__)

# def get_speech_config():
#     """Create a speech config object with Azure credentials"""
#     if not settings.AZURE_SPEECH_KEY or not settings.AZURE_SPEECH_REGION:
#         logger.error("Azure Speech Service credentials not configured")
#         raise ValueError("Azure Speech Service is not properly configured")
    
#     speech_config = speechsdk.SpeechConfig(
#         subscription=settings.AZURE_SPEECH_KEY,
#         region=settings.AZURE_SPEECH_REGION
#     )
#     return speech_config

# async def text_to_speech(text: str, voice_gender: str = "female", voice_accent: str = "polish") -> bytes:
#     """Convert text to speech using Azure Speech Services"""
#     try:
#         # Map voice parameters to Azure voice names
#         voice_mapping = {
#             ("female", "polish"): "pl-PL-AgnieszkaNeural",
#             ("male", "polish"): "pl-PL-MarekNeural",
#             ("female", "us"): "en-US-JennyNeural",
#             ("male", "us"): "en-US-GuyNeural",
#             ("female", "uk"): "en-GB-SoniaNeural",
#             ("male", "uk"): "en-GB-RyanNeural"
#         }
        
#         # Get voice name from mapping
#         voice_name = voice_mapping.get((voice_gender, voice_accent), "pl-PL-AgnieszkaNeural")
        
#         # Set up Azure Speech config
#         speech_config = get_speech_config()
#         speech_config.speech_synthesis_voice_name = voice_name
        
#         # Create a temporary file to store the audio
#         temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
#         temp_file.close()
        
#         # Set up audio output to wave file
#         audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)
        
#         # Create speech synthesizer
#         synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
#         # Convert text to speech
#         loop = asyncio.get_event_loop()
#         result = await loop.run_in_executor(None, lambda: synthesizer.speak_text_async(text).get())
        
#         # Check result
#         if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#             # Read the audio data
#             with open(temp_file.name, "rb") as audio_file:
#                 audio_data = audio_file.read()
            
#             # Clean up the temporary file
#             os.unlink(temp_file.name)
            
#             return audio_data
#         else:
#             logger.error(f"Speech synthesis failed: {result.reason}")
#             if result.reason == speechsdk.ResultReason.Canceled:
#                 cancellation_details = speechsdk.CancellationDetails(result)
#                 logger.error(f"Speech synthesis canceled: {cancellation_details.reason}")
#                 logger.error(f"Error details: {cancellation_details.error_details}")
            
#             # Clean up the temporary file
#             os.unlink(temp_file.name)
#             raise Exception("Speech synthesis failed")
    
#     except Exception as e:
#         logger.error(f"Error in text_to_speech: {str(e)}")
#         raise

# async def speech_to_text(audio_data: bytes) -> str:
#     """Convert speech to text using Azure Speech Services"""
#     try:
#         # Set up Azure Speech config
#         speech_config = get_speech_config()
        
#         # Create a temporary file to store the audio
#         temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
#         temp_file.write(audio_data)
#         temp_file.close()
        
#         # Set up audio input from wave file
#         audio_config = speechsdk.audio.AudioConfig(filename=temp_file.name)
        
#         # Create speech recognizer
#         recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
#         # Convert speech to text
#         loop = asyncio.get_event_loop()
#         result = await loop.run_in_executor(None, lambda: recognizer.recognize_once())
        
#         # Clean up the temporary file
#         os.unlink(temp_file.name)
        
#         # Check result
#         if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#             return result.text
#         else:
#             logger.error(f"Speech recognition failed: {result.reason}")
#             if result.reason == speechsdk.ResultReason.Canceled:
#                 cancellation_details = speechsdk.CancellationDetails(result)
#                 logger.error(f"Speech recognition canceled: {cancellation_details.reason}")
#                 logger.error(f"Error details: {cancellation_details.error_details}")
            
#             raise Exception("Speech recognition failed")
    
#     except Exception as e:
#         logger.error(f"Error in speech_to_text: {str(e)}")
#         raise 