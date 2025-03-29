# Docker Setup for PiChat Backend

This document provides instructions for setting up the PiChat Backend using Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your system
- Access to Azure services (OpenAI, Speech) if using in production mode

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/karolk75/PiChat.git
   cd PiChat
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your specific configuration. At minimum, you should set:
   - `API_TOKEN` - A secure token for API access
   - Azure credentials if you're using Azure services

3. Start the Docker containers:
   ```bash
   docker-compose up -d
   ```

4. Access the services:
   - Backend API: `http://localhost:8080`
   - WebSocket: `ws://localhost:8080/ws`
   - pgAdmin (database management): `http://localhost:5050` (login with the credentials set in `.env`)

## Services

The Docker Compose setup includes the following services:

### pichat-backend

This is the main Go backend service that provides the WebSocket functionality and API endpoints.

- **Port**: 8080 (configurable via .env)
- **Volumes**: 
  - `./Backend:/app` - Maps the Backend directory for development
  - `backend-data:/root/data` - Persistent volume for data storage

### db (PostgreSQL)

PostgreSQL database for storing conversations, messages, and user settings.

- **Port**: 5432 (configurable via .env)
- **Default Credentials**:
  - Database: pichat
  - User: pichat_admin
  - Password: secure_password (change this in production)

### pgAdmin (Optional)

Web interface for managing the PostgreSQL database.

- **Port**: 5050 (configurable via .env)
- **Default Credentials**:
  - Email: admin@pichat.com
  - Password: admin (change this in production)

## Database Migration

The application should handle database migrations automatically on startup. If you need to manually run migrations or seed data, you can use the following command:

```bash
docker-compose exec pichat-backend ./api migrate
```

## Development Workflow

For development:

1. Make changes to the Go code in the Backend directory
2. Restart the backend service to apply changes:
   ```bash
   docker-compose restart pichat-backend
   ```

For hot-reloading during development, you may want to:
1. Install [Air](https://github.com/cosmtrek/air) for Go hot-reloading
2. Modify the Dockerfile to use Air in development mode

## Production Deployment

For production deployment:

1. Update the `.env` file with production settings:
   - Set `ENVIRONMENT=production`
   - Use strong passwords for database and API tokens
   - Configure Azure services with production credentials

2. Build and start the services:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

## Troubleshooting

### Cannot connect to the WebSocket

- Ensure ports are correctly mapped in docker-compose.yml
- Check that the backend service is running: `docker-compose ps`
- Verify logs for any errors: `docker-compose logs pichat-backend`

### Database connection issues

- Check if the database container is running: `docker-compose ps db`
- Verify database credentials in the .env file
- Inspect database logs: `docker-compose logs db`

## Maintenance

### Backup Database

```bash
docker-compose exec db pg_dump -U pichat_admin -d pichat > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker-compose exec -T db psql -U pichat_admin -d pichat
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs pichat-backend
``` 