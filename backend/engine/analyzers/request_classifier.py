"""
Request Classifier - Determines if a request can be handled by rules or needs AI.
Routes questions to the appropriate handler.
"""

import re
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class RequestType(Enum):
    RULES = "rules"
    AI = "ai"
    HYBRID = "hybrid"  # Rules first, AI as fallback


@dataclass
class ClassifiedRequest:
    """Result of classifying a user request."""
    request_type: RequestType
    category: str  # e.g., "lineup", "upgrade", "gear", etc.
    confidence: float  # 0.0 to 1.0
    rule_handler: Optional[str]  # Which analyzer should handle it
    reason: str


# Patterns that can be answered by rules
RULE_PATTERNS = [
    # Upgrade/progression questions
    (r"what should i (upgrade|level|focus)", "upgrade", "hero_analyzer", 0.9),
    (r"(upgrade|level) .* (first|next)", "upgrade", "hero_analyzer", 0.85),
    (r"priority", "priority", "progression_tracker", 0.8),
    (r"what to (upgrade|do) next", "upgrade", "hero_analyzer", 0.85),
    (r"how (should|do) i (upgrade|improve|progress)", "upgrade", "progression_tracker", 0.8),

    # Lineup questions
    (r"best (lineup|team|composition|heroes)", "lineup", "lineup_builder", 0.9),
    (r"(bear trap|crazy joe|rally)", "lineup", "lineup_builder", 0.85),
    (r"who should i use", "lineup", "lineup_builder", 0.8),
    (r"garrison|defense|reinforce", "lineup", "lineup_builder", 0.85),
    (r"joiner|joining", "lineup", "lineup_builder", 0.9),
    (r"exploration|frozen|pve", "lineup", "lineup_builder", 0.8),

    # Gear questions
    (r"(chief|hero) gear", "gear", "gear_advisor", 0.9),
    (r"ring|amulet|gloves|boots|helmet|armor", "gear", "gear_advisor", 0.85),
    (r"upgrade.*gear", "gear", "gear_advisor", 0.85),
    (r"what gear", "gear", "gear_advisor", 0.8),

    # Hero-specific questions (only factual lookups, not opinions/comparisons)
    (r"jessie|sergey", "joiner_heroes", "hero_analyzer", 0.9),
    (r"(expedition|exploration) skill", "skills", "hero_analyzer", 0.85),
    (r"(hero|heroes) to invest", "invest", "hero_analyzer", 0.8),

    # Shop/spending questions (often need AI for complex decisions)
    (r"what to buy", "shop", "rules", 0.7),

    # Phase/progression questions
    (r"(early|mid|late) game", "phase", "progression_tracker", 0.8),
    (r"furnace|fc ", "progression", "progression_tracker", 0.75),
]

# Patterns that need AI (complex, contextual, hypothetical)
AI_PATTERNS = [
    (r"what if", "hypothetical", 0.95),
    (r"should i (buy|spend|invest)", "spending_decision", 0.85),
    (r"compare .* vs", "comparison", 0.9),
    (r"explain|why", "explanation", 0.8),
    (r"is it worth", "value_judgment", 0.85),
    (r"(worth|good) (to |)(invest|upgrading|leveling|promoting)", "value_judgment", 0.85),
    (r"better|worse", "comparison", 0.8),
    (r"more important", "comparison", 0.9),
    (r"which (is|should|do) .* (more|first|better)", "comparison", 0.85),
    (r"(hero power|chief gear|troop).* or .*(hero power|chief gear|troop)", "comparison", 0.85),
    (r"or should i", "comparison", 0.85),
    (r"stick with|switch to|replace", "comparison", 0.8),
    (r"mistake|wrong", "advice", 0.75),
    (r"(your|what do you) (think|recommend)", "opinion", 0.7),
    (r"strategy|plan|approach", "strategic", 0.7),
    # Hero opinions and evaluations (need AI context)
    (r"(is|are) .* (good|worth|viable)", "hero_opinion", 0.8),
    (r"what is .* good (for|at)", "hero_opinion", 0.8),
    (r"how (good|useful) is", "hero_opinion", 0.8),
    (r"tell me about", "hero_info_ai", 0.75),
    # Alliance and R4/R5 specific topics
    (r"alliance (tech|research|gift)", "alliance", 0.9),
    (r"r4|r5|rally lead", "alliance_role", 0.85),
    (r"alliance", "alliance", 0.75),
]


class RequestClassifier:
    """Classify user requests to route them appropriately."""

    def __init__(self):
        self.rule_patterns = RULE_PATTERNS
        self.ai_patterns = AI_PATTERNS

    def classify(self, question: str) -> ClassifiedRequest:
        """
        Classify a user's question.

        Args:
            question: The user's question or request

        Returns:
            ClassifiedRequest with routing information
        """
        question_lower = question.lower().strip()

        # Check for explicit AI request
        if any(phrase in question_lower for phrase in ["ai", "claude", "gpt", "help me think"]):
            return ClassifiedRequest(
                request_type=RequestType.AI,
                category="explicit_ai",
                confidence=1.0,
                rule_handler=None,
                reason="User explicitly requested AI assistance"
            )

        # Check AI patterns first (they take precedence)
        for pattern, category, confidence in self.ai_patterns:
            if re.search(pattern, question_lower):
                return ClassifiedRequest(
                    request_type=RequestType.AI,
                    category=category,
                    confidence=confidence,
                    rule_handler=None,
                    reason=f"Question type '{category}' requires contextual AI analysis"
                )

        # Check rule patterns
        best_match = None
        best_confidence = 0.0

        for pattern, category, handler, confidence in self.rule_patterns:
            if re.search(pattern, question_lower):
                if confidence > best_confidence:
                    best_match = (pattern, category, handler, confidence)
                    best_confidence = confidence

        if best_match:
            _, category, handler, confidence = best_match
            return ClassifiedRequest(
                request_type=RequestType.RULES,
                category=category,
                confidence=confidence,
                rule_handler=handler,
                reason=f"Question about '{category}' can be answered with game rules"
            )

        # Default: route to AI when no specific pattern matched
        return ClassifiedRequest(
            request_type=RequestType.AI,
            category="general",
            confidence=0.5,
            rule_handler=None,
            reason="No specific rule pattern matched - using AI"
        )

    def get_handler_for_category(self, category: str) -> str:
        """Get the appropriate handler for a category."""
        handlers = {
            "upgrade": "hero_analyzer",
            "lineup": "lineup_builder",
            "gear": "gear_advisor",
            "phase": "progression_tracker",
            "progression": "progression_tracker",
            "joiner_heroes": "hero_analyzer",
            "skills": "hero_analyzer",
            "invest": "hero_analyzer",
            "shop": "shop_advisor",  # Not implemented yet
            "general": "progression_tracker"
        }
        return handlers.get(category, "progression_tracker")

    def needs_ai_fallback(self, rules_result: list, question: str) -> bool:
        """
        Determine if AI fallback is needed after rules produced a result.

        Args:
            rules_result: Result from rule-based analysis
            question: Original question

        Returns:
            True if AI should be called for additional context
        """
        # If no rules matched, need AI
        if not rules_result:
            return True

        # If question is asking for explanation and we only have facts
        question_lower = question.lower()
        if any(word in question_lower for word in ["why", "explain", "how come", "reason"]):
            return True

        # If question is comparative and we only have single recommendations
        if "vs" in question_lower or "or" in question_lower:
            return True

        return False

    def extract_entities(self, question: str) -> dict:
        """
        Extract game-specific entities from a question.

        Args:
            question: User's question

        Returns:
            Dict with extracted entities
        """
        entities = {
            "heroes": [],
            "game_modes": [],
            "gear_pieces": [],
            "resources": []
        }

        question_lower = question.lower()

        # Extract hero names
        hero_names = [
            "jessie", "sergey", "jeronimo", "natalia", "molly", "zinman",
            "bahiti", "gina", "flint", "philly", "alonso", "logan", "mia",
            "greg", "ahmose", "reina", "lynn", "hector", "wu ming", "patrick",
            "charlie", "cloris", "gordon", "renee", "eugene"
        ]
        for hero in hero_names:
            if hero in question_lower:
                entities["heroes"].append(hero.title())

        # Extract game modes
        modes = {
            "bear trap": "bear_trap",
            "crazy joe": "crazy_joe",
            "garrison": "garrison",
            "rally": "rally",
            "svs": "svs",
            "exploration": "exploration",
            "pve": "exploration"
        }
        for mode_text, mode_id in modes.items():
            if mode_text in question_lower:
                entities["game_modes"].append(mode_id)

        # Extract gear pieces
        gear_pieces = ["ring", "amulet", "gloves", "boots", "helmet", "armor"]
        for piece in gear_pieces:
            if piece in question_lower:
                entities["gear_pieces"].append(piece.title())

        return entities
