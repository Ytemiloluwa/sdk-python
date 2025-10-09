import subprocess
import asyncio
from typing import Optional


def exec_command(command: str) -> str:
    """
    Execute a shell command and return the output.

    Args:
        command: The shell command to execute

    Returns:
        The command output as a string

    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise e


async def exec_command_async(command: str) -> str:
    """
    Execute a shell command asynchronously and return the output.

    Args:
        command: The shell command to execute

    Returns:
        The command output as a string

    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    try:
        process = await asyncio.create_subprocess_shell(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, command, stdout, stderr
            )

        return stdout.strip()
    except subprocess.CalledProcessError as e:
        raise e
