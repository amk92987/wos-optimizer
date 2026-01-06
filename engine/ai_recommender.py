"""
AI-Powered Recommendation Engine using OpenAI API.
Submits compact, structured data for intelligent analysis.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AIRecommendation:
    """A single AI-generated recommendation."""
    priority: int  # 1-5, 1 being highest
    action: str  # What to do
    hero: str  # Which hero (if applicable)
    reason: str  # Why
    resources_needed: str  # What you need


class AIRecommender:
    """Generate recommendations using OpenAI API."""

    SYSTEM_PROMPT = """You are a Whiteout Survival expert advisor. Analyze the player's data and give specific upgrade recommendations.

GAME KNOWLEDGE:
- Hero tiers: S+ (best) > S > A > B > C > D (worst)
- Classes: Infantry (front tank), Marksman (back damage), Lancer (balanced)
- Skill types: Expedition (PvP/SvS combat), Exploration (PvE/stages)
- Generations: New heroes unlock every ~80 days. Older gen heroes become less relevant unless S+ tier.
- SvS: State vs State - the main competitive event. Expedition skills matter most.
- Rally: Group attacks on bosses/cities. Need strong expedition skills.

PRIORITIES SCALE: 1=low, 5=critical

OUTPUT FORMAT - Return ONLY valid JSON array, no markdown:
[
  {"priority": 1, "action": "Level Jeronimo to 60", "hero": "Jeronimo", "reason": "S+ tier, your top combat hero", "resources": "Hero EXP items"},
  {"priority": 2, "action": "...", "hero": "...", "reason": "...", "resources": "..."}
]

Give 5-10 specific, actionable recommendations sorted by priority (1=do first)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key from param or environment."""
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')

        # On Windows, also check user environment variables
        if not self.api_key:
            try:
                import subprocess
                result = subprocess.run(
                    ['powershell', '-Command', "[Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')"],
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    self.api_key = result.stdout.strip()
            except Exception:
                pass

        self.client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                pass

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.client is not None

    def format_user_data(self, profile, user_heroes: list, heroes_data: dict, inventory: dict = None) -> str:
        """
        Format user data into compact, clear prompt format.

        Returns a structured string like:

        PROFILE: Gen2 (Day 85), Furnace 18
        PRIORITIES: SvS=5, Rally=4, Castle=4, PvE=2, Gather=1

        MY HEROES:
        - Jeronimo [S+|Infantry|Gen1] Lv45 ★★★ Skills: Exp 3/2 Exped 4/3
        - Natalia [A|Infantry|Gen1] Lv30 ★★ Skills: Exp 2/2 Exped 2/2

        INVENTORY: 50 Epic Shards, 20 Leg Shards, 500 Combat Manuals
        """
        lines = []

        # Profile section
        server_age = getattr(profile, 'server_age_days', 0)
        furnace = getattr(profile, 'furnace_level', 1)

        # Calculate generation
        if server_age < 40: gen = 1
        elif server_age < 120: gen = 2
        elif server_age < 200: gen = 3
        elif server_age < 280: gen = 4
        elif server_age < 360: gen = 5
        elif server_age < 440: gen = 6
        elif server_age < 520: gen = 7
        else: gen = 8

        lines.append(f"PROFILE: Gen{gen} (Day {server_age}), Furnace {furnace}")

        # Priorities - compact format
        p_svs = getattr(profile, 'priority_svs', 5)
        p_rally = getattr(profile, 'priority_rally', 4)
        p_castle = getattr(profile, 'priority_castle_battle', 4)
        p_pve = getattr(profile, 'priority_exploration', 3)
        p_gather = getattr(profile, 'priority_gathering', 2)

        lines.append(f"PRIORITIES: SvS={p_svs}, Rally={p_rally}, Castle={p_castle}, PvE={p_pve}, Gather={p_gather}")
        lines.append("")

        # Heroes section
        hero_lookup = {h['name']: h for h in heroes_data.get('heroes', [])}

        lines.append("MY HEROES:")
        if not user_heroes:
            lines.append("- None added yet")
        else:
            for uh in user_heroes:
                hero_name = uh.hero.name if hasattr(uh, 'hero') else uh.get('name', 'Unknown')
                hero_data = hero_lookup.get(hero_name, {})

                tier = hero_data.get('tier_overall', '?')
                h_class = hero_data.get('hero_class', '?')[:3]  # Inf/Mar/Lan
                h_gen = hero_data.get('generation', '?')

                level = getattr(uh, 'level', 1)
                stars = getattr(uh, 'stars', 1)
                star_str = '★' * stars + '☆' * (5 - stars)

                # Skills: Exploration / Expedition
                exp1 = getattr(uh, 'exploration_skill_1_level', 1)
                exp2 = getattr(uh, 'exploration_skill_2_level', 1)
                exped1 = getattr(uh, 'expedition_skill_1_level', 1)
                exped2 = getattr(uh, 'expedition_skill_2_level', 1)

                lines.append(f"- {hero_name} [{tier}|{h_class}|Gen{h_gen}] Lv{level} {star_str} Skills: Expl {exp1}/{exp2} Exped {exped1}/{exped2}")

        # Inventory section (if provided)
        if inventory:
            lines.append("")
            lines.append("INVENTORY:")
            inv_items = []
            for category, items in inventory.items():
                for item in items:
                    if item['quantity'] > 0:
                        inv_items.append(f"{item['quantity']} {item['name']}")
            if inv_items:
                lines.append(", ".join(inv_items[:10]))  # Limit to 10 items
            else:
                lines.append("- Empty")

        return "\n".join(lines)

    def get_recommendations(self, profile, user_heroes: list, heroes_data: dict,
                          inventory: dict = None, custom_question: str = None) -> List[Dict]:
        """
        Get AI-powered recommendations.

        Args:
            profile: User profile with priorities
            user_heroes: List of user's heroes
            heroes_data: Static hero data
            inventory: Optional inventory data
            custom_question: Optional specific question to ask

        Returns:
            List of recommendation dicts
        """
        if not self.is_available():
            return [{"error": "OpenAI not available. Set OPENAI_API_KEY environment variable."}]

        # Format the data
        user_data = self.format_user_data(profile, user_heroes, heroes_data, inventory)

        # Build the user message
        if custom_question:
            user_message = f"{user_data}\n\nQUESTION: {custom_question}"
        else:
            user_message = f"{user_data}\n\nWhat should I upgrade next? Give me a prioritized action plan."

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap, good for this use case
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Parse the response
            content = response.choices[0].message.content.strip()

            # Try to extract JSON from response
            # Handle cases where AI might wrap in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            recommendations = json.loads(content)
            return recommendations

        except json.JSONDecodeError as e:
            return [{"error": f"Failed to parse AI response: {str(e)}", "raw": content}]
        except Exception as e:
            return [{"error": f"API error: {str(e)}"}]

    def ask_question(self, profile, user_heroes: list, heroes_data: dict,
                    question: str, inventory: dict = None) -> str:
        """
        Ask a specific question about your account.

        Returns plain text response.
        """
        if not self.is_available():
            return "OpenAI not available. Set OPENAI_API_KEY environment variable."

        user_data = self.format_user_data(profile, user_heroes, heroes_data, inventory)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Whiteout Survival expert. Answer questions about the player's account concisely and specifically."},
                    {"role": "user", "content": f"{user_data}\n\nQUESTION: {question}"}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error: {str(e)}"


def format_data_preview(profile, user_heroes: list, heroes_data: dict) -> str:
    """
    Generate a preview of what data will be sent to AI.
    Useful for showing users exactly what the AI sees.
    """
    recommender = AIRecommender()
    return recommender.format_user_data(profile, user_heroes, heroes_data)
