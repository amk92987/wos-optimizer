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

    # Skill names (for reference) - 3 exploration + 3 expedition skills
    exploration_skill_1 = Column(String(100))
    exploration_skill_2 = Column(String(100))
    exploration_skill_3 = Column(String(100))
    expedition_skill_1 = Column(String(100))
    expedition_skill_2 = Column(String(100))
    expedition_skill_3 = Column(String(100))

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

    # Skill levels - 3 exploration + 3 expedition skills
    exploration_skill_1_level = Column(Integer, default=1)
    exploration_skill_2_level = Column(Integer, default=1)
    exploration_skill_3_level = Column(Integer, default=1)
    expedition_skill_1_level = Column(Integer, default=1)
    expedition_skill_2_level = Column(Integer, default=1)
    expedition_skill_3_level = Column(Integer, default=1)

    # Hero gear - 4 slots with quality, level, and mastery
    # Quality: 0=None, 1=Gray, 2=Green, 3=Blue, 4=Purple, 5=Gold, 6=Legendary
    # Mastery: 0-20 (unlocks at gear level 20 for Gold+ quality)
    gear_slot1_quality = Column(Integer, default=0)
    gear_slot1_level = Column(Integer, default=0)
    gear_slot1_mastery = Column(Integer, default=0)
    gear_slot2_quality = Column(Integer, default=0)
    gear_slot2_level = Column(Integer, default=0)
    gear_slot2_mastery = Column(Integer, default=0)
    gear_slot3_quality = Column(Integer, default=0)
    gear_slot3_level = Column(Integer, default=0)
    gear_slot3_mastery = Column(Integer, default=0)
    gear_slot4_quality = Column(Integer, default=0)
    gear_slot4_level = Column(Integer, default=0)
    gear_slot4_mastery = Column(Integer, default=0)

    # Exclusive hero gear (like Dawnbreak, Eternal Guardian, etc.)
    mythic_gear_unlocked = Column(Boolean, default=False)
    mythic_gear_quality = Column(Integer, default=0)  # 1=Gray through 6=Legendary
    mythic_gear_level = Column(Integer, default=0)
    mythic_gear_mastery = Column(Integer, default=0)  # 0-20

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


class UserChiefGear(Base):
    """User's Chief Gear levels."""
    __tablename__ = 'user_chief_gear'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)

    # 6 Chief Gear slots - quality: 1=Gray, 2=Green, 3=Blue, 4=Purple, 5=Gold, 6=Legendary, 7=Mythic
    helmet_quality = Column(Integer, default=1)
    helmet_level = Column(Integer, default=1)
    armor_quality = Column(Integer, default=1)
    armor_level = Column(Integer, default=1)
    gloves_quality = Column(Integer, default=1)
    gloves_level = Column(Integer, default=1)
    boots_quality = Column(Integer, default=1)
    boots_level = Column(Integer, default=1)
    ring_quality = Column(Integer, default=1)
    ring_level = Column(Integer, default=1)
    amulet_quality = Column(Integer, default=1)
    amulet_level = Column(Integer, default=1)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    profile = relationship("UserProfile", backref="chief_gear")


class UserChiefCharm(Base):
    """User's Chief Charm levels - 18 charms total (6 gear pieces × 3 charm types)."""
    __tablename__ = 'user_chief_charms'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)

    # Cap charms (3 types) - levels 1-16
    cap_protection = Column(Integer, default=1)  # Infantry
    cap_keenness = Column(Integer, default=1)    # Lancer
    cap_vision = Column(Integer, default=1)      # Marksman

    # Watch charms (3 types)
    watch_protection = Column(Integer, default=1)
    watch_keenness = Column(Integer, default=1)
    watch_vision = Column(Integer, default=1)

    # Coat charms (3 types)
    coat_protection = Column(Integer, default=1)
    coat_keenness = Column(Integer, default=1)
    coat_vision = Column(Integer, default=1)

    # Pants charms (3 types)
    pants_protection = Column(Integer, default=1)
    pants_keenness = Column(Integer, default=1)
    pants_vision = Column(Integer, default=1)

    # Belt charms (3 types)
    belt_protection = Column(Integer, default=1)
    belt_keenness = Column(Integer, default=1)
    belt_vision = Column(Integer, default=1)

    # Weapon charms (3 types)
    weapon_protection = Column(Integer, default=1)
    weapon_keenness = Column(Integer, default=1)
    weapon_vision = Column(Integer, default=1)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    profile = relationship("UserProfile", backref="chief_charms")


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
