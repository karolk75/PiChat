package websocket

import (
	"context"
	"encoding/json"
	"net/http"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"github.com/karolk75/PiChat/Backend/pkg/azure"
	"github.com/karolk75/PiChat/Backend/pkg/logger"
)

// Upgrader upgrades HTTP connections to WebSocket connections
var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	// Allow all origins for now - in production, this should be restricted
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

// Services holds all the service dependencies
type Services struct {
	OpenAI *azure.OpenAIService
	Speech *azure.SpeechService
}

// ServeWs handles WebSocket connections
func ServeWs(hub *Hub, w http.ResponseWriter, r *http.Request, logger *logger.Logger) {
	// Upgrade HTTP connection to WebSocket
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		logger.Error("Failed to upgrade connection: ", err)
		return
	}

	// Create a unique user ID for this connection
	// In a real authentication system, this would come from the token
	userID := r.URL.Query().Get("user_id")
	if userID == "" {
		userID = uuid.New().String()
	}

	// Create a new client
	client := NewClient(hub, conn, userID, logger)

	// Register client with hub
	hub.register <- client

	// Start goroutines for reading from and writing to the WebSocket
	go client.readPump()
	go client.writePump()
}

// handleMessage processes WebSocket messages from clients
func (h *Hub) handleMessage(client *Client, request WebSocketRequest) {
	// Log the received message (omit large payloads)
	h.logger.Info("Received message: " + request.Action)

	// Handle different message types
	switch request.Action {
	case "get_conversations":
		h.handleGetConversations(client)
	case "create_conversation":
		h.handleCreateConversation(client, request.Payload)
	case "get_conversation":
		h.handleGetConversation(client, request.Payload)
	case "update_conversation":
		h.handleUpdateConversation(client, request.Payload)
	case "delete_conversation":
		h.handleDeleteConversation(client, request.Payload)
	case "send_message":
		h.handleSendMessage(client, request.Payload)
	case "get_messages":
		h.handleGetMessages(client, request.Payload)
	case "get_settings":
		h.handleGetSettings(client)
	case "update_settings":
		h.handleUpdateSettings(client, request.Payload)
	case "text_to_speech":
		h.handleTextToSpeech(client, request.Payload)
	case "speech_to_text":
		h.handleSpeechToText(client, request.Payload)
	default:
		client.sendErrorResponse("unknown_action", "Unknown action: "+request.Action)
	}
}

// Handler implementations (these would be fully implemented in a real system)

func (h *Hub) handleGetConversations(client *Client) {
	// Example implementation - in a real system, this would fetch from the database
	conversations := []ConversationPayload{
		{
			ID:            uuid.New(),
			Title:         "Example Conversation",
			LastMessageAt: time.Now(),
		},
	}

	client.sendResponse("conversations_list", ConversationsListPayload{
		Conversations: conversations,
	})
}

func (h *Hub) handleCreateConversation(client *Client, payload interface{}) {
	// Parse the payload
	var request ConversationRequest
	if err := parsePayload(payload, &request); err != nil {
		client.sendErrorResponse("create_conversation", "Invalid request format")
		return
	}

	// Example implementation
	conversation := ConversationPayload{
		ID:            uuid.New(),
		Title:         request.Title,
		LastMessageAt: time.Now(),
	}

	client.sendResponse("conversation_created", conversation)
}

func (h *Hub) handleGetConversation(client *Client, payload interface{}) {
	var request ConversationRequest
	if err := parsePayload(payload, &request); err != nil {
		client.sendErrorResponse("get_conversation", "Invalid request format")
		return
	}

	// Example implementation
	conversation := ConversationPayload{
		ID:            request.ID,
		Title:         "Example Conversation",
		LastMessageAt: time.Now(),
	}

	client.sendResponse("conversation", conversation)
}

func (h *Hub) handleUpdateConversation(client *Client, payload interface{}) {
	var request ConversationRequest
	if err := parsePayload(payload, &request); err != nil {
		client.sendErrorResponse("update_conversation", "Invalid request format")
		return
	}

	// Example implementation
	conversation := ConversationPayload{
		ID:            request.ID,
		Title:         request.Title,
		LastMessageAt: time.Now(),
	}

	client.sendResponse("conversation_updated", conversation)
}

func (h *Hub) handleDeleteConversation(client *Client, payload interface{}) {
	var request ConversationRequest
	if err := parsePayload(payload, &request); err != nil {
		client.sendErrorResponse("delete_conversation", "Invalid request format")
		return
	}

	// Example implementation - just acknowledge deletion
	client.sendResponse("conversation_deleted", map[string]interface{}{
		"id": request.ID,
	})
}

func (h *Hub) handleSendMessage(client *Client, payload interface{}) {
	var request MessageRequest
	if err := parsePayload(payload, &request); err != nil {
		client.sendErrorResponse("send_message", "Invalid request format")
		return
	}

	// Create message
	messageID := uuid.New()

	// Acknowledge the message was received
	client.sendResponse("message_sent", map[string]interface{}{
		"id":              messageID,
		"conversation_id": request.ConversationID,
	})

	// Create a context with timeout for the AI response
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Start a goroutine to handle the AI response
	go func() {
		// Send typing indicator
		typingPayload := TypingIndicatorPayload{
			ConversationID: request.ConversationID,
			IsTyping:       true,
		}
		client.sendResponse("typing_indicator", typingPayload)

		// If we have OpenAI service configured, use it
		if h.services != nil && h.services.OpenAI != nil {
			// Create OpenAI request
			openAIReq := azure.CompletionRequest{
				Model: "gpt-4", // Use config or user settings in production
				Messages: []azure.Message{
					{
						Role:    "user",
						Content: request.Content,
					},
				},
			}

			// Stream the response
			err := h.services.OpenAI.StreamCompletion(ctx, openAIReq, func(token string, finished bool) error {
				streamPayload := MessageStreamPayload{
					ConversationID: request.ConversationID,
					MessageID:      messageID,
					Token:          token,
					Finished:       finished,
				}
				client.sendResponse("message_stream", streamPayload)
				return nil
			})

			if err != nil {
				h.logger.Error("Error streaming completion:", err)
				client.sendErrorResponse("completion_error", "Error generating AI response")
			}
		} else {
			// Fallback to mock implementation if service not available
			// Example AI response text
			responseText := "This is a simulated AI response to your message. In a real implementation, this would come from Azure OpenAI."

			// Stream the response token by token
			for i, char := range responseText {
				select {
				case <-ctx.Done():
					return
				default:
					// Send token
					streamPayload := MessageStreamPayload{
						ConversationID: request.ConversationID,
						MessageID:      messageID,
						Token:          string(char),
						Finished:       i == len(responseText)-1,
					}
					client.sendResponse("message_stream", streamPayload)

					// Small delay between tokens to simulate typing
					time.Sleep(50 * time.Millisecond)
				}
			}
		}

		// End typing indicator
		typingPayload.IsTyping = false
		client.sendResponse("typing_indicator", typingPayload)
	}()
}

func (h *Hub) handleGetMessages(client *Client, payload interface{}) {
	var request struct {
		ConversationID uuid.UUID `json:"conversation_id"`
	}
	if err := parsePayload(payload, &request); err != nil {
		client.sendErrorResponse("get_messages", "Invalid request format")
		return
	}

	// Example implementation
	messages := []MessagePayload{
		{
			ID:             uuid.New(),
			ConversationID: request.ConversationID,
			Role:           "user",
			Content:        "Example user message",
			CreatedAt:      time.Now().Add(-2 * time.Minute),
			IsAudio:        false,
		},
		{
			ID:             uuid.New(),
			ConversationID: request.ConversationID,
			Role:           "assistant",
			Content:        "Example assistant response",
			CreatedAt:      time.Now().Add(-1 * time.Minute),
			IsAudio:        false,
		},
	}

	client.sendResponse("messages_list", MessagesListPayload{
		Messages: messages,
	})
}

func (h *Hub) handleGetSettings(client *Client) {
	// Example implementation
	settings := UserSettingsPayload{
		SelectedModel: "gpt-4",
		VoiceSettings: VoiceSettingsPayload{
			Gender: "female",
			Accent: "polish",
			Speed:  1.0,
		},
		AssistantPersonality: "helpful and friendly",
	}

	client.sendResponse("settings", settings)
}

func (h *Hub) handleUpdateSettings(client *Client, payload interface{}) {
	var settings UserSettingsPayload
	if err := parsePayload(payload, &settings); err != nil {
		client.sendErrorResponse("update_settings", "Invalid request format")
		return
	}

	// Example implementation - just echo back the updated settings
	client.sendResponse("settings_updated", settings)
}

func (h *Hub) handleTextToSpeech(client *Client, payload interface{}) {
	var request TextToSpeechRequest
	if err := parsePayload(payload, &request); err != nil {
		client.sendErrorResponse("text_to_speech", "Invalid request format")
		return
	}

	// Create a context with timeout for the speech service
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// If we have Speech service configured, use it
	if h.services != nil && h.services.Speech != nil {
		voiceOptions := azure.VoiceOptions{
			Gender: request.VoiceSettings.Gender,
			Accent: request.VoiceSettings.Accent,
			Speed:  request.VoiceSettings.Speed,
		}

		audioBase64, err := h.services.Speech.TextToSpeech(ctx, request.Text, voiceOptions)
		if err != nil {
			h.logger.Error("Error in text-to-speech conversion:", err)
			client.sendErrorResponse("text_to_speech", "Error converting text to speech")
			return
		}

		client.sendResponse("text_to_speech_result", map[string]interface{}{
			"audio_data": audioBase64,
		})
	} else {
		// Fallback to mock implementation
		client.sendResponse("text_to_speech_result", map[string]interface{}{
			"audio_data": "base64_encoded_audio_would_be_here",
		})
	}
}

func (h *Hub) handleSpeechToText(client *Client, payload interface{}) {
	var request SpeechToTextRequest
	if err := parsePayload(payload, &request); err != nil {
		client.sendErrorResponse("speech_to_text", "Invalid request format")
		return
	}

	// Create a context with timeout for the speech service
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// If we have Speech service configured, use it
	if h.services != nil && h.services.Speech != nil {
		text, err := h.services.Speech.SpeechToText(ctx, request.AudioData)
		if err != nil {
			h.logger.Error("Error in speech-to-text conversion:", err)
			client.sendErrorResponse("speech_to_text", "Error converting speech to text")
			return
		}

		client.sendResponse("speech_to_text_result", map[string]interface{}{
			"text": text,
		})
	} else {
		// Fallback to mock implementation
		client.sendResponse("speech_to_text_result", map[string]interface{}{
			"text": "This is the transcribed text from the audio (mock implementation)",
		})
	}
}

// Helper function to parse payload
func parsePayload(payload interface{}, target interface{}) error {
	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	return json.Unmarshal(payloadBytes, target)
}
