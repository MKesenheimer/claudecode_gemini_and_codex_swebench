import os
import subprocess
from typing import Dict, List
from utils.logger_utils import logger

class CodexCodeInterface:
    """Interface for interacting with the Codex CLI."""

    def __init__(self):
        """Ensure the Codex CLI is available on the system."""
        logger.info("Initializing CodexCodeInterface")
        try:
            print("Checking Codex CLI...")
            output_lines = []
            process = subprocess.Popen(
                ["codex", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                output_lines.append(line)
            process.wait()

            stdout_output = ''.join(output_lines)
            logger.debug(f"Codex version check returned code {process.returncode}")
            if process.returncode != 0:
                logger.error(f"Codex CLI version check failed: {stdout_output.strip()}")
                raise RuntimeError(
                    "Codex CLI not found. Please ensure 'codex' is installed and in PATH"
                )
            else:
                logger.info(f"Codex CLI detected: {stdout_output.strip()}")
        except FileNotFoundError:
            logger.error("Codex CLI executable not found in PATH")
            raise RuntimeError(
                "Codex CLI not found. Please ensure 'codex' is installed and in PATH"
            )

    def execute_code_cli(self, prompt: str, cwd: str, model: str = None) -> Dict[str, any]:
        """Execute Codex via CLI and capture the response."""
        logger.info(f"Executing Codex CLI (cwd={cwd}, model={model})")
        try:
            original_cwd = os.getcwd()
            logger.debug(f"Saved original working directory: {original_cwd}")
            os.chdir(cwd)
            logger.debug(f"Changed to working directory: {cwd}")
            cmd = ["codex"]
            if model:
                cmd.extend(["--model", model])
            logger.debug(f"Built CLI command: {' '.join(cmd)}")
            logger.debug(f"Sending prompt to Codex CLI ({len(prompt)} chars)")

            # Use Popen to stream output in real-time
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                timeout=3600,
            )

            # Stream output in real-time
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                output_lines.append(line)
            process.wait()

            os.chdir(original_cwd)
            logger.debug(f"Restored original working directory: {original_cwd}")
            logger.info(
                "Codex CLI execution complete: success=%s, returncode=%d, stdout=%d chars, stderr=%d chars",
                process.returncode == 0, process.returncode, len(process.stdout), len(process.stderr),
            )
            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode,
            }
        except subprocess.TimeoutExpired:
            os.chdir(original_cwd)
            logger.warning("Codex CLI command timed out after 10 minutes")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 10 minutes",
                "returncode": -1,
            }
        except Exception as e:
            os.chdir(original_cwd)
            logger.error(f"Unexpected error in Codex CLI execution: {str(e)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    def extract_file_changes(self, response: str) -> List[Dict[str, str]]:
        """Extract file changes from Codex's response (placeholder)."""
        logger.debug(f"Extracting file changes from Codex response ({len(response)} chars)")
        return []
