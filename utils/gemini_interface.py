import os
import subprocess
from typing import Dict, List
from utils.logger_utils import logger

class GeminiCodeInterface:
    """Interface for interacting with the Google Gemini CLI."""

    def __init__(self):
        """Ensure the Gemini CLI is available on the system."""
        logger.info("Initializing GeminiCodeInterface")
        try:
            print("Checking Gemini CLI...")
            output_lines = []
            process = subprocess.Popen(
                ["gemini", "--version"],
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
            logger.debug(f"Gemini version check returned code {process.returncode}")
            if process.returncode != 0:
                logger.error(f"Gemini CLI version check failed: {stdout_output.strip()}")
                raise RuntimeError(
                    "Gemini CLI not found. Please ensure 'gemini' is installed and in PATH"
                )
            else:
                logger.info(f"Gemini CLI detected: {stdout_output.strip()}")
        except FileNotFoundError:
            logger.error("Gemini CLI executable not found in PATH")
            raise RuntimeError(
                "Gemini CLI not found. Please ensure 'gemini' is installed and in PATH"
            )

    def execute_code_cli(self, prompt: str, cwd: str, model: str = None) -> Dict[str, any]:
        """Execute Gemini via CLI and capture the response.

        Args:
            prompt: The prompt to send to Gemini.
            cwd: Working directory to execute in.
            model: Optional model to use.
        """
        logger.info(f"Executing Gemini CLI (cwd={cwd}, model={model})")
        try:
            original_cwd = os.getcwd()
            logger.debug(f"Saved original working directory: {original_cwd}")
            os.chdir(cwd)
            logger.debug(f"Changed to working directory: {cwd}")

            # Build command
            cmd = ["gemini"]
            if model:
                cmd.extend(["--model", model])
            logger.debug(f"Built CLI command: {' '.join(cmd)}")

            # Execute gemini command with the prompt via stdin
            logger.debug(f"Sending prompt to Gemini CLI ({len(prompt)} chars)")

            # Use Popen to stream output in real-time
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                timeout=600,  # 10 minute timeout
            )

            # Stream output in real-time
            output_lines = []
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                output_lines.append(line)
            process.wait()

            os.chdir(original_cwd)
            logger.debug(f"Restored original working directory: {original_cwd}")

            logger.info(f"Gemini CLI execution complete: success={process.returncode == 0}, returncode={process.returncode}, stdout={len(process.stdout)} chars, stderr={len(process.stderr)} chars")

            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode,
            }

        except subprocess.TimeoutExpired:
            os.chdir(original_cwd)
            logger.warning("Gemini CLI command timed out after 10 minutes")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 10 minutes",
                "returncode": -1,
            }
        except Exception as e:
            os.chdir(original_cwd)
            logger.error(f"Unexpected error in Gemini CLI execution: {str(e)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    def extract_file_changes(self, response: str) -> List[Dict[str, str]]:
        """Extract file changes from Gemini's response (placeholder)."""
        logger.debug(f"Extracting file changes from Gemini response ({len(response)} chars)")
        return []
