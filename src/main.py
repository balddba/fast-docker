"""FastAPI-based REST API for managing Docker hosts and containers.

This module provides the main FastAPI application that serves as a REST API for managing
Docker hosts, containers, and Docker Compose stacks. It includes endpoints for host
management, container operations, and stack management.

The API uses SQLModel for database operations and provides a clean interface for
managing Docker resources across multiple hosts using both direct Docker API
and SSH-based connections.
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import Stack, Host
from db import init_db, get_session
from docker_manager import DockerManager
from compose_manager import ComposeManager
import json

app = FastAPI(title="Remote Docker Manager with DB")
init_db()

# --- Host Management ---

@app.post("/hosts", response_model=Host)
def add_host(host: Host, session: Session = Depends(get_session)) -> Host:
    """Create a new Docker host in the system.

    Args:
        host (Host): Host object containing connection details and configuration.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        Host: The created host object with assigned ID.
    """
    session.add(host)
    session.commit()
    session.refresh(host)
    return host

@app.get("/hosts", response_model=List[Host])
def list_hosts(session: Session = Depends(get_session)) -> List[Host]:
    """Retrieve all registered Docker hosts.

    Args:
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        List[Host]: List of all registered hosts.
    """
    return session.exec(select(Host)).all()

@app.get("/hosts/{host_id}", response_model=Host)
def get_host(host_id: int, session: Session = Depends(get_session)) -> Host:
    """Retrieve a specific Docker host by ID.

    Args:
        host_id (int): ID of the host to retrieve.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        Host: The requested host object.

    Raises:
        HTTPException: If the host with specified ID is not found (404).
    """
    host = session.get(Host, host_id)
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host

@app.delete("/hosts/{host_id}")
def delete_host(host_id: int, session: Session = Depends(get_session)) -> dict:
    """Delete a Docker host from the system.

    Args:
        host_id (int): ID of the host to delete.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        dict: Confirmation message.

    Raises:
        HTTPException: If the host with specified ID is not found (404).
    """
    host = session.get(Host, host_id)
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    session.delete(host)
    session.commit()
    return {"message": "Host deleted"}

# --- Container Operations Using Host ID ---

@app.get("/hosts/{host_id}/containers")
def list_containers(host_id: int, session: Session = Depends(get_session)) -> List[dict]:
    """List all containers on a specific host.

    Args:
        host_id (int): ID of the host to list containers from.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        List[dict]: List of containers with their details (ID, name, status).
    """
    host = session.get(Host, host_id)
    manager = DockerManager(host)
    if host.connection_type == "docker":
        client = manager.get_docker_client()
        return [{"id": c.short_id, "name": c.name, "status": c.status} 
                for c in client.containers.list(all=True)]
    else:
        output = manager.run_ssh_command("docker ps -a --format '{{json .}}'")
        return [json.loads(line) for line in output.splitlines()]

@app.post("/hosts/{host_id}/containers/start/{container_id}")
def start_container(host_id: int, container_id: str, 
                   session: Session = Depends(get_session)) -> dict:
    """Start a specific container on a host.

    Args:
        host_id (int): ID of the host where the container is located.
        container_id (str): ID or name of the container to start.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        dict: Confirmation message.
    """
    host = session.get(Host, host_id)
    manager = DockerManager(host)
    if host.connection_type == "docker":
        client = manager.get_docker_client()
        container = client.containers.get(container_id)
        container.start()
    else:
        manager.run_ssh_command(f"docker start {container_id}")
    return {"message": f"Started container {container_id}"}

@app.post("/hosts/{host_id}/stacks", response_model=Stack)
def create_stack(host_id: int, stack: Stack, 
                session: Session = Depends(get_session)) -> Stack:
    """Create a new Docker Compose stack for a specific host.

    Args:
        host_id (int): ID of the host where the stack will be created.
        stack (Stack): Stack configuration including compose file path.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        Stack: The created stack object.

    Raises:
        HTTPException: If the host with a specified ID is not found (404).
    """
    host = session.get(Host, host_id)
    if not host:
        raise HTTPException(404, "Host not found")
    stack.host_id = host_id
    session.add(stack)
    session.commit()
    session.refresh(stack)
    return stack

@app.get("/hosts/{host_id}/stacks", response_model=List[Stack])
def list_stacks(host_id: int, session: Session = Depends(get_session)) -> List[Stack]:
    """List all Docker Compose stacks for a specific host.

    Args:
        host_id (int): ID of the host to list stacks from.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        List[Stack]: List of stacks associated with the host.
    """
    return session.exec(select(Stack).where(Stack.host_id == host_id)).all()

@app.post("/stacks/{stack_id}/up")
def stack_up(stack_id: int, session: Session = Depends(get_session)):
    """Start up a Docker Compose stack.

    Args:
        stack_id (int): ID of the stack to start.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        Any: Result of the docker-compose up operation.

    Raises:
        HTTPException: If the stack with specified ID is not found (404).
    """
    stack = session.get(Stack, stack_id)
    if not stack:
        raise HTTPException(404, "Stack not found")
    host = session.get(Host, stack.host_id)
    return ComposeManager(stack, host).up()

@app.post("/stacks/{stack_id}/down")
def stack_down(stack_id: int, session: Session = Depends(get_session)):
    """Stop and remove a Docker Compose stack.

    Args:
        stack_id (int): ID of the stack to stop.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        Any: Result of the docker-compose down operation.

    Raises:
        HTTPException: If the stack with specified ID is not found (404).
    """
    stack = session.get(Stack, stack_id)
    if not stack:
        raise HTTPException(404, "Stack not found")
    host = session.get(Host, stack.host_id)
    return ComposeManager(stack, host).down()

@app.get("/stacks/{stack_id}/ps")
def stack_ps(stack_id: int, session: Session = Depends(get_session)):
    """List containers in a Docker Compose stack.

    Args:
        stack_id (int): ID of the stack to list containers from.
        session (Session): Database session provided by FastAPI dependency.

    Returns:
        Any: Result of the docker-compose ps operation.

    Raises:
        HTTPException: If the stack with specified ID is not found (404).
    """
    stack = session.get(Stack, stack_id)
    if not stack:
        raise HTTPException(404, "Stack not found")
    host = session.get(Host, stack.host_id)
    return ComposeManager(stack, host).ps()