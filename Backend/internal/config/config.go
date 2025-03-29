package config

import (
	"errors"
	"os"
)

// Config holds all configuration for the application
type Config struct {
	// Server configuration
	ServerPort  string
	APIToken    string
	Environment string

	// Azure OpenAI configuration
	AzureOpenAIEndpoint        string
	AzureOpenAIKey             string
	AzureOpenAIDeploymentGPT4  string
	AzureOpenAIDeploymentGPT35 string

	// Azure Speech configuration
	AzureSpeechKey    string
	AzureSpeechRegion string

	// Database configuration
	DBHost     string
	DBName     string
	DBUser     string
	DBPassword string
	DBPort     string
}

// LoadConfig loads configuration from environment variables
func LoadConfig() (*Config, error) {
	serverPort := os.Getenv("SERVER_PORT")
	if serverPort == "" {
		serverPort = "8080" // Default port
	}

	apiToken := os.Getenv("API_TOKEN")
	if apiToken == "" {
		return nil, errors.New("API_TOKEN environment variable is required")
	}

	environment := os.Getenv("ENVIRONMENT")
	if environment == "" {
		environment = "development" // Default environment
	}

	// Azure OpenAI configurations
	azureOpenAIEndpoint := os.Getenv("AZURE_OPENAI_ENDPOINT")
	azureOpenAIKey := os.Getenv("AZURE_OPENAI_KEY")
	azureOpenAIDeploymentGPT4 := os.Getenv("AZURE_OPENAI_DEPLOYMENT_GPT4")
	azureOpenAIDeploymentGPT35 := os.Getenv("AZURE_OPENAI_DEPLOYMENT_GPT35")

	// Check if Azure OpenAI is configured
	if azureOpenAIEndpoint == "" || azureOpenAIKey == "" {
		return nil, errors.New("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY environment variables are required")
	}

	// Azure Speech configurations
	azureSpeechKey := os.Getenv("AZURE_SPEECH_KEY")
	azureSpeechRegion := os.Getenv("AZURE_SPEECH_REGION")

	// Check if Azure Speech is configured
	if azureSpeechKey == "" || azureSpeechRegion == "" {
		return nil, errors.New("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables are required")
	}

	// Database configurations
	dbHost := os.Getenv("DB_HOST")
	dbName := os.Getenv("DB_NAME")
	dbUser := os.Getenv("DB_USER")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbPort := os.Getenv("DB_PORT")

	// Check if database is configured
	if dbHost == "" || dbName == "" || dbUser == "" || dbPassword == "" {
		return nil, errors.New("DB_HOST, DB_NAME, DB_USER, and DB_PASSWORD environment variables are required")
	}

	if dbPort == "" {
		dbPort = "1433" // Default SQL Server port
	}

	return &Config{
		ServerPort:  serverPort,
		APIToken:    apiToken,
		Environment: environment,

		AzureOpenAIEndpoint:        azureOpenAIEndpoint,
		AzureOpenAIKey:             azureOpenAIKey,
		AzureOpenAIDeploymentGPT4:  azureOpenAIDeploymentGPT4,
		AzureOpenAIDeploymentGPT35: azureOpenAIDeploymentGPT35,

		AzureSpeechKey:    azureSpeechKey,
		AzureSpeechRegion: azureSpeechRegion,

		DBHost:     dbHost,
		DBName:     dbName,
		DBUser:     dbUser,
		DBPassword: dbPassword,
		DBPort:     dbPort,
	}, nil
}
