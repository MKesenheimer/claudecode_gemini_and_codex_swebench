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
            logger.debug(f"Codex version check returned code {result.returncode}")
            if result.returncode != 0:
                logger.error(f"Codex CLI version check failed: {result.stderr.strip()}")
                raise RuntimeError(
                    "Codex CLI not found. Please ensure 'codex' is installed and in PATH"
                )
            else:
                logger.info(f"Codex CLI detected: {result.stdout.strip()}")
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
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=600,
            )
            os.chdir(original_cwd)
            logger.debug(f"Restored original working directory: {original_cwd}")
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
