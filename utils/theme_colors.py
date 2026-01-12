"""Theme-aware color utilities for inline styles.

Use these functions when building HTML with inline styles to ensure
proper contrast on both dark and light themes.
"""

import streamlit as st
from database.auth import get_current_user_id, get_user_theme
from database.db import get_db


def get_theme() -> str:
    """Get current user's theme preference."""
    try:
        db = get_db()
        user_id = get_current_user_id()
        if user_id:
            return get_user_theme(db, user_id)
    except Exception:
        pass
    return 'dark'


def is_light_theme() -> bool:
    """Check if current theme is light."""
    return get_theme() == 'light'


# Theme-aware color palette
def get_colors():
    """Get color palette based on current theme."""
    if is_light_theme():
        return {
            'text_primary': '#1A365D',      # Dark blue text
            'text_secondary': '#4A6B8A',    # Medium blue text
            'text_muted': '#6B7280',         # Gray text
            'gold': '#B8860B',               # Dark gold (visible on light)
            'fire': '#D4510A',               # Dark orange
            'ice': '#2E7BC4',                # Ice blue
            'danger': '#C0392B',             # Dark red
            'success': '#27AE60',            # Green
            'warning': '#D68910',            # Dark yellow
            'infantry': '#DC2626',           # Red
            'lancer': '#16A34A',             # Green
            'marksman': '#2563EB',           # Blue
            'background_card': 'rgba(255, 255, 255, 0.7)',
            'background_hover': 'rgba(255, 255, 255, 0.9)',
            'border': 'rgba(74, 144, 217, 0.2)',
        }
    else:
        return {
            'text_primary': '#E8F4F8',       # Frost white
            'text_secondary': '#B8D4E8',     # Light blue
            'text_muted': '#888888',          # Gray
            'gold': '#FFD700',                # Bright gold
            'fire': '#FF6B35',                # Bright orange
            'ice': '#4A90D9',                 # Ice blue
            'danger': '#E74C3C',              # Bright red
            'success': '#2ECC71',             # Bright green
            'warning': '#F39C12',             # Yellow
            'infantry': '#E74C3C',            # Red
            'lancer': '#2ECC71',              # Green
            'marksman': '#3498DB',            # Blue
            'background_card': 'rgba(46, 90, 140, 0.3)',
            'background_hover': 'rgba(46, 90, 140, 0.4)',
            'border': 'rgba(255, 255, 255, 0.15)',
        }


# Convenience functions for common colors
def text_primary() -> str:
    """Get primary text color."""
    return get_colors()['text_primary']


def text_secondary() -> str:
    """Get secondary text color."""
    return get_colors()['text_secondary']


def text_gold() -> str:
    """Get gold accent color."""
    return get_colors()['gold']


def text_fire() -> str:
    """Get fire/orange accent color."""
    return get_colors()['fire']


def text_danger() -> str:
    """Get danger/red color."""
    return get_colors()['danger']


def text_success() -> str:
    """Get success/green color."""
    return get_colors()['success']


def text_warning() -> str:
    """Get warning/yellow color."""
    return get_colors()['warning']


def card_background() -> str:
    """Get card background color."""
    return get_colors()['background_card']


def text_shadow() -> str:
    """Get appropriate text shadow for readability."""
    if is_light_theme():
        return 'text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);'
    else:
        return 'text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);'
