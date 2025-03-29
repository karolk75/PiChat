package models

import (
	"fmt"

	"github.com/karolk75/PiChat/Backend/internal/config"
	"gorm.io/driver/sqlserver"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// InitDB initializes the database connection
func InitDB(cfg *config.Config) (*gorm.DB, error) {
	// Construct the connection string for SQL Server
	dsn := fmt.Sprintf("sqlserver://%s:%s@%s:%s?database=%s",
		cfg.DBUser,
		cfg.DBPassword,
		cfg.DBHost,
		cfg.DBPort,
		cfg.DBName,
	)

	// Set GORM logger config based on environment
	var logLevel logger.LogLevel
	if cfg.Environment == "development" {
		logLevel = logger.Info
	} else {
		logLevel = logger.Error
	}

	// Configure GORM
	gormConfig := &gorm.Config{
		Logger: logger.Default.LogMode(logLevel),
	}

	// Connect to the database
	db, err := gorm.Open(sqlserver.Open(dsn), gormConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Get the underlying SQL DB object
	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("failed to get SQL DB: %w", err)
	}

	// Set connection pool settings
	sqlDB.SetMaxIdleConns(10)
	sqlDB.SetMaxOpenConns(100)

	return db, nil
}

// RunMigrations runs all database migrations
func RunMigrations(db *gorm.DB) error {
	// Auto migrate all models
	err := db.AutoMigrate(
		&User{},
		&Conversation{},
		&Message{},
		&UserSettings{},
	)

	if err != nil {
		return fmt.Errorf("failed to run migrations: %w", err)
	}

	return nil
}
