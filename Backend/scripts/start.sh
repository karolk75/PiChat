#!/bin/bash

# Change to the root directory of the backend
cd "$(dirname "$0")/.."

# Ensure dependencies are up to date
go mod tidy

# Run the server
go run cmd/api/main.go 