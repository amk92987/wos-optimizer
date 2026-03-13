"""
OpenAI Review Hook System for WoS Optimizer.

Provides automated code review via OpenAI before major changes.
Claude Code remains the primary builder; OpenAI acts as a review agent.

Usage:
    from scripts.review import ReviewOrchestrator, ReviewType

    orchestrator = ReviewOrchestrator()
    result = orchestrator.review_diff(
        diff_text="...",
        review_types=[ReviewType.CODE_QUALITY, ReviewType.SECURITY_SANITY],
        context="Adding new feature to heroes page"
    )
    print(result.summary)

CLI:
    python scripts/review/cli.py --diff --types code_quality,security_sanity
"""

from scripts.review.openai_client import OpenAIReviewClient
from scripts.review.orchestrator import ReviewOrchestrator
from scripts.review.prompts import PromptBuilder, ReviewType
from scripts.review.parser import ResponseParser, ReviewResult

__all__ = [
    "OpenAIReviewClient",
    "ReviewOrchestrator",
    "PromptBuilder",
    "ReviewType",
    "ResponseParser",
    "ReviewResult",
]
