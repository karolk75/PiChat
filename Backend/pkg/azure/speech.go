package azure

import (
	"context"
	"encoding/base64"
	"fmt"
	"math/rand"
	"time"

	"github.com/karolk75/PiChat/Backend/internal/config"
	"github.com/karolk75/PiChat/Backend/pkg/logger"
)

// SpeechService handles interactions with Azure Speech Service
type SpeechService struct {
	config *config.Config
	logger *logger.Logger
}

// VoiceOptions represents options for text-to-speech
type VoiceOptions struct {
	Gender string  `json:"gender"`
	Accent string  `json:"accent"`
	Speed  float64 `json:"speed"`
}

// NewSpeechService creates a new Speech service instance
func NewSpeechService(config *config.Config, logger *logger.Logger) *SpeechService {
	return &SpeechService{
		config: config,
		logger: logger,
	}
}

// TextToSpeech converts text to speech (mock implementation for development)
func (s *SpeechService) TextToSpeech(ctx context.Context, text string, options VoiceOptions) (string, error) {
	// In development, we'll just return a mock audio data
	// In production, this would call the actual Azure Speech API
	s.logger.Info("Mock Text-to-Speech conversion requested")

	// Simulate processing time
	time.Sleep(300 * time.Millisecond)

	// Generate random bytes to simulate audio data
	audioBytes := make([]byte, 100)
	rand.Read(audioBytes)

	// Convert to base64
	audioBase64 := base64.StdEncoding.EncodeToString(audioBytes)

	s.logger.Infof("Generated mock audio for text: %s with voice options: %+v", text, options)

	return audioBase64, nil
}

// SpeechToText converts speech to text (mock implementation for development)
func (s *SpeechService) SpeechToText(ctx context.Context, audioBase64 string) (string, error) {
	// In development, we'll just return mock text
	// In production, this would call the actual Azure Speech API
	s.logger.Info("Mock Speech-to-Text conversion requested")

	// Simulate processing time
	time.Sleep(500 * time.Millisecond)

	// Return a fixed response for testing
	return fmt.Sprintf("This is a mock transcription of audio (base64 length: %d)", len(audioBase64)), nil
}
