#!/usr/bin/env python3
"""
Test different prompt injection strategies for AI Advisor.

Compares:
1. BASELINE - Current hardcoded VERIFIED_MECHANICS
2. DYNAMIC_HEROES - Load tier data from heroes.json
3. EXPANDED_SKILLS - Include expedition skill details
4. COMPACT_TABLES - Markdown table format
5. MINIMAL_RULES - Just critical rules, trust AI knowledge

Measures:
- Token count (input/output)
- Response quality (manual review)
- Factual accuracy (hero classes, skills correct?)
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

CORE_INSTRUCTIONS = """You are Bear, a Whiteout Survival optimization assistant.
Address the player as "Chief." Use game terminology. Be concise and decisive.

CRITICAL RULES:
1. Only use hero names that exist in the game
2. Only cite skill effects that are verified
3. Reference the Chief's actual hero data when giving advice
4. If uncertain about something, say so rather than guessing"""

# Template 1: Current baseline (hardcoded)
BASELINE_MECHANICS = """
=== GAME MECHANICS ===

HERO CLASSES:
- Infantry: Frontline tanks, high HP
- Lancer: Balanced fighters
- Marksman: Ranged DPS, fragile

RALLY MECHANICS:
- Rally LEADER: All 9 expedition skills from 3 heroes apply
- Rally JOINER: Only FIRST hero's TOP-RIGHT expedition skill matters
- Top 4 highest skill levels from joiners contribute

BEST JOINERS:
- Attack: Jessie (Stand of Arms +25% DMG dealt at max)
- Defense: Sergey (Defenders' Edge -20% DMG taken at max)

HERO TIERS: S+ > S > A > B > C > D
"""


def build_dynamic_heroes_template() -> str:
    """Template 2: Load actual tier data from heroes.json."""
    heroes_file = PROJECT_ROOT / "data" / "heroes.json"
    with open(heroes_file, encoding='utf-8') as f:
        data = json.load(f)

    # Group heroes by tier and class
    by_tier = {}
    by_class = {'Infantry': [], 'Lancer': [], 'Marksman': []}

    for h in data['heroes']:
        tier = h.get('tier_overall', 'Unknown')
        hero_class = h.get('hero_class', 'Unknown')
        gen = h.get('generation', '?')
        name = h['name']

        by_tier.setdefault(tier, []).append(f"{name} (Gen{gen})")
        if hero_class in by_class:
            by_class[hero_class].append(name)

    lines = ["=== VERIFIED HERO DATA ===\n"]

    # Tier list
    lines.append("HERO TIERS (invest in order):")
    for tier in ['S+', 'S', 'A', 'B', 'C', 'D']:
        if tier in by_tier:
            heroes = by_tier[tier][:10]  # Limit to 10 per tier
            lines.append(f"  {tier}: {', '.join(heroes)}")

    lines.append("\nHEROES BY CLASS:")
    for cls, heroes in by_class.items():
        lines.append(f"  {cls}: {', '.join(heroes[:12])}")

    # Add rally mechanics
    lines.append("""
RALLY MECHANICS:
- Rally LEADER: All 9 expedition skills from 3 heroes apply
- Rally JOINER: Only FIRST hero's TOP-RIGHT expedition skill matters
- Top 4 highest skill levels from joiners contribute

BEST JOINERS:
- Attack: Jessie (Stand of Arms +5/10/15/20/25% DMG dealt)
- Defense: Sergey (Defenders' Edge -4/8/12/16/20% DMG taken)
""")

    return "\n".join(lines)


def build_expanded_skills_template() -> str:
    """Template 3: Include detailed expedition skill effects."""
    verified_file = PROJECT_ROOT / "data" / "verified_research.json"
    heroes_file = PROJECT_ROOT / "data" / "heroes.json"

    with open(verified_file, encoding='utf-8') as f:
        verified = json.load(f)
    with open(heroes_file, encoding='utf-8') as f:
        heroes_data = json.load(f)

    lines = ["=== VERIFIED GAME DATA ===\n"]

    # Hero tiers (compact)
    by_tier = {}
    for h in heroes_data['heroes']:
        tier = h.get('tier_overall', 'Unknown')
        by_tier.setdefault(tier, []).append(h['name'])

    lines.append("HERO TIERS:")
    for tier in ['S+', 'S', 'A']:
        if tier in by_tier:
            lines.append(f"  {tier}: {', '.join(by_tier[tier][:8])}")

    # Detailed skill data
    lines.append("\nKEY EXPEDITION SKILLS (for rally joining):")
    for hero_name, skill_data in verified.get('hero_skills', {}).items():
        lines.append(f"\n{hero_name.upper()} ({skill_data.get('class', '?')}, Gen{skill_data.get('generation', '?')}):")
        for skill_name, effect in skill_data.get('expedition_skills', {}).items():
            scaling = effect.get('scaling', [])
            scaling_str = '/'.join(str(s) for s in scaling)
            pos = effect.get('position', '')
            joiner_note = f" [JOINER: {effect.get('joiner_value', '')}]" if effect.get('joiner_value') else ""
            lines.append(f"  - {skill_name}: {effect.get('effect', '')} ({scaling_str}%){joiner_note}")

    # Rally mechanics
    lines.append("""
RALLY MECHANICS (verified):
- Rally LEADER: 3 heroes x 3 expedition skills = 9 skills apply
- Rally JOINER: Only leftmost hero's TOP-RIGHT expedition skill
- Top 4 highest SKILL LEVELS from all joiners contribute
- Higher level = more likely selected AND stronger effect

TROOP RATIOS:
| Event | Infantry | Lancer | Marksman | Why |
|-------|----------|--------|----------|-----|
| Default | 50% | 20% | 30% | Balanced |
| Bear Trap | 0% | 10% | 90% | Bear is slow, max ranged DPS |
| Crazy Joe | 90% | 5% | 5% | Infantry kills before backline attacks |
""")

    return "\n".join(lines)


def build_compact_tables_template() -> str:
    """Template 4: Markdown tables (efficient token use)."""
    heroes_file = PROJECT_ROOT / "data" / "heroes.json"
    with open(heroes_file, encoding='utf-8') as f:
        heroes_data = json.load(f)

    # Build compact hero reference
    by_tier_class = {}
    for h in heroes_data['heroes']:
        tier = h.get('tier_overall', 'Unknown')
        cls = h.get('hero_class', 'Unknown')
        key = f"{tier}_{cls}"
        by_tier_class.setdefault(key, []).append(h['name'])

    lines = ["""=== GAME DATA (VERIFIED) ===

## Hero Tiers by Class
| Tier | Infantry | Lancer | Marksman |
|------|----------|--------|----------|"""]

    for tier in ['S+', 'S', 'A', 'B']:
        inf = by_tier_class.get(f'{tier}_Infantry', [])[:4]
        lan = by_tier_class.get(f'{tier}_Lancer', [])[:4]
        mar = by_tier_class.get(f'{tier}_Marksman', [])[:4]
        lines.append(f"| {tier} | {', '.join(inf) or '-'} | {', '.join(lan) or '-'} | {', '.join(mar) or '-'} |")

    lines.append("""
## Rally Mechanics
| Role | What Matters | Example |
|------|--------------|---------|
| Leader | All 9 expedition skills apply | Use highest power heroes |
| Joiner | Only slot 1 hero's top-right skill | Jessie=attack, Sergey=defense |

## Best Joiner Heroes
| Situation | Hero | Skill | Effect (Lv1-5) |
|-----------|------|-------|----------------|
| Attack rally | Jessie | Stand of Arms | +5/10/15/20/25% DMG dealt |
| Garrison defense | Sergey | Defenders' Edge | -4/8/12/16/20% DMG taken |

## Troop Ratios
| Event | Inf/Lan/Mar | Reasoning |
|-------|-------------|-----------|
| Bear Trap | 0/10/90 | Bear is slow, maximize marksman DPS |
| Crazy Joe | 90/5/5 | Infantry kills before Joe attacks backline |
| Garrison | 60/25/15 | Infantry survives longer |
| SvS March | 40/20/40 | Balanced for field combat |
""")

    return "\n".join(lines)


def build_owned_context_template(owned_heroes: List[str], user_gen: int) -> str:
    """Template 5: Full context with owned vs not-owned heroes."""
    heroes_file = PROJECT_ROOT / "data" / "heroes.json"
    with open(heroes_file, encoding='utf-8') as f:
        heroes_data = json.load(f)

    owned_set = set(owned_heroes)
    lines = ["=== GAME DATA (VERIFIED) ===\n"]

    # Group all heroes by tier, filtered by generation
    available_heroes = []
    for h in heroes_data['heroes']:
        gen = h.get('generation', 99)
        if gen <= user_gen:
            available_heroes.append(h)

    # Owned heroes summary
    lines.append("YOUR HEROES (you own these):")
    owned_by_tier = {}
    for h in available_heroes:
        if h['name'] in owned_set:
            tier = h.get('tier_overall', '?')
            cls = h.get('hero_class', '?')
            gen = h.get('generation', '?')
            owned_by_tier.setdefault(tier, []).append(f"{h['name']} ({cls[:3]}, Gen{gen})")

    for tier in ['S+', 'S', 'A', 'B', 'C', 'D']:
        if tier in owned_by_tier:
            lines.append(f"  {tier}: {', '.join(owned_by_tier[tier])}")

    # Not owned - recommended to get
    lines.append("\nHEROES TO CONSIDER GETTING:")
    not_owned_by_tier = {}
    for h in available_heroes:
        if h['name'] not in owned_set:
            tier = h.get('tier_overall', '?')
            if tier in ['S+', 'S', 'A']:  # Only recommend good ones
                cls = h.get('hero_class', '?')
                gen = h.get('generation', '?')
                not_owned_by_tier.setdefault(tier, []).append(f"{h['name']} ({cls[:3]}, Gen{gen})")

    for tier in ['S+', 'S', 'A']:
        if tier in not_owned_by_tier:
            lines.append(f"  {tier}: {', '.join(not_owned_by_tier[tier][:6])}")  # Top 6

    # Rally mechanics (critical rules)
    lines.append("""
RALLY MECHANICS (verified):
- Rally JOINER: Only slot 1 hero's TOP-RIGHT expedition skill matters!
- Top 4 highest skill levels from all joiners contribute
- BEST ATTACK JOINER: Jessie (Stand of Arms +5/10/15/20/25% DMG dealt)
- BEST GARRISON JOINER: Sergey (Defenders' Edge -4/8/12/16/20% DMG taken)

TROOP RATIOS:
| Event | Inf/Lan/Mar | Why |
|-------|-------------|-----|
| Bear Trap | 0/10/90 | Bear is slow, maximize marksman |
| Crazy Joe | 90/5/5 | Infantry kills before backline attacks |
| Garrison | 60/25/15 | Infantry survives longer |
| Default | 50/20/30 | Balanced |
""")

    return "\n".join(lines)


def build_comprehensive_template(owned_heroes: List[str], user_gen: int) -> str:
    """Template 6: Comprehensive verified data - heroes, gear, events, strategy."""
    heroes_file = PROJECT_ROOT / "data" / "heroes.json"
    with open(heroes_file, encoding='utf-8') as f:
        heroes_data = json.load(f)

    owned_set = set(owned_heroes)
    lines = ["=== VERIFIED GAME DATA ===\n"]

    # Filter heroes by generation
    available_heroes = [h for h in heroes_data['heroes'] if h.get('generation', 99) <= user_gen]

    # Owned heroes
    lines.append("YOUR HEROES:")
    owned_by_tier = {}
    for h in available_heroes:
        if h['name'] in owned_set:
            tier = h.get('tier_overall', '?')
            cls = h.get('hero_class', '?')[:3]
            owned_by_tier.setdefault(tier, []).append(f"{h['name']}({cls})")

    for tier in ['S+', 'S', 'A', 'B']:
        if tier in owned_by_tier:
            lines.append(f"  {tier}: {', '.join(owned_by_tier[tier])}")

    # Heroes to get
    lines.append("\nHEROES TO GET:")
    not_owned = {}
    for h in available_heroes:
        if h['name'] not in owned_set and h.get('tier_overall') in ['S+', 'S', 'A']:
            tier = h.get('tier_overall')
            cls = h.get('hero_class', '?')[:3]
            not_owned.setdefault(tier, []).append(f"{h['name']}({cls})")
    for tier in ['S+', 'S', 'A']:
        if tier in not_owned:
            lines.append(f"  {tier}: {', '.join(not_owned[tier][:5])}")

    # Add comprehensive game rules
    lines.append("""
=== RALLY MECHANICS ===
- JOINER: Only slot 1 hero's TOP-RIGHT expedition skill matters!
- BEST ATTACK JOINER: Jessie (+25% DMG dealt)
- BEST GARRISON JOINER: Sergey (-20% DMG taken)
- Joiner hero stats/gear DON'T matter - only the skill!

=== CHIEF GEAR (6 pieces) ===
| Piece | Troop Type | Priority |
|-------|------------|----------|
| Coat | Infantry | 1st (highest) |
| Pants | Infantry | 2nd |
| Belt | Marksman | 3rd |
| Weapon | Marksman | 4th |
| Cap | Lancer | 5th |
| Watch | Lancer | 6th (lowest) |

RULES:
- Keep ALL 6 pieces at SAME quality tier for set bonuses
- 3-piece bonus = Defense all troops
- 6-piece bonus = Attack all troops
- Quality: Green < Blue < Purple < Gold < Orange

=== HERO GEAR vs CHIEF GEAR ===
CRITICAL: Chief gear ALWAYS comes first!
- Chief gear benefits ALL heroes universally
- Hero gear only benefits ONE hero in specific situations

HERO GEAR PRIORITY:
- DO NOT gear rally joiners (Jessie, Sergey) - their stats don't matter!
- Only gear field DPS heroes who fight directly
- F2P: Max 1-2 heroes with gear (Molly, Alonso typical choices)
- Dolphins: 3-4 heroes
- Whales: All core heroes

=== TROOP RATIOS ===
| Event | Inf/Lan/Mar | Why |
|-------|-------------|-----|
| Bear Trap | 0/10/90 | Bear is slow, max marksman DPS |
| Crazy Joe | 90/5/5 | Infantry kills before backline dies |
| Garrison | 60/25/15 | Infantry survives longer |
| SvS March | 40/20/40 | Balanced field combat |
| Default | 50/20/30 | Balanced |

=== SVS PREP TIPS ===
- Speedups give points on Day 1, 2, 5 ONLY
- Fire Crystals: 2,000 pts each (Day 1)
- Lucky Wheel: 8,000 pts per spin (Day 2/3)
- Mithril: 40,000 pts each (Day 4)
- Day 4: Troop promotion > speedups

=== F2P PRIORITIES ===
1. Chief gear to same tier (all 6 pieces)
2. Top 3-4 heroes only (don't spread resources)
3. Jessie expedition skill for rally joining
4. Sergey expedition skill for garrison
5. Hero gear on 1 field DPS hero max
""")

    return "\n".join(lines)


def build_minimal_rules_template() -> str:
    """Template 7: Minimal critical rules only."""
    return """=== CRITICAL RULES (must follow) ===

RALLY JOINING:
- Only slot 1 hero's TOP-RIGHT expedition skill matters
- Jessie = best attack joiner (+25% DMG dealt)
- Sergey = best garrison joiner (-20% DMG taken)

HERO CLASSES:
- Infantry: Tank (Jeronimo, Natalia, Wu Ming)
- Lancer: Balanced (Jessie, Gordon, Norah)
- Marksman: DPS (Philly, Hendrik, Blanchette)

TROOP RATIOS:
- Bear Trap: 0/10/90 (marksman heavy)
- Crazy Joe: 90/5/5 (infantry heavy)
- Default: 50/20/30

TIER ORDER: S+ > S > A > B > C > D
"""


# =============================================================================
# TEST FRAMEWORK
# =============================================================================

@dataclass
class TestResult:
    template_name: str
    question: str
    response: str
    input_tokens: int
    output_tokens: int
    response_time: float
    factual_errors: List[str]  # Manual annotation later


TEST_QUESTIONS = [
    # Lineup questions
    "Who should I put in slot 1 when joining a rally attack?",
    "What heroes should I use for Bear Trap?",
    "What troop ratio should I use for Crazy Joe?",
    # Hero investment
    "Is Natalia a good hero to invest in?",
    "Which hero should I level up next?",
    # Gear questions
    "Should I put hero gear on Jessie since she's my rally joiner?",
    "Should I upgrade my chief gear or hero gear first?",
    "What chief gear pieces should I prioritize?",
    # Event/resource questions
    "How should I prepare for SvS prep phase?",
    "Should I save my speedups or use them now?",
    # General strategy
    "I'm F2P, what should I focus on?",
    "How do I get stronger for rallies?",
]

# Edge case questions for additional testing
EDGE_CASE_QUESTIONS = [
    # Spending profile
    "I'm a whale, should I gear all my heroes?",
    "As a dolphin spender, how many heroes should I focus on?",
    # Farm account
    "This is my farm account, what heroes should I invest in?",
    "Should I upgrade my farm account's chief gear?",
    # Specific mechanics
    "What's the difference between exploration and expedition skills?",
    "Why does slot 1 matter for rally joining?",
    # Common mistakes
    "Should I spread my resources across all heroes?",
    "Is Molly good for rally joining?",
]

# Simple test user profile
TEST_PROFILE = """
PROFILE: Gen5 (Day 300), Furnace 25
PRIORITIES: SvS=5, Rally=4, Castle=3, PvE=2, Gather=1

MY HEROES:
- Jeronimo [S+|Inf|Gen1] Lv60 ★★★★★ Skills: Expl 3/3/3 Exped 4/4/4
- Natalia [A|Inf|Gen1] Lv50 ★★★★ Skills: Expl 3/3/2 Exped 3/3/3
- Jessie [A|Lan|Gen5] Lv55 ★★★★ Skills: Expl 3/3/3 Exped 4/4/4
- Sergey [B|Inf|Gen1] Lv45 ★★★ Skills: Expl 2/2/2 Exped 3/3/3
- Philly [A|Mar|Gen2] Lv40 ★★★ Skills: Expl 2/2/2 Exped 2/2/2
- Gordon [S|Lan|Gen7] Lv50 ★★★★ Skills: Expl 3/3/3 Exped 3/3/3
"""


def call_openai(system_prompt: str, user_message: str) -> Tuple[str, int, int]:
    """Call OpenAI and return (response, input_tokens, output_tokens)."""
    from openai import OpenAI

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return (
        response.choices[0].message.content.strip(),
        response.usage.prompt_tokens,
        response.usage.completion_tokens
    )


def run_template_test(template_name: str, mechanics_prompt: str, questions: List[str]) -> List[TestResult]:
    """Run all questions through a template and collect results."""
    results = []

    full_system = f"{CORE_INSTRUCTIONS}\n\n{mechanics_prompt}"

    for question in questions:
        user_message = f"{TEST_PROFILE}\n\nQUESTION: {question}"

        start_time = time.time()
        try:
            response, input_tokens, output_tokens = call_openai(full_system, user_message)
            elapsed = time.time() - start_time

            results.append(TestResult(
                template_name=template_name,
                question=question,
                response=response,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time=elapsed,
                factual_errors=[]
            ))
        except Exception as e:
            results.append(TestResult(
                template_name=template_name,
                question=question,
                response=f"ERROR: {e}",
                input_tokens=0,
                output_tokens=0,
                response_time=0,
                factual_errors=[str(e)]
            ))

        time.sleep(0.5)  # Rate limit

    return results


def main():
    """Run all template tests and generate comparison report."""
    import argparse

    parser = argparse.ArgumentParser(description='Test prompt injection strategies')
    parser.add_argument('--template', choices=['baseline', 'dynamic', 'expanded', 'compact', 'owned', 'comprehensive', 'minimal', 'all'],
                       default='all', help='Which template to test')
    parser.add_argument('--questions', type=int, default=5, help='Number of questions to test')
    parser.add_argument('--edge-cases', action='store_true', help='Test edge case questions instead')
    parser.add_argument('--dry-run', action='store_true', help='Show templates without calling API')
    args = parser.parse_args()

    # Test user owns these heroes (Gen 5 player)
    test_owned_heroes = ['Jeronimo', 'Natalia', 'Jessie', 'Sergey', 'Philly', 'Gordon']
    test_user_gen = 5

    templates = {
        'baseline': ('BASELINE', BASELINE_MECHANICS),
        'dynamic': ('DYNAMIC_HEROES', build_dynamic_heroes_template()),
        'expanded': ('EXPANDED_SKILLS', build_expanded_skills_template()),
        'compact': ('COMPACT_TABLES', build_compact_tables_template()),
        'owned': ('OWNED_CONTEXT', build_owned_context_template(test_owned_heroes, test_user_gen)),
        'comprehensive': ('COMPREHENSIVE', build_comprehensive_template(test_owned_heroes, test_user_gen)),
        'minimal': ('MINIMAL_RULES', build_minimal_rules_template()),
    }

    if args.dry_run:
        print("=" * 80)
        print("DRY RUN - Showing templates without API calls")
        print("=" * 80)

        for key, (name, prompt) in templates.items():
            print(f"\n{'='*40}")
            print(f"TEMPLATE: {name}")
            print(f"{'='*40}")
            print(prompt[:1500])
            if len(prompt) > 1500:
                print(f"... ({len(prompt)} chars total)")
            print(f"\nEstimated tokens: ~{len(prompt) // 4}")
        return

    # Run tests
    all_results = []
    question_set = EDGE_CASE_QUESTIONS if args.edge_cases else TEST_QUESTIONS
    questions = question_set[:args.questions]

    if args.template == 'all':
        test_templates = templates.items()
    else:
        test_templates = [(args.template, templates[args.template])]

    for key, (name, prompt) in test_templates:
        print(f"\n{'='*60}")
        print(f"Testing template: {name}")
        print(f"{'='*60}")

        results = run_template_test(name, prompt, questions)
        all_results.extend(results)

        # Show quick summary
        total_input = sum(r.input_tokens for r in results)
        total_output = sum(r.output_tokens for r in results)
        avg_time = sum(r.response_time for r in results) / len(results)

        print(f"  Total tokens: {total_input} in / {total_output} out")
        print(f"  Avg response time: {avg_time:.2f}s")

    # Generate comparison report
    print("\n" + "=" * 80)
    print("COMPARISON REPORT")
    print("=" * 80)

    # Group by template
    by_template = {}
    for r in all_results:
        by_template.setdefault(r.template_name, []).append(r)

    print("\n### Token Usage by Template")
    print(f"{'Template':<20} {'Input Tokens':<15} {'Output Tokens':<15} {'Total':<10}")
    print("-" * 60)

    for name, results in by_template.items():
        total_in = sum(r.input_tokens for r in results)
        total_out = sum(r.output_tokens for r in results)
        print(f"{name:<20} {total_in:<15} {total_out:<15} {total_in + total_out:<10}")

    # Show sample responses for manual review
    print("\n" + "=" * 80)
    print("SAMPLE RESPONSES (for manual quality review)")
    print("=" * 80)

    # Show first question across all templates
    first_q = questions[0]
    print(f"\nQuestion: {first_q}\n")

    for name, results in by_template.items():
        for r in results:
            if r.question == first_q:
                print(f"--- {name} ---")
                print(r.response[:500])
                if len(r.response) > 500:
                    print("...")
                print()

    # Save detailed results
    output_file = PROJECT_ROOT / "scripts" / "prompt_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([{
            'template': r.template_name,
            'question': r.question,
            'response': r.response,
            'input_tokens': r.input_tokens,
            'output_tokens': r.output_tokens,
            'response_time': r.response_time
        } for r in all_results], f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")


if __name__ == '__main__':
    main()
