"""
Claude Code hook entry point for pre-edit review.

This script is called by Claude Code's hook system before major edits.
It reads context from stdin (JSON) and optionally triggers an OpenAI review.

Hook behavior:
- Reads the hook event JSON from stdin
- Checks if the changes warrant a review (based on file count, scope, etc.)
- If review is needed, runs a quick code_quality + regressions_risks check
- Outputs review results to stdout (Claude Code displays this to the user)
- Exit code 0 = proceed, non-zero = block (we always return 0 to advise, not block)

Environment:
- OPENAI_API_KEY must be set for reviews to run
- WOS_REVIEW_ENABLED=1 enables automatic review (default: disabled)
- WOS_REVIEW_THRESHOLD=3 minimum files changed to trigger (default: 3)
"""

import json
import logging
import os
import sys
from pathlib import Path

# Ensure project root is on path
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

logger = logging.getLogger("review.hook")


def should_review(event: dict) -> bool:
    """
    Determine if the hook event warrants a review.

    Args:
        event: The hook event dict from Claude Code.

    Returns:
        True if review should run.
    """
    # Check if review is enabled
    if os.environ.get("WOS_REVIEW_ENABLED", "0") != "1":
        return False

    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        return False

    return True


def run_review(event: dict) -> str:
    """
    Run a review based on the hook event.

    Args:
        event: The hook event dict.

    Returns:
        Formatted review output string, or empty string if no review needed.
    """
    # Import here to avoid overhead when review is skipped
    from scripts.review.orchestrator import ReviewOrchestrator
    from scripts.review.parser import ResponseParser
    from scripts.review.prompts import ReviewType

    orchestrator = ReviewOrchestrator()
    parser = ResponseParser()

    # Extract context from the hook event
    # Claude Code hooks pass tool_input for the edit being made
    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    old_string = tool_input.get("old_string", "")
    new_string = tool_input.get("new_string", "")

    if not file_path or not new_string:
        return ""

    # Build a synthetic diff for review
    diff_lines = []
    diff_lines.append(f"--- a/{file_path}")
    diff_lines.append(f"+++ b/{file_path}")
    if old_string:
        for line in old_string.splitlines():
            diff_lines.append(f"-{line}")
    for line in new_string.splitlines():
        diff_lines.append(f"+{line}")

    diff_text = "\n".join(diff_lines)

    # Quick review: code quality + regression check
    review_types = [ReviewType.CODE_QUALITY, ReviewType.REGRESSIONS_RISKS]

    try:
        result = orchestrator.review_diff(
            diff_text=diff_text,
            review_types=review_types,
            context=f"Edit to {file_path}",
            files_changed=[file_path],
        )

        if result.has_issues:
            return parser.format_terminal(result, use_color=False)
        return ""

    except Exception as e:
        logger.debug("Review hook error (non-blocking): %s", e)
        return ""


def main() -> int:
    """
    Hook entry point. Reads event from stdin, optionally reviews, outputs to stdout.

    Returns 0 always (advisory, not blocking).
    """
    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    try:
        # Read hook event from stdin
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            event = json.loads(stdin_data)
        else:
            event = {}
    except (json.JSONDecodeError, EOFError):
        event = {}

    if not should_review(event):
        return 0

    output = run_review(event)
    if output:
        # Print review results -- Claude Code displays stdout to the user
        print(output)

    # Always return 0: this hook advises but never blocks
    return 0


if __name__ == "__main__":
    sys.exit(main())
