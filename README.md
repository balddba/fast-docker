

# Remote Docker Manager API
A FastAPI-based REST API service for managing Docker hosts, containers, and Docker Compose stacks remotely. The project provides a robust interface for managing Docker resources across multiple hosts using both direct Docker API and SSH-based connections.
## Key Features
### Host Management
- Add, list, retrieve, and delete Docker hosts
- Support for both direct Docker API and SSH-based connections
- Secure storage of host configurations in a database

### Container Operations
- List containers across hosts
- Start containers remotely
- Container status monitoring

### Docker Compose Stack Management
- Create and manage Docker Compose stacks
- Stack operations support:
    - Starting stacks () `up`
    - Stopping stacks () `down`
    - Listing stack containers () `ps`
    - Restarting stack services

## Technical Stack
- **Framework**: FastAPI
- **Database**: SQLModel (SQL database with Python type annotations)
- **Dependency Management**: uv.lock
- **Key Components**:
    - : Handles Docker Compose operations `ComposeManager`
    - : Manages Docker operations on remote hosts `DockerManager`
    - `Models`: SQLModel-based data models for Hosts and Stacks

## Architecture
The project follows a clean architecture with clear separation of concerns:
1. REST API layer (FastAPI endpoints)
2. Business logic layer (Managers)
3. Data persistence layer (SQLModel)
4. Infrastructure layer (Docker/SSH communication)

 Quick Start

1. Start the API server:
```bash uvicorn main:app --reload```

2. The API will be available at `http://localhost:8000`

3. Access the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### Host Management
- `POST /hosts` - Add a new Docker host
- `GET /hosts` - List all registered hosts
- `GET /hosts/{host_id}` - Get specific host details
- `DELETE /hosts/{host_id}` - Remove a host

### Container Operations
- `GET /hosts/{host_id}/containers` - List containers on a host
- `POST /hosts/{host_id}/containers/start/{container_id}` - Start a container

### Stack Management
- `POST /hosts/{host_id}/stacks` - Create a new stack
- `GET /hosts/{host_id}/stacks` - List all stacks on a host
- `POST /stacks/{stack_id}/up` - Start a stack
- `POST /stacks/{stack_id}/down` - Stop a stack
- `GET /stacks/{stack_id}/ps` - List stack containers

## Dependencies

- `docker` - Docker SDK for Python
- `docker-composer-v2` - Docker Compose operations
- `docker-manager` - Docker management utilities
- `fabric` - SSH operations
- `fastapi` - FastAPI framework
- `sqlmodel` - SQL database with Python type annotations
- `uvicorn` - ASGI server
- `loguru` - Logging utility
