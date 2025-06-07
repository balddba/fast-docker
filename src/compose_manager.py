"""Provides Docker Compose functionality for managing stacks on remote hosts.

This module implements the ComposeManager class, which handles Docker Compose operations
for stacks defined in the system. It works in conjunction with the DockerManager to
execute Docker Compose commands on remote hosts via SSH connections.

The module serves as an abstraction layer between the REST API endpoints and the
actual Docker Compose operations, handling common operations like up, down, ps, and
restart.

Typical usage example:
    stack = session.get(Stack, stack_id)
    host = session.get(Host, stack.host_id)
    compose_manager = ComposeManager(stack, host)
    compose_manager.up()  # Starts the stack

Dependencies:
    - models: Provides Stack and Host data models
    - docker_manager: Provides DockerManager for executing commands
    - docker_composer_v2: Provides DockerCompose implementation
    - fastapi: Used for HTTP exception handling
"""

from docker_composer_v2.runner.cmd.down import DockerComposeDown
from docker_composer_v2.runner.cmd.ps import DockerComposePs
from docker_composer_v2.runner.cmd.restart import DockerComposeRestart
from docker_composer_v2.runner.cmd.up import DockerComposeUp

from models import Stack, Host
from docker_manager import DockerManager
from docker_composer_v2 import DockerCompose
from fastapi import HTTPException

class ComposeManager:
    """Manages Docker Compose operations for a stack on a host.

    This class provides an interface for executing Docker Compose commands like up,
    down, ps, and restart on a specified stack and host.

    Attributes:
        stack (Stack): The stack configuration for Docker Compose.
        host (Host): The host where Docker Compose commands will be executed.
        manager (DockerManager): Docker manager instance for the host.
    """

    def __init__(self, stack: Stack, host: Host):
        """Initialize the ComposeManager.

        Args:
            stack (Stack): Stack configuration containing compose file information.
            host (Host): Host configuration for executing Docker commands.
        """
        self.stack: Stack = stack
        self.host: Host = host
        self.manager: DockerManager = DockerManager(host)
    def _get_compose(self) -> DockerCompose:
        """Creates a DockerCompose instance for the current stack.

        Returns:
            DockerCompose: An initialized DockerCompose instance.

        Raises:
            HTTPException: If the host connection type is 'docker' instead of SSH.
        """
        if self.host.connection_type == "docker":
            raise HTTPException(400, "Docker Compose operations require SSH access")

        return DockerCompose(
            working_dir=self.stack.compose_file.rsplit("/", 1)[0],
            filename=self.stack.compose_file,
            run_command=self.manager.run_ssh_command
        )

    def up(self) -> DockerComposeUp:
        """Starts up the Docker Compose stack in detached mode.

        Returns:
            DockerComposeUp: Result of the 'docker-compose up' command execution, providing output and status information of the stack startup.
        """
        compose = self._get_compose()
        return compose.up(detach=True)

    def down(self) -> DockerComposeDown:
        """Stops and removes the Docker Compose stack.

        Returns:
            DockerComposeDown: Result of the 'docker-compose down' command execution, providing output and status information of the stack teardown.
        """
        compose = self._get_compose()
        return compose.down()
        compose = self._get_compose()
        return compose.down()
    def ps(self) -> DockerComposePs:
        """Lists the running containers in the Docker Compose stack.

        Returns:
            DockerComposePs: Result of the 'docker-compose ps' command execution, providing output and status information about the running containers.
        """
        compose = self._get_compose()
        return compose.ps()

    def restart(self) -> DockerComposeRestart:
        """Restarts all containers in the Docker Compose stack.

        Returns:
            DockerComposeRestart: Result of the 'docker-compose restart' command execution, providing output and status information of the containers restart.
        """
        compose = self._get_compose()
        return compose.restart()
