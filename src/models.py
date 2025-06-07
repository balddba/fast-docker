"""Database models for Docker host and stack management.

This module defines SQLModel-based models for managing Docker hosts and their
associated Docker Compose stacks. It provides two main models:
- Host: Represents a Docker host with various connection methods (Docker API or SSH)
- Stack: Represents a Docker Compose stack associated with a specific host

The models use SQLModel for database integration and provide type hints for better
IDE support and code safety.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Stack(SQLModel, table=True):
    """Docker Compose stack configuration model.

    This model represents a Docker Compose stack that can be deployed to a host.
    Each stack is associated with a specific host and contains information about
    the location of the compose file on that host.

    Attributes:
        id (Optional[int]): Primary key for the stack.
        name (str): Name of the stack for identification.
        compose_file (str): Path to the docker-compose.yml file on the host.
        host_id (int): Foreign key reference to the host where this stack is deployed.
        host (Optional[Host]): Relationship reference to the associated host object.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    compose_file: str  # path to the docker-compose.yml on the host
    host_id: int = Field(foreign_key="host.id")

    host: Optional["Host"] = Relationship(back_populates="stacks")


class Host(SQLModel, table=True):
    """Docker host configuration model.

    This model represents a Docker host that can be managed either through direct
    Docker API access or via SSH connection. It supports both connection methods
    and includes optional sudo configuration for SSH connections.

    Attributes:
        id (Optional[int]): Primary key for the host.
        name (str): Friendly name for the host.
        host (str): Hostname or IP address of the Docker host.
        connection_type (str): Type of connection to use ("docker" or "ssh").
        docker_url (Optional[str]): Docker daemon URL for API connections.
        ssh_user (Optional[str]): Username for SSH connections.
        ssh_key_filename (Optional[str]): Path to SSH private key file.
        ssh_port (Optional[int]): SSH port number, defaults to 22.
        sudo_user (Optional[str]): Username to use for sudo commands.
        sudo_password (Optional[str]): Password for sudo operations.

    Note:
        For SSH connections, at least ssh_user and ssh_key_filename should be provided.
        For Docker API connections, docker_url must be provided.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    host: str
    connection_type: str  # "docker" or "ssh"
    docker_url: Optional[str] = None
    ssh_user: Optional[str] = None
    ssh_key_filename: Optional[str] = None
    ssh_port: Optional[int] = 22
    sudo_user: Optional[str] = None
    sudo_password: Optional[str] = None