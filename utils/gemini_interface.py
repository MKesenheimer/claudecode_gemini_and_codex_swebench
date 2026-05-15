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
            result = subprocess.run(["gemini", "--version"], capture_output=True, text=True)
            logger.debug("Gemini version check returned code %d", result.returncode)
            if result.returncode != 0:
                logger.error("Gemini CLI version check failed: %s", result.stderr.strip())
                raise RuntimeError(
                    "Gemini CLI not found. Please ensure 'gemini' is installed and in PATH"
                )
            else:
                logger.info("Gemini CLI detected: %s", result.stdout.strip())
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
        logger.info("Executing Gemini CLI (cwd=%s, model=%s)", cwd, model)
        try:
            original_cwd = os.getcwd()
            logger.debug("Saved original working directory: %s", original_cwd)
            os.chdir(cwd)
            logger.debug("Changed to working directory: %s", cwd)

            # Build command
            cmd = ["gemini"]
            if model:
                cmd.extend(["--model", model])
            logger.debug("Built CLI command: %s", " ".join(cmd))

            # Execute gemini command with the prompt via stdin
            logger.debug("Sending prompt to Gemini CLI (%d chars)", len(prompt))
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            os.chdir(original_cwd)
            logger.debug("Restored original working directory: %s", original_cwd)

            logger.info(
                "Gemini CLI execution complete: success=%s, returncode=%d, stdout=%d chars, stderr=%d chars",
                result.returncode == 0, result.returncode, len(result.stdout), len(result.stderr),
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
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
            logger.error("Unexpected error in Gemini CLI execution: %s", str(e))
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    def extract_file_changes(self, response: str) -> List[Dict[str, str]]:
        """Extract file changes from Gemini's response (placeholder)."""
        logger.debug("Extracting file changes from Gemini response (%d chars)", len(response))
        return []
