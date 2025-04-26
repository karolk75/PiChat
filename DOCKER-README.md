# Docker Setup for PiChat

This document provides instructions for setting up and running PiChat using Docker.

## Prerequisites

Before you begin, make sure you have the following tools installed on your system:

- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)

## Components

The PiChat application consists of the following containers:

1. **pichat-backend** - FastAPI backend that provides WebSocket API and integrations with Azure services
2. **db** - PostgreSQL database for storing conversations and user data
3. **pgadmin** (optional) - Administration tool for PostgreSQL database

## Configuration

Create a `.env` file in the root directory with the following variables:

```
# Server configuration
SERVER_PORT=8080
API_TOKEN=your_secure_token_here
ENVIRONMENT=development

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT_GPT4=your_gpt4_deployment_name
AZURE_OPENAI_DEPLOYMENT_GPT35=your_gpt35_deployment_name

# Azure Speech configuration
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_speech_region

# Database configuration
DB_NAME=pichat
DB_USER=pichat_admin
DB_PASSWORD=secure_password
DB_PORT=5432

# pgAdmin configuration (optional)
PGADMIN_EMAIL=admin@pichat.com
PGADMIN_PASSWORD=admin
PGADMIN_PORT=5050
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

- Backend API: http://localhost:8080
- Backend API Documentation: http://localhost:8080/docs
- PgAdmin (if enabled): http://localhost:5050

## Database Management with pgAdmin

1. Access pgAdmin at http://localhost:5050
2. Login with the credentials specified in the `.env` file
3. Add a new server with the following details:
   - Name: PiChat
   - Host: db
   - Port: 5432
   - Username: [DB_USER from .env]
   - Password: [DB_PASSWORD from .env]

## Development Workflow

During development, you can use the following commands:

- View logs from all containers:
  ```bash
  docker-compose logs -f
  ```

- View logs from a specific container:
  ```bash
  docker-compose logs -f pichat-backend
  ```

- Restart a specific container:
  ```bash
  docker-compose restart pichat-backend
  ```

- Rebuild and restart containers after code changes:
  ```bash
  docker-compose up -d --build
  ```

## Data Persistence

The following data is persisted using Docker volumes:

- **postgres-data**: PostgreSQL database files
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
   docker-compose logs pichat-backend
   ```

### Database Issues

If the application can't connect to the database:

1. Check the database container is running:
   ```bash
   docker-compose ps db
   ```

2. Verify database environment variables in `.env` match those in `docker-compose.yml`

3. Check database logs:
   ```bash
   docker-compose logs db
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