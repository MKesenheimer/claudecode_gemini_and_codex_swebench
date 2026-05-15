import os
import json
import subprocess
from typing import Dict, List, Optional
from dotenv import load_dotenv
from utils.logger_utils import logger

load_dotenv()

class ClaudeCodeInterface:
    """Interface for interacting with Claude Code CLI."""

    def __init__(self):
        """Ensure the Claude CLI is available on the system."""
        logger.info("Initializing ClaudeCodeInterface")
        try:
            logger.debug("Running `claude --version`")
            result = subprocess.run([
                "claude", "--version"
            ], capture_output=True, text=True)
            logger.debug(f"Claude version check returned code {result.returncode}")
            if result.returncode != 0:
                logger.error(f"Claude CLI version check failed: {result.stderr.strip()}")
                raise RuntimeError(
                    "Claude CLI not found. Please ensure 'claude' is installed and in PATH"
                )
            else:
                logger.info(f"Claude CLI detected: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("Claude CLI executable not found in PATH")
            raise RuntimeError(
                "Claude CLI not found. Please ensure 'claude' is installed and in PATH"
            )

    def execute_code_cli(self, prompt: str, cwd: str, model: str = None) -> Dict[str, any]:
        """Execute Claude Code via CLI and capture the response.

        Args:
            prompt: The prompt to send to Claude.
            cwd: Working directory to execute in.
            model: Optional model to use (e.g., 'opus-4.1', 'sonnet-3.7').
        """
        logger.info(f"Executing Claude Code CLI (cwd={cwd}, model={model})")
        try:
            # Save the current directory
            original_cwd = os.getcwd()
            logger.debug(f"Saved original working directory: {original_cwd}")

            # Change to the working directory
            os.chdir(cwd)
            logger.debug(f"Changed to working directory: {cwd}")

            # Build command with optional model parameter
            cmd = ["claude", "--dangerously-skip-permissions"]
            if model:
                cmd.extend(["--model", model])
            logger.debug(f"Built CLI command: {' '.join(cmd)}")

            # Execute claude command with the prompt via stdin
            logger.debug(f"Sending prompt to Claude CLI ({len(prompt)} chars)")
            logger.debug(f"Prompt: {prompt}")
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            # Restore original directory
            os.chdir(original_cwd)
            logger.debug(f"Restored original working directory: {original_cwd}")
            logger.info(f"Claude CLI execution complete: success={result.returncode == 0}, returncode={result.returncode}, stdout={len(result.stdout)} chars, stderr={len(result.stderr)} chars")
            logger.debug(f"Result: {result.stdout}")

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            os.chdir(original_cwd)
            logger.warning("Claude CLI command timed out after 10 minutes")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 10 minutes",
                "returncode": -1,
            }
        except Exception as e:
            os.chdir(original_cwd)
            logger.error(f"Unexpected error in Claude CLI execution: {str(e)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    def extract_file_changes(self, response: str) -> List[Dict[str, str]]:
        """Extract file changes from Claude's response."""
        logger.debug(f"Extracting file changes from Claude response ({len(response)} chars)")
        # This will be implemented by patch_extractor.py
        # For now, return empty list
        return []