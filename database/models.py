"""SQLAlchemy models for Whiteout Survival Optimizer."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class UserProfile(Base):
    """User's game profile and preferences."""
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), default="Chief")
    server_age_days = Column(Integer, default=0)
    furnace_level = Column(Integer, default=1)
    furnace_fc_level = Column(String(10), nullable=True)  # e.g., "FC3-0", "30-1"

    # Optimizer settings
    spending_profile = Column(String(20), default="f2p")  # f2p, minnow, dolphin, orca, whale
    priority_focus = Column(String(20), default="balanced_growth")  # svs_combat, balanced_growth, economy_focus
    alliance_role = Column(String(20), default="filler")  # rally_lead, filler, farmer, casual

    # Priority settings (1-5 scale)
    priority_svs = Column(Integer, default=5)
    priority_rally = Column(Integer, default=4)
    priority_castle_battle = Column(Integer, default=4)
    priority_exploration = Column(Integer, default=3)
    priority_gathering = Column(Integer, default=2)

    # SvS tracking
    last_svs_date = Column(DateTime, nullable=True)
    svs_wins = Column(Integer, default=0)
    svs_losses = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    heroes = relationship("UserHero", back_populates="profile")
    inventory = relationship("UserInventory", back_populates="profile")


class Hero(Base):
    """Static hero reference data."""
    __tablename__ = 'heroes'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    generation = Column(Integer, nullable=False)
    hero_class = Column(String(20), nullable=False)  # Infantry, Marksman, Lancer
    rarity = Column(String(20), nullable=False)  # Epic, Legendary

    # Tier rankings
    tier_overall = Column(String(5))  # S+, S, A, B, C, D
    tier_expedition = Column(String(5))  # Combat/SvS rating
    tier_exploration = Column(String(5))  # PvE rating

    # Image path
    image_filename = Column(String(100))

    # Skill names (for reference)
    exploration_skill_1 = Column(String(100))
    exploration_skill_2 = Column(String(100))
    expedition_skill_1 = Column(String(100))
    expedition_skill_2 = Column(String(100))

    # Additional info
    how_to_obtain = Column(String(200))
    notes = Column(String(500))


class UserHero(Base):
    """User's owned heroes with their current levels."""
    __tablename__ = 'user_heroes'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    hero_id = Column(Integer, ForeignKey('heroes.id'), nullable=False)

    # Hero progression
    level = Column(Integer, default=1)  # 1-80
    stars = Column(Integer, default=0)  # 0-5
    ascension_tier = Column(Integer, default=0)  # 0-5 per star (6 = next star)

    # Skill levels
    exploration_skill_1_level = Column(Integer, default=1)
    exploration_skill_2_level = Column(Integer, default=1)
    expedition_skill_1_level = Column(Integer, default=1)
    expedition_skill_2_level = Column(Integer, default=1)

    # Hero gear - 4 slots with quality and level
    # Quality: 0=None, 1=Gray, 2=Green, 3=Blue, 4=Purple, 5=Orange/Legendary, 6=Mythic
    gear_slot1_quality = Column(Integer, default=0)
    gear_slot1_level = Column(Integer, default=0)
    gear_slot2_quality = Column(Integer, default=0)
    gear_slot2_level = Column(Integer, default=0)
    gear_slot3_quality = Column(Integer, default=0)
    gear_slot3_level = Column(Integer, default=0)
    gear_slot4_quality = Column(Integer, default=0)
    gear_slot4_level = Column(Integer, default=0)

    # Mythic hero gear (exclusive gear like Dawnbreak)
    mythic_gear_unlocked = Column(Boolean, default=False)
    mythic_gear_quality = Column(Integer, default=0)  # Same scale: 1-6
    mythic_gear_level = Column(Integer, default=0)

    owned = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="heroes")
    hero = relationship("Hero")


class Item(Base):
    """Item definitions for backpack tracking."""
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # Shard, XP, Material, Gear, etc.
    subcategory = Column(String(50))  # Hero-specific, Class-specific, etc.
    rarity = Column(String(20))  # Common, Rare, Epic, Legendary

    # For OCR matching
    ocr_aliases = Column(JSON)  # Alternative names OCR might detect

    # Item image (if we have it)
    image_filename = Column(String(100))


class UserInventory(Base):
    """User's backpack items."""
    __tablename__ = 'user_inventory'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity = Column(Integer, default=0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="inventory")
    item = relationship("Item")


class UpgradeHistory(Base):
    """Track upgrade decisions for analytics."""
    __tablename__ = 'upgrade_history'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)

    upgrade_type = Column(String(50))  # hero_level, hero_skill, hero_gear, etc.
    target_name = Column(String(100))  # What was upgraded
    from_value = Column(Integer)
    to_value = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
