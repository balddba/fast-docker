"""Docker management functionality for remote and local Docker hosts.

This module provides a unified interface for managing Docker operations across different
connection types (direct Docker API or SSH). It handles both direct Docker daemon
connections and SSH-based remote command execution.

Typical usage example:
    host = Host(name="prod-server", connection_type="ssh", host="prod.example.com")
    manager = DockerManager(host)
    manager.run_ssh_command("docker ps")

Dependencies:
    - fabric: For SSH connections and command execution
    - docker: For direct Docker API interactions
    - fastapi: For HTTP exception handling
    - models: For a Host data model
"""

from fabric import Connection, Config
import docker
from fastapi import HTTPException
from models import Host


class DockerManager:
    """Manages Docker operations for both direct API and SSH-based connections.

    This class provides a unified interface for executing Docker commands either
    through the Docker API or via SSH, depending on the host's connection type.

    Attributes:
        host (Host): Configuration for the Docker host, containing connection details
            and authentication information.
    """

    def __init__(self, host: Host):
        """Initialize the DockerManager with host configuration.

        Args:
            host (Host): Host configuration object containing connection details
                such as hostname, connection type, and authentication information.
        """
        self.host = host

    def get_docker_client(self) -> docker.DockerClient | None:
        """Creates a Docker client for direct API connections.

        Returns:
            docker.DockerClient | None: A Docker client instance if the connection type
                is 'docker', None if the connection type is SSH-based.

        Raises:
            HTTPException: If the connection type is 'docker' but no docker_url
                is provided in the host configuration.
        """
        if self.host.connection_type == "docker":
            if not self.host.docker_url:
                raise HTTPException(status_code=400, detail="Missing docker_url")
            return docker.DockerClient(base_url=self.host.docker_url)
        return None  # SSH-based

    def run_ssh_command(self, cmd: str) -> str:
        """Executes a command on the remote host via SSH.

        This method handles SSH connection setup, including sudo configuration
        if required, and executes the provided command on the remote host.

        Args:
            cmd (str): The command to execute on the remote host.

        Returns:
            str: The stdout output from the command execution, with whitespace trimmed.

        Raises:
            HTTPException: If the SSH connection fails or the command execution fails.
                Includes the original error message in the exception detail.

        Example:
            manager = DockerManager(host)
            output = manager.run_ssh_command("docker ps -a")
        """
        try:
            # Set up Fabric config with an optional sudo password
            config = Config(overrides={})
            if self.host.sudo_password:
                config = Config(overrides={
                    "sudo": {"password": self.host.sudo_password}
                })

            conn = Connection(
                host=self.host.host,
                user=self.host.ssh_user,
                port=self.host.ssh_port,
                connect_kwargs={"key_filename": self.host.ssh_key_filename},
                config=config
            )

            if self.host.sudo_user:
                result = conn.sudo(
                    cmd,
                    user=self.host.sudo_user,
                    hide=True
                )
            else:
                result = conn.run(cmd, hide=True)

            return result.stdout.strip()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"SSH command failed: {str(e)}")