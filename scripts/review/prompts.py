"""
Prompt builder for OpenAI review requests.

Each review type has a specific system message and structured request format
tailored to that concern area.
"""

import json
from enum import Enum
from typing import Any, Optional


class ReviewType(Enum):
    """Available review types, each with a specific focus area."""
    CODE_QUALITY = "code_quality"
    UI_UX = "ui_ux"
    ARCHITECTURE = "architecture"
    INTEGRATION_IMPACT = "integration_impact"
    REGRESSIONS_RISKS = "regressions_risks"
    SECURITY_SANITY = "security_sanity"
    PERFORMANCE_SANITY = "performance_sanity"
    IMPLEMENTATION_OPTIONS = "implementation_options"

    @classmethod
    def from_string(cls, value: str) -> "ReviewType":
        """Parse a string into a ReviewType, case-insensitive."""
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        valid = ", ".join(m.value for m in cls)
        raise ValueError(f"Unknown review type: '{value}'. Valid types: {valid}")

    @classmethod
    def all_types(cls) -> list["ReviewType"]:
        """Return all review types."""
        return list(cls)


# --- System messages per review type ---

SYSTEM_MESSAGES: dict[ReviewType, str] = {
    ReviewType.CODE_QUALITY: (
        "You are a senior code reviewer specializing in TypeScript/React (Next.js) and Python "
        "(AWS Lambda). Focus on code clarity, maintainability, naming conventions, error handling, "
        "type safety, and adherence to established patterns. Flag dead code, magic numbers, "
        "inconsistent naming, and missing error boundaries. Do NOT nitpick formatting or style "
        "preferences that are already consistent within the codebase.\n\n"
        "Respond with a JSON object matching the specified response format."
    ),
    ReviewType.UI_UX: (
        "You are a UX engineer reviewing frontend changes for a gaming utility web app "
        "(Whiteout Survival Optimizer). The app uses Next.js with Tailwind CSS and has an "
        "arctic/frost design theme. Users are mobile gamers who also use desktop. Focus on: "
        "touch target sizes (44px minimum), visual hierarchy, loading states, error feedback, "
        "responsive layout, color contrast, and interaction patterns. The app uses a dark theme "
        "with ice-blue accents.\n\n"
        "Respond with a JSON object matching the specified response format."
    ),
    ReviewType.ARCHITECTURE: (
        "You are a software architect reviewing changes to a Next.js + AWS Serverless application. "
        "The stack is: Next.js 14 (static export to S3/CloudFront), Python Lambda functions behind "
        "API Gateway, DynamoDB for storage, and Cognito for auth. Review for: separation of concerns, "
        "proper layering, API contract consistency, data model implications, and scalability. "
        "Flag changes that create tight coupling, violate the existing architecture, or will be "
        "hard to evolve.\n\n"
        "Respond with a JSON object matching the specified response format."
    ),
    ReviewType.INTEGRATION_IMPACT: (
        "You are a QA engineer analyzing the blast radius of code changes. This is a full-stack "
        "application with Next.js frontend, Python Lambda backend, DynamoDB, and Cognito auth. "
        "Identify all components, pages, and data flows that could be affected by the proposed "
        "changes. Consider: API contract changes, shared state, database schema impacts, "
        "authentication flows, and cross-page dependencies.\n\n"
        "Respond with a JSON object matching the specified response format."
    ),
    ReviewType.REGRESSIONS_RISKS: (
        "You are a QA specialist focused on regression risk analysis. Given code changes, identify "
        "specific scenarios that could break existing functionality. Consider: edge cases in the "
        "changed code, features that depend on modified APIs or data structures, browser/device "
        "compatibility concerns, and race conditions. Prioritize risks by likelihood and severity.\n\n"
        "Respond with a JSON object matching the specified response format."
    ),
    ReviewType.SECURITY_SANITY: (
        "You are a security engineer doing a sanity review of code changes. This application "
        "handles user authentication (Cognito), stores user data (DynamoDB), and has admin "
        "functionality. Check for: exposed secrets, injection vulnerabilities (XSS, NoSQL injection), "
        "broken auth/access control, insecure data handling, CORS misconfigurations, and missing "
        "input validation. Do NOT flag theoretical risks that require unlikely attack vectors; "
        "focus on practical vulnerabilities.\n\n"
        "Respond with a JSON object matching the specified response format."
    ),
    ReviewType.PERFORMANCE_SANITY: (
        "You are a performance engineer reviewing code changes. The frontend is a statically "
        "exported Next.js app served via CloudFront, and the backend is AWS Lambda + DynamoDB. "
        "Focus on: unnecessary re-renders, large bundle impacts, N+1 query patterns, missing "
        "pagination, unoptimized images, memory leaks in effects/subscriptions, cold start impacts "
        "for Lambda, and DynamoDB access patterns (scan vs query, index usage).\n\n"
        "Respond with a JSON object matching the specified response format."
    ),
    ReviewType.IMPLEMENTATION_OPTIONS: (
        "You are a technical advisor evaluating implementation approaches. Given a feature or "
        "change description, propose 2-3 implementation options with trade-offs. Consider: "
        "development effort, maintainability, performance, user experience, and compatibility "
        "with the existing Next.js + AWS Serverless architecture. For each option, clearly state "
        "pros, cons, and your recommendation.\n\n"
        "Respond with a JSON object matching the specified response format."
    ),
}


# --- Response format instruction appended to all prompts ---

RESPONSE_FORMAT_INSTRUCTION = """
You MUST respond with a valid JSON object in this exact structure:
{
  "summary": "A concise 1-3 sentence summary of findings",
  "top_concerns": ["Concern 1", "Concern 2", ...],
  "recommended_changes": [
    {
      "priority": "high|medium|low",
      "area": "The file or component affected",
      "recommendation": "What to change",
      "reason": "Why this matters"
    }
  ],
  "follow_up_questions": ["Question for the developer to consider"],
  "confidence": "high|medium|low"
}

Rules:
- Keep the summary concise and actionable
- Limit top_concerns to the 3-5 most important issues
- Sort recommended_changes by priority (high first)
- Only include follow_up_questions if genuinely useful (0-3 max)
- Set confidence based on how much context you have about the changes
- If no issues found, say so in summary and leave arrays empty
"""


class PromptBuilder:
    """
    Builds structured prompts for each review type.

    Constructs the system message and user message with all relevant context
    for the OpenAI API call.
    """

    def __init__(self):
        pass

    def build_system_message(self, review_type: ReviewType) -> str:
        """Get the system message for a given review type."""
        return SYSTEM_MESSAGES[review_type]

    def build_user_message(
        self,
        review_type: ReviewType,
        *,
        diff_text: Optional[str] = None,
        file_contents: Optional[list[dict[str, str]]] = None,
        context: Optional[str] = None,
        feature: Optional[str] = None,
        files_changed: Optional[list[str]] = None,
        subsystems: Optional[list[str]] = None,
        constraints: Optional[dict[str, list[str]]] = None,
        existing_patterns: Optional[list[str]] = None,
        questions: Optional[list[str]] = None,
    ) -> str:
        """
        Build the user message for a review request.

        Args:
            review_type: The type of review to perform.
            diff_text: Git diff output to review.
            file_contents: List of {"file": "...", "purpose": "...", "snippet": "..."} dicts.
            context: Free-text description of what the changes are for.
            feature: Name of the feature being changed.
            files_changed: List of file paths that were modified.
            subsystems: List of subsystem names affected (e.g., ["frontend", "heroes API"]).
            constraints: Dict with keys like "must_keep", "avoid", "performance_notes", "design_goals".
            existing_patterns: List of patterns to maintain consistency with.
            questions: Specific questions for the reviewer.

        Returns:
            The formatted user message string.
        """
        # Build the structured request payload
        request: dict[str, Any] = {
            "task_summary": context or "Review the following code changes",
            "review_type": [review_type.value],
            "change_scope": {},
            "response_format": {
                "summary": True,
                "risks": True,
                "recommendations": True,
            },
        }

        # Change scope
        scope = request["change_scope"]
        if feature:
            scope["feature"] = feature
        if files_changed:
            scope["files_changed"] = files_changed
        if subsystems:
            scope["subsystems"] = subsystems

        # Constraints
        if constraints:
            request["constraints"] = constraints

        # Existing patterns
        if existing_patterns:
            request["existing_patterns"] = existing_patterns

        # Code context
        if file_contents:
            request["code_context"] = file_contents

        # Questions
        if questions:
            request["questions_for_openai"] = questions

        # Build the user message
        parts = [
            "## Review Request",
            f"**Review type:** {review_type.value}",
            "",
            json.dumps(request, indent=2),
        ]

        # Add diff if provided
        if diff_text:
            # Truncate very large diffs to stay within token limits
            max_diff_chars = 12000  # ~3000 tokens
            if len(diff_text) > max_diff_chars:
                truncated = diff_text[:max_diff_chars]
                parts.extend([
                    "",
                    "## Git Diff (truncated - showing first ~3000 tokens)",
                    "```diff",
                    truncated,
                    "```",
                    "",
                    f"(Diff truncated from {len(diff_text)} to {max_diff_chars} characters. "
                    "Focus review on the visible portion.)",
                ])
            else:
                parts.extend([
                    "",
                    "## Git Diff",
                    "```diff",
                    diff_text,
                    "```",
                ])

        # Add file contents if provided (without diff)
        if file_contents and not diff_text:
            parts.append("")
            parts.append("## File Contents")
            for fc in file_contents:
                parts.extend([
                    f"### {fc.get('file', 'unknown')}",
                    f"**Purpose:** {fc.get('purpose', 'N/A')}",
                    "```",
                    fc.get("snippet", ""),
                    "```",
                    "",
                ])

        # Append response format instruction
        parts.extend(["", RESPONSE_FORMAT_INSTRUCTION])

        return "\n".join(parts)

    def build_follow_up_message(self, question: str) -> str:
        """
        Build a follow-up message for an ongoing review conversation.

        Args:
            question: The follow-up question to ask.

        Returns:
            The formatted follow-up message.
        """
        return (
            f"## Follow-up Question\n\n"
            f"{question}\n\n"
            f"Please respond in the same JSON format as before.\n\n"
            f"{RESPONSE_FORMAT_INSTRUCTION}"
        )

    def build_combined_prompt(
        self,
        review_types: list[ReviewType],
        **kwargs: Any,
    ) -> tuple[str, str]:
        """
        Build a combined system+user message for multiple review types.

        When reviewing multiple types at once, the system message combines
        all relevant perspectives, and the user message lists all types.

        Args:
            review_types: List of review types to combine.
            **kwargs: Same keyword arguments as build_user_message.

        Returns:
            Tuple of (system_message, user_message).
        """
        if len(review_types) == 1:
            rt = review_types[0]
            return (
                self.build_system_message(rt),
                self.build_user_message(rt, **kwargs),
            )

        # Combine system messages
        combined_system = (
            "You are a senior engineering reviewer performing a multi-faceted review. "
            "Apply ALL of the following review perspectives simultaneously:\n\n"
        )
        for rt in review_types:
            combined_system += f"### {rt.value} perspective\n{SYSTEM_MESSAGES[rt]}\n\n"

        combined_system += (
            "Synthesize findings from all perspectives into a single cohesive review. "
            "Respond with a JSON object matching the specified response format."
        )

        # User message with multiple types
        kwargs_copy = dict(kwargs)
        user_msg_parts = [
            "## Multi-Type Review Request",
            f"**Review types:** {', '.join(rt.value for rt in review_types)}",
            "",
        ]

        # Build a single structured request
        request: dict[str, Any] = {
            "task_summary": kwargs_copy.pop("context", None) or "Review the following code changes",
            "review_type": [rt.value for rt in review_types],
            "change_scope": {},
            "response_format": {
                "summary": True,
                "risks": True,
                "recommendations": True,
            },
        }

        feature = kwargs_copy.pop("feature", None)
        files_changed = kwargs_copy.pop("files_changed", None)
        subsystems = kwargs_copy.pop("subsystems", None)
        constraints = kwargs_copy.pop("constraints", None)
        existing_patterns = kwargs_copy.pop("existing_patterns", None)
        file_contents = kwargs_copy.pop("file_contents", None)
        questions = kwargs_copy.pop("questions", None)
        diff_text = kwargs_copy.pop("diff_text", None)

        if feature:
            request["change_scope"]["feature"] = feature
        if files_changed:
            request["change_scope"]["files_changed"] = files_changed
        if subsystems:
            request["change_scope"]["subsystems"] = subsystems
        if constraints:
            request["constraints"] = constraints
        if existing_patterns:
            request["existing_patterns"] = existing_patterns
        if file_contents:
            request["code_context"] = file_contents
        if questions:
            request["questions_for_openai"] = questions

        user_msg_parts.append(json.dumps(request, indent=2))

        if diff_text:
            max_diff_chars = 12000
            if len(diff_text) > max_diff_chars:
                user_msg_parts.extend([
                    "",
                    "## Git Diff (truncated)",
                    "```diff",
                    diff_text[:max_diff_chars],
                    "```",
                    f"(Truncated from {len(diff_text)} to {max_diff_chars} chars.)",
                ])
            else:
                user_msg_parts.extend([
                    "",
                    "## Git Diff",
                    "```diff",
                    diff_text,
                    "```",
                ])

        if file_contents and not diff_text:
            user_msg_parts.append("")
            user_msg_parts.append("## File Contents")
            for fc in file_contents:
                user_msg_parts.extend([
                    f"### {fc.get('file', 'unknown')}",
                    f"**Purpose:** {fc.get('purpose', 'N/A')}",
                    "```",
                    fc.get("snippet", ""),
                    "```",
                    "",
                ])

        user_msg_parts.extend(["", RESPONSE_FORMAT_INSTRUCTION])

        return combined_system, "\n".join(user_msg_parts)
