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
            result = subprocess.run(["codex", "--version"], capture_output=True, text=True)
            logger.debug("Codex version check returned code %d", result.returncode)
            if result.returncode != 0:
                logger.error("Codex CLI version check failed: %s", result.stderr.strip())
                raise RuntimeError(
                    "Codex CLI not found. Please ensure 'codex' is installed and in PATH"
                )
            else:
                logger.info("Codex CLI detected: %s", result.stdout.strip())
        except FileNotFoundError:
            logger.error("Codex CLI executable not found in PATH")
            raise RuntimeError(
                "Codex CLI not found. Please ensure 'codex' is installed and in PATH"
            )

    def execute_code_cli(self, prompt: str, cwd: str, model: str = None) -> Dict[str, any]:
        """Execute Codex via CLI and capture the response."""
        logger.info("Executing Codex CLI (cwd=%s, model=%s)", cwd, model)
        try:
            original_cwd = os.getcwd()
            logger.debug("Saved original working directory: %s", original_cwd)
            os.chdir(cwd)
            logger.debug("Changed to working directory: %s", cwd)
            cmd = ["codex"]
            if model:
                cmd.extend(["--model", model])
            logger.debug("Built CLI command: %s", " ".join(cmd))
            logger.debug("Sending prompt to Codex CLI (%d chars)", len(prompt))
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=600,
            )
            os.chdir(original_cwd)
            logger.debug("Restored original working directory: %s", original_cwd)
            logger.info(
                "Codex CLI execution complete: success=%s, returncode=%d, stdout=%d chars, stderr=%d chars",
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
            logger.warning("Codex CLI command timed out after 10 minutes")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 10 minutes",
                "returncode": -1,
            }
        except Exception as e:
            os.chdir(original_cwd)
            logger.error("Unexpected error in Codex CLI execution: %s", str(e))
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    def extract_file_changes(self, response: str) -> List[Dict[str, str]]:
        """Extract file changes from Codex's response (placeholder)."""
        logger.debug("Extracting file changes from Codex response (%d chars)", len(response))
        return []
