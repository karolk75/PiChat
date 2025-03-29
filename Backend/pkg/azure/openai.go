package azure

import (
	"context"
	"fmt"
	"time"

	"github.com/karolk75/PiChat/Backend/internal/config"
	"github.com/karolk75/PiChat/Backend/pkg/logger"
)

// OpenAIService handles interactions with Azure OpenAI
type OpenAIService struct {
	config *config.Config
	logger *logger.Logger
}

// NewOpenAIService creates a new OpenAI service instance
func NewOpenAIService(config *config.Config, logger *logger.Logger) *OpenAIService {
	return &OpenAIService{
		config: config,
		logger: logger,
	}
}

// CompletionRequest represents a request for OpenAI completion
type CompletionRequest struct {
	Model     string    `json:"model"`
	Messages  []Message `json:"messages"`
	MaxTokens int       `json:"max_tokens,omitempty"`
}

// Message represents a message in a completion request
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// CompletionResponse represents the response from an OpenAI completion
type CompletionResponse struct {
	ID      string    `json:"id"`
	Object  string    `json:"object"`
	Created int64     `json:"created"`
	Choices []Choice  `json:"choices"`
	Usage   UsageInfo `json:"usage"`
}

// Choice represents a completion choice
type Choice struct {
	Index        int     `json:"index"`
	Message      Message `json:"message"`
	FinishReason string  `json:"finish_reason"`
}

// UsageInfo represents token usage information
type UsageInfo struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

// CreateCompletion creates a completion (mock implementation for development)
func (s *OpenAIService) CreateCompletion(ctx context.Context, req CompletionRequest) (*CompletionResponse, error) {
	// For development, we'll just return a mock response
	// In production, this would call the actual Azure OpenAI API
	s.logger.Info("Mock OpenAI completion requested")

	// Simulate some processing time
	time.Sleep(500 * time.Millisecond)

	// Create a mock response
	return &CompletionResponse{
		ID:      "mock-completion-id",
		Object:  "chat.completion",
		Created: time.Now().Unix(),
		Choices: []Choice{
			{
				Index: 0,
				Message: Message{
					Role:    "assistant",
					Content: fmt.Sprintf("This is a mock response from the OpenAI service. You asked about: %s", getLastUserMessage(req.Messages)),
				},
				FinishReason: "stop",
			},
		},
		Usage: UsageInfo{
			PromptTokens:     100,
			CompletionTokens: 50,
			TotalTokens:      150,
		},
	}, nil
}

// StreamCompletion creates a streaming completion
func (s *OpenAIService) StreamCompletion(ctx context.Context, req CompletionRequest, callback func(string, bool) error) error {
	// For development, we'll simulate a streaming response
	s.logger.Info("Mock OpenAI streaming completion requested")

	// Simulate response
	mockResponse := fmt.Sprintf("This is a mock streaming response from the OpenAI service. You asked about: %s", getLastUserMessage(req.Messages))

	// Stream each word with a delay
	words := splitIntoWords(mockResponse)
	for i, word := range words {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			isLast := i == len(words)-1
			if err := callback(word+" ", isLast); err != nil {
				return err
			}
			// Simulate streaming delay
			time.Sleep(100 * time.Millisecond)
		}
	}

	return nil
}

// Helper functions
func getLastUserMessage(messages []Message) string {
	for i := len(messages) - 1; i >= 0; i-- {
		if messages[i].Role == "user" {
			return messages[i].Content
		}
	}
	return ""
}

func splitIntoWords(text string) []string {
	var result []string
	var currentWord string

	for _, char := range text {
		if char == ' ' || char == '.' || char == ',' || char == '!' || char == '?' {
			if currentWord != "" {
				result = append(result, currentWord)
				currentWord = ""
			}
			result = append(result, string(char))
		} else {
			currentWord += string(char)
		}
	}

	if currentWord != "" {
		result = append(result, currentWord)
	}

	return result
}
