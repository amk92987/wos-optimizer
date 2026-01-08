"""
Download hero portrait images from the Whiteout Survival Wiki.
Saves images locally to assets/heroes/ for reliable offline access.
"""

import os
import requests
from pathlib import Path
import time

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "heroes"

# Ensure directory exists
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Hero image URLs from whiteoutsurvival.wiki
HERO_IMAGES = {
    "smith": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/smith.png",
    "eugene": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/eugene.png",
    "charlie": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/charlie.png",
    "cloris": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/cloris.png",
    "sergey": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/sergey.png",
    "jessie": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/jessie.png",
    "patrick": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/patrick.png",
    "lumak_bokan": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/05/3.png",
    "ling_xue": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/12/%E5%87%8C%E9%9B%AA350.jpg",
    "gina": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/Gina.png",
    "bahiti": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/bahiti.png",
    "jasser": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/1.jpg",
    "seo-yoon": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/10/2.jpg",
    "natalia": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/natalia.png",
    "jeronimo": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/jeronimo.png",
    "molly": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/molly.png",
    "zinman": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/zinman.png",
    "flint": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/flint.png",
    "philly": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/philly.png",
    "alonso": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/alonso.png",
    "logan": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/logan.png",
    "mia": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/mia.png",
    "greg": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/05/greg.png",
    "ahmose": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/09/ahmos.png",
    "reina": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/09/1690429616516_7.jpg",
    "lynn": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/09/1690429616507_5.jpg",
    "hector": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/09/1690429616489_3.jpg",
    "norah": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/09/1690429616480_2.jpg",
    "gwen": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/09/1690429616472_1.jpg",
    "wu_ming": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/11/wuming.jpg",
    "renee": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/11/rene.jpg",
    "wayne": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2023/11/wayne.jpg",
    "edith": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/03/20240222_2.jpg",
    "gordon": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/03/20240222_1.jpg",
    "bradley": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/03/20240222_3.jpg",
    "gatot": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/07/5.jpg",
    "sonya": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/07/6.jpg",
    "hendrik": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/07/7.jpg",
    "magnus": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/08/magnus.jpg",
    "fred": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/08/fred.jpg",
    "xura": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/08/xura.jpg",
    "gregory": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/12/gregory350.jpg",
    "freya": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/12/freya350.jpg",
    "blanchette": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2024/12/blanchette350.jpg",
    "eleonora": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/03/eleonora.jpg",
    "lloyd": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/03/Lloyd.jpg",
    "rufus": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/03/rufus.jpg",
    "hervor": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/05/20250519%E8%8B%B1%E9%9B%84%E5%A4%B4%E5%83%8FHervor-1.jpg",
    "karol": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/05/20250519%E8%8B%B1%E9%9B%84%E5%A4%B4%E5%83%8Fkarol-1.jpg",
    "ligeia": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/05/20250519%E8%8B%B1%E9%9B%84%E5%A4%B4%E5%83%8FLigeia-1.jpg",
    "gisela": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/08/20250519%E8%8B%B1%E9%9B%84%E5%A4%B4%E5%83%8Fgisela.jpg",
    "flora": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/08/20250519%E8%8B%B1%E9%9B%84%E5%A4%B4%E5%83%8FFlora.jpg",
    "vulcanus": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2025/08/20250519%E8%8B%B1%E9%9B%84%E5%A4%B4%E5%83%8Fvulcanus.jpg",
    "elif": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2026/01/%E8%89%BE%E4%B8%BD%E8%8A%99.png",
    "dominic": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2026/01/%E5%A4%9A%E7%B1%B3%E5%B0%BC%E5%85%8B.png",
    "cara": "https://gom-s3-user-avatar.s3.us-west-2.amazonaws.com/wp-content/uploads/2026/01/%E5%8D%A1%E6%8B%89.png",
}


def download_image(name: str, url: str) -> bool:
    """Download a single hero image."""
    # Determine file extension from URL
    ext = url.split('.')[-1].split('?')[0].lower()
    if ext not in ['png', 'jpg', 'jpeg', 'webp']:
        ext = 'png'

    # Normalize filename
    filename = f"{name}.{ext}"
    filepath = ASSETS_DIR / filename

    # Skip if already downloaded
    if filepath.exists():
        print(f"  [SKIP] {name} - already exists")
        return True

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"  [OK] {name} - downloaded ({len(response.content)} bytes)")
        return True

    except Exception as e:
        print(f"  [FAIL] {name} - {e}")
        return False


def main():
    """Download all hero images."""
    print(f"Downloading hero images to: {ASSETS_DIR}")
    print(f"Total heroes: {len(HERO_IMAGES)}")
    print("-" * 50)

    success = 0
    failed = 0

    for name, url in HERO_IMAGES.items():
        if download_image(name, url):
            success += 1
        else:
            failed += 1
        # Small delay to be nice to the server
        time.sleep(0.2)

    print("-" * 50)
    print(f"Complete! Success: {success}, Failed: {failed}")

    # List downloaded files
    print("\nDownloaded files:")
    for f in sorted(ASSETS_DIR.glob("*")):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
