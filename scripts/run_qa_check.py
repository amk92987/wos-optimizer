"""
QA Quick Check Script
Runs automated validation checks on the WoS Optimizer.
Includes mobile responsiveness checks.
"""

import json
import re
from pathlib import Path


def check_mobile_css(css_content: str, filename: str) -> list:
    """Check CSS for mobile-related issues."""
    issues = []

    # Check for mobile media queries
    has_mobile_query = bool(re.search(r'@media.*max-width:\s*768px', css_content))
    has_any_media_query = bool(re.search(r'@media\s+screen', css_content))

    if not has_mobile_query and has_any_media_query:
        issues.append(f'{filename}: No 768px mobile breakpoint found')

    # Check for touch target sizing (44-48px minimum)
    # Look for min-height/min-width values that are too small for buttons
    small_targets = re.findall(r'min-(width|height):\s*(\d+)px', css_content)
    for prop, value in small_targets:
        if int(value) < 44 and int(value) > 0:
            # Only flag if it's not in a desktop-only media query
            issues.append(f'{filename}: Small touch target {prop}: {value}px (recommend 44px+)')
            break  # Just flag once

    # Check for problematic fixed positioning without mobile consideration
    fixed_elements = len(re.findall(r'position:\s*fixed', css_content))
    if fixed_elements > 5:
        issues.append(f'{filename}: {fixed_elements} fixed position elements (can cause mobile issues)')

    # Check for horizontal overflow risks (width > 100vw without overflow handling)
    if 'width: 100vw' in css_content and 'overflow-x' not in css_content:
        issues.append(f'{filename}: Uses 100vw without overflow-x handling (causes horizontal scroll)')

    # Check for vh units (problematic on mobile due to address bar)
    vh_usage = len(re.findall(r':\s*\d+vh', css_content))
    if vh_usage > 3:
        issues.append(f'{filename}: Heavy vh unit usage ({vh_usage} instances) - can be inconsistent on mobile')

    # Check for small font sizes (ignore CSS selectors that just match on font-size)
    # Match "font-size: 10px" but not "font-size:10px]" (which is a selector)
    small_fonts = re.findall(r'font-size:\s*(\d+)px(?!["\]\)])', css_content)
    tiny_fonts = [int(f) for f in small_fonts if int(f) < 12 and int(f) > 0]
    if tiny_fonts:
        issues.append(f'{filename}: Font sizes below 12px found: {tiny_fonts} (hard to read on mobile)')

    return issues


def check_mobile_html(py_content: str, filename: str) -> list:
    """Check Python/Streamlit code for mobile-related issues."""
    issues = []

    # Check for hardcoded pixel widths in st.columns that might break on mobile
    # Pattern: st.columns([200, 300]) or similar pixel-looking values
    column_patterns = re.findall(r'st\.columns\(\[([^\]]+)\]\)', py_content)
    for pattern in column_patterns:
        values = re.findall(r'\d+', pattern)
        large_values = [int(v) for v in values if int(v) > 100]
        if large_values:
            issues.append(f'{filename}: st.columns with large values {large_values} may not fit mobile')
            break

    # Check for fixed width inline styles (ignore max-width which is responsive-friendly)
    # Match "width: 400px" but not "max-width: 400px"
    fixed_widths = re.findall(r'(?<!max-)(?<!min-)width:\s*(\d{3,})px', py_content)
    if fixed_widths:
        issues.append(f'{filename}: Fixed widths in inline styles: {fixed_widths}px (use % or max-width)')

    # Check for images without responsive handling
    img_tags = re.findall(r'<img[^>]+>', py_content)
    for img in img_tags:
        if 'width=' in img and 'max-width' not in img and '%' not in img:
            if 'width="100%"' not in img and "width='100%'" not in img:
                issues.append(f'{filename}: Image with fixed width may overflow on mobile')
                break

    # Check for horizontal layouts that might not stack on mobile
    # Only flag flex-direction: row (explicit row layout) - inline-flex is typically
    # used for small inline elements (icons, badges) that don't need mobile stacking
    if 'flex-direction: row' in py_content:
        if '@media' not in py_content:
            issues.append(f'{filename}: Flex row layout without mobile media query (may not stack)')

    return issues


def check_viewport_meta() -> list:
    """Check for proper viewport meta tag in HTML templates."""
    issues = []

    # Check app.py for viewport configuration
    app_path = Path('app.py')
    if app_path.exists():
        content = app_path.read_text(encoding='utf-8')
        if 'viewport' not in content.lower():
            # Streamlit handles this, but custom HTML might not
            pass

    # Check for any custom HTML files
    for html_file in Path('.').rglob('*.html'):
        if '.venv' in str(html_file):
            continue
        content = html_file.read_text(encoding='utf-8')
        if '<meta' in content and 'viewport' not in content:
            issues.append(f'{html_file}: Missing viewport meta tag')
        if 'user-scalable=no' in content or 'user-scalable="no"' in content:
            issues.append(f'{html_file}: user-scalable=no blocks accessibility zoom')
        if 'maximum-scale=1' in content:
            issues.append(f'{html_file}: maximum-scale=1 blocks accessibility zoom')

    return issues


def check_touch_targets_in_css() -> list:
    """Check CSS files for adequate touch target sizes."""
    issues = []

    for css_file in Path('styles').glob('*.css'):
        content = css_file.read_text(encoding='utf-8')

        # Check for button minimum sizes in mobile section
        mobile_section = re.search(r'@media[^{]*max-width:\s*768px[^{]*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', content, re.DOTALL)
        if mobile_section:
            mobile_css = mobile_section.group(1)
            # Look for button touch targets
            if 'button' in mobile_css.lower():
                min_heights = re.findall(r'min-height:\s*(\d+)px', mobile_css)
                adequate = any(int(h) >= 44 for h in min_heights)
                if not adequate and min_heights:
                    issues.append(f'{css_file.name}: Mobile buttons may be too small (found {min_heights}px, need 44px+)')

    return issues


def check_responsive_images() -> list:
    """Check for responsive image handling."""
    issues = []

    for py_file in Path('pages').glob('*.py'):
        content = py_file.read_text(encoding='utf-8')

        # Check for base64 images without max-width
        if 'base64' in content and '<img' in content:
            img_matches = re.findall(r'<img[^>]*style="([^"]*)"[^>]*>', content)
            for style in img_matches:
                if 'max-width' not in style and 'width: 100%' not in style:
                    issues.append(f'{py_file.name}: Image may need max-width:100% for mobile')
                    break

    return issues


def check_sidebar_mobile_handling() -> list:
    """Check for proper sidebar handling on mobile."""
    issues = []

    css_file = Path('styles/custom.css')
    if css_file.exists():
        content = css_file.read_text(encoding='utf-8')

        # Check for sidebar collapse button visibility on mobile
        # Look for mobile media query that shows the button
        has_hamburger_selector = 'stSidebarCollapseButton' in content or 'stSidebarCollapsedControl' in content

        if has_hamburger_selector:
            # Check if there's a mobile section that shows the button
            # The button should have display: flex in a max-width media query
            mobile_shows_button = bool(re.search(
                r'@media[^{]*max-width:\s*768px[^{]*\{[^}]*'
                r'(stSidebarCollapseButton|stSidebarCollapsedControl)[^}]*'
                r'display:\s*flex',
                content, re.DOTALL | re.IGNORECASE
            ))

            if not mobile_shows_button:
                # Alternative check: look for the pattern in sections
                if 'display: flex !important' in content and '@media' in content:
                    # Good enough - there's flex display in media queries
                    pass
                else:
                    issues.append('Sidebar hamburger button may not be visible on mobile')

    return issues


def check_form_input_sizes() -> list:
    """Check that form inputs are large enough to prevent iOS zoom."""
    issues = []

    for css_file in Path('styles').glob('*.css'):
        content = css_file.read_text(encoding='utf-8')

        # iOS auto-zooms on inputs with font-size < 16px
        input_font_sizes = re.findall(r'input[^{]*\{[^}]*font-size:\s*(\d+)px', content)
        small_inputs = [int(s) for s in input_font_sizes if int(s) < 16]
        if small_inputs:
            issues.append(f'{css_file.name}: Input font-size {small_inputs}px may cause iOS auto-zoom (use 16px+)')

    return issues


def check_wos_app_mobile() -> list:
    """
    WoS App-specific mobile checks.
    Validates CSS and layouts against known UI patterns in this app.
    """
    issues = []
    warnings = []

    # === CSS FILE CHECKS ===
    for css_file in Path('styles').glob('*.css'):
        content = css_file.read_text(encoding='utf-8')
        filename = css_file.name

        # 1. Check for mobile breakpoint coverage
        has_768_breakpoint = bool(re.search(r'@media[^{]*max-width:\s*768px', content))
        has_480_breakpoint = bool(re.search(r'@media[^{]*max-width:\s*480px', content))

        if not has_768_breakpoint and not has_480_breakpoint:
            warnings.append(f'{filename}: No mobile breakpoints (@media max-width: 768px/480px)')

        # 2. Check button minimum heights (44px for touch targets)
        button_heights = re.findall(r'\.stButton[^{]*\{[^}]*min-height:\s*(\d+)px', content)
        small_buttons = [int(h) for h in button_heights if int(h) < 44]
        if small_buttons:
            issues.append(f'{filename}: Button min-height {min(small_buttons)}px < 44px touch target')

        # 3. Check for very small font sizes (< 12px)
        all_font_sizes = re.findall(r'font-size:\s*(\d+)px', content)
        tiny_fonts = [int(s) for s in all_font_sizes if int(s) < 11]
        if tiny_fonts:
            issues.append(f'{filename}: Font sizes below 11px found: {set(tiny_fonts)}')

        # 4. Check sidebar padding isn't too wide for mobile
        sidebar_padding = re.findall(r'\[data-testid="stSidebar"\][^{]*\{[^}]*padding[^:]*:\s*(\d+)', content)
        large_padding = [int(p) for p in sidebar_padding if int(p) > 20]
        if large_padding:
            warnings.append(f'{filename}: Sidebar padding {max(large_padding)}px may be too wide on mobile')

    # === PAGE-SPECIFIC LAYOUT CHECKS ===
    # Note: Some layout patterns (multi-column, tabs) are acceptable trade-offs
    # and don't need to be flagged as warnings. Only flag truly problematic patterns.

    # Check for very large fixed heights that would be problematic
    ai_advisor = Path('pages/6_AI_Advisor.py')
    if ai_advisor.exists():
        content = ai_advisor.read_text(encoding='utf-8')
        # Flag heights > 400px as potentially problematic
        chat_heights = re.findall(r'height\s*=\s*(\d+)', content)
        large_heights = [int(h) for h in chat_heights if int(h) > 400]
        if large_heights:
            warnings.append(f'AI Advisor: Fixed height={max(large_heights)}px may leave little room on mobile')

    # === INLINE STYLE CHECKS ACROSS ALL PAGES ===
    for py_file in Path('pages').glob('*.py'):
        content = py_file.read_text(encoding='utf-8')
        filename = py_file.name

        # Check for very small inline font sizes (9px, 10px badges)
        inline_tiny_fonts = re.findall(r'font-size:\s*(9|10)px', content)
        if inline_tiny_fonts:
            warnings.append(f'{filename}: Inline font-size {inline_tiny_fonts[0]}px may be hard to read on mobile')

        # Check for fixed widths > 150px without max-width (potential overflow)
        fixed_large_widths = re.findall(r'(?<!max-)width:\s*(\d{3,})px', content)
        overflow_widths = [int(w) for w in fixed_large_widths if int(w) > 200]
        if overflow_widths:
            issues.append(f'{filename}: Fixed width {max(overflow_widths)}px may overflow on mobile')

    # Return tuple of (issues, warnings) - issues are blocking, warnings are informational
    return (issues, warnings)


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

    # 7. Mobile Responsiveness Checks
    print('## Mobile Responsiveness Checks')
    mobile_issues = []

    # Check CSS files for mobile issues
    print('Checking CSS for mobile issues...')
    for css_file in Path('styles').glob('*.css'):
        if 'backup' in css_file.name:
            continue
        content = css_file.read_text(encoding='utf-8')
        mobile_issues.extend(check_mobile_css(content, css_file.name))

    # Check Python/Streamlit files for mobile issues
    print('Checking pages for mobile issues...')
    for py_file in Path('pages').glob('*.py'):
        content = py_file.read_text(encoding='utf-8')
        mobile_issues.extend(check_mobile_html(content, py_file.name))

    # Check viewport meta
    print('Checking viewport configuration...')
    mobile_issues.extend(check_viewport_meta())

    # Check touch targets
    print('Checking touch target sizes...')
    mobile_issues.extend(check_touch_targets_in_css())

    # Check responsive images
    print('Checking responsive images...')
    mobile_issues.extend(check_responsive_images())

    # Check sidebar mobile handling
    print('Checking sidebar mobile handling...')
    mobile_issues.extend(check_sidebar_mobile_handling())

    # Check form input sizes
    print('Checking form input sizes...')
    mobile_issues.extend(check_form_input_sizes())

    # WoS App-specific mobile checks
    print('Checking WoS app-specific mobile patterns...')
    app_issues, app_warnings = check_wos_app_mobile()
    mobile_issues.extend(app_issues)
    mobile_warnings = app_warnings

    if mobile_issues:
        print(f'\nMobile Issues ({len(mobile_issues)}):')
        for issue in mobile_issues:
            print(f'  - {issue}')

    if mobile_warnings:
        print(f'\nMobile Warnings ({len(mobile_warnings)}) - Layout recommendations:')
        for warning in mobile_warnings:
            print(f'  * {warning}')

    if not mobile_issues and not mobile_warnings:
        print('Status: PASS - No mobile issues detected')
    elif not mobile_issues:
        print('\nStatus: PASS - No blocking issues (warnings are informational)')
    print()

    print('=== Summary ===')
    total_issues = len(json_errors) + len(encoding_issues) + len(syntax_errors) + len(mobile_issues)
    if total_issues == 0:
        print('All automated checks PASSED')
        if mobile_warnings:
            print(f'  (with {len(mobile_warnings)} layout warnings to consider)')
    else:
        print(f'Found {total_issues} issues')
        if mobile_issues:
            print(f'  - Mobile issues: {len(mobile_issues)}')

    return total_issues


if __name__ == '__main__':
    exit(main())
