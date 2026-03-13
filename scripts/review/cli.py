"""
CLI entry point for the OpenAI review system.

Usage:
    # Review staged git changes
    python scripts/review/cli.py --diff

    # Review all changes (staged + unstaged)
    python scripts/review/cli.py --diff --all

    # Review specific files
    python scripts/review/cli.py --files frontend/app/heroes/page.tsx backend/handlers/heroes.py

    # Review with specific types
    python scripts/review/cli.py --diff --types code_quality,security_sanity

    # Review with custom context
    python scripts/review/cli.py --diff --context "Adding expert skill calculator to upgrades page"

    # Follow-up on previous review
    python scripts/review/cli.py --follow-up "What about edge cases with level 20 skills?"

    # Output as JSON instead of terminal format
    python scripts/review/cli.py --diff --json

    # Use a different model
    python scripts/review/cli.py --diff --model gpt-4o

    # List available review types
    python scripts/review/cli.py --list-types
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `scripts.review` can be imported
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from scripts.review.orchestrator import ReviewOrchestrator
from scripts.review.parser import ResponseParser, ReviewResult
from scripts.review.prompts import ReviewType


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    # Suppress noisy HTTP logs unless verbose
    if not verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)


def parse_review_types(types_str: str) -> list[ReviewType]:
    """Parse comma-separated review type strings."""
    types = []
    for t in types_str.split(","):
        t = t.strip()
        if t:
            types.append(ReviewType.from_string(t))
    return types


def get_git_diff_all() -> str:
    """Get combined staged + unstaged diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return result.stdout
    except Exception as e:
        logging.getLogger(__name__).error("Failed to get git diff: %s", e)
        return ""


def get_git_diff_staged() -> str:
    """Get staged changes diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return result.stdout
    except Exception as e:
        logging.getLogger(__name__).error("Failed to get git diff: %s", e)
        return ""


def read_files(file_paths: list[str]) -> list[str]:
    """Resolve file paths relative to the current directory."""
    resolved = []
    for fp in file_paths:
        path = Path(fp)
        if path.exists():
            resolved.append(str(path))
        else:
            # Try relative to project root
            alt = Path(_project_root) / fp
            if alt.exists():
                resolved.append(str(alt))
            else:
                print(f"Warning: File not found: {fp}", file=sys.stderr)
    return resolved


def print_list_types() -> None:
    """Print all available review types."""
    print("\nAvailable review types:")
    print("-" * 50)
    descriptions = {
        "code_quality": "Code clarity, naming, error handling, type safety",
        "ui_ux": "Touch targets, visual hierarchy, responsive layout, accessibility",
        "architecture": "Separation of concerns, API contracts, scalability",
        "integration_impact": "Blast radius analysis, cross-component dependencies",
        "regressions_risks": "Regression scenarios, edge cases, breaking changes",
        "security_sanity": "Auth, injection, data exposure, input validation",
        "performance_sanity": "Re-renders, N+1 queries, bundle size, cold starts",
        "implementation_options": "Compare 2-3 approaches with trade-offs",
    }
    for rt in ReviewType:
        desc = descriptions.get(rt.value, "")
        print(f"  {rt.value:<25} {desc}")
    print()


def output_result(
    result: ReviewResult,
    parser: ResponseParser,
    as_json: bool = False,
    no_color: bool = False,
) -> None:
    """Print the review result to the terminal."""
    if as_json:
        print(result.to_json())
    else:
        use_color = not no_color and sys.stdout.isatty()
        print(parser.format_terminal(result, use_color=use_color))


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code (0=success, 1=issues found, 2=error)."""
    arg_parser = argparse.ArgumentParser(
        description="OpenAI code review for WoS Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/review/cli.py --diff\n"
            "  python scripts/review/cli.py --diff --types code_quality,security_sanity\n"
            "  python scripts/review/cli.py --files frontend/app/heroes/page.tsx\n"
            "  python scripts/review/cli.py --follow-up 'What about edge cases?'\n"
        ),
    )

    # Input source (mutually exclusive)
    input_group = arg_parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--diff",
        action="store_true",
        help="Review staged git changes (or use --all for all changes)",
    )
    input_group.add_argument(
        "--files",
        nargs="+",
        metavar="FILE",
        help="Review specific files",
    )
    input_group.add_argument(
        "--follow-up",
        metavar="QUESTION",
        help="Ask a follow-up question on the previous review",
    )
    input_group.add_argument(
        "--list-types",
        action="store_true",
        help="List available review types and exit",
    )

    # Options
    arg_parser.add_argument(
        "--all",
        action="store_true",
        help="With --diff, review all changes (staged + unstaged), not just staged",
    )
    arg_parser.add_argument(
        "--types",
        default="code_quality,regressions_risks",
        help="Comma-separated review types (default: code_quality,regressions_risks)",
    )
    arg_parser.add_argument(
        "--context",
        help="Description of what the changes are for",
    )
    arg_parser.add_argument(
        "--feature",
        help="Name of the feature being changed",
    )
    arg_parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)",
    )
    arg_parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output as JSON instead of formatted terminal output",
    )
    arg_parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color codes in output",
    )
    arg_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = arg_parser.parse_args(argv)

    # Handle --list-types
    if args.list_types:
        print_list_types()
        return 0

    # Setup
    setup_logging(args.verbose)
    logger = logging.getLogger("review.cli")

    # Validate that at least one action is specified
    if not args.diff and not args.files and not args.follow_up:
        arg_parser.print_help()
        return 2

    # Parse review types
    try:
        review_types = parse_review_types(args.types)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    # Create orchestrator
    orchestrator = ReviewOrchestrator(model=args.model)
    response_parser = ResponseParser()

    try:
        if args.follow_up:
            # Follow-up on previous review
            logger.info("Sending follow-up question...")
            result = orchestrator.follow_up(args.follow_up)
            output_result(result, response_parser, as_json=args.output_json, no_color=args.no_color)

        elif args.diff:
            # Review git diff
            if args.all:
                logger.info("Getting all changes (staged + unstaged)...")
                diff_text = get_git_diff_all()
            else:
                logger.info("Getting staged changes...")
                diff_text = get_git_diff_staged()

            if not diff_text.strip():
                source = "all" if args.all else "staged"
                print(f"\nNo {source} changes found. ", end="")
                if not args.all:
                    print("Try --all to include unstaged changes, or stage changes with 'git add'.")
                else:
                    print("Make some changes first.")
                return 0

            logger.info(
                "Reviewing diff (%d chars, types: %s)...",
                len(diff_text),
                [rt.value for rt in review_types],
            )
            result = orchestrator.review_diff(
                diff_text,
                review_types=review_types,
                context=args.context,
                feature=args.feature,
            )
            output_result(result, response_parser, as_json=args.output_json, no_color=args.no_color)

        elif args.files:
            # Review specific files
            resolved_files = read_files(args.files)
            if not resolved_files:
                print("Error: No valid files found.", file=sys.stderr)
                return 2

            logger.info(
                "Reviewing %d files (types: %s)...",
                len(resolved_files),
                [rt.value for rt in review_types],
            )
            result = orchestrator.review_files(
                resolved_files,
                review_types=review_types,
                context=args.context,
                feature=args.feature,
            )
            output_result(result, response_parser, as_json=args.output_json, no_color=args.no_color)

    except EnvironmentError as e:
        # Missing API key
        print(f"\nConfiguration Error: {e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        # API errors (auth, rate limit exhaustion, etc.)
        print(f"\nAPI Error: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nReview cancelled.", file=sys.stderr)
        return 2

    # Return 1 if high-priority issues found, 0 otherwise
    if result.high_priority_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
