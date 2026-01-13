"""
Data Audit Script
Validates game data against documented sources and cross-references.
"""

import json
from pathlib import Path
from datetime import datetime


def main():
    print('=== WoS Data Audit - Quick Check ===')
    print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print()

    issues = []

    # 1. Core Data Validation
    print('## Core Data Files')

    # Heroes
    with open('data/heroes.json', encoding='utf-8') as f:
        heroes_data = json.load(f)
    heroes = heroes_data.get('heroes', [])
    print(f'heroes.json: {len(heroes)} heroes')

    # Check generation coverage
    gens = set(h.get('generation') for h in heroes)
    print(f'  Generations covered: {sorted(gens)}')
    if max(gens) < 14:
        issues.append('Heroes missing Gen 14+')

    # Chief Gear
    with open('data/chief_gear.json', encoding='utf-8') as f:
        gear = json.load(f)
    pieces = gear.get('slots', {}).get('pieces', [])
    print(f'chief_gear.json: {len(pieces)} slots')

    expected_slots = ['coat', 'pants', 'belt', 'weapon', 'cap', 'watch']
    actual_slots = [p.get('slot') for p in pieces]
    if set(actual_slots) != set(expected_slots):
        issues.append(f'Chief Gear slots mismatch: {actual_slots}')
    else:
        print('  Slots verified: coat, pants, belt, weapon, cap, watch')

    # Quick Tips
    with open('data/guides/quick_tips.json', encoding='utf-8') as f:
        tips = json.load(f)
    categories = tips.get('categories', {})
    total_tips = sum(len(c.get('tips', [])) for c in categories.values())
    print(f'quick_tips.json: {len(categories)} categories, {total_tips} tips')
    print()

    # 2. High-Impact Value Verification
    print('## High-Impact Values')

    # Tool Enhancement
    print('Checking Tool Enhancement tip...')
    research_cat = categories.get('research', {})
    tool_tips = [t for t in research_cat.get('tips', []) if 'Tool Enhancement' in t.get('tip', '')]
    if tool_tips:
        detail = tool_tips[0].get('detail', '')
        if '0.4%' in detail or 'incremental' in detail.lower():
            print('  Tool Enhancement: VERIFIED (incremental bonuses)')
        else:
            issues.append(f'Tool Enhancement tip may be incorrect: {detail[:100]}')
    else:
        issues.append('Tool Enhancement tip not found')

    # SvS Points
    print('Checking SvS point values...')
    svs_prep = categories.get('svs_prep', {})
    svs_tips = svs_prep.get('tips', [])
    fire_crystal_found = any('2,000' in t.get('detail', '') or '2000' in t.get('detail', '') for t in svs_tips)
    mithril_found = any('40,000' in t.get('detail', '') or '40000' in t.get('detail', '') for t in svs_tips)

    with open('data/events.json', encoding='utf-8') as f:
        events = json.load(f)

    if fire_crystal_found:
        print('  Fire Crystal 2000 pts: Found in tips')
    if mithril_found:
        print('  Mithril 40000 pts: Found in tips')

    # Chief Gear Set Bonuses
    print('Checking Chief Gear set bonuses...')
    set_bonuses = gear.get('set_bonuses', {}).get('bonuses', {})
    if 'Defense' in set_bonuses.get('3_piece', '') and 'Attack' in set_bonuses.get('6_piece', ''):
        print('  Set bonuses: VERIFIED (3pc=Defense, 6pc=Attack)')
    else:
        issues.append('Chief Gear set bonus data may be incorrect')

    print()

    # 3. Cross-Reference Checks
    print('## Cross-Reference Checks')

    # Hero images match hero count
    hero_images = list(Path('assets/heroes').glob('*'))
    print(f'Hero images vs database: {len(hero_images)} images, {len(heroes)} heroes')
    if len(hero_images) == len(heroes):
        print('  Status: MATCH')
    else:
        print(f'  Status: MISMATCH (diff: {abs(len(hero_images) - len(heroes))})')

    # wos_schema.json chief gear consistency
    with open('data/wos_schema.json', encoding='utf-8') as f:
        schema = json.load(f)
    schema_pieces = schema.get('entities', {}).get('chief_gear', {}).get('pieces', [])
    schema_slots = [p.get('slot') for p in schema_pieces]
    if set(schema_slots) == set(expected_slots):
        print('Chief Gear in wos_schema.json: CONSISTENT')
    else:
        issues.append(f'wos_schema.json chief gear slots: {schema_slots}')

    print()

    # 4. Upgrade Edge Validation
    print('## Upgrade Edge Graphs')
    edge_files = list(Path('data/upgrades').glob('*.json'))
    total_edges = 0
    for ef in edge_files:
        if 'manifest' in ef.name or 'sources' in ef.name:
            continue
        try:
            with open(ef, encoding='utf-8') as f:
                data = json.load(f)
            edges = data.get('edges', [])
            total_edges += len(edges)
        except:
            issues.append(f'Failed to load {ef.name}')

    print(f'Edge files: {len(edge_files)}, Total edges: {total_edges}')
    print()

    # 5. Summary
    print('=== Audit Summary ===')
    if issues:
        print(f'Found {len(issues)} issues:')
        for issue in issues:
            print(f'  - {issue}')
    else:
        print('All checks PASSED')

    return len(issues)


if __name__ == '__main__':
    exit(main())
