package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// User represents a user in the system
type User struct {
	ID        uuid.UUID `gorm:"type:uuid;primary_key"`
	CreatedAt time.Time
	UpdatedAt time.Time
	DeletedAt *time.Time `gorm:"index"`
}

// BeforeCreate will set a UUID rather than numeric ID
func (u *User) BeforeCreate(tx *gorm.DB) error {
	if u.ID == uuid.Nil {
		u.ID = uuid.New()
	}
	return nil
}

// Conversation represents a chat conversation
type Conversation struct {
	ID            uuid.UUID `gorm:"type:uuid;primary_key"`
	Title         string
	CreatedAt     time.Time
	UpdatedAt     time.Time
	DeletedAt     *time.Time `gorm:"index"`
	LastMessageAt time.Time
	Messages      []Message `gorm:"foreignKey:ConversationID"`
}

// BeforeCreate will set a UUID rather than numeric ID
func (c *Conversation) BeforeCreate(tx *gorm.DB) error {
	if c.ID == uuid.Nil {
		c.ID = uuid.New()
	}
	return nil
}

// Message represents a single message in a conversation
type Message struct {
	ID             uuid.UUID `gorm:"type:uuid;primary_key"`
	ConversationID uuid.UUID `gorm:"type:uuid;index"`
	Role           string    // "user" or "assistant"
	Content        string    `gorm:"type:text"`
	CreatedAt      time.Time
	UpdatedAt      time.Time
	AudioFile      string `gorm:"type:varchar(255)"`
}

// BeforeCreate will set a UUID rather than numeric ID
func (m *Message) BeforeCreate(tx *gorm.DB) error {
	if m.ID == uuid.Nil {
		m.ID = uuid.New()
	}
	return nil
}

// UserSettings represents user preferences
type UserSettings struct {
	ID                   uuid.UUID `gorm:"type:uuid;primary_key"`
	UserID               uuid.UUID `gorm:"type:uuid;unique"`
	SelectedModel        string    `gorm:"type:varchar(50);default:'gpt-4'"`
	VoiceSettings        string    `gorm:"type:json"` // JSON field for voice settings
	AssistantPersonality string    `gorm:"type:text"`
	CreatedAt            time.Time
	UpdatedAt            time.Time
}

// BeforeCreate will set a UUID rather than numeric ID
func (us *UserSettings) BeforeCreate(tx *gorm.DB) error {
	if us.ID == uuid.Nil {
		us.ID = uuid.New()
	}
	return nil
}

// VoiceSettingsData represents the structure of the VoiceSettings JSON field
type VoiceSettingsData struct {
	Gender string  `json:"gender"`
	Accent string  `json:"accent"`
	Speed  float64 `json:"speed"`
}
