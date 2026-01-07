"""
AI-Powered Recommendation Engine using OpenAI API.
Submits compact, structured data for intelligent analysis.
Includes verified game mechanics to prevent hallucination.
"""

import os
import json
from pathlib import Path
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


# Condensed verified game mechanics for AI context
VERIFIED_MECHANICS = """
=== VERIFIED GAME MECHANICS (USE ONLY THESE - DO NOT MAKE UP DATA) ===

HERO SKILL SYSTEM:
- Each hero has 2 skill types on their skill screen:
  - LEFT SIDE: Exploration Skills (upgraded with Exploration Manuals) - for PvE
  - RIGHT SIDE: Expedition Skills (upgraded with Expedition Manuals) - for PvP/rallies
- All skills scale levels 1-5 with EQUAL % increments per level
- Example: If max is 25%, then levels give +5%, +10%, +15%, +20%, +25%

RALLY MECHANICS:
- Rally LEADER: Your 3 heroes provide 9 expedition skills (3 right-side skills × 3 heroes)
- Rally JOINER: Only your LEFTMOST hero's TOP-RIGHT expedition skill contributes!
  - "Leftmost hero" = First hero in march lineup (slot 1)
  - "Top-right skill" = Expedition skill in top-right position on skill screen
- Top 4 highest SKILL LEVEL expedition skills from all joiners apply
- Higher skill level = more likely to be selected AND stronger effect

BEST JOINER HEROES:
| Role | Hero | Skill | Effect per Level (1-5) |
|------|------|-------|------------------------|
| Attack Joiner | Jessie (Gen 1) | Stand of Arms | +5/10/15/20/25% DMG dealt |
| Garrison Joiner | Sergey (Gen 1) | Defenders' Edge | -4/8/12/16/20% DMG taken |

If player doesn't have Jessie/Sergey, recommend joining rallies with TROOPS ONLY (no heroes).

TROOP RATIOS BY EVENT:
| Event | Infantry | Lancer | Marksman | Why |
|-------|----------|--------|----------|-----|
| Default/Castle | 50% | 20% | 30% | Balanced |
| Bear Trap/Hunt | 0% | 10% | 90% | Max DPS, bear is slow |
| Crazy Joe | 90% | 10% | 0% | Infantry kills before backline attacks |

COMBAT ORDER: Infantry fights first → Lancers → Marksmen
CLASS COUNTERS: Infantry > Lancer > Marksman > Infantry

HERO TIERS: S+ (best) > S > A > B > C > D
CLASSES: Infantry (tank), Marksman (ranged DPS), Lancer (balanced)

GENERATION TIMELINE:
- Gen 1: Days 0-40 (Jeronimo, Natalia, Molly, Zinman, Sergey, Gina, Bahiti, Jessie)
- Gen 2: Days 40-120 (Flint, Philly, Alonso)
- Gen 3: Days 120-200 (Logan, Mia, Greg)
- Gen 4: Days 200-280 (Ahmose, Reina, Lynn)
- Gen 5: Days 280-360 (Hector, Wu Ming)
- Gen 6: Days 360-440 (Patrick, Charlie, Cloris)
- Gen 7: Days 440-520 (Gordon, Renee, Eugene)
- Gen 8+: Days 520+

PRIORITIES SCALE: 1=low focus, 5=critical focus
- SvS = State vs State (main competitive event)
- Rally = Group attacks (Bear Trap, Crazy Joe, castle attacks)
- Castle = Castle defense/garrison
- PvE = Exploration stages
- Gather = Resource gathering

CHIEF GEAR (Global buffs - always active):
| Piece | Stat | Priority |
|-------|------|----------|
| Ring | Troop Attack (All) | 1 - Upgrade first |
| Amulet | Lethality/Damage | 2 - PvP decisive |
| Gloves | Marksman Attack | 3 |
| Boots | Lancer Attack | 4 |
| Helmet | Infantry Defense | 5 |
| Armor | Infantry Health | 6 |

Quality: Common → Uncommon → Rare → Epic → Legendary → Mythic
Goal: Mythic on Ring & Amulet first
Note: Ring & Amulet affect ALL troops and stack with hero buffs

SPENDER-LEVEL GEAR PATHS:
| Spender | Chief Gear | Hero Gear | Mistake Tolerance |
|---------|------------|-----------|-------------------|
| F2P | Mandatory priority | 1 hero max (field DPS only) | None |
| Low | Dominant priority | 2 heroes max | Low |
| Medium | Foundational | 3-4 heroes (strategic) | Medium |
| Whale | Max everything | All core heroes | High |

F2P RULES: Chief Gear Ring+Amulet first. Hero gear only on Molly OR Alonso. NEVER gear rally joiners.
LOW SPENDER: Chief Gear still #1. Hero gear on daily-use multi-mode heroes only.
HERO GEAR ROI: Rally joiner = very low. Rally leader = medium. Field PvP = high.

COMBAT SYNERGY MODEL (what matters in each context):
Rally Leader: Chief Gear ★★★★★, Hero Selection ★★★★★, Hero Gear ★★★, Joiner Gear ☆
Rally Joiner: Chief Gear ★★★★★, First Hero Skill ★★★★, Hero Gear ★
Field PvP: Hero Gear ★★★★★, Hero DPS ★★★★★, Chief Gear ★★★
Garrison: Damage Reduction ★★★★★, Chief Gear (def) ★★★★, Hero Gear ★★

HERO ROLES:
- Jeronimo: rally_leader, attack_buffer
- Jessie: attack_joiner (BEST for rally joining)
- Sergey: defense_joiner, garrison (BEST for garrison joining)
- Molly: field_dps, solo (poor joiner despite DPS)
- Alonso: field_dps, hybrid

NEVER RECOMMEND: DPS heroes as joiners, Defensive heroes as rally leaders, Gearing joiner-only heroes

POWER ILLUSION: Hero gear increases visible damage. Chief gear increases battle outcomes.

CORE TRUTHS:
1. Rallies are won by BUFFS, not DPS
2. Joiners carry SKILLS, not damage
3. Chief Gear = universal power
4. Hero Gear = situational power

=== END VERIFIED MECHANICS ===
"""


class AIRecommender:
    """Generate recommendations using OpenAI API."""

    SYSTEM_PROMPT = f"""You are a Whiteout Survival expert advisor. Analyze the player's data and give specific upgrade recommendations.

{VERIFIED_MECHANICS}

CRITICAL RULES:
1. ONLY use hero names from the verified list above - DO NOT invent heroes
2. ONLY use skill mechanics exactly as described - DO NOT make up percentages
3. Reference the player's ACTUAL hero levels and skills from their data
4. Consider their priorities when ranking recommendations

OUTPUT FORMAT - Return ONLY valid JSON array, no markdown:
[
  {{"priority": 1, "action": "Level Jeronimo to 60", "hero": "Jeronimo", "reason": "S+ tier, your top combat hero", "resources": "Hero EXP items"}},
  {{"priority": 2, "action": "...", "hero": "...", "reason": "...", "resources": "..."}}
]

Give 5-10 specific, actionable recommendations sorted by priority (1=do first)."""

    QUESTION_PROMPT = f"""You are a Whiteout Survival expert advisor. Answer questions about the player's account using ONLY the verified mechanics below.

{VERIFIED_MECHANICS}

CRITICAL: Only reference heroes and mechanics from the verified data above. If you don't know something specific, say so rather than guessing."""

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
                    {"role": "system", "content": self.QUESTION_PROMPT},
                    {"role": "user", "content": f"{user_data}\n\nQUESTION: {question}"}
                ],
                temperature=0.7,
                max_tokens=800
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
