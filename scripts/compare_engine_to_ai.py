"""
Compare Lineup Engine to AI Results

Runs the same test profiles through the lineup engine and compares
against stored AI recommendations from a previous comparison run.

Usage:
    python scripts/compare_engine_to_ai.py --run-id 8
    python scripts/compare_engine_to_ai.py --run-id 8 --verbose
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import LineupTestResult, LineupTestRun
from engine.analyzers.lineup_builder import LineupBuilder, LINEUP_TEMPLATES, IDEAL_LINEUPS
from scripts.test_lineups import get_test_profiles


# Scenario mapping: AI test scenarios -> engine template keys
SCENARIO_TO_TEMPLATE = {
    'bear_trap': 'bear_trap',
    'crazy_joe': 'crazy_joe',
    'garrison_joiner': 'rally_joiner_defense',  # Sergey for garrison defense
    'rally_joiner': 'rally_joiner_attack',  # Jessie for attack
    'svs_march': 'svs_march',
}


def normalize_hero_name(name: str) -> str:
    """Strip parenthetical info from hero names."""
    if not name:
        return ""
    return re.sub(r'\s*\([^)]+\)\s*$', '', name.strip())


def extract_slot1_from_json(lineup_json: str) -> str:
    """Extract slot 1 hero from lineup JSON."""
    if not lineup_json:
        return ""
    try:
        lineup = json.loads(lineup_json)
        if isinstance(lineup, list) and len(lineup) > 0:
            return normalize_hero_name(lineup[0].get('hero', ''))
        elif isinstance(lineup, dict):
            return normalize_hero_name(lineup.get('slot1', lineup.get('hero1', '')))
    except (json.JSONDecodeError, TypeError):
        pass
    return ""


def convert_profile_to_user_heroes(profile: dict) -> dict:
    """Convert test profile format to user_heroes dict for lineup builder."""
    user_heroes = {}
    for hero in profile.get('heroes', []):
        name = hero.get('name')
        if name:
            user_heroes[name] = {
                'level': hero.get('level', 1),
                'stars': hero.get('stars', 0),
                'gear_slot1_quality': hero.get('gear_quality', 0),
                'gear_slot2_quality': hero.get('gear_quality', 0),
                'gear_slot3_quality': hero.get('gear_quality', 0),
                'gear_slot4_quality': hero.get('gear_quality', 0),
                'expedition_skill_1_level': 3,  # Default skill level
            }
    return user_heroes


def run_engine_comparison(run_id: int, verbose: bool = False):
    """
    Compare lineup engine output against stored AI results.

    Args:
        run_id: Test run ID to compare against
        verbose: Show detailed per-profile results
    """
    init_db()
    db = get_db()

    try:
        # Get the test run
        test_run = db.query(LineupTestRun).filter_by(id=run_id).first()
        if not test_run:
            print(f"Error: Test run {run_id} not found")
            return

        # Get all results for this run
        results = db.query(LineupTestResult).filter_by(test_run_id=run_id).all()
        print(f"Found {len(results)} AI results from run {run_id}")
        print()

        # Get test profiles
        all_profiles = get_test_profiles()
        profile_lookup = {p['name']: p for p in all_profiles}

        # Initialize lineup builder
        builder = LineupBuilder()

        # Track comparisons
        stats = {
            'total': 0,
            'engine_matches_claude': 0,
            'engine_matches_openai': 0,
            'engine_matches_both': 0,
            'engine_matches_neither': 0,
            'by_scenario': {},
        }

        disagreements = []

        print("=" * 70)
        print("ENGINE vs AI COMPARISON")
        print("=" * 70)
        print()

        for result in results:
            scenario = result.scenario
            profile_name = result.profile_name

            # Skip scenarios we don't have templates for
            if scenario not in SCENARIO_TO_TEMPLATE:
                continue

            template_key = SCENARIO_TO_TEMPLATE[scenario]

            # Get the profile
            profile = profile_lookup.get(profile_name)
            if not profile:
                continue

            # Convert to user_heroes format
            user_heroes = convert_profile_to_user_heroes(profile)

            # Run engine
            lineup = builder.build_personalized_lineup(
                template_key,
                user_heroes,
                max_generation=profile.get('gen', 99)
            )

            # Extract slot 1 hero from engine
            engine_slot1 = ""
            if lineup.heroes and len(lineup.heroes) > 0:
                engine_slot1 = lineup.heroes[0].get('hero', '')
                # Handle "Need Infantry" type placeholders
                if engine_slot1.startswith('Need '):
                    engine_slot1 = ""

            # Extract slot 1 from AI results
            claude_slot1 = normalize_hero_name(extract_slot1_from_json(result.claude_lineup))
            openai_slot1 = normalize_hero_name(extract_slot1_from_json(result.openai_lineup))

            # Compare
            matches_claude = engine_slot1 == claude_slot1
            matches_openai = engine_slot1 == openai_slot1

            # Update stats
            stats['total'] += 1

            if scenario not in stats['by_scenario']:
                stats['by_scenario'][scenario] = {
                    'total': 0, 'claude': 0, 'openai': 0, 'both': 0, 'neither': 0
                }
            stats['by_scenario'][scenario]['total'] += 1

            if matches_claude and matches_openai:
                stats['engine_matches_both'] += 1
                stats['by_scenario'][scenario]['both'] += 1
            elif matches_claude:
                stats['engine_matches_claude'] += 1
                stats['by_scenario'][scenario]['claude'] += 1
            elif matches_openai:
                stats['engine_matches_openai'] += 1
                stats['by_scenario'][scenario]['openai'] += 1
            else:
                stats['engine_matches_neither'] += 1
                stats['by_scenario'][scenario]['neither'] += 1
                disagreements.append({
                    'profile': profile_name,
                    'scenario': scenario,
                    'engine': engine_slot1,
                    'claude': claude_slot1,
                    'openai': openai_slot1,
                })

            if verbose:
                match_str = ""
                if matches_claude and matches_openai:
                    match_str = "MATCH ALL"
                elif matches_claude:
                    match_str = "=Claude"
                elif matches_openai:
                    match_str = "=OpenAI"
                else:
                    match_str = "DIFF"

                print(f"[{profile_name}] {scenario}: Engine={engine_slot1}, Claude={claude_slot1}, OpenAI={openai_slot1} -> {match_str}")

        # Print summary
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print()

        total = stats['total']
        if total == 0:
            print("No comparisons made")
            return

        print(f"Total Comparisons: {total}")
        print()

        # Overall agreement rates
        matches_claude_total = stats['engine_matches_claude'] + stats['engine_matches_both']
        matches_openai_total = stats['engine_matches_openai'] + stats['engine_matches_both']

        print(f"Engine agrees with Claude:  {matches_claude_total}/{total} ({100*matches_claude_total/total:.1f}%)")
        print(f"Engine agrees with OpenAI:  {matches_openai_total}/{total} ({100*matches_openai_total/total:.1f}%)")
        print(f"Engine agrees with BOTH:    {stats['engine_matches_both']}/{total} ({100*stats['engine_matches_both']/total:.1f}%)")
        print(f"Engine agrees with NEITHER: {stats['engine_matches_neither']}/{total} ({100*stats['engine_matches_neither']/total:.1f}%)")
        print()

        # By scenario
        print("BY SCENARIO:")
        print("-" * 50)
        for scenario, s_stats in stats['by_scenario'].items():
            s_total = s_stats['total']
            s_claude = s_stats['claude'] + s_stats['both']
            s_openai = s_stats['openai'] + s_stats['both']
            s_both = s_stats['both']

            print(f"  {scenario}:")
            print(f"    =Claude: {s_claude}/{s_total} ({100*s_claude/s_total:.0f}%)")
            print(f"    =OpenAI: {s_openai}/{s_total} ({100*s_openai/s_total:.0f}%)")
            print(f"    =Both:   {s_both}/{s_total} ({100*s_both/s_total:.0f}%)")

        # Show disagreements
        if disagreements:
            print()
            print("=" * 70)
            print(f"DISAGREEMENTS (Engine differs from both AIs): {len(disagreements)}")
            print("=" * 70)
            print()

            # Group by scenario
            by_scenario = {}
            for d in disagreements:
                s = d['scenario']
                if s not in by_scenario:
                    by_scenario[s] = []
                by_scenario[s].append(d)

            for scenario, items in by_scenario.items():
                print(f"\n{scenario} ({len(items)} disagreements):")
                for d in items[:5]:  # Show first 5
                    print(f"  {d['profile']}: Engine={d['engine']}, Claude={d['claude']}, OpenAI={d['openai']}")
                if len(items) > 5:
                    print(f"  ... and {len(items) - 5} more")

        print()
        print("=" * 70)
        print("INTERPRETATION")
        print("=" * 70)
        print()
        print("- High '=Both' percentage means engine matches AI consensus")
        print("- '=Claude only' or '=OpenAI only' means engine agrees with one AI")
        print("- 'NEITHER' means engine recommendation differs from both AIs")
        print()
        print("For joiner scenarios (garrison_joiner, rally_joiner):")
        print("  - Slot 1 should be Sergey (garrison) or Jessie (rally)")
        print("  - 100% agreement expected when hero is in roster")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='Compare lineup engine to AI results')
    parser.add_argument('--run-id', type=int, required=True, help='Test run ID to compare against')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed per-profile results')

    args = parser.parse_args()
    run_engine_comparison(args.run_id, args.verbose)


if __name__ == '__main__':
    main()
