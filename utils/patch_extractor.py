import re
import os
import subprocess
from typing import List, Dict, Optional, Tuple
from unidiff import PatchSet
import tempfile
import difflib
from utils.logger_utils import logger

class PatchExtractor:
    """Extract patches from Claude Code's responses and file changes."""
    
    def __init__(self):
        logger.info("Initializing PatchExtractor")
        self.file_edit_pattern = re.compile(
            r"(?:Creating|Editing|Modifying|Writing to) file: (.*?)$",
            re.MULTILINE
        )
        self.diff_pattern = re.compile(
            r"```diff\n(.*?)```",
            re.DOTALL
        )
        logger.debug(f"Compiled regex patterns: file_edit={self.file_edit_pattern.pattern}, diff={self.diff_pattern.pattern}")
        
    def extract_from_cli_output(self, output: str, repo_path: str) -> str:
        """Extract patch from Claude Code CLI output by analyzing git diff."""
        logger.info(f"Extracting patch from CLI output (repo={repo_path})")
        try:
            # Change to repo directory
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            logger.debug(f"Changed to repo directory: {repo_path}")

            # First, add any untracked files to the index so they appear in diff
            logger.debug("Running git add -N .")
            subprocess.run(
                ["git", "add", "-N", "."],
                capture_output=True,
                text=True
            )

            # Get the diff against HEAD to capture all changes
            logger.debug("Running git diff HEAD --no-color --no-ext-diff")
            result = subprocess.run(
                ["git", "diff", "HEAD", "--no-color", "--no-ext-diff"],
                capture_output=True,
                text=True
            )

            os.chdir(original_cwd)
            logger.debug(f"Restored working directory: {original_cwd}")

            if result.returncode == 0:
                logger.debug(f"Git diff succeeded ({len(result.stdout)} chars of output)")
                return result.stdout
            else:
                logger.warning(f"Git diff failed: {result.stderr.strip()}")
                return ""

        except Exception as e:
            logger.error(f"Error extracting patch: {str(e)}")
            return ""
            
    def extract_from_response(self, response: str) -> List[Dict[str, str]]:
        """Extract file changes from Claude's response text."""
        logger.debug(f"Extracting file changes from response ({len(response)} chars)")
        changes = []

        # Look for diff blocks
        diff_matches = self.diff_pattern.findall(response)
        logger.debug(f"Found {len(diff_matches)} diff blocks")
        for diff in diff_matches:
            changes.append({
                "type": "diff",
                "content": diff
            })

        # Look for file edits mentioned in the response
        file_mentions = self.file_edit_pattern.findall(response)
        logger.debug(f"Found {len(file_mentions)} file mentions")
        for file_path in file_mentions:
            logger.debug(f"  File mention: {file_path.strip()}")
            changes.append({
                "type": "file_mention",
                "path": file_path.strip()
            })

        logger.info(f"Extracted {len(changes)} total file changes")
        return changes
    
    def create_patch_from_changes(self, before_state: Dict[str, str],
                                after_state: Dict[str, str]) -> str:
        """Create a unified diff patch from before/after file states."""
        logger.debug(f"Creating patch from changes (before={len(before_state)} files, after={len(after_state)} files)")
        patch_lines = []

        # Find all files that changed
        all_files = set(before_state.keys()) | set(after_state.keys())
        logger.debug(f"Total unique files to consider: {len(all_files)}")

        for file_path in sorted(all_files):
            before_content = before_state.get(file_path, "").splitlines(keepends=True)
            after_content = after_state.get(file_path, "").splitlines(keepends=True)

            if before_content == after_content:
                logger.debug(f"  No change detected for: {file_path}")
                continue

            logger.debug(f"  Generating diff for: {file_path} ({len(before_content)} before lines, {len(after_content)} after lines)")
            diff_output = difflib.unified_diff(
                before_content,
                after_content,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
            )

            patch_lines.extend(diff_output)

        result = "".join(patch_lines)
        logger.info(f"Created patch ({len(result)} chars, {len(patch_lines)} files changed)")
        return result
    
    def validate_patch(self, patch: str) -> Tuple[bool, Optional[str]]:
        """Validate that a patch is well-formed."""
        logger.debug(f"Validating patch ({len(patch)} chars)")
        if not patch or not patch.strip():
            logger.warning("Validation failed: empty patch")
            return False, "Empty patch"

        try:
            # Try to parse the patch
            logger.debug("Parsing patch with PatchSet")
            patchset = PatchSet(patch)

            # Check if patch has any files
            if not patchset:
                logger.warning("Validation failed: patch contains no file changes")
                return False, "Patch contains no file changes"

            logger.info("Patch validation passed")
            # Basic validation passed
            return True, None

        except Exception as e:
            logger.error(f"Patch validation failed: {str(e)}")
            return False, f"Invalid patch format: {str(e)}"
            
    def apply_patch_test(self, patch: str, repo_path: str) -> Tuple[bool, str]:
        """Test if a patch can be applied cleanly."""
        try:
            # Save patch to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
                f.write(patch)
                patch_file = f.name
                
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Test patch application
            result = subprocess.run(
                ["git", "apply", "--check", patch_file],
                capture_output=True,
                text=True
            )
            
            os.chdir(original_cwd)
            os.unlink(patch_file)
            
            if result.returncode == 0:
                return True, "Patch can be applied cleanly"
            else:
                return False, f"Patch application failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Error testing patch: {str(e)}"
            
    def format_for_swebench(self, patch: str, instance_id: str, model_name: str = "claude-code") -> Dict:
        """Format patch for SWE-bench submission."""
        return {
            "instance_id": instance_id,
            "model": model_name,
            "prediction": patch
        }