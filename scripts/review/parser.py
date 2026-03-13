"""
Response parser for OpenAI review results.

Parses JSON responses into a consistent ReviewResult dataclass and
provides terminal-friendly formatted output with colors.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ANSI color codes for terminal output
class Colors:
    """ANSI escape codes for terminal coloring."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"

    @classmethod
    def disable(cls):
        """Disable all colors (for non-terminal output)."""
        for attr in dir(cls):
            if attr.isupper() and not attr.startswith("_"):
                setattr(cls, attr, "")


@dataclass
class RecommendedChange:
    """A single recommended change from the review."""
    priority: str  # "high", "medium", "low"
    area: str
    recommendation: str
    reason: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecommendedChange":
        """Parse from a dict, with safe defaults."""
        return cls(
            priority=str(data.get("priority", "medium")).lower(),
            area=str(data.get("area", "unknown")),
            recommendation=str(data.get("recommendation", "")),
            reason=str(data.get("reason", "")),
        )


@dataclass
class ReviewResult:
    """Parsed and structured review result."""
    summary: str = ""
    top_concerns: list[str] = field(default_factory=list)
    recommended_changes: list[RecommendedChange] = field(default_factory=list)
    follow_up_questions: list[str] = field(default_factory=list)
    confidence: str = "medium"  # "high", "medium", "low"
    review_types: list[str] = field(default_factory=list)
    raw_response: Optional[dict] = None
    is_raw_text: bool = False

    @property
    def has_issues(self) -> bool:
        """Whether the review found any issues."""
        return bool(self.top_concerns or self.recommended_changes)

    @property
    def high_priority_count(self) -> int:
        """Count of high-priority recommendations."""
        return sum(1 for c in self.recommended_changes if c.priority == "high")

    @property
    def medium_priority_count(self) -> int:
        """Count of medium-priority recommendations."""
        return sum(1 for c in self.recommended_changes if c.priority == "medium")

    @property
    def low_priority_count(self) -> int:
        """Count of low-priority recommendations."""
        return sum(1 for c in self.recommended_changes if c.priority == "low")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        return {
            "summary": self.summary,
            "top_concerns": self.top_concerns,
            "recommended_changes": [
                {
                    "priority": c.priority,
                    "area": c.area,
                    "recommendation": c.recommendation,
                    "reason": c.reason,
                }
                for c in self.recommended_changes
            ],
            "follow_up_questions": self.follow_up_questions,
            "confidence": self.confidence,
            "review_types": self.review_types,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class ResponseParser:
    """
    Parses OpenAI JSON responses into ReviewResult objects.

    Handles malformed responses gracefully and provides formatted
    terminal output with ANSI colors.
    """

    def parse(
        self,
        response: dict[str, Any],
        review_types: Optional[list[str]] = None,
    ) -> ReviewResult:
        """
        Parse an OpenAI response dict into a ReviewResult.

        Args:
            response: The JSON dict returned by OpenAIReviewClient.
            review_types: List of review type strings that were requested.

        Returns:
            A structured ReviewResult.
        """
        result = ReviewResult(
            review_types=review_types or [],
            raw_response=response,
        )

        # Check if this was a raw text fallback
        if response.get("_raw_response"):
            result.summary = response.get("summary", "")
            result.is_raw_text = True
            result.confidence = "low"
            return result

        # Parse summary
        result.summary = str(response.get("summary", "No summary provided."))

        # Parse top concerns
        concerns = response.get("top_concerns", [])
        if isinstance(concerns, list):
            result.top_concerns = [str(c) for c in concerns if c]
        elif isinstance(concerns, str):
            result.top_concerns = [concerns]

        # Parse recommended changes
        changes = response.get("recommended_changes", [])
        if isinstance(changes, list):
            for change_data in changes:
                if isinstance(change_data, dict):
                    result.recommended_changes.append(
                        RecommendedChange.from_dict(change_data)
                    )
                elif isinstance(change_data, str):
                    # Handle case where model returns strings instead of objects
                    result.recommended_changes.append(
                        RecommendedChange(
                            priority="medium",
                            area="general",
                            recommendation=change_data,
                            reason="",
                        )
                    )

        # Parse follow-up questions
        questions = response.get("follow_up_questions", [])
        if isinstance(questions, list):
            result.follow_up_questions = [str(q) for q in questions if q]
        elif isinstance(questions, str):
            result.follow_up_questions = [questions]

        # Parse confidence
        confidence = str(response.get("confidence", "medium")).lower()
        if confidence in ("high", "medium", "low"):
            result.confidence = confidence
        else:
            result.confidence = "medium"

        return result

    def format_terminal(self, result: ReviewResult, use_color: bool = True) -> str:
        """
        Format a ReviewResult for terminal display with optional colors.

        Args:
            result: The parsed ReviewResult.
            use_color: Whether to use ANSI color codes.

        Returns:
            A formatted string for terminal output.
        """
        if not use_color:
            Colors.disable()

        lines: list[str] = []

        # Header
        lines.append("")
        lines.append(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        types_str = ", ".join(result.review_types) if result.review_types else "general"
        lines.append(f"{Colors.BOLD}{Colors.CYAN}  REVIEW RESULTS  [{types_str}]{Colors.RESET}")
        lines.append(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")

        # Confidence indicator
        conf_color = {
            "high": Colors.GREEN,
            "medium": Colors.YELLOW,
            "low": Colors.RED,
        }.get(result.confidence, Colors.WHITE)
        lines.append(f"  Confidence: {conf_color}{Colors.BOLD}{result.confidence.upper()}{Colors.RESET}")
        lines.append("")

        # Summary
        lines.append(f"{Colors.BOLD}  SUMMARY{Colors.RESET}")
        lines.append(f"  {result.summary}")
        lines.append("")

        # Top concerns
        if result.top_concerns:
            lines.append(f"{Colors.BOLD}{Colors.YELLOW}  TOP CONCERNS{Colors.RESET}")
            for i, concern in enumerate(result.top_concerns, 1):
                lines.append(f"  {Colors.YELLOW}{i}.{Colors.RESET} {concern}")
            lines.append("")

        # Recommended changes
        if result.recommended_changes:
            lines.append(f"{Colors.BOLD}  RECOMMENDED CHANGES{Colors.RESET}")

            # Group by priority
            for priority in ("high", "medium", "low"):
                changes = [c for c in result.recommended_changes if c.priority == priority]
                if not changes:
                    continue

                priority_color = {
                    "high": Colors.RED,
                    "medium": Colors.YELLOW,
                    "low": Colors.BLUE,
                }.get(priority, Colors.WHITE)

                priority_icon = {
                    "high": "!!!",
                    "medium": " !! ",
                    "low": "  ! ",
                }.get(priority, "   ")

                lines.append(
                    f"  {priority_color}{Colors.BOLD}"
                    f"  [{priority.upper()}]{Colors.RESET}"
                )

                for change in changes:
                    lines.append(
                        f"    {priority_color}{priority_icon}{Colors.RESET} "
                        f"{Colors.BOLD}{change.area}{Colors.RESET}"
                    )
                    lines.append(f"        {change.recommendation}")
                    if change.reason:
                        lines.append(f"        {Colors.DIM}Reason: {change.reason}{Colors.RESET}")
                    lines.append("")

        # Stats summary line
        if result.recommended_changes:
            lines.append(
                f"  {Colors.DIM}Changes: "
                f"{Colors.RED}{result.high_priority_count} high{Colors.DIM}, "
                f"{Colors.YELLOW}{result.medium_priority_count} medium{Colors.DIM}, "
                f"{Colors.BLUE}{result.low_priority_count} low{Colors.RESET}"
            )
            lines.append("")

        # Follow-up questions
        if result.follow_up_questions:
            lines.append(f"{Colors.BOLD}{Colors.MAGENTA}  FOLLOW-UP QUESTIONS{Colors.RESET}")
            for i, question in enumerate(result.follow_up_questions, 1):
                lines.append(f"  {Colors.MAGENTA}{i}.{Colors.RESET} {question}")
            lines.append("")

        # No issues case
        if not result.has_issues and not result.is_raw_text:
            lines.append(f"  {Colors.GREEN}{Colors.BOLD}No issues found.{Colors.RESET}")
            lines.append("")

        # Raw text warning
        if result.is_raw_text:
            lines.append(
                f"  {Colors.YELLOW}Note: Response was not structured JSON. "
                f"Results may be incomplete.{Colors.RESET}"
            )
            lines.append("")

        lines.append(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        lines.append("")

        return "\n".join(lines)

    def format_compact(self, result: ReviewResult) -> str:
        """
        Format a ReviewResult as a compact single-paragraph summary.

        Useful for embedding in commit messages or PR descriptions.
        """
        parts = [result.summary]

        if result.high_priority_count > 0:
            parts.append(
                f"({result.high_priority_count} high-priority, "
                f"{result.medium_priority_count} medium, "
                f"{result.low_priority_count} low)"
            )

        if result.top_concerns:
            concerns_str = "; ".join(result.top_concerns[:3])
            parts.append(f"Key concerns: {concerns_str}")

        return " ".join(parts)
