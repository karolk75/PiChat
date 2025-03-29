package websocket

import (
	"sync"

	"github.com/karolk75/PiChat/Backend/internal/config"
	"github.com/karolk75/PiChat/Backend/pkg/azure"
	"github.com/karolk75/PiChat/Backend/pkg/logger"
	"gorm.io/gorm"
)

// Hub maintains the set of active clients and broadcasts messages to clients
type Hub struct {
	// Registered clients
	clients map[*Client]bool

	// Inbound messages from clients
	broadcast chan []byte

	// Register requests from clients
	register chan *Client

	// Unregister requests from clients
	unregister chan *Client

	// Mutex for thread-safe operations
	mutex sync.Mutex

	// Database connection
	db *gorm.DB

	// Logger
	logger *logger.Logger

	// Config
	config *config.Config

	// Services
	services *Services
}

// NewHub creates a new Hub
func NewHub(db *gorm.DB, logger *logger.Logger, config *config.Config) *Hub {
	// Initialize services
	openAIService := azure.NewOpenAIService(config, logger)
	speechService := azure.NewSpeechService(config, logger)

	services := &Services{
		OpenAI: openAIService,
		Speech: speechService,
	}

	return &Hub{
		broadcast:  make(chan []byte),
		register:   make(chan *Client),
		unregister: make(chan *Client),
		clients:    make(map[*Client]bool),
		db:         db,
		logger:     logger,
		config:     config,
		services:   services,
	}
}

// Run starts the hub's main loop
func (h *Hub) Run() {
	for {
		select {
		case client := <-h.register:
			h.mutex.Lock()
			h.clients[client] = true
			h.mutex.Unlock()
			h.logger.Info("client connected")

		case client := <-h.unregister:
			h.mutex.Lock()
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				close(client.send)
				h.logger.Info("client disconnected")
			}
			h.mutex.Unlock()

		case message := <-h.broadcast:
			h.mutex.Lock()
			for client := range h.clients {
				select {
				case client.send <- message:
				default:
					close(client.send)
					delete(h.clients, client)
				}
			}
			h.mutex.Unlock()
		}
	}
}

// BroadcastToAll sends a message to all connected clients
func (h *Hub) BroadcastToAll(message []byte) {
	h.broadcast <- message
}

// BroadcastTo sends a message to a specific client
func (h *Hub) BroadcastTo(client *Client, message []byte) {
	select {
	case client.send <- message:
	default:
		h.mutex.Lock()
		close(client.send)
		delete(h.clients, client)
		h.mutex.Unlock()
	}
}

// GetClient retrieves a client by user ID
func (h *Hub) GetClient(userID string) *Client {
	h.mutex.Lock()
	defer h.mutex.Unlock()

	for client := range h.clients {
		if client.userID == userID {
			return client
		}
	}

	return nil
}

// GetClientCount returns the number of connected clients
func (h *Hub) GetClientCount() int {
	h.mutex.Lock()
	defer h.mutex.Unlock()
	return len(h.clients)
}
