"""
Review orchestrator for managing multi-type, multi-round review workflows.

Coordinates the OpenAI client, prompt builder, and response parser to
execute scoped reviews on code changes.
"""

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from scripts.review.openai_client import OpenAIReviewClient
from scripts.review.parser import ResponseParser, ReviewResult
from scripts.review.prompts import PromptBuilder, ReviewType

logger = logging.getLogger(__name__)

# Maximum characters for a single review request diff/content
MAX_CHUNK_CHARS = 12000


@dataclass
class ReviewSession:
    """Tracks a multi-round review conversation."""
    session_id: str
    review_types: list[ReviewType]
    context: Optional[str] = None
    system_message: str = ""
    conversation: list[dict[str, str]] = field(default_factory=list)
    results: list[ReviewResult] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)

    @property
    def turn_count(self) -> int:
        """Number of user turns in the conversation."""
        return sum(1 for m in self.conversation if m["role"] == "user")


class ReviewOrchestrator:
    """
    Manages the review workflow: building prompts, calling OpenAI,
    parsing results, and supporting multi-round conversations.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ):
        self.client = OpenAIReviewClient(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        self.prompt_builder = PromptBuilder()
        self.parser = ResponseParser()
        self._sessions: dict[str, ReviewSession] = {}
        self._session_counter = 0

    # --- Primary review methods ---

    def review_diff(
        self,
        diff_text: str,
        review_types: Optional[list[ReviewType]] = None,
        context: Optional[str] = None,
        feature: Optional[str] = None,
        files_changed: Optional[list[str]] = None,
        subsystems: Optional[list[str]] = None,
        constraints: Optional[dict[str, list[str]]] = None,
        existing_patterns: Optional[list[str]] = None,
        questions: Optional[list[str]] = None,
    ) -> ReviewResult:
        """
        Review a git diff.

        Args:
            diff_text: The git diff output.
            review_types: Types of review to perform (defaults to code_quality + regressions_risks).
            context: Free-text description of the changes.
            feature: Name of the feature.
            files_changed: List of changed file paths.
            subsystems: Affected subsystems.
            constraints: Constraints dict (must_keep, avoid, etc.).
            existing_patterns: Patterns to maintain.
            questions: Specific questions for the reviewer.

        Returns:
            Parsed ReviewResult.
        """
        if not review_types:
            review_types = [ReviewType.CODE_QUALITY, ReviewType.REGRESSIONS_RISKS]

        # Extract file list from diff if not provided
        if not files_changed and diff_text:
            files_changed = self._extract_files_from_diff(diff_text)

        # Detect subsystems from file paths if not provided
        if not subsystems and files_changed:
            subsystems = self._detect_subsystems(files_changed)

        # Build prompts
        system_msg, user_msg = self.prompt_builder.build_combined_prompt(
            review_types,
            diff_text=diff_text,
            context=context,
            feature=feature,
            files_changed=files_changed,
            subsystems=subsystems,
            constraints=constraints,
            existing_patterns=existing_patterns,
            questions=questions,
        )

        # Create session for follow-ups
        session = self._create_session(review_types, context, system_msg)
        session.conversation.append({"role": "user", "content": user_msg})

        # Call OpenAI
        logger.info(
            "Sending review request (types: %s, diff_size: %d chars)",
            [rt.value for rt in review_types],
            len(diff_text),
        )
        response = self.client.chat(
            system_message=system_msg,
            user_message=user_msg,
            response_format={"type": "json_object"},
        )

        # Store assistant response
        session.conversation.append({"role": "assistant", "content": json.dumps(response)})

        # Parse result
        result = self.parser.parse(response, [rt.value for rt in review_types])
        session.results.append(result)

        return result

    def review_files(
        self,
        file_paths: list[str],
        review_types: Optional[list[ReviewType]] = None,
        context: Optional[str] = None,
        feature: Optional[str] = None,
        constraints: Optional[dict[str, list[str]]] = None,
        existing_patterns: Optional[list[str]] = None,
        questions: Optional[list[str]] = None,
    ) -> ReviewResult:
        """
        Review specific files by reading their contents.

        Args:
            file_paths: Paths to files to review.
            review_types: Types of review to perform.
            context: Description of what to look for.
            feature: Feature name.
            constraints: Constraints dict.
            existing_patterns: Patterns to maintain.
            questions: Specific questions.

        Returns:
            Parsed ReviewResult.
        """
        if not review_types:
            review_types = [ReviewType.CODE_QUALITY]

        # Read file contents
        file_contents = []
        for fp in file_paths:
            path = Path(fp)
            if not path.exists():
                logger.warning("File not found: %s", fp)
                continue

            try:
                content = path.read_text(encoding="utf-8")
                # Truncate large files
                if len(content) > 6000:
                    content = content[:6000] + "\n... (truncated)"

                file_contents.append({
                    "file": str(path),
                    "purpose": self._infer_file_purpose(path),
                    "snippet": content,
                })
            except Exception as e:
                logger.warning("Could not read %s: %s", fp, e)

        if not file_contents:
            result = ReviewResult(
                summary="No files could be read for review.",
                confidence="low",
                review_types=[rt.value for rt in review_types],
            )
            return result

        # Detect subsystems
        subsystems = self._detect_subsystems(file_paths)

        # Build prompts
        system_msg, user_msg = self.prompt_builder.build_combined_prompt(
            review_types,
            file_contents=file_contents,
            context=context,
            feature=feature,
            files_changed=file_paths,
            subsystems=subsystems,
            constraints=constraints,
            existing_patterns=existing_patterns,
            questions=questions,
        )

        # Create session
        session = self._create_session(review_types, context, system_msg)
        session.conversation.append({"role": "user", "content": user_msg})

        # Call OpenAI
        logger.info(
            "Sending file review request (types: %s, files: %d)",
            [rt.value for rt in review_types],
            len(file_contents),
        )
        response = self.client.chat(
            system_message=system_msg,
            user_message=user_msg,
            response_format={"type": "json_object"},
        )

        session.conversation.append({"role": "assistant", "content": json.dumps(response)})

        result = self.parser.parse(response, [rt.value for rt in review_types])
        session.results.append(result)

        return result

    def review_staged(
        self,
        review_types: Optional[list[ReviewType]] = None,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> ReviewResult:
        """
        Review staged git changes (git diff --cached).

        Args:
            review_types: Types of review to perform.
            context: Description of the changes.
            **kwargs: Additional kwargs passed to review_diff.

        Returns:
            Parsed ReviewResult.
        """
        diff_text = self._get_git_diff(staged=True)
        if not diff_text.strip():
            return ReviewResult(
                summary="No staged changes found. Stage changes with 'git add' first.",
                confidence="high",
                review_types=[rt.value for rt in (review_types or [])],
            )

        return self.review_diff(diff_text, review_types=review_types, context=context, **kwargs)

    def review_unstaged(
        self,
        review_types: Optional[list[ReviewType]] = None,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> ReviewResult:
        """
        Review all unstaged changes (git diff).

        Args:
            review_types: Types of review to perform.
            context: Description of the changes.
            **kwargs: Additional kwargs passed to review_diff.

        Returns:
            Parsed ReviewResult.
        """
        diff_text = self._get_git_diff(staged=False)
        if not diff_text.strip():
            return ReviewResult(
                summary="No unstaged changes found.",
                confidence="high",
                review_types=[rt.value for rt in (review_types or [])],
            )

        return self.review_diff(diff_text, review_types=review_types, context=context, **kwargs)

    def follow_up(
        self,
        question: str,
        session_id: Optional[str] = None,
    ) -> ReviewResult:
        """
        Send a follow-up question in an existing review session.

        Args:
            question: The follow-up question.
            session_id: Session ID to continue (uses most recent if None).

        Returns:
            Parsed ReviewResult with the follow-up response.
        """
        session = self._get_session(session_id)
        if not session:
            return ReviewResult(
                summary=(
                    "No active review session found. Run a review first, "
                    "then use --follow-up for follow-up questions."
                ),
                confidence="low",
            )

        follow_up_msg = self.prompt_builder.build_follow_up_message(question)
        session.conversation.append({"role": "user", "content": follow_up_msg})

        logger.info("Sending follow-up (session: %s, turn: %d)", session.session_id, session.turn_count)
        response = self.client.chat_multi_turn(
            system_message=session.system_message,
            conversation=session.conversation,
            response_format={"type": "json_object"},
        )

        session.conversation.append({"role": "assistant", "content": json.dumps(response)})

        result = self.parser.parse(response, [rt.value for rt in session.review_types])
        session.results.append(result)

        return result

    # --- Session management ---

    def _create_session(
        self,
        review_types: list[ReviewType],
        context: Optional[str],
        system_message: str,
    ) -> ReviewSession:
        """Create and store a new review session."""
        self._session_counter += 1
        session_id = f"review-{self._session_counter}-{int(time.time())}"
        session = ReviewSession(
            session_id=session_id,
            review_types=review_types,
            context=context,
            system_message=system_message,
        )
        self._sessions[session_id] = session
        return session

    def _get_session(self, session_id: Optional[str] = None) -> Optional[ReviewSession]:
        """Get a session by ID, or the most recent one."""
        if session_id:
            return self._sessions.get(session_id)
        if self._sessions:
            return list(self._sessions.values())[-1]
        return None

    @property
    def last_session_id(self) -> Optional[str]:
        """Return the most recent session ID, or None."""
        if self._sessions:
            return list(self._sessions.keys())[-1]
        return None

    # --- Git helpers ---

    @staticmethod
    def _get_git_diff(staged: bool = True) -> str:
        """
        Run git diff and return the output.

        Args:
            staged: If True, show staged changes (--cached). Otherwise, unstaged.

        Returns:
            The diff text, or empty string on error.
        """
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--cached")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error("git diff timed out")
            return ""
        except FileNotFoundError:
            logger.error("git not found on PATH")
            return ""

    @staticmethod
    def _extract_files_from_diff(diff_text: str) -> list[str]:
        """Extract file paths from a git diff."""
        files = []
        for line in diff_text.splitlines():
            if line.startswith("+++ b/"):
                filepath = line[6:]
                if filepath != "/dev/null":
                    files.append(filepath)
            elif line.startswith("--- a/"):
                filepath = line[6:]
                if filepath != "/dev/null" and filepath not in files:
                    files.append(filepath)
        return files

    @staticmethod
    def _detect_subsystems(file_paths: list[str]) -> list[str]:
        """Detect affected subsystems from file paths."""
        subsystems = set()
        for fp in file_paths:
            fp_lower = fp.replace("\\", "/").lower()
            if fp_lower.startswith("frontend/") or fp_lower.endswith((".tsx", ".ts", ".css")):
                subsystems.add("frontend")
            if fp_lower.startswith("backend/") or fp_lower.startswith("infra/"):
                subsystems.add("backend")
            if "lambda" in fp_lower or "handler" in fp_lower:
                subsystems.add("lambda")
            if "dynamo" in fp_lower or "database" in fp_lower or "models" in fp_lower:
                subsystems.add("database")
            if "auth" in fp_lower or "cognito" in fp_lower:
                subsystems.add("auth")
            if "hero" in fp_lower:
                subsystems.add("heroes")
            if "lineup" in fp_lower:
                subsystems.add("lineups")
            if "upgrade" in fp_lower or "calculator" in fp_lower:
                subsystems.add("upgrades")
            if fp_lower.startswith("data/") or fp_lower.endswith(".json"):
                subsystems.add("game-data")
            if fp_lower.startswith("scripts/"):
                subsystems.add("scripts")
            if "test" in fp_lower or "spec" in fp_lower or "e2e" in fp_lower:
                subsystems.add("tests")
        return sorted(subsystems)

    @staticmethod
    def _infer_file_purpose(path: Path) -> str:
        """Infer a file's purpose from its path and name."""
        name = path.name.lower()
        parts = str(path).replace("\\", "/").lower()

        if "page.tsx" in name:
            return "Next.js page component"
        if "layout.tsx" in name:
            return "Next.js layout component"
        if name.endswith(".tsx") and "component" in parts:
            return "React component"
        if name.endswith(".ts") and "hook" in parts:
            return "React hook"
        if name.endswith(".ts") and "util" in parts:
            return "Utility module"
        if "handler" in name:
            return "Lambda handler"
        if "model" in name:
            return "Data model"
        if name.endswith(".json") and "data" in parts:
            return "Game data file"
        if name.endswith(".json") and "edge" in parts:
            return "Upgrade edge graph"
        if name == "template.yaml" or name == "samconfig.toml":
            return "Infrastructure config"
        if name.endswith(".py") and "script" in parts:
            return "Utility script"
        if "test" in name or "spec" in name:
            return "Test file"
        if name.endswith(".css"):
            return "Stylesheet"
        if name.endswith(".md"):
            return "Documentation"

        return "Source file"

    # --- Chunk management for large reviews ---

    def review_large_diff(
        self,
        diff_text: str,
        review_types: Optional[list[ReviewType]] = None,
        context: Optional[str] = None,
        **kwargs: Any,
    ) -> list[ReviewResult]:
        """
        Break a large diff into file-based chunks and review each separately.

        Useful when the diff is too large for a single request.

        Args:
            diff_text: The full git diff.
            review_types: Types of review.
            context: Change description.
            **kwargs: Additional kwargs.

        Returns:
            List of ReviewResults, one per chunk.
        """
        if len(diff_text) <= MAX_CHUNK_CHARS:
            return [self.review_diff(diff_text, review_types=review_types, context=context, **kwargs)]

        chunks = self._split_diff_by_file(diff_text)
        results = []

        logger.info("Large diff split into %d file chunks", len(chunks))

        for i, (files, chunk) in enumerate(chunks, 1):
            logger.info("Reviewing chunk %d/%d (files: %s)", i, len(chunks), ", ".join(files))
            chunk_context = f"{context or 'Code review'} [chunk {i}/{len(chunks)}: {', '.join(files)}]"
            result = self.review_diff(
                chunk,
                review_types=review_types,
                context=chunk_context,
                files_changed=files,
                **kwargs,
            )
            results.append(result)

        return results

    @staticmethod
    def _split_diff_by_file(diff_text: str) -> list[tuple[list[str], str]]:
        """
        Split a diff into per-file chunks.

        Returns a list of (file_list, diff_chunk) tuples.
        Adjacent small files are grouped together to reduce API calls.
        """
        chunks: list[tuple[list[str], str]] = []
        current_files: list[str] = []
        current_lines: list[str] = []
        current_size = 0

        for line in diff_text.splitlines(keepends=True):
            if line.startswith("diff --git"):
                # Start of a new file diff
                if current_lines and current_size > MAX_CHUNK_CHARS:
                    # Current chunk is full, flush it
                    chunks.append((current_files[:], "".join(current_lines)))
                    current_files = []
                    current_lines = []
                    current_size = 0

            if line.startswith("+++ b/"):
                filepath = line[6:].strip()
                if filepath != "/dev/null" and filepath not in current_files:
                    current_files.append(filepath)

            current_lines.append(line)
            current_size += len(line)

        # Flush remaining
        if current_lines:
            chunks.append((current_files, "".join(current_lines)))

        return chunks
