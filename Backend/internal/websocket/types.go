package websocket

import (
	"time"

	"github.com/google/uuid"
)

// WebSocketRequest represents an incoming WebSocket message
type WebSocketRequest struct {
	Action  string      `json:"action"`
	Payload interface{} `json:"payload"`
}

// WebSocketResponse represents an outgoing WebSocket message
type WebSocketResponse struct {
	Action  string      `json:"action"`
	Payload interface{} `json:"payload"`
}

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error string `json:"error"`
}

// ConversationPayload represents a conversation in responses
type ConversationPayload struct {
	ID            uuid.UUID `json:"id"`
	Title         string    `json:"title"`
	LastMessageAt time.Time `json:"last_message_at"`
}

// ConversationsListPayload represents the payload for the conversations list response
type ConversationsListPayload struct {
	Conversations []ConversationPayload `json:"conversations"`
}

// ConversationRequest represents a request to get, create, update, or delete a conversation
type ConversationRequest struct {
	ID    uuid.UUID `json:"id"`
	Title string    `json:"title"`
}

// MessagePayload represents a message in responses
type MessagePayload struct {
	ID             uuid.UUID `json:"id"`
	ConversationID uuid.UUID `json:"conversation_id"`
	Role           string    `json:"role"`
	Content        string    `json:"content"`
	CreatedAt      time.Time `json:"created_at"`
	IsAudio        bool      `json:"is_audio"`
	AudioURL       string    `json:"audio_url,omitempty"`
}

// MessagesListPayload represents the payload for the messages list response
type MessagesListPayload struct {
	Messages []MessagePayload `json:"messages"`
}

// MessageRequest represents a request to send a message
type MessageRequest struct {
	ConversationID uuid.UUID `json:"conversation_id"`
	Content        string    `json:"content"`
	IsAudio        bool      `json:"is_audio"`
}

// MessageStreamPayload represents a token in a streamed response
type MessageStreamPayload struct {
	ConversationID uuid.UUID `json:"conversation_id"`
	MessageID      uuid.UUID `json:"message_id"`
	Token          string    `json:"token"`
	Finished       bool      `json:"finished"`
}

// TypingIndicatorPayload represents a typing indicator notification
type TypingIndicatorPayload struct {
	ConversationID uuid.UUID `json:"conversation_id"`
	IsTyping       bool      `json:"is_typing"`
}

// VoiceSettingsPayload represents voice settings
type VoiceSettingsPayload struct {
	Gender string  `json:"gender"`
	Accent string  `json:"accent"`
	Speed  float64 `json:"speed"`
}

// UserSettingsPayload represents user settings
type UserSettingsPayload struct {
	SelectedModel        string               `json:"selected_model"`
	VoiceSettings        VoiceSettingsPayload `json:"voice_settings"`
	AssistantPersonality string               `json:"assistant_personality"`
}

// TextToSpeechRequest represents a request to convert text to speech
type TextToSpeechRequest struct {
	Text          string               `json:"text"`
	VoiceSettings VoiceSettingsPayload `json:"voice_settings"`
}

// SpeechToTextRequest represents a request to convert speech to text
type SpeechToTextRequest struct {
	AudioData string `json:"audio_data"` // Base64 encoded audio
}
