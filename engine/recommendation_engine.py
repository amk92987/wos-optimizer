"""
Main Recommendation Engine - Orchestrates all analyzers for WoS optimization.
Uses rule-based analysis first, with AI fallback for complex questions.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from .analyzers import (
    HeroAnalyzer,
    GearAdvisor,
    LineupBuilder,
    ProgressionTracker,
    RequestClassifier,
    PowerOptimizer,
    PowerUpgrade
)
from .analyzers.request_classifier import RequestType


@dataclass
class Recommendation:
    """Unified recommendation format."""
    priority: int  # 1-5, 1 being highest
    action: str
    category: str  # hero, gear, lineup, progression
    hero: Optional[str]
    reason: str
    resources: str
    relevance_tags: List[str]
    source: str  # 'rules' or 'ai'


class RecommendationEngine:
    """
    Main recommendation engine that coordinates all analyzers.

    Usage:
        engine = RecommendationEngine()
        recommendations = engine.get_recommendations(profile, user_heroes)
        lineup = engine.get_lineup("bear_trap", user_heroes)
        answer = engine.ask(profile, user_heroes, "What should I upgrade next?")
    """

    def __init__(self, data_dir: Path = None):
        """
        Initialize the recommendation engine with game data.

        Args:
            data_dir: Path to data directory (defaults to project data/)
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        elif isinstance(data_dir, str):
            data_dir = Path(data_dir)

        self.data_dir = data_dir

        # Load static game data
        self.heroes_data = self._load_json("heroes.json")
        self.gear_data = self._load_json("chief_gear.json")

        # Initialize analyzers
        self.hero_analyzer = HeroAnalyzer(self.heroes_data)
        self.gear_advisor = GearAdvisor(self.gear_data)
        self.lineup_builder = LineupBuilder(self.heroes_data)
        self.progression_tracker = ProgressionTracker()
        self.request_classifier = RequestClassifier()
        self.power_optimizer = PowerOptimizer(str(data_dir))

        # AI fallback (lazy loaded)
        self._ai_recommender = None

    def _load_json(self, filename: str) -> dict:
        """Load a JSON file from the data directory."""
        path = self.data_dir / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @property
    def ai_recommender(self):
        """Lazy load AI recommender only when needed."""
        if self._ai_recommender is None:
            try:
                from .ai_recommender import AIRecommender
                self._ai_recommender = AIRecommender()
            except Exception:
                self._ai_recommender = None
        return self._ai_recommender

    def get_recommendations(
        self,
        profile,
        user_heroes: list,
        user_gear: list = None,
        user_charms: list = None,
        gear_dict: dict = None,
        limit: int = 10,
        include_power: bool = True
    ) -> List[Recommendation]:
        """
        Get personalized recommendations based on user's profile and heroes.

        Args:
            profile: User profile with priorities and server info
            user_heroes: List of user's owned heroes with stats
            user_gear: Optional list of user's chief gear ORM objects (for PowerOptimizer)
            user_charms: Optional list of user's chief charms ORM objects (for PowerOptimizer)
            gear_dict: Optional dict for GearAdvisor (format: {'chief_gear': {...}, 'hero_gear': {...}})
            limit: Maximum recommendations to return
            include_power: Whether to include power-based recommendations

        Returns:
            List of Recommendation objects, sorted by priority
        """
        all_recommendations = []

        # Convert user_heroes list to dict for easier lookup
        heroes_dict = self._heroes_list_to_dict(user_heroes)

        # Get hero recommendations
        hero_recs = self.hero_analyzer.analyze(profile, user_heroes)
        for rec in hero_recs:
            all_recommendations.append(Recommendation(
                priority=rec.priority,
                action=rec.action,
                category="hero",
                hero=rec.hero,
                reason=rec.reason,
                resources=rec.resources,
                relevance_tags=rec.relevance_tags,
                source="rules"
            ))

        # Get gear recommendations (from rule-based GearAdvisor)
        # GearAdvisor expects dict format: {'chief_gear': {...}, 'hero_gear': {...}}
        # Convert user_gear ORM objects to dict format if gear_dict not provided
        if not gear_dict and user_gear:
            gear_dict = self._convert_gear_to_dict(user_gear)
        gear_recs = self.gear_advisor.analyze(profile, gear_dict or {})
        for rec in gear_recs:
            all_recommendations.append(Recommendation(
                priority=rec.priority,
                action=rec.action,
                category="gear",
                hero=rec.piece if rec.gear_type == "hero" else None,
                reason=rec.reason,
                resources=rec.resources,
                relevance_tags=rec.relevance_tags,
                source="rules"
            ))

        # Get progression tips
        phase_tips = self.progression_tracker.get_phase_tips(profile)
        for tip in phase_tips:
            all_recommendations.append(Recommendation(
                priority=tip.priority,
                action=tip.action,
                category="progression",
                hero=None,
                reason=tip.reason,
                resources="",
                relevance_tags=tip.relevance_tags,
                source="rules"
            ))

        # Get power-based recommendations
        if include_power:
            user_data = {
                "user_heroes": user_heroes,
                "user_gear": user_gear or [],
                "user_charms": user_charms or []
            }
            power_recs = self.power_optimizer.get_top_recommendations(profile, user_data, limit=limit)
            for rec in power_recs:
                # Convert PowerUpgrade to Recommendation
                power_str = f"+{rec.power_gain:,.0f} power" if rec.power_gain > 0 else ""
                bonus_str = f"+{rec.bonus_gain:.1f}%" if rec.bonus_gain > 0 else ""
                efficiency_str = f"Efficiency: {rec.efficiency:.1f}" if rec.efficiency > 0 else ""

                detail_parts = [p for p in [power_str, bonus_str, efficiency_str] if p]
                detail = f" ({', '.join(detail_parts)})" if detail_parts else ""

                all_recommendations.append(Recommendation(
                    priority=rec.priority,
                    action=f"Upgrade {rec.target}: {rec.from_level} → {rec.to_level}",
                    category=rec.upgrade_type,
                    hero=rec.target if rec.upgrade_type in ["hero_level", "hero_star"] else None,
                    reason=f"{rec.reason}{detail}",
                    resources=", ".join(f"{k}: {v}" for k, v in rec.resource_cost.items()) if rec.resource_cost else "",
                    relevance_tags=rec.relevance_tags,
                    source="power"
                ))

        # Sort by priority and deduplicate
        all_recommendations.sort(key=lambda x: x.priority)

        # Remove duplicate actions
        seen_actions = set()
        unique_recommendations = []
        for rec in all_recommendations:
            action_key = rec.action.lower()
            if action_key not in seen_actions:
                seen_actions.add(action_key)
                unique_recommendations.append(rec)

        return unique_recommendations[:limit]

    def get_power_recommendations(
        self,
        profile,
        user_heroes: list,
        user_gear: list = None,
        user_charms: list = None,
        limit: int = 10
    ) -> List[PowerUpgrade]:
        """
        Get power-based upgrade recommendations only.

        Args:
            profile: User profile
            user_heroes: List of user's heroes
            user_gear: List of user's chief gear
            user_charms: List of user's chief charms
            limit: Maximum recommendations

        Returns:
            List of PowerUpgrade objects sorted by efficiency
        """
        user_data = {
            "user_heroes": user_heroes,
            "user_gear": user_gear or [],
            "user_charms": user_charms or []
        }
        return self.power_optimizer.get_top_recommendations(profile, user_data, limit)

    def get_lineup(
        self,
        game_mode: str,
        user_heroes: list,
        profile=None
    ) -> dict:
        """
        Get the best lineup for a specific game mode.

        Args:
            game_mode: Game mode (e.g., "bear_trap", "rally_joiner_attack")
            user_heroes: List of user's owned heroes
            profile: Optional user profile

        Returns:
            Dict with lineup information
        """
        heroes_dict = self._heroes_list_to_dict(user_heroes)
        lineup = self.lineup_builder.build_lineup(game_mode, heroes_dict, profile)

        return {
            "mode": lineup.game_mode,
            "heroes": lineup.heroes,
            "troop_ratio": lineup.troop_ratio,
            "notes": lineup.notes,
            "confidence": lineup.confidence
        }

    def get_all_lineups(self, user_heroes: list, profile=None) -> Dict[str, dict]:
        """Get lineups for all game modes."""
        heroes_dict = self._heroes_list_to_dict(user_heroes)
        lineups = self.lineup_builder.get_all_lineups(heroes_dict, profile)

        return {
            mode: {
                "mode": lineup.game_mode,
                "heroes": lineup.heroes,
                "troop_ratio": lineup.troop_ratio,
                "notes": lineup.notes,
                "confidence": lineup.confidence
            }
            for mode, lineup in lineups.items()
        }

    def get_joiner_recommendation(self, user_heroes: list, attack: bool = True) -> dict:
        """Get specific recommendation for joining rallies."""
        heroes_dict = self._heroes_list_to_dict(user_heroes)
        return self.lineup_builder.get_joiner_recommendation(heroes_dict, attack)

    def ask(
        self,
        profile,
        user_heroes: list,
        question: str,
        user_gear: dict = None,
        force_ai: bool = False
    ) -> Dict[str, Any]:
        """
        Answer a question using rules or AI as appropriate.

        Args:
            profile: User profile
            user_heroes: List of user's heroes
            question: User's question
            user_gear: Optional gear status
            force_ai: Force AI response even if rules could answer

        Returns:
            Dict with answer, source, and any recommendations
        """
        # Classify the request
        classified = self.request_classifier.classify(question)

        heroes_dict = self._heroes_list_to_dict(user_heroes)

        # Try rules first unless forcing AI
        if not force_ai and classified.request_type in [RequestType.RULES, RequestType.HYBRID]:
            rules_result = self._handle_with_rules(
                classified,
                profile,
                user_heroes,
                heroes_dict,
                user_gear,
                question
            )

            if rules_result:
                # Check if we need AI fallback
                if classified.request_type == RequestType.HYBRID:
                    if self.request_classifier.needs_ai_fallback(
                        rules_result.get("recommendations", []),
                        question
                    ):
                        # Enhance with AI
                        ai_result = self._handle_with_ai(profile, user_heroes, question)
                        if ai_result:
                            rules_result["ai_enhancement"] = ai_result

                return rules_result

        # Use AI
        ai_result = self._handle_with_ai(profile, user_heroes, question)
        return ai_result or {
            "answer": "Unable to process request. Please try rephrasing your question.",
            "source": "error",
            "recommendations": []
        }

    def _handle_with_rules(
        self,
        classified,
        profile,
        user_heroes: list,
        heroes_dict: dict,
        user_gear: dict,
        question: str
    ) -> Optional[Dict[str, Any]]:
        """Handle a request using rule-based analyzers."""

        result = {
            "source": "rules",
            "category": classified.category,
            "confidence": classified.confidence,
            "recommendations": []
        }

        # Route to appropriate handler
        if classified.category in ["lineup", "joiner_heroes"]:
            # Try to find matching lineup
            lineup_rec = self.lineup_builder.get_lineup_for_question(question, heroes_dict)
            if lineup_rec:
                result["lineup"] = {
                    "mode": lineup_rec.game_mode,
                    "heroes": lineup_rec.heroes,
                    "troop_ratio": lineup_rec.troop_ratio,
                    "notes": lineup_rec.notes,
                    "confidence": lineup_rec.confidence
                }
                result["answer"] = f"For {lineup_rec.game_mode}, here's your recommended lineup."

            # Also check joiner recommendation if relevant
            if "join" in question.lower():
                attack = "attack" in question.lower() or "defense" not in question.lower()
                joiner_rec = self.lineup_builder.get_joiner_recommendation(heroes_dict, attack)
                result["joiner_recommendation"] = joiner_rec

        elif classified.category in ["upgrade", "skills", "invest"]:
            hero_recs = self.hero_analyzer.analyze(profile, user_heroes)
            result["recommendations"] = [asdict(r) for r in hero_recs[:5]]
            result["answer"] = f"Based on your heroes and priorities, here are your top upgrade recommendations."

        elif classified.category == "gear":
            gear_recs = self.gear_advisor.analyze(profile, user_gear or {})
            result["recommendations"] = [asdict(r) for r in gear_recs[:5]]
            result["answer"] = "Here's your gear upgrade priority order."

        elif classified.category in ["phase", "progression"]:
            phase_id = self.progression_tracker.detect_phase(profile)
            phase_info = self.progression_tracker.get_phase_info(phase_id)
            phase_tips = self.progression_tracker.get_phase_tips(profile)
            next_milestone = self.progression_tracker.get_next_milestone(profile)

            result["phase"] = {
                "id": phase_id,
                "name": phase_info.get("name", phase_id),
                "focus": phase_info.get("focus", []),
                "next_milestone": next_milestone
            }
            result["recommendations"] = [asdict(t) for t in phase_tips[:5]]
            result["answer"] = f"You're in {phase_info.get('name', 'Unknown')} phase."

        elif classified.category == "priority":
            # Combined recommendations
            all_recs = self.get_recommendations(profile, user_heroes, user_gear, limit=5)
            result["recommendations"] = [asdict(r) for r in all_recs]
            result["answer"] = "Here are your top priorities right now."

        else:
            # Default to combined recommendations
            all_recs = self.get_recommendations(profile, user_heroes, user_gear, limit=5)
            result["recommendations"] = [asdict(r) for r in all_recs]
            result["answer"] = "Here's what I recommend based on your current status."

        return result

    def _handle_with_ai(self, profile, user_heroes: list, question: str) -> Optional[Dict[str, Any]]:
        """Handle a request using AI."""
        if not self.ai_recommender or not self.ai_recommender.is_available():
            return None

        try:
            answer = self.ai_recommender.ask_question(
                profile,
                user_heroes,
                self.heroes_data,
                question
            )

            return {
                "answer": answer,
                "source": "ai",
                "recommendations": []
            }
        except Exception as e:
            return {
                "answer": f"AI unavailable: {str(e)}",
                "source": "error",
                "recommendations": []
            }

    def _heroes_list_to_dict(self, user_heroes: list) -> dict:
        """Convert user_heroes list to dict format."""
        heroes_dict = {}
        for uh in user_heroes:
            if hasattr(uh, 'hero') and uh.hero:
                name = uh.hero.name
            else:
                name = getattr(uh, 'name', '')

            if name:
                # Get individual skill levels (UserHero has 3 of each type)
                exp_skill_1 = getattr(uh, 'expedition_skill_1_level', None) or 1
                exp_skill_2 = getattr(uh, 'expedition_skill_2_level', None) or 1
                exp_skill_3 = getattr(uh, 'expedition_skill_3_level', None) or 1
                expl_skill_1 = getattr(uh, 'exploration_skill_1_level', None) or 1
                expl_skill_2 = getattr(uh, 'exploration_skill_2_level', None) or 1
                expl_skill_3 = getattr(uh, 'exploration_skill_3_level', None) or 1

                heroes_dict[name] = {
                    'level': getattr(uh, 'level', 1) or 1,
                    'stars': getattr(uh, 'stars', 1) or 1,
                    # Individual skills
                    'expedition_skill_1': exp_skill_1,
                    'expedition_skill_2': exp_skill_2,
                    'expedition_skill_3': exp_skill_3,
                    'exploration_skill_1': expl_skill_1,
                    'exploration_skill_2': expl_skill_2,
                    'exploration_skill_3': expl_skill_3,
                    # Max of each type for general use
                    'expedition_skill': max(exp_skill_1, exp_skill_2, exp_skill_3),
                    'exploration_skill': max(expl_skill_1, expl_skill_2, expl_skill_3),
                }

        return heroes_dict

    def _convert_gear_to_dict(self, user_gear: list) -> dict:
        """Convert user_gear ORM objects to dict format for GearAdvisor."""
        gear_dict = {'chief_gear': {}, 'hero_gear': {}}

        for gear in user_gear:
            # UserChiefGear has attributes like ring_quality, amulet_quality, etc.
            if hasattr(gear, 'ring_quality'):
                gear_dict['chief_gear'] = {
                    'ring': getattr(gear, 'ring_quality', None) or 1,
                    'amulet': getattr(gear, 'amulet_quality', None) or 1,
                    'helmet': getattr(gear, 'helmet_quality', None) or 1,
                    'armor': getattr(gear, 'armor_quality', None) or 1,
                    'gloves': getattr(gear, 'gloves_quality', None) or 1,
                    'boots': getattr(gear, 'boots_quality', None) or 1,
                }

        return gear_dict

    def get_phase_info(self, profile) -> dict:
        """Get current progression phase information."""
        phase_id = self.progression_tracker.detect_phase(profile)
        phase_info = self.progression_tracker.get_phase_info(phase_id)
        next_milestone = self.progression_tracker.get_next_milestone(profile)

        return {
            "phase_id": phase_id,
            "phase_name": phase_info.get("name", phase_id),
            "focus_areas": phase_info.get("focus", []),
            "common_mistakes": phase_info.get("common_mistakes", []),
            "bottlenecks": phase_info.get("bottlenecks", []),
            "next_milestone": next_milestone
        }

    def get_gear_priority(self, spending_profile: str = "f2p") -> List[dict]:
        """Get gear upgrade priority order for a spending profile."""
        return self.gear_advisor.get_gear_priority_order(spending_profile)

    def to_json(self, recommendations: List[Recommendation]) -> str:
        """Convert recommendations to JSON string."""
        return json.dumps([asdict(r) for r in recommendations], indent=2)


# Convenience function for quick access
def get_engine(data_dir: Path = None) -> RecommendationEngine:
    """Get a recommendation engine instance."""
    return RecommendationEngine(data_dir)
