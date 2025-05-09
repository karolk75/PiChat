# Docker Setup for PiChat

This document provides instructions for setting up and running PiChat using Docker.

## Prerequisites

Before you begin, make sure you have the following tools installed on your system:

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)

## Components

The PiChat application consists of the following containers:

1. **frontend** - React-based frontend that provides the user interface
2. **backend** - FastAPI backend that provides WebSocket API and integrations with Azure services

## Configuration

Create a `.env` file in the root directory with the following variables:

```
# Server configuration
SERVER_PORT=8080
FRONTEND_PORT=8501
API_TOKEN=your_secure_token_here
ENVIRONMENT=development

# Azure CosmosDB configuration
COSMOS_ENDPOINT=your_cosmos_db_endpoint
COSMOS_KEY=your_cosmos_db_key

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=your_api_version

# Azure IoT Hub configuration (optional)
IOT_HUB_NAME=your_iothub_name
IOT_HUB_HOST_NAME=your_iothub_hostname
IOT_HUB_CONSUMER_GROUP=backend
```

## Quick Start

To start all containers:

```bash
docker-compose up -d
```

To stop all containers:

```bash
docker-compose down
```

## Service Access

After starting the containers, you can access the following services:

- Frontend: http://localhost:8501
- Backend API: http://localhost:8080
- Backend API Documentation: http://localhost:8080/docs


## Development Workflow

During development, you can use the following commands:

- View logs from all containers:
  ```bash
  docker-compose logs -f
  ```

- View logs from a specific container:
  ```bash
  docker-compose logs -f backend
  ```

- Restart a specific container:
  ```bash
  docker-compose restart backend
  ```

- Rebuild and restart containers after code changes:
  ```bash
  docker-compose up -d --build
  ```

## Data Persistence

The following data is persisted using Docker volumes:

- **backend-data**: Backend application data (like temporary files)

## Troubleshooting

### Connection Issues

If you can't connect to the services, check that:

1. Docker containers are running:
   ```bash
   docker-compose ps
   ```

2. Container logs for errors:
   ```bash
   docker-compose logs frontend
   docker-compose logs backend
   ```

### Frontend Issues

If the frontend isn't working properly:

1. Check that the frontend container is running:
   ```bash
   docker-compose ps frontend
   ```
   
2. Look at the frontend logs:
   ```bash
   docker-compose logs frontend
   ```

## Advanced Configuration

### Custom Networks

By default, all services use the `pichat-network` bridge network. You can modify this in the `docker-compose.yml` file if needed.

### Production Deployment

For production, consider:

1. Changing default passwords and using secrets management
2. Using a reverse proxy like Nginx for SSL termination
3. Implementing proper backups for the database
4. Setting `ENVIRONMENT=production` to disable development features
5. Using Docker Swarm or Kubernetes for container orchestration 