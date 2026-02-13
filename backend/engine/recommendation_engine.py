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
        """Load a JSON file from the data directory, with DynamoDB fallback for heroes."""
        path = self.data_dir / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        # Lambda fallback: load heroes from DynamoDB reference table
        if filename == "heroes.json":
            try:
                from common.hero_repo import get_all_reference_heroes_from_db
                heroes = get_all_reference_heroes_from_db()
                if heroes:
                    return {"heroes": heroes}
            except Exception:
                pass
        return {}

    def _get_hero_info_from_question(self, question: str) -> Optional[Dict[str, Any]]:
        """Extract hero name from question and return hero info in conversational WoS style."""
        question_lower = question.lower()

        # Search for hero names in the question
        heroes = self.heroes_data.get('heroes', [])
        matched_hero = None

        for hero in heroes:
            hero_name = hero.get('name', '').lower()
            if hero_name and hero_name in question_lower:
                matched_hero = hero
                break

        if not matched_hero:
            return None

        # Build a conversational summary using WoS terminology
        name = matched_hero.get('name', 'Unknown')
        hero_class = matched_hero.get('hero_class', 'Unknown')
        generation = matched_hero.get('generation', '?')
        tier = matched_hero.get('tier_overall', '?')
        rarity = matched_hero.get('rarity', 'Unknown')

        # Get the top expedition skill (most important for rallies)
        top_exped_skill = matched_hero.get('expedition_skill_1', '')
        top_exped_desc = matched_hero.get('expedition_skill_1_desc', '')

        # Build conversational response
        summary_parts = []

        # Opening line with tier assessment
        if tier in ['S+', 'S']:
            summary_parts.append(f"Chief, {name} is a high-value {hero_class} from Gen {generation}. Rated {tier} tier - definitely worth committing resources to.")
        elif tier == 'A':
            summary_parts.append(f"{name} is a solid Gen {generation} {hero_class}, rated {tier} tier. Good efficiency for most content.")
        elif tier == 'B':
            summary_parts.append(f"{name} is a Gen {generation} {hero_class}, rated {tier} tier. Decent early-mid game but you'll want to transition to higher gen heroes eventually.")
        else:
            summary_parts.append(f"{name} is a Gen {generation} {hero_class}, rated {tier} tier. Low-return investment at this point - hold your resources for better options.")

        # Class-specific value
        summary_parts.append("")
        if hero_class == "Infantry":
            summary_parts.append(f"As Infantry, {name} buffs your frontline troops. Your Coat and Pants chief gear directly boost {name}'s effectiveness.")
        elif hero_class == "Marksman":
            summary_parts.append(f"As Marksman, {name} deals ranged damage from the back line. Belt and Shortstaff chief gear are your efficiency multipliers here.")
        elif hero_class == "Lancer":
            summary_parts.append(f"As Lancer, {name} is a balanced fighter with good survivability. Hat and Watch chief gear boost this class.")

        # Key skill callout
        if top_exped_skill:
            summary_parts.append("")
            if top_exped_desc:
                summary_parts.append(f"Key expedition skill: **{top_exped_skill}** - {top_exped_desc}")
            else:
                summary_parts.append(f"Key expedition skill: **{top_exped_skill}**")

        # Practical advice based on tier
        summary_parts.append("")
        if tier in ['S+', 'S']:
            summary_parts.append(f"Bottom line: Promote {name} when you can. This is almost always a good investment for your settlement's power.")
        elif tier == 'A':
            summary_parts.append(f"Bottom line: {name} is worth promoting if you don't have higher-tier alternatives. Check your roster first.")
        else:
            summary_parts.append(f"Bottom line: Unless {name} is one of your only options, you're better off holding those manuals for a higher-value hero.")

        return {
            "hero": matched_hero,
            "summary": "\n".join(summary_parts)
        }

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
            "game_mode": lineup.game_mode,
            "heroes": lineup.heroes,
            "troop_ratio": lineup.troop_ratio,
            "notes": lineup.notes,
            "confidence": lineup.confidence,
            "recommended_to_get": lineup.recommended_to_get,
        }

    def get_all_lineups(self, user_heroes: list, profile=None) -> Dict[str, dict]:
        """Get lineups for all game modes."""
        heroes_dict = self._heroes_list_to_dict(user_heroes)
        lineups = self.lineup_builder.get_all_lineups(heroes_dict, profile)

        return {
            mode: {
                "game_mode": lineup.game_mode,
                "heroes": lineup.heroes,
                "troop_ratio": lineup.troop_ratio,
                "notes": lineup.notes,
                "confidence": lineup.confidence,
                "recommended_to_get": lineup.recommended_to_get,
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
        if ai_result:
            return ai_result

        # AI not available - try rules as fallback
        rules_fallback = self._handle_with_rules(
            classified, profile, user_heroes,
            self._heroes_list_to_dict(user_heroes), user_gear, question
        )
        if rules_fallback and rules_fallback.get("answer"):
            rules_fallback["source"] = "rules"
            return rules_fallback

        return {
            "answer": "Hey Chief! I can help with hero lineups, upgrade priorities, SvS strategy, gear recommendations, and rally compositions. What specifically would you like to know?",
            "source": "rules",
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
                # Build a conversational answer with the lineup details
                hero_list = ", ".join([f"{h['hero']} ({h['role']})" for h in lineup_rec.heroes])
                troop_parts = [f"{v}% {k}" for k, v in lineup_rec.troop_ratio.items() if v > 0]
                troop_str = " / ".join(troop_parts)
                result["answer"] = f"Chief, for {lineup_rec.game_mode}:\n\nRun **{hero_list}** in that order.\n\nTroop composition: {troop_str}\n\n{lineup_rec.notes}"
            else:
                # Fallback answer if no specific lineup matched
                result["answer"] = "Chief, I'm not sure which lineup you're asking about. Try asking about Bear Trap, Crazy Joe, Garrison defense, SvS marches, or rally joining - I can give you specific hero and troop recommendations for each."

            # Also check joiner recommendation if relevant
            if "join" in question.lower():
                attack = "attack" in question.lower() or "defense" not in question.lower()
                joiner_rec = self.lineup_builder.get_joiner_recommendation(heroes_dict, attack)
                result["joiner_recommendation"] = joiner_rec

        elif classified.category == "hero_info":
            # Extract hero name from question and look up info
            hero_info = self._get_hero_info_from_question(question)
            if hero_info:
                result["hero_info"] = hero_info
                result["answer"] = hero_info["summary"]
            else:
                result["answer"] = "Chief, I couldn't identify which hero you're asking about. Try asking something like 'What is Jessie good for?' or 'Tell me about Sergey' - I can give you tier ratings, skill breakdowns, and investment advice."

        elif classified.category in ["upgrade", "skills", "invest"]:
            hero_recs = self.hero_analyzer.analyze(profile, user_heroes)
            result["recommendations"] = [asdict(r) for r in hero_recs[:5]]
            if hero_recs:
                top_hero = hero_recs[0].hero if hasattr(hero_recs[0], 'hero') else "your top hero"
                result["answer"] = f"Chief, based on your roster and priorities, I'd focus on promoting {top_hero} first. That's your highest efficiency play right now."
            else:
                result["answer"] = "Chief, I need more info about your heroes to give specific upgrade advice. Add some heroes to your tracker first."

        elif classified.category == "gear":
            gear_recs = self.gear_advisor.analyze(profile, user_gear or {})
            result["recommendations"] = [asdict(r) for r in gear_recs[:5]]
            result["answer"] = "Chief, for gear upgrades, focus on your main class first. Each tier jump is a significant power boost to your settlement."

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
            phase_name = phase_info.get('name', 'Unknown')
            next_name = next_milestone.get('name', 'your next goal') if next_milestone else 'endgame'
            result["answer"] = f"Chief, you're in {phase_name}. Your route to {next_name} should be your main focus - don't get distracted by side upgrades."

        elif classified.category == "priority":
            # Combined recommendations
            all_recs = self.get_recommendations(profile, user_heroes, user_gear, limit=5)
            result["recommendations"] = [asdict(r) for r in all_recs]
            result["answer"] = "Chief, here's where to commit your resources for maximum efficiency right now."

        else:
            # Default - friendly open-ended response
            result["answer"] = "Hey Chief! I can help with things like hero lineups, upgrade priorities, SvS strategy, gear recommendations, rally compositions, and pretty much anything else about Whiteout Survival. What's on your mind?"

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
                "provider": self.ai_recommender.active_provider or "openai",
                "model": "claude-sonnet-4-20250514" if self.ai_recommender.active_provider == "anthropic" else "gpt-4o-mini",
                "recommendations": []
            }
        except Exception as e:
            # Log the actual error but show user-friendly message
            error_str = str(e).lower()
            if 'api' in error_str or 'key' in error_str or 'auth' in error_str:
                user_message = "AI service configuration issue. Please contact support."
            elif 'timeout' in error_str or 'connection' in error_str:
                user_message = "Could not reach AI service. Please try again."
            elif 'rate' in error_str or 'limit' in error_str:
                user_message = "AI request limit reached. Please try again later."
            else:
                user_message = "AI service is temporarily unavailable."
            return {
                "answer": user_message,
                "source": "error",
                "recommendations": []
            }

    def _heroes_list_to_dict(self, user_heroes: list) -> dict:
        """Convert user_heroes list to dict format.

        Handles both SQLAlchemy ORM objects (Streamlit) and plain dicts (DynamoDB).
        """
        heroes_dict = {}
        for uh in user_heroes:
            # Determine hero name based on data type
            if isinstance(uh, dict):
                # DynamoDB items are plain dicts with hero_name or name key
                name = uh.get('hero_name', uh.get('name', ''))
            elif hasattr(uh, 'hero') and uh.hero:
                name = uh.hero.name
            else:
                name = getattr(uh, 'name', '')

            if name:
                # Helper to get a value from either a dict or ORM object
                # Cast to int to handle DynamoDB Decimal types
                def _val(key, default=1):
                    if isinstance(uh, dict):
                        v = uh.get(key, default) or default
                    else:
                        v = getattr(uh, key, default) or default
                    return int(v)

                # Get individual skill levels
                # DynamoDB stores as *_level suffix, ORM uses *_level attribute
                if isinstance(uh, dict):
                    exp_skill_1 = int(uh.get('expedition_skill_1_level', uh.get('expedition_skill_1', 1)) or 1)
                    exp_skill_2 = int(uh.get('expedition_skill_2_level', uh.get('expedition_skill_2', 1)) or 1)
                    exp_skill_3 = int(uh.get('expedition_skill_3_level', uh.get('expedition_skill_3', 1)) or 1)
                    expl_skill_1 = int(uh.get('exploration_skill_1_level', uh.get('exploration_skill_1', 1)) or 1)
                    expl_skill_2 = int(uh.get('exploration_skill_2_level', uh.get('exploration_skill_2', 1)) or 1)
                    expl_skill_3 = int(uh.get('exploration_skill_3_level', uh.get('exploration_skill_3', 1)) or 1)
                else:
                    exp_skill_1 = int(getattr(uh, 'expedition_skill_1_level', None) or getattr(uh, 'expedition_skill_1', None) or 1)
                    exp_skill_2 = int(getattr(uh, 'expedition_skill_2_level', None) or getattr(uh, 'expedition_skill_2', None) or 1)
                    exp_skill_3 = int(getattr(uh, 'expedition_skill_3_level', None) or getattr(uh, 'expedition_skill_3', None) or 1)
                    expl_skill_1 = int(getattr(uh, 'exploration_skill_1_level', None) or getattr(uh, 'exploration_skill_1', None) or 1)
                    expl_skill_2 = int(getattr(uh, 'exploration_skill_2_level', None) or getattr(uh, 'exploration_skill_2', None) or 1)
                    expl_skill_3 = int(getattr(uh, 'exploration_skill_3_level', None) or getattr(uh, 'exploration_skill_3', None) or 1)

                heroes_dict[name] = {
                    'level': _val('level', 1),
                    'stars': _val('stars', 1),
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

    def get_hero_investments(
        self,
        profile,
        user_heroes: list,
        limit: int = 10
    ) -> List[dict]:
        """
        Get hero investment recommendations based on spending profile.

        Returns a list of dicts matching the frontend HeroInvestment interface:
            hero, hero_class, tier, generation, current_level, target_level,
            current_stars, target_stars, priority, reason
        """
        heroes_dict = self._heroes_list_to_dict(user_heroes)
        if not heroes_dict:
            return []

        server_age = getattr(profile, 'server_age_days', 0) or 0
        current_gen = self.hero_analyzer.get_current_generation(int(server_age))
        spending_profile = getattr(profile, 'spending_profile', 'f2p') or 'f2p'
        is_farm = getattr(profile, 'is_farm_account', False)

        # Rank heroes by investment value
        ranked = self.hero_analyzer.rank_heroes_by_value(heroes_dict, current_gen)

        # Hero investment limits by spending profile
        hero_limits = {
            'f2p': 3, 'minnow': 4, 'dolphin': 6, 'orca': 10, 'whale': 999,
        }
        max_heroes = hero_limits.get(spending_profile, 3)
        if is_farm:
            max_heroes = 2

        results = []
        for priority_rank, name in enumerate(ranked[:max_heroes], start=1):
            hero_data = self.hero_analyzer.hero_lookup.get(name, {})
            hero_gen = hero_data.get('generation', 1)
            tier = hero_data.get('tier_overall', 'C')
            hero_class = hero_data.get('hero_class', 'Unknown')

            stats = heroes_dict.get(name, {})
            current_level = int(stats.get('level', 1))
            current_stars = int(stats.get('stars', 0))

            # Determine target level/stars based on spending profile and generation
            if spending_profile in ('whale', 'orca'):
                target_level = 80
                target_stars = 5
            elif spending_profile == 'dolphin':
                if hero_gen >= current_gen - 1:
                    target_level = 70
                    target_stars = 4
                else:
                    target_level = 60
                    target_stars = 3
            elif spending_profile == 'minnow':
                if hero_gen >= current_gen - 2:
                    target_level = 60
                    target_stars = 3
                else:
                    target_level = 50
                    target_stars = 2
            else:  # f2p
                if hero_gen >= current_gen - 1:
                    target_level = 50
                    target_stars = 2
                else:
                    target_level = 40
                    target_stars = 1

            # Generate investment advice
            if is_farm:
                reason = "Farm account: minimal investment. Focus on joining rallies."
            elif hero_gen < current_gen - 2:
                reason = f"Outdated (Gen {hero_gen}). Save resources for newer heroes."
                target_level = min(target_level, current_level)
            elif hero_gen == current_gen:
                reason = f"Current gen {tier} tier hero! Worth investing heavily."
            elif hero_gen >= current_gen - 1:
                reason = f"Still relevant {tier} tier hero. Upgrade to Lv{target_level}, {target_stars} stars recommended."
            else:
                reason = f"Gen {hero_gen} {tier} tier. Moderate investment, save for newer heroes."

            # Skip if already at or above target
            if current_level >= target_level and current_stars >= target_stars:
                reason = f"At target level. {tier} tier, maintain and focus elsewhere."

            results.append({
                'hero': name,
                'hero_class': hero_class,
                'tier': tier,
                'generation': int(hero_gen),
                'current_level': current_level,
                'target_level': max(target_level, current_level),
                'current_stars': current_stars,
                'target_stars': max(target_stars, current_stars),
                'priority': priority_rank,
                'reason': reason,
            })

        return results[:limit]

    def to_json(self, recommendations: List[Recommendation]) -> str:
        """Convert recommendations to JSON string."""
        return json.dumps([asdict(r) for r in recommendations], indent=2)


# Convenience function for quick access
def get_engine(data_dir: Path = None) -> RecommendationEngine:
    """Get a recommendation engine instance."""
    return RecommendationEngine(data_dir)
