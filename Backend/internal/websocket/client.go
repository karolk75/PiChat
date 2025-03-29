package websocket

import (
	"bytes"
	"encoding/json"
	"time"

	"github.com/gorilla/websocket"
	"github.com/karolk75/PiChat/Backend/pkg/logger"
)

const (
	// Time allowed to write a message to the client
	writeWait = 10 * time.Second

	// Time allowed to read the next pong message from the client
	pongWait = 60 * time.Second

	// Send pings to client with this period (must be less than pongWait)
	pingPeriod = (pongWait * 9) / 10

	// Maximum message size allowed from client
	maxMessageSize = 1024 * 1024 // 1MB
)

var (
	newline = []byte{'\n'}
	space   = []byte{' '}
)

// Client represents a single websocket client connection
type Client struct {
	hub    *Hub
	conn   *websocket.Conn
	send   chan []byte
	userID string
	logger *logger.Logger
}

// NewClient creates a new WebSocket client
func NewClient(hub *Hub, conn *websocket.Conn, userID string, logger *logger.Logger) *Client {
	return &Client{
		hub:    hub,
		conn:   conn,
		send:   make(chan []byte, 256),
		userID: userID,
		logger: logger,
	}
}

// readPump pumps messages from the websocket connection to the hub
func (c *Client) readPump() {
	defer func() {
		c.hub.unregister <- c
		c.conn.Close()
	}()

	c.conn.SetReadLimit(maxMessageSize)
	c.conn.SetReadDeadline(time.Now().Add(pongWait))
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(pongWait))
		return nil
	})

	for {
		_, message, err := c.conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				c.logger.Error("error: ", err)
			}
			break
		}
		message = bytes.TrimSpace(bytes.Replace(message, newline, space, -1))

		var request WebSocketRequest
		if err := json.Unmarshal(message, &request); err != nil {
			c.logger.Error("error unmarshaling message: ", err)
			c.sendErrorResponse("invalid_json", "Invalid JSON format")
			continue
		}

		// Send the request to the hub for processing
		c.hub.handleMessage(c, request)
	}
}

// writePump pumps messages from the hub to the websocket connection
func (c *Client) writePump() {
	ticker := time.NewTicker(pingPeriod)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			c.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if !ok {
				// The hub closed the channel
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			w, err := c.conn.NextWriter(websocket.TextMessage)
			if err != nil {
				return
			}
			w.Write(message)

			// Add queued messages to the current websocket message
			n := len(c.send)
			for i := 0; i < n; i++ {
				w.Write(newline)
				w.Write(<-c.send)
			}

			if err := w.Close(); err != nil {
				return
			}
		case <-ticker.C:
			c.conn.SetWriteDeadline(time.Now().Add(writeWait))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// sendResponse sends a response to the client
func (c *Client) sendResponse(action string, payload interface{}) {
	response := WebSocketResponse{
		Action:  action,
		Payload: payload,
	}

	responseBytes, err := json.Marshal(response)
	if err != nil {
		c.logger.Error("error marshaling response: ", err)
		return
	}

	c.send <- responseBytes
}

// sendErrorResponse sends an error response to the client
func (c *Client) sendErrorResponse(action string, message string) {
	errorPayload := ErrorResponse{
		Error: message,
	}

	c.sendResponse(action+"_error", errorPayload)
}
