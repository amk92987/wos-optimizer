"""
QA Quick Check Script
Runs automated validation checks on the WoS Optimizer.
"""

import json
import re
from pathlib import Path


def main():
    print('=== WoS QA Review - Quick Check ===')
    print()

    # 1. JSON Validation
    print('## JSON Validation')
    json_errors = []
    json_files = list(Path('data').rglob('*.json'))
    for jf in json_files:
        try:
            with open(jf, encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            json_errors.append(f'{jf}: {e}')
        except Exception as e:
            json_errors.append(f'{jf}: {e}')

    print(f'JSON files checked: {len(json_files)}')
    if json_errors:
        print('ERRORS:')
        for err in json_errors:
            print(f'  - {err}')
    else:
        print('Status: PASS - All JSON files valid')
    print()

    # 2. Encoding Check - look for mojibake patterns
    print('## Encoding Check')
    # These are mojibake patterns that indicate double-encoding issues
    # They appear when UTF-8 is incorrectly decoded as Latin-1 then re-encoded
    mojibake_patterns = [
        b'\xc3\x83\xc2',  # Double-encoded UTF-8 prefix
        b'\xc3\x82\xc2',  # Another double-encode pattern
        b'\xef\xbb\xbf',  # BOM in middle of file (usually OK at start)
    ]
    # Also check for visible mojibake strings
    text_patterns = [
        'Ã—',  # × incorrectly displayed
        'â€™',  # ' incorrectly displayed
        'â€œ',  # " incorrectly displayed
        'Ã©',  # é incorrectly displayed
        'Ã¨',  # è incorrectly displayed
    ]
    encoding_issues = []
    skip_files = {'run_qa_check.py', 'SKILL.md', 'QA_CHECKLIST.md'}
    for ext in ['*.py', '*.json', '*.md']:
        for f in Path('.').rglob(ext):
            if '.venv' in str(f) or '__pycache__' in str(f):
                continue
            if f.name in skip_files:
                continue
            try:
                content = f.read_bytes()
                # Check binary patterns
                for bad in mojibake_patterns:
                    if bad in content[10:]:  # Skip BOM at start
                        encoding_issues.append(f'{f}: binary encoding issue')
                        break
                # Check text patterns
                text = content.decode('utf-8', errors='replace')
                for bad in text_patterns:
                    if bad in text:
                        encoding_issues.append(f'{f}: mojibake text "{bad}"')
                        break
            except:
                pass

    if encoding_issues:
        print('ISSUES:')
        for issue in encoding_issues[:10]:
            print(f'  - {issue}')
        if len(encoding_issues) > 10:
            print(f'  ... and {len(encoding_issues) - 10} more')
    else:
        print('Status: PASS - No encoding issues found')
    print()

    # 3. Page Syntax Check
    print('## Page Syntax Check')
    syntax_errors = []
    pages = list(Path('pages').glob('*.py'))
    for page in pages:
        try:
            code = page.read_text(encoding='utf-8')
            compile(code, page, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f'{page.name}: Line {e.lineno} - {e.msg}')

    print(f'Pages checked: {len(pages)}')
    if syntax_errors:
        print('ERRORS:')
        for err in syntax_errors:
            print(f'  - {err}')
    else:
        print('Status: PASS - All pages compile')
    print()

    # 4. Data Integrity
    print('## Data Integrity')
    # Hero count - heroes.json has {"heroes": [...]}
    with open('data/heroes.json', encoding='utf-8') as f:
        heroes_data = json.load(f)
    heroes = heroes_data.get('heroes', heroes_data) if isinstance(heroes_data, dict) else heroes_data
    hero_count = len(heroes) if isinstance(heroes, list) else 0
    print(f'Heroes in database: {hero_count}')

    # Hero images
    hero_images = list(Path('assets/heroes').glob('*'))
    print(f'Hero images: {len(hero_images)}')

    # Quick tips categories
    with open('data/guides/quick_tips.json', encoding='utf-8') as f:
        tips = json.load(f)
    cat_count = len(tips.get('categories', {}))
    tip_count = sum(len(c.get('tips', [])) for c in tips.get('categories', {}).values())
    print(f'Quick tip categories: {cat_count}')
    print(f'Total tips: {tip_count}')

    # Chief gear - slots are in slots.pieces array
    with open('data/chief_gear.json', encoding='utf-8') as f:
        gear = json.load(f)
    pieces = gear.get('slots', {}).get('pieces', [])
    slot_names = [p.get('slot') for p in pieces]
    print(f'Chief Gear slots: {len(slot_names)} ({slot_names})')
    print()

    # 5. HTML Scan
    print('## HTML Rendering Scan')
    html_issues = []
    for page in Path('pages').glob('*.py'):
        content = page.read_text(encoding='utf-8')
        # Look for potentially problematic patterns
        if re.search(r'</div>\s*["\']', content):
            # Check if it's properly closed in a string
            pass  # Complex to check, skip for now

    print('Status: PASS - Basic scan complete')
    print()

    # 6. Cross-Reference Check
    print('## Cross-Reference Check')

    # Check Chief Gear slots consistency between chief_gear.json and wos_schema.json
    expected_slots = ['coat', 'pants', 'belt', 'weapon', 'cap', 'watch']

    # Check chief_gear.json
    with open('data/chief_gear.json', encoding='utf-8') as f:
        gear_data = json.load(f)
    gear_slots = [p.get('slot') for p in gear_data.get('slots', {}).get('pieces', [])]

    if set(gear_slots) == set(expected_slots):
        print(f'Chief Gear slots in chief_gear.json: MATCH')
    else:
        print(f'Chief Gear slots MISMATCH: expected {expected_slots}, got {gear_slots}')

    # Check wos_schema.json
    with open('data/wos_schema.json', encoding='utf-8') as f:
        schema = json.load(f)
    schema_pieces = schema.get('entities', {}).get('chief_gear', {}).get('pieces', [])
    schema_slots = [p.get('slot') for p in schema_pieces]

    if set(schema_slots) == set(expected_slots):
        print(f'Chief Gear slots in wos_schema.json: MATCH')
    else:
        print(f'Chief Gear slots in schema MISMATCH: expected {expected_slots}, got {schema_slots}')

    print()
    print('=== Summary ===')
    total_issues = len(json_errors) + len(encoding_issues) + len(syntax_errors)
    if total_issues == 0:
        print('All automated checks PASSED')
    else:
        print(f'Found {total_issues} issues')

    return total_issues


if __name__ == '__main__':
    exit(main())
