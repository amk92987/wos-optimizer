"""
Utility to download hero images from Whiteout Survival Wiki.
Run this script to populate the assets/heroes folder.
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import json
import re

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "heroes"
DATA_DIR = PROJECT_ROOT / "data"

# Wiki URLs
WIKI_BASE = "https://www.whiteoutsurvival.wiki"
HEROES_PAGE = f"{WIKI_BASE}/heroes/"

# Headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def ensure_dirs():
    """Create necessary directories."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_image(url: str, filename: str) -> bool:
    """Download an image from URL to the assets folder."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            filepath = ASSETS_DIR / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  Downloaded: {filename}")
            return True
        else:
            print(f"  Failed ({response.status_code}): {url}")
            return False
    except Exception as e:
        print(f"  Error downloading {filename}: {e}")
        return False


def scrape_hero_images():
    """Scrape hero images from the wiki."""
    print("Fetching heroes page...")

    try:
        response = requests.get(HEROES_PAGE, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            print(f"Failed to fetch heroes page: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        heroes_found = []

        # Find all hero links/images on the page
        # The wiki typically has hero cards with images
        hero_elements = soup.find_all(['a', 'img'], href=True) if soup.find_all('a', href=True) else []

        # Also look for specific hero image patterns
        img_tags = soup.find_all('img')

        for img in img_tags:
            src = img.get('src', '') or img.get('data-src', '')
            alt = img.get('alt', '')

            if not src:
                continue

            # Skip non-hero images
            if any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'background', 'button']):
                continue

            # Try to extract hero name from alt text or URL
            hero_name = None
            if alt:
                hero_name = alt.strip()
            else:
                # Try to get name from URL
                match = re.search(r'/([A-Za-z]+)[-_]?(?:portrait|hero)?\.', src)
                if match:
                    hero_name = match.group(1)

            if hero_name and len(hero_name) > 2:
                # Normalize the URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = WIKI_BASE + src

                heroes_found.append({
                    'name': hero_name,
                    'image_url': src
                })

        print(f"Found {len(heroes_found)} potential hero images")
        return heroes_found

    except Exception as e:
        print(f"Error scraping: {e}")
        return []


def download_all_heroes():
    """Download all hero images."""
    ensure_dirs()

    print("=" * 50)
    print("Whiteout Survival Hero Image Downloader")
    print("=" * 50)

    heroes = scrape_hero_images()

    if not heroes:
        print("\nNo heroes found via scraping. Using fallback list...")
        # Fallback: just create placeholder info
        return

    downloaded = 0
    for hero in heroes:
        name = hero['name']
        url = hero['image_url']

        # Create safe filename
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        filename = f"{safe_name}.png"

        if download_image(url, filename):
            downloaded += 1

        # Be nice to the server
        time.sleep(0.5)

    print(f"\nDownloaded {downloaded} hero images to {ASSETS_DIR}")


def create_placeholder_images():
    """Create placeholder images for heroes if downloads fail."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not installed. Run: pip install Pillow")
        return

    ensure_dirs()

    # Load hero data to get names
    heroes_file = DATA_DIR / "heroes.json"
    if not heroes_file.exists():
        print("heroes.json not found. Create it first.")
        return

    with open(heroes_file, encoding='utf-8') as f:
        heroes_data = json.load(f)

    for hero in heroes_data.get('heroes', []):
        name = hero['name']
        hero_class = hero.get('hero_class', 'Unknown')

        # Create safe filename
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        filename = f"{safe_name}.png"
        filepath = ASSETS_DIR / filename

        if filepath.exists():
            continue

        # Create placeholder image
        img = Image.new('RGBA', (200, 200), color=(30, 42, 58, 255))
        draw = ImageDraw.Draw(img)

        # Class colors
        class_colors = {
            'Infantry': '#E74C3C',
            'Marksman': '#3498DB',
            'Lancer': '#2ECC71'
        }
        color = class_colors.get(hero_class, '#4A90D9')

        # Draw border
        draw.rectangle([0, 0, 199, 199], outline=color, width=4)

        # Draw text (hero name)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # Center the text
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2

        draw.text((x, y), name, fill='white', font=font)

        # Draw class indicator
        draw.text((10, 170), hero_class, fill=color, font=font)

        img.save(filepath)
        print(f"Created placeholder: {filename}")


if __name__ == "__main__":
    # First try to download from wiki
    download_all_heroes()

    # Then create placeholders for any missing heroes
    print("\nCreating placeholders for missing heroes...")
    create_placeholder_images()
