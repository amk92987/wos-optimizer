"""
Screenshot OCR Parser for Whiteout Survival backpack screenshots.
"""

from pathlib import Path
from PIL import Image
import re
from typing import List, Dict, Tuple, Optional

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class ScreenshotParser:
    """Parse backpack screenshots using OCR."""

    def __init__(self):
        self.reader = None
        if EASYOCR_AVAILABLE:
            # Initialize EasyOCR with English
            self.reader = easyocr.Reader(['en'], gpu=False)

        # Common item patterns in WoS
        self.item_patterns = {
            # Hero shards
            r'(\w+)\s*shard': 'Hero Shard',
            r'general\s*shard': 'General Hero Shard',
            r'epic\s*shard': 'Epic General Shard',
            r'legendary\s*shard': 'Legendary General Shard',

            # XP items
            r'hero\s*exp': 'Hero EXP',
            r'combat\s*manual': 'Combat Manual',
            r'advanced\s*combat': 'Advanced Combat Manual',

            # Gear materials
            r'gear\s*material': 'Gear Material',
            r'iron\s*ore': 'Iron Ore',
            r'refined\s*iron': 'Refined Iron',
            r'steel\s*ingot': 'Steel Ingot',

            # Skill books
            r'skill\s*book': 'Skill Book',
            r'exploration\s*skill': 'Exploration Skill Book',
            r'expedition\s*skill': 'Expedition Skill Book',

            # Resources
            r'food': 'Food',
            r'wood': 'Wood',
            r'coal': 'Coal',
            r'iron': 'Iron',
            r'speedup': 'Speedup',
        }

    def is_available(self) -> bool:
        """Check if OCR is available."""
        return EASYOCR_AVAILABLE and self.reader is not None

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize if too large (for performance)
        max_dimension = 2000
        if max(image.size) > max_dimension:
            ratio = max_dimension / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        return image

    def extract_text(self, image_path: str) -> List[Tuple[str, float]]:
        """Extract text from image using OCR.

        Returns list of (text, confidence) tuples.
        """
        if not self.is_available():
            return []

        try:
            image = Image.open(image_path)
            image = self.preprocess_image(image)

            # Run OCR
            results = self.reader.readtext(
                image,
                detail=1,
                paragraph=False
            )

            # Extract text and confidence
            extracted = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Filter low confidence
                    extracted.append((text.strip(), confidence))

            return extracted

        except Exception as e:
            print(f"OCR Error: {e}")
            return []

    def parse_quantity(self, text: str) -> Optional[int]:
        """Extract quantity from text like '×150' or 'x150' or '150'."""
        # Try to find quantity patterns
        patterns = [
            r'[×x]\s*(\d+)',  # ×150 or x150
            r'(\d+)\s*[×x]',  # 150× or 150x
            r'(\d{1,6})',     # Just numbers
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue

        return None

    def identify_item(self, text: str) -> Optional[Dict]:
        """Try to identify an item from OCR text."""
        text_lower = text.lower().strip()

        for pattern, item_type in self.item_patterns.items():
            if re.search(pattern, text_lower):
                return {
                    'type': item_type,
                    'raw_text': text,
                    'matched_pattern': pattern
                }

        # If no pattern matched but text is substantial
        if len(text) > 3:
            return {
                'type': 'Unknown',
                'raw_text': text,
                'matched_pattern': None
            }

        return None

    def parse_screenshot(self, image_path: str) -> List[Dict]:
        """Parse a backpack screenshot and extract items.

        Returns list of detected items with quantities.
        """
        if not self.is_available():
            return [{
                'error': 'EasyOCR not available. Install with: pip install easyocr'
            }]

        # Extract all text
        text_results = self.extract_text(image_path)

        if not text_results:
            return [{
                'error': 'No text detected in image'
            }]

        # Process results
        items = []
        for text, confidence in text_results:
            # Try to identify item
            item = self.identify_item(text)
            if item:
                # Try to find associated quantity
                quantity = self.parse_quantity(text)
                item['quantity'] = quantity
                item['confidence'] = confidence
                items.append(item)

        # Deduplicate and merge
        merged = {}
        for item in items:
            key = item['type']
            if key in merged:
                # Keep higher confidence version
                if item['confidence'] > merged[key]['confidence']:
                    merged[key] = item
            else:
                merged[key] = item

        return list(merged.values())

    def parse_from_pil_image(self, image: Image.Image) -> List[Dict]:
        """Parse from a PIL Image object directly."""
        if not self.is_available():
            return [{
                'error': 'EasyOCR not available. Install with: pip install easyocr'
            }]

        try:
            image = self.preprocess_image(image)

            # Run OCR
            results = self.reader.readtext(
                image,
                detail=1,
                paragraph=False
            )

            # Process results
            items = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:
                    item = self.identify_item(text)
                    if item:
                        quantity = self.parse_quantity(text)
                        item['quantity'] = quantity
                        item['confidence'] = confidence
                        items.append(item)

            return items

        except Exception as e:
            return [{'error': f'OCR Error: {str(e)}'}]
