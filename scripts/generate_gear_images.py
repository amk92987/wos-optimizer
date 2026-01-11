"""
Generate chief gear image variations with different colors, tiers, and stars.
Uses PIL to create color-tinted versions of base gear images.
"""

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from pathlib import Path
import colorsys

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_ROOT / "assets" / "chief_gear"
OUTPUT_DIR = PROJECT_ROOT / "assets" / "chief_gear" / "tiers"

# Gear slots and their base images
GEAR_SLOTS = {
    "cap": "hat.png",
    "watch": "watch.png",
    "coat": "coat.png",
    "pants": "pants.png",
    "belt": "ring.png",
    "weapon": "staff.png",
}

# Tier colors (background gradient colors)
TIER_COLORS = {
    "gray": {"primary": (120, 120, 120), "secondary": (80, 80, 80), "border": (100, 100, 100)},
    "green": {"primary": (60, 140, 60), "secondary": (40, 100, 40), "border": (80, 160, 80)},
    "blue": {"primary": (60, 100, 180), "secondary": (40, 70, 140), "border": (80, 130, 200)},
    "purple": {"primary": (140, 60, 180), "secondary": (100, 40, 140), "border": (160, 80, 200)},
    "gold": {"primary": (200, 150, 50), "secondary": (160, 110, 30), "border": (220, 180, 80)},
    "pink": {"primary": (220, 80, 150), "secondary": (180, 50, 120), "border": (240, 120, 180)},
}

# Star colors
STAR_FILLED = (255, 215, 0)  # Gold
STAR_EMPTY = (80, 80, 80)    # Dark gray


def create_gradient_background(size, color1, color2):
    """Create a diagonal gradient background."""
    img = Image.new('RGBA', size)
    draw = ImageDraw.Draw(img)

    for y in range(size[1]):
        for x in range(size[0]):
            # Diagonal gradient
            ratio = (x + y) / (size[0] + size[1])
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.point((x, y), fill=(r, g, b, 255))

    return img


def draw_stars(draw, x, y, filled_count, total=3, size=8, vertical=False):
    """Draw star indicators (horizontal or vertical)."""
    star_spacing = size + 2
    import math

    for i in range(total):
        if vertical:
            star_x = x
            star_y = y + i * star_spacing
            # For vertical, fill from bottom up (reverse order)
            color = STAR_FILLED if (total - 1 - i) < filled_count else STAR_EMPTY
        else:
            star_x = x + i * star_spacing
            star_y = y
            color = STAR_FILLED if i < filled_count else STAR_EMPTY

        # Simple 5-point star approximation using polygon
        points = []
        for j in range(5):
            # Outer points
            angle = -90 + j * 72
            ox = star_x + size/2 + (size/2) * math.cos(math.radians(angle))
            oy = star_y + size/2 + (size/2) * math.sin(math.radians(angle))
            points.append((ox, oy))

            # Inner points
            inner_angle = angle + 36
            ix = star_x + size/2 + (size/4) * math.cos(math.radians(inner_angle))
            iy = star_y + size/2 + (size/4) * math.sin(math.radians(inner_angle))
            points.append((ix, iy))

        draw.polygon(points, fill=color, outline=(0, 0, 0))


def draw_tier_badge(draw, tier_num, x, y, color):
    """Draw tier badge (T1, T2, T3)."""
    text = f"T{tier_num}"

    # Draw background rectangle - much larger for readability
    bbox_w, bbox_h = 42, 32
    draw.rectangle([x, y, x + bbox_w, y + bbox_h], fill=color, outline=(0, 0, 0), width=2)

    # Draw text with bold larger font
    try:
        font = ImageFont.truetype("arialbd.ttf", 24)  # Bold Arial
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

    draw.text((x + 6, y + 3), text, fill=(255, 255, 255), font=font)


def extract_gear_subject(img):
    """Try to extract the gear item from the background."""
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Get the center region (where the gear item likely is)
    width, height = img.size

    # Create a mask based on non-uniform colors (the gear item has texture, background is gradient)
    # This is a simple approach - we'll keep pixels that aren't pure gradient colors

    return img  # For now, return the original - we'll overlay on new background


def apply_color_tint(img, tint_color, strength=0.5):
    """Apply a color tint to an image using fast numpy blending."""
    import numpy as np

    img = img.convert('RGBA')
    arr = np.array(img, dtype=np.float32)

    # Create tint array
    tint = np.array([tint_color[0], tint_color[1], tint_color[2], 255], dtype=np.float32)

    # Blend RGB channels, preserve alpha
    arr[:, :, 0] = arr[:, :, 0] * (1 - strength) + tint[0] * strength
    arr[:, :, 1] = arr[:, :, 1] * (1 - strength) + tint[1] * strength
    arr[:, :, 2] = arr[:, :, 2] * (1 - strength) + tint[2] * strength
    # Alpha stays unchanged

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def generate_gear_variation(base_img_path, color_name, tier_num, stars, output_path):
    """Generate a single gear image variation."""

    # Load base image
    try:
        base_img = Image.open(base_img_path).convert('RGBA')
    except Exception as e:
        print(f"Error loading {base_img_path}: {e}")
        return False

    size = base_img.size
    colors = TIER_COLORS[color_name]

    # Apply strong color tint to the entire image
    # This shifts the hue of the background while preserving the gear detail
    tint_strength = 0.6 if color_name != "gold" else 0.3  # Gold is already close to original
    result = apply_color_tint(base_img, colors["primary"], tint_strength)

    # Convert to RGB for drawing
    result_rgb = result.convert('RGBA')
    draw = ImageDraw.Draw(result_rgb)

    # Add border
    border_color = colors["border"]
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=border_color, width=2)

    # Draw tier badge (top-left) - only if tier > 0
    if tier_num > 0:
        draw_tier_badge(draw, tier_num, 2, 2, colors["secondary"])
        star_y_start = 36  # Just below tier badge
    else:
        # For base (tier 0), just draw solid color block where badge would be
        draw.rectangle([2, 2, 44, 34], fill=colors["secondary"], outline=(0, 0, 0), width=2)
        star_y_start = 36

    # Draw stars vertically below tier badge on left side
    star_size = 28
    draw_stars(draw, 8, star_y_start, stars, total=3, size=star_size, vertical=True)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_rgb.save(output_path, 'PNG')

    return True


def generate_all_variations():
    """Generate all gear image variations."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    errors = 0

    for slot_name, base_filename in GEAR_SLOTS.items():
        base_path = ASSETS_DIR / base_filename

        if not base_path.exists():
            print(f"Warning: Base image not found: {base_path}")
            continue

        print(f"\nProcessing {slot_name}...")

        for color_name in TIER_COLORS.keys():
            for tier in [0, 1, 2, 3]:  # 0 = base (no T badge)
                for stars in [0, 1, 2, 3]:
                    # Output filename: cap_gold_t0_2star.png (t0 = base)
                    output_filename = f"{slot_name}_{color_name}_t{tier}_{stars}star.png"
                    output_path = OUTPUT_DIR / output_filename

                    if generate_gear_variation(base_path, color_name, tier, stars, output_path):
                        generated += 1
                    else:
                        errors += 1

        print(f"  Generated {generated} images for {slot_name}")

    print(f"\n{'='*50}")
    print(f"Total generated: {generated}")
    print(f"Errors: {errors}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    print("Chief Gear Image Generator")
    print("="*50)
    generate_all_variations()
