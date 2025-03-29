package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/joho/godotenv"
	"github.com/karolk75/PiChat/Backend/internal/config"
	"github.com/karolk75/PiChat/Backend/internal/middleware"
	"github.com/karolk75/PiChat/Backend/internal/models"
	"github.com/karolk75/PiChat/Backend/internal/websocket"
	"github.com/karolk75/PiChat/Backend/pkg/logger"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found or not valid: %v", err)
	}

	// Initialize logger
	logger := logger.NewLogger()
	logger.Info("Starting PiChat Backend Server")

	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		logger.Fatalf("Failed to load configuration: %v", err)
	}

	// Connect to database
	db, err := models.InitDB(cfg)
	if err != nil {
		logger.Fatalf("Failed to connect to database: %v", err)
	}

	// Run migrations
	if err := models.RunMigrations(db); err != nil {
		logger.Fatalf("Failed to run database migrations: %v", err)
	}

	// Create a new WebSocket hub
	hub := websocket.NewHub(db, logger, cfg)
	go hub.Run()

	// Set up HTTP server
	server := &http.Server{
		Addr:         fmt.Sprintf(":%s", cfg.ServerPort),
		Handler:      setupRoutes(hub, cfg, logger),
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Start the server in a goroutine
	go func() {
		logger.Infof("Server listening on port %s", cfg.ServerPort)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatalf("Could not listen on port %s: %v", cfg.ServerPort, err)
		}
	}()

	// Set up graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	// Block until a signal is received
	sig := <-quit
	logger.Infof("Server is shutting down: %v", sig)

	// Create a deadline for server shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Attempt to gracefully shut down the server
	if err := server.Shutdown(ctx); err != nil {
		logger.Fatalf("Server forced to shutdown: %v", err)
	}

	logger.Info("Server exited properly")
}

func setupRoutes(hub *websocket.Hub, cfg *config.Config, logger *logger.Logger) http.Handler {
	mux := http.NewServeMux()

	// Auth middleware
	authMiddleware := middleware.NewAuthMiddleware(cfg.APIToken)

	// WebSocket endpoint
	mux.HandleFunc("/ws", authMiddleware.Authenticate(
		func(w http.ResponseWriter, r *http.Request) {
			websocket.ServeWs(hub, w, r, logger)
		},
	))

	// Health check endpoint
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	return middleware.LoggingMiddleware(logger)(mux)
}
