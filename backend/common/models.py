"""Pydantic v2 models for DynamoDB single-table design.

Replaces SQLAlchemy models with:
- DynamoDB entity models with to_dynamo() / from_dynamo() methods
- API request/response models for FastAPI contracts

Table Design:
- MainTable: User data, profiles, heroes, conversations, threads, notifications
- AdminTable: Feature flags, AI settings, audit logs, feedback, metrics
- ReferenceTable: Static hero and item data

ULID Generation:
Uses time-sortable ULIDs for all entity IDs. Falls back to a simple
timestamp+uuid implementation if the 'ulid' package is not installed.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator


# ---------------------------------------------------------------------------
# ULID helper
# ---------------------------------------------------------------------------

def generate_ulid() -> str:
    """Generate a ULID string (time-sortable unique ID)."""
    try:
        from ulid import ULID
        return str(ULID())
    except ImportError:
        # Fallback: timestamp prefix (ms hex) + random suffix
        ts = format(int(time.time() * 1000), "012x")
        rnd = uuid.uuid4().hex[:16]
        return f"{ts}{rnd}"


def utcnow_iso() -> str:
    """Return current UTC time as ISO-8601 string."""
    return datetime.utcnow().isoformat() + "Z"


def _strip_none(d: dict) -> dict:
    """Remove keys whose value is None from a dict (DynamoDB doesn't store None)."""
    return {k: v for k, v in d.items() if v is not None}


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class SpendingProfile(str, Enum):
    f2p = "f2p"
    minnow = "minnow"
    dolphin = "dolphin"
    orca = "orca"
    whale = "whale"


class PriorityFocus(str, Enum):
    svs_combat = "svs_combat"
    balanced_growth = "balanced_growth"
    economy_focus = "economy_focus"


class AllianceRole(str, Enum):
    rally_lead = "rally_lead"
    filler = "filler"
    farmer = "farmer"
    casual = "casual"


class AIMode(str, Enum):
    off = "off"
    on = "on"
    unlimited = "unlimited"


class AIProvider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"


class FeedbackCategory(str, Enum):
    bug = "bug"
    feature = "feature"
    data_error = "data_error"
    other = "other"


class FeedbackStatus(str, Enum):
    new = "new"
    pending_fix = "pending_fix"
    pending_update = "pending_update"
    completed = "completed"
    archive = "archive"


class AnnouncementType(str, Enum):
    info = "info"
    warning = "warning"
    success = "success"
    error = "error"


class DisplayType(str, Enum):
    banner = "banner"
    inbox = "inbox"
    both = "both"


class ErrorStatus(str, Enum):
    new = "new"
    reviewed = "reviewed"
    fixed = "fixed"
    ignored = "ignored"


class AIAccessLevel(str, Enum):
    off = "off"
    limited = "limited"
    unlimited = "unlimited"


class RoutedTo(str, Enum):
    rules = "rules"
    ai = "ai"
    hybrid = "hybrid"


class HeroClass(str, Enum):
    infantry = "Infantry"
    marksman = "Marksman"
    lancer = "Lancer"


class Rarity(str, Enum):
    epic = "Epic"
    legendary = "Legendary"


class TierRating(str, Enum):
    s_plus = "S+"
    s = "S"
    a = "A"
    b = "B"
    c = "C"
    d = "D"


# ===================================================================
# BASE DYNAMO MODEL
# ===================================================================

class DynamoBase(BaseModel):
    """Base for all DynamoDB entity models."""

    model_config = {"populate_by_name": True, "use_enum_values": True}

    # Subclasses define entity_type for GSI queries
    entity_type: str = ""

    def _base_item(self) -> dict:
        """Shared fields appended to every DynamoDB item."""
        return {"entity_type": self.entity_type}


# ===================================================================
# MAIN TABLE ENTITIES
# ===================================================================

# -------------------------------------------------------------------
# User  (PK=USER#<cognito_sub>  SK=METADATA)
# -------------------------------------------------------------------

class UserEntity(DynamoBase):
    """User account stored in MainTable."""

    entity_type: str = "User"

    cognito_sub: str
    username: str
    email: str
    role: UserRole = UserRole.user
    theme: str = "dark"

    is_active: bool = True
    is_verified: bool = False
    is_test_account: bool = False

    # AI rate limiting
    ai_requests_today: int = 0
    ai_request_reset_date: Optional[str] = None
    last_ai_request: Optional[str] = None
    ai_access_level: AIAccessLevel = AIAccessLevel.limited
    ai_daily_limit: Optional[int] = None

    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)
    last_login: Optional[str] = None
    deleted_at: Optional[str] = None

    # GSI attributes
    # GSI1: email -> user lookup  (GSI1PK=EMAIL#<email>, GSI1SK=USER)
    # GSI2: username -> user lookup (GSI2PK=USERNAME#<username>, GSI2SK=USER)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"USER#{self.cognito_sub}",
            "SK": "METADATA",
            "entity_type": self.entity_type,
            "cognito_sub": self.cognito_sub,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "theme": self.theme,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_test_account": self.is_test_account,
            "ai_requests_today": self.ai_requests_today,
            "ai_request_reset_date": self.ai_request_reset_date,
            "last_ai_request": self.last_ai_request,
            "ai_access_level": self.ai_access_level,
            "ai_daily_limit": self.ai_daily_limit,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login,
            "deleted_at": self.deleted_at,
            # GSI keys for email/username lookups
            "GSI1PK": f"EMAIL#{self.email}",
            "GSI1SK": "USER",
            "GSI2PK": f"USERNAME#{self.username}",
            "GSI2SK": "USER",
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> UserEntity:
        return cls(
            cognito_sub=item["cognito_sub"],
            username=item["username"],
            email=item["email"],
            role=item.get("role", "user"),
            theme=item.get("theme", "dark"),
            is_active=item.get("is_active", True),
            is_verified=item.get("is_verified", False),
            is_test_account=item.get("is_test_account", False),
            ai_requests_today=item.get("ai_requests_today", 0),
            ai_request_reset_date=item.get("ai_request_reset_date"),
            last_ai_request=item.get("last_ai_request"),
            ai_access_level=item.get("ai_access_level", "limited"),
            ai_daily_limit=item.get("ai_daily_limit"),
            created_at=item.get("created_at", utcnow_iso()),
            updated_at=item.get("updated_at", utcnow_iso()),
            last_login=item.get("last_login"),
            deleted_at=item.get("deleted_at"),
        )


# -------------------------------------------------------------------
# Uniqueness Guard  (PK=UNIQUE#EMAIL / UNIQUE#USERNAME  SK=<value>)
# -------------------------------------------------------------------

class UniquenessGuard(DynamoBase):
    """Ensures email/username uniqueness via conditional writes."""

    entity_type: str = "UniquenessGuard"

    guard_type: str  # "EMAIL" or "USERNAME"
    value: str       # the email or username
    cognito_sub: str  # which user owns it

    def to_dynamo(self) -> dict:
        return {
            "PK": f"UNIQUE#{self.guard_type}",
            "SK": self.value,
            "entity_type": self.entity_type,
            "cognito_sub": self.cognito_sub,
        }

    @classmethod
    def from_dynamo(cls, item: dict) -> UniquenessGuard:
        pk = item["PK"]  # UNIQUE#EMAIL or UNIQUE#USERNAME
        guard_type = pk.split("#", 1)[1]
        return cls(
            guard_type=guard_type,
            value=item["SK"],
            cognito_sub=item["cognito_sub"],
        )


# -------------------------------------------------------------------
# UserProfile  (PK=USER#<cognito_sub>  SK=PROFILE#<ulid>)
# -------------------------------------------------------------------

class UserProfileEntity(DynamoBase):
    """User's game profile."""

    entity_type: str = "UserProfile"

    profile_id: str = Field(default_factory=generate_ulid)
    cognito_sub: str  # owner
    name: str = "Chief"
    is_default: bool = False
    state_number: Optional[int] = None
    server_age_days: int = 0
    furnace_level: int = 1
    furnace_fc_level: Optional[str] = None

    spending_profile: SpendingProfile = SpendingProfile.f2p
    priority_focus: PriorityFocus = PriorityFocus.balanced_growth
    alliance_role: AllianceRole = AllianceRole.filler

    priority_pvp_attack: int = Field(default=5, ge=1, le=5)
    priority_defense: int = Field(default=4, ge=1, le=5)
    priority_pve: int = Field(default=3, ge=1, le=5)
    priority_economy: int = Field(default=2, ge=1, le=5)

    last_svs_date: Optional[str] = None
    svs_wins: int = 0
    svs_losses: int = 0

    is_farm_account: bool = False
    linked_main_profile_id: Optional[str] = None

    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)
    deleted_at: Optional[str] = None

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"USER#{self.cognito_sub}",
            "SK": f"PROFILE#{self.profile_id}",
            "entity_type": self.entity_type,
            "profile_id": self.profile_id,
            "cognito_sub": self.cognito_sub,
            "name": self.name,
            "is_default": self.is_default,
            "state_number": self.state_number,
            "server_age_days": self.server_age_days,
            "furnace_level": self.furnace_level,
            "furnace_fc_level": self.furnace_fc_level,
            "spending_profile": self.spending_profile,
            "priority_focus": self.priority_focus,
            "alliance_role": self.alliance_role,
            "priority_pvp_attack": self.priority_pvp_attack,
            "priority_defense": self.priority_defense,
            "priority_pve": self.priority_pve,
            "priority_economy": self.priority_economy,
            "last_svs_date": self.last_svs_date,
            "svs_wins": self.svs_wins,
            "svs_losses": self.svs_losses,
            "is_farm_account": self.is_farm_account,
            "linked_main_profile_id": self.linked_main_profile_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at,
            # GSI: lookup profiles by user
            "GSI1PK": f"USER#{self.cognito_sub}",
            "GSI1SK": f"PROFILE#{self.created_at}",
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> UserProfileEntity:
        return cls(
            profile_id=item["SK"].split("#", 1)[1],
            cognito_sub=item.get("cognito_sub", item["PK"].split("#", 1)[1]),
            name=item.get("name", "Chief"),
            is_default=item.get("is_default", False),
            state_number=item.get("state_number"),
            server_age_days=item.get("server_age_days", 0),
            furnace_level=item.get("furnace_level", 1),
            furnace_fc_level=item.get("furnace_fc_level"),
            spending_profile=item.get("spending_profile", "f2p"),
            priority_focus=item.get("priority_focus", "balanced_growth"),
            alliance_role=item.get("alliance_role", "filler"),
            priority_pvp_attack=item.get("priority_pvp_attack", 5),
            priority_defense=item.get("priority_defense", 4),
            priority_pve=item.get("priority_pve", 3),
            priority_economy=item.get("priority_economy", 2),
            last_svs_date=item.get("last_svs_date"),
            svs_wins=item.get("svs_wins", 0),
            svs_losses=item.get("svs_losses", 0),
            is_farm_account=item.get("is_farm_account", False),
            linked_main_profile_id=item.get("linked_main_profile_id"),
            created_at=item.get("created_at", utcnow_iso()),
            updated_at=item.get("updated_at", utcnow_iso()),
            deleted_at=item.get("deleted_at"),
        )


# -------------------------------------------------------------------
# UserHero  (PK=PROFILE#<ulid>  SK=HERO#<hero_name>)
# -------------------------------------------------------------------

class UserHeroEntity(DynamoBase):
    """User's owned hero with progression data."""

    entity_type: str = "UserHero"

    profile_id: str
    hero_name: str

    level: int = Field(default=1, ge=1, le=80)
    stars: int = Field(default=0, ge=0, le=5)
    ascension_tier: int = Field(default=0, ge=0, le=5)

    # Skill levels (1-5)
    exploration_skill_1_level: int = Field(default=1, ge=1, le=5)
    exploration_skill_2_level: int = Field(default=1, ge=1, le=5)
    exploration_skill_3_level: int = Field(default=1, ge=1, le=5)
    expedition_skill_1_level: int = Field(default=1, ge=1, le=5)
    expedition_skill_2_level: int = Field(default=1, ge=1, le=5)
    expedition_skill_3_level: int = Field(default=1, ge=1, le=5)

    # Hero gear - 4 slots (quality 0-7, level 0-100, mastery 0-20)
    gear_slot1_quality: int = Field(default=0, ge=0, le=7)
    gear_slot1_level: int = Field(default=0, ge=0, le=100)
    gear_slot1_mastery: int = Field(default=0, ge=0, le=20)
    gear_slot2_quality: int = Field(default=0, ge=0, le=7)
    gear_slot2_level: int = Field(default=0, ge=0, le=100)
    gear_slot2_mastery: int = Field(default=0, ge=0, le=20)
    gear_slot3_quality: int = Field(default=0, ge=0, le=7)
    gear_slot3_level: int = Field(default=0, ge=0, le=100)
    gear_slot3_mastery: int = Field(default=0, ge=0, le=20)
    gear_slot4_quality: int = Field(default=0, ge=0, le=7)
    gear_slot4_level: int = Field(default=0, ge=0, le=100)
    gear_slot4_mastery: int = Field(default=0, ge=0, le=20)

    # Exclusive/mythic gear
    mythic_gear_unlocked: bool = False
    mythic_gear_quality: int = Field(default=0, ge=0, le=7)
    mythic_gear_level: int = Field(default=0, ge=0, le=100)
    mythic_gear_mastery: int = Field(default=0, ge=0, le=20)
    exclusive_gear_skill_level: int = Field(default=0, ge=0, le=10)

    owned: bool = True
    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"PROFILE#{self.profile_id}",
            "SK": f"HERO#{self.hero_name}",
            "entity_type": self.entity_type,
            "profile_id": self.profile_id,
            "hero_name": self.hero_name,
            "level": self.level,
            "stars": self.stars,
            "ascension_tier": self.ascension_tier,
            "exploration_skill_1_level": self.exploration_skill_1_level,
            "exploration_skill_2_level": self.exploration_skill_2_level,
            "exploration_skill_3_level": self.exploration_skill_3_level,
            "expedition_skill_1_level": self.expedition_skill_1_level,
            "expedition_skill_2_level": self.expedition_skill_2_level,
            "expedition_skill_3_level": self.expedition_skill_3_level,
            "gear_slot1_quality": self.gear_slot1_quality,
            "gear_slot1_level": self.gear_slot1_level,
            "gear_slot1_mastery": self.gear_slot1_mastery,
            "gear_slot2_quality": self.gear_slot2_quality,
            "gear_slot2_level": self.gear_slot2_level,
            "gear_slot2_mastery": self.gear_slot2_mastery,
            "gear_slot3_quality": self.gear_slot3_quality,
            "gear_slot3_level": self.gear_slot3_level,
            "gear_slot3_mastery": self.gear_slot3_mastery,
            "gear_slot4_quality": self.gear_slot4_quality,
            "gear_slot4_level": self.gear_slot4_level,
            "gear_slot4_mastery": self.gear_slot4_mastery,
            "mythic_gear_unlocked": self.mythic_gear_unlocked,
            "mythic_gear_quality": self.mythic_gear_quality,
            "mythic_gear_level": self.mythic_gear_level,
            "mythic_gear_mastery": self.mythic_gear_mastery,
            "exclusive_gear_skill_level": self.exclusive_gear_skill_level,
            "owned": self.owned,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> UserHeroEntity:
        return cls(
            profile_id=item["PK"].split("#", 1)[1],
            hero_name=item["SK"].split("#", 1)[1],
            level=item.get("level", 1),
            stars=item.get("stars", 0),
            ascension_tier=item.get("ascension_tier", 0),
            exploration_skill_1_level=item.get("exploration_skill_1_level", 1),
            exploration_skill_2_level=item.get("exploration_skill_2_level", 1),
            exploration_skill_3_level=item.get("exploration_skill_3_level", 1),
            expedition_skill_1_level=item.get("expedition_skill_1_level", 1),
            expedition_skill_2_level=item.get("expedition_skill_2_level", 1),
            expedition_skill_3_level=item.get("expedition_skill_3_level", 1),
            gear_slot1_quality=item.get("gear_slot1_quality", 0),
            gear_slot1_level=item.get("gear_slot1_level", 0),
            gear_slot1_mastery=item.get("gear_slot1_mastery", 0),
            gear_slot2_quality=item.get("gear_slot2_quality", 0),
            gear_slot2_level=item.get("gear_slot2_level", 0),
            gear_slot2_mastery=item.get("gear_slot2_mastery", 0),
            gear_slot3_quality=item.get("gear_slot3_quality", 0),
            gear_slot3_level=item.get("gear_slot3_level", 0),
            gear_slot3_mastery=item.get("gear_slot3_mastery", 0),
            gear_slot4_quality=item.get("gear_slot4_quality", 0),
            gear_slot4_level=item.get("gear_slot4_level", 0),
            gear_slot4_mastery=item.get("gear_slot4_mastery", 0),
            mythic_gear_unlocked=item.get("mythic_gear_unlocked", False),
            mythic_gear_quality=item.get("mythic_gear_quality", 0),
            mythic_gear_level=item.get("mythic_gear_level", 0),
            mythic_gear_mastery=item.get("mythic_gear_mastery", 0),
            exclusive_gear_skill_level=item.get("exclusive_gear_skill_level", 0),
            owned=item.get("owned", True),
            created_at=item.get("created_at", utcnow_iso()),
            updated_at=item.get("updated_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# ChiefGear  (PK=PROFILE#<ulid>  SK=CHIEFGEAR)
# -------------------------------------------------------------------

class ChiefGearEntity(DynamoBase):
    """User's Chief Gear levels (6 slots)."""

    entity_type: str = "ChiefGear"

    profile_id: str

    # Quality: 1=Gray, 2=Green, 3=Blue, 4=Purple, 5=Gold, 6=Legendary, 7=Mythic
    helmet_quality: int = Field(default=1, ge=0, le=7)
    helmet_level: int = Field(default=1, ge=0, le=100)
    armor_quality: int = Field(default=1, ge=0, le=7)
    armor_level: int = Field(default=1, ge=0, le=100)
    gloves_quality: int = Field(default=1, ge=0, le=7)
    gloves_level: int = Field(default=1, ge=0, le=100)
    boots_quality: int = Field(default=1, ge=0, le=7)
    boots_level: int = Field(default=1, ge=0, le=100)
    ring_quality: int = Field(default=1, ge=0, le=7)
    ring_level: int = Field(default=1, ge=0, le=100)
    amulet_quality: int = Field(default=1, ge=0, le=7)
    amulet_level: int = Field(default=1, ge=0, le=100)

    updated_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"PROFILE#{self.profile_id}",
            "SK": "CHIEFGEAR",
            "entity_type": self.entity_type,
            "profile_id": self.profile_id,
            "helmet_quality": self.helmet_quality,
            "helmet_level": self.helmet_level,
            "armor_quality": self.armor_quality,
            "armor_level": self.armor_level,
            "gloves_quality": self.gloves_quality,
            "gloves_level": self.gloves_level,
            "boots_quality": self.boots_quality,
            "boots_level": self.boots_level,
            "ring_quality": self.ring_quality,
            "ring_level": self.ring_level,
            "amulet_quality": self.amulet_quality,
            "amulet_level": self.amulet_level,
            "updated_at": self.updated_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> ChiefGearEntity:
        return cls(
            profile_id=item["PK"].split("#", 1)[1],
            helmet_quality=item.get("helmet_quality", 1),
            helmet_level=item.get("helmet_level", 1),
            armor_quality=item.get("armor_quality", 1),
            armor_level=item.get("armor_level", 1),
            gloves_quality=item.get("gloves_quality", 1),
            gloves_level=item.get("gloves_level", 1),
            boots_quality=item.get("boots_quality", 1),
            boots_level=item.get("boots_level", 1),
            ring_quality=item.get("ring_quality", 1),
            ring_level=item.get("ring_level", 1),
            amulet_quality=item.get("amulet_quality", 1),
            amulet_level=item.get("amulet_level", 1),
            updated_at=item.get("updated_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# ChiefCharm  (PK=PROFILE#<ulid>  SK=CHIEFCHARM)
# -------------------------------------------------------------------

class ChiefCharmEntity(DynamoBase):
    """User's Chief Charm levels (18 slots = 6 gear pieces x 3 slots).

    Levels stored as strings to support sub-level format (e.g. "4-1", "4-2").
    """

    entity_type: str = "ChiefCharm"

    profile_id: str

    # Cap charms - Keenness (Lancer)
    cap_slot_1: str = "1"
    cap_slot_2: str = "1"
    cap_slot_3: str = "1"

    # Watch charms - Keenness (Lancer)
    watch_slot_1: str = "1"
    watch_slot_2: str = "1"
    watch_slot_3: str = "1"

    # Coat charms - Protection (Infantry)
    coat_slot_1: str = "1"
    coat_slot_2: str = "1"
    coat_slot_3: str = "1"

    # Pants charms - Protection (Infantry)
    pants_slot_1: str = "1"
    pants_slot_2: str = "1"
    pants_slot_3: str = "1"

    # Belt charms - Vision (Marksman)
    belt_slot_1: str = "1"
    belt_slot_2: str = "1"
    belt_slot_3: str = "1"

    # Weapon charms - Vision (Marksman)
    weapon_slot_1: str = "1"
    weapon_slot_2: str = "1"
    weapon_slot_3: str = "1"

    updated_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"PROFILE#{self.profile_id}",
            "SK": "CHIEFCHARM",
            "entity_type": self.entity_type,
            "profile_id": self.profile_id,
            "cap_slot_1": self.cap_slot_1,
            "cap_slot_2": self.cap_slot_2,
            "cap_slot_3": self.cap_slot_3,
            "watch_slot_1": self.watch_slot_1,
            "watch_slot_2": self.watch_slot_2,
            "watch_slot_3": self.watch_slot_3,
            "coat_slot_1": self.coat_slot_1,
            "coat_slot_2": self.coat_slot_2,
            "coat_slot_3": self.coat_slot_3,
            "pants_slot_1": self.pants_slot_1,
            "pants_slot_2": self.pants_slot_2,
            "pants_slot_3": self.pants_slot_3,
            "belt_slot_1": self.belt_slot_1,
            "belt_slot_2": self.belt_slot_2,
            "belt_slot_3": self.belt_slot_3,
            "weapon_slot_1": self.weapon_slot_1,
            "weapon_slot_2": self.weapon_slot_2,
            "weapon_slot_3": self.weapon_slot_3,
            "updated_at": self.updated_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> ChiefCharmEntity:
        return cls(
            profile_id=item["PK"].split("#", 1)[1],
            cap_slot_1=item.get("cap_slot_1", "1"),
            cap_slot_2=item.get("cap_slot_2", "1"),
            cap_slot_3=item.get("cap_slot_3", "1"),
            watch_slot_1=item.get("watch_slot_1", "1"),
            watch_slot_2=item.get("watch_slot_2", "1"),
            watch_slot_3=item.get("watch_slot_3", "1"),
            coat_slot_1=item.get("coat_slot_1", "1"),
            coat_slot_2=item.get("coat_slot_2", "1"),
            coat_slot_3=item.get("coat_slot_3", "1"),
            pants_slot_1=item.get("pants_slot_1", "1"),
            pants_slot_2=item.get("pants_slot_2", "1"),
            pants_slot_3=item.get("pants_slot_3", "1"),
            belt_slot_1=item.get("belt_slot_1", "1"),
            belt_slot_2=item.get("belt_slot_2", "1"),
            belt_slot_3=item.get("belt_slot_3", "1"),
            weapon_slot_1=item.get("weapon_slot_1", "1"),
            weapon_slot_2=item.get("weapon_slot_2", "1"),
            weapon_slot_3=item.get("weapon_slot_3", "1"),
            updated_at=item.get("updated_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# Inventory  (PK=PROFILE#<ulid>  SK=INV#<item_name>)
# -------------------------------------------------------------------

class InventoryEntity(DynamoBase):
    """User's backpack item quantity."""

    entity_type: str = "Inventory"

    profile_id: str
    item_name: str
    quantity: int = 0
    updated_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"PROFILE#{self.profile_id}",
            "SK": f"INV#{self.item_name}",
            "entity_type": self.entity_type,
            "profile_id": self.profile_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "updated_at": self.updated_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> InventoryEntity:
        return cls(
            profile_id=item["PK"].split("#", 1)[1],
            item_name=item["SK"].split("#", 1)[1],
            quantity=item.get("quantity", 0),
            updated_at=item.get("updated_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# AIConversation  (PK=USER#<cognito_sub>  SK=AICONV#<timestamp>#<ulid>)
# -------------------------------------------------------------------

class AIConversationEntity(DynamoBase):
    """AI conversation log entry."""

    entity_type: str = "AIConversation"

    conversation_id: str = Field(default_factory=generate_ulid)
    cognito_sub: str
    profile_id: Optional[str] = None

    question: str
    answer: str
    context_summary: Optional[str] = None
    user_snapshot: Optional[str] = None  # JSON blob

    provider: str  # openai, anthropic, rules
    model: str
    tokens_input: Optional[int] = None
    tokens_output: Optional[int] = None
    response_time_ms: Optional[int] = None

    routed_to: Optional[str] = None  # rules, ai, hybrid
    rule_ids_matched: Optional[str] = None

    rating: Optional[int] = Field(default=None, ge=1, le=5)
    is_helpful: Optional[bool] = None
    user_feedback: Optional[str] = None

    is_good_example: bool = False
    is_bad_example: bool = False
    admin_notes: Optional[str] = None

    source_page: Optional[str] = None
    question_type: Optional[str] = None
    is_favorite: bool = False

    thread_id: Optional[str] = None
    thread_title: Optional[str] = None

    created_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"USER#{self.cognito_sub}",
            "SK": f"AICONV#{self.created_at}#{self.conversation_id}",
            "entity_type": self.entity_type,
            "conversation_id": self.conversation_id,
            "cognito_sub": self.cognito_sub,
            "profile_id": self.profile_id,
            "question": self.question,
            "answer": self.answer,
            "context_summary": self.context_summary,
            "user_snapshot": self.user_snapshot,
            "provider": self.provider,
            "model": self.model,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "response_time_ms": self.response_time_ms,
            "routed_to": self.routed_to,
            "rule_ids_matched": self.rule_ids_matched,
            "rating": self.rating,
            "is_helpful": self.is_helpful,
            "user_feedback": self.user_feedback,
            "is_good_example": self.is_good_example,
            "is_bad_example": self.is_bad_example,
            "admin_notes": self.admin_notes,
            "source_page": self.source_page,
            "question_type": self.question_type,
            "is_favorite": self.is_favorite,
            "thread_id": self.thread_id,
            "thread_title": self.thread_title,
            "created_at": self.created_at,
            # GSI for admin browsing all conversations by date
            "GSI1PK": "AICONV",
            "GSI1SK": self.created_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> AIConversationEntity:
        # SK = AICONV#<timestamp>#<ulid>
        sk_parts = item["SK"].split("#", 2)
        conv_id = sk_parts[2] if len(sk_parts) > 2 else generate_ulid()
        return cls(
            conversation_id=item.get("conversation_id", conv_id),
            cognito_sub=item["PK"].split("#", 1)[1],
            profile_id=item.get("profile_id"),
            question=item["question"],
            answer=item["answer"],
            context_summary=item.get("context_summary"),
            user_snapshot=item.get("user_snapshot"),
            provider=item.get("provider", "unknown"),
            model=item.get("model", "unknown"),
            tokens_input=item.get("tokens_input"),
            tokens_output=item.get("tokens_output"),
            response_time_ms=item.get("response_time_ms"),
            routed_to=item.get("routed_to"),
            rule_ids_matched=item.get("rule_ids_matched"),
            rating=item.get("rating"),
            is_helpful=item.get("is_helpful"),
            user_feedback=item.get("user_feedback"),
            is_good_example=item.get("is_good_example", False),
            is_bad_example=item.get("is_bad_example", False),
            admin_notes=item.get("admin_notes"),
            source_page=item.get("source_page"),
            question_type=item.get("question_type"),
            is_favorite=item.get("is_favorite", False),
            thread_id=item.get("thread_id"),
            thread_title=item.get("thread_title"),
            created_at=item.get("created_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# MessageThread  (PK=USER#<cognito_sub>  SK=THREAD#<ulid>)
# -------------------------------------------------------------------

class MessageThreadEntity(DynamoBase):
    """Conversation container for admin-to-user messaging."""

    entity_type: str = "MessageThread"

    thread_id: str = Field(default_factory=generate_ulid)
    cognito_sub: str  # user who owns the thread
    subject: str
    is_closed: bool = False

    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"USER#{self.cognito_sub}",
            "SK": f"THREAD#{self.thread_id}",
            "entity_type": self.entity_type,
            "thread_id": self.thread_id,
            "cognito_sub": self.cognito_sub,
            "subject": self.subject,
            "is_closed": self.is_closed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            # GSI for admin to browse all open threads
            "GSI1PK": "THREAD",
            "GSI1SK": self.updated_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> MessageThreadEntity:
        return cls(
            thread_id=item["SK"].split("#", 1)[1],
            cognito_sub=item["PK"].split("#", 1)[1],
            subject=item.get("subject", ""),
            is_closed=item.get("is_closed", False),
            created_at=item.get("created_at", utcnow_iso()),
            updated_at=item.get("updated_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# Message  (PK=THREAD#<ulid>  SK=MSG#<timestamp>#<ulid>)
# -------------------------------------------------------------------

class MessageEntity(DynamoBase):
    """Individual message within a conversation thread."""

    entity_type: str = "Message"

    message_id: str = Field(default_factory=generate_ulid)
    thread_id: str
    sender_sub: str  # cognito_sub of sender
    content: str
    is_from_admin: bool = False
    is_read: bool = False
    read_at: Optional[str] = None

    created_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"THREAD#{self.thread_id}",
            "SK": f"MSG#{self.created_at}#{self.message_id}",
            "entity_type": self.entity_type,
            "message_id": self.message_id,
            "thread_id": self.thread_id,
            "sender_sub": self.sender_sub,
            "content": self.content,
            "is_from_admin": self.is_from_admin,
            "is_read": self.is_read,
            "read_at": self.read_at,
            "created_at": self.created_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> MessageEntity:
        sk_parts = item["SK"].split("#", 2)
        msg_id = sk_parts[2] if len(sk_parts) > 2 else generate_ulid()
        return cls(
            message_id=item.get("message_id", msg_id),
            thread_id=item["PK"].split("#", 1)[1],
            sender_sub=item.get("sender_sub", ""),
            content=item.get("content", ""),
            is_from_admin=item.get("is_from_admin", False),
            is_read=item.get("is_read", False),
            read_at=item.get("read_at"),
            created_at=item.get("created_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# Notification  (PK=USER#<cognito_sub>  SK=NOTIF#<announcement_ulid>)
# -------------------------------------------------------------------

class NotificationEntity(DynamoBase):
    """Per-user delivery of an announcement."""

    entity_type: str = "Notification"

    cognito_sub: str
    announcement_id: str  # ULID of the announcement

    is_read: bool = False
    read_at: Optional[str] = None
    created_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"USER#{self.cognito_sub}",
            "SK": f"NOTIF#{self.announcement_id}",
            "entity_type": self.entity_type,
            "cognito_sub": self.cognito_sub,
            "announcement_id": self.announcement_id,
            "is_read": self.is_read,
            "read_at": self.read_at,
            "created_at": self.created_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> NotificationEntity:
        return cls(
            cognito_sub=item["PK"].split("#", 1)[1],
            announcement_id=item["SK"].split("#", 1)[1],
            is_read=item.get("is_read", False),
            read_at=item.get("read_at"),
            created_at=item.get("created_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# DailyLogin  (PK=USER#<cognito_sub>  SK=LOGIN#<date>)
# -------------------------------------------------------------------

class DailyLoginEntity(DynamoBase):
    """Track daily login for analytics."""

    entity_type: str = "DailyLogin"

    cognito_sub: str
    login_date: str  # YYYY-MM-DD
    created_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        return {
            "PK": f"USER#{self.cognito_sub}",
            "SK": f"LOGIN#{self.login_date}",
            "entity_type": self.entity_type,
            "cognito_sub": self.cognito_sub,
            "login_date": self.login_date,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dynamo(cls, item: dict) -> DailyLoginEntity:
        return cls(
            cognito_sub=item["PK"].split("#", 1)[1],
            login_date=item["SK"].split("#", 1)[1],
            created_at=item.get("created_at", utcnow_iso()),
        )


# ===================================================================
# ADMIN TABLE ENTITIES
# ===================================================================

# -------------------------------------------------------------------
# FeatureFlag  (PK=FLAG  SK=<flag_name>)
# -------------------------------------------------------------------

class FeatureFlagEntity(DynamoBase):
    """Feature flag for controlling app features."""

    entity_type: str = "FeatureFlag"

    name: str
    description: Optional[str] = None
    is_enabled: bool = False
    value: Optional[str] = None  # For multi-state flags

    enabled_for_roles: Optional[list[str]] = None
    enabled_for_users: Optional[list[str]] = None  # cognito_subs

    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": "FLAG",
            "SK": self.name,
            "entity_type": self.entity_type,
            "name": self.name,
            "description": self.description,
            "is_enabled": self.is_enabled,
            "value": self.value,
            "enabled_for_roles": self.enabled_for_roles,
            "enabled_for_users": self.enabled_for_users,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> FeatureFlagEntity:
        return cls(
            name=item["SK"],
            description=item.get("description"),
            is_enabled=item.get("is_enabled", False),
            value=item.get("value"),
            enabled_for_roles=item.get("enabled_for_roles"),
            enabled_for_users=item.get("enabled_for_users"),
            created_at=item.get("created_at", utcnow_iso()),
            updated_at=item.get("updated_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# AISettings  (PK=SETTINGS  SK=AI)
# -------------------------------------------------------------------

class AISettingsEntity(DynamoBase):
    """Global AI settings (singleton)."""

    entity_type: str = "AISettings"

    mode: AIMode = AIMode.off

    daily_limit_free: int = 20
    daily_limit_admin: int = 1000
    cooldown_seconds: int = 30

    primary_provider: AIProvider = AIProvider.openai
    fallback_provider: Optional[str] = None

    openai_model: str = "gpt-4o-mini"
    anthropic_model: str = "claude-sonnet-4-20250514"

    total_requests: int = 0
    total_tokens_used: int = 0

    updated_at: str = Field(default_factory=utcnow_iso)
    updated_by: Optional[str] = None  # cognito_sub

    def to_dynamo(self) -> dict:
        item = {
            "PK": "SETTINGS",
            "SK": "AI",
            "entity_type": self.entity_type,
            "mode": self.mode,
            "daily_limit_free": self.daily_limit_free,
            "daily_limit_admin": self.daily_limit_admin,
            "cooldown_seconds": self.cooldown_seconds,
            "primary_provider": self.primary_provider,
            "fallback_provider": self.fallback_provider,
            "openai_model": self.openai_model,
            "anthropic_model": self.anthropic_model,
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> AISettingsEntity:
        return cls(
            mode=item.get("mode", "off"),
            daily_limit_free=item.get("daily_limit_free", 20),
            daily_limit_admin=item.get("daily_limit_admin", 1000),
            cooldown_seconds=item.get("cooldown_seconds", 30),
            primary_provider=item.get("primary_provider", "openai"),
            fallback_provider=item.get("fallback_provider"),
            openai_model=item.get("openai_model", "gpt-4o-mini"),
            anthropic_model=item.get("anthropic_model", "claude-sonnet-4-20250514"),
            total_requests=item.get("total_requests", 0),
            total_tokens_used=item.get("total_tokens_used", 0),
            updated_at=item.get("updated_at", utcnow_iso()),
            updated_by=item.get("updated_by"),
        )


# -------------------------------------------------------------------
# AuditLog  (PK=AUDIT#<yyyy-mm>  SK=<timestamp>#<ulid>)
# -------------------------------------------------------------------

class AuditLogEntity(DynamoBase):
    """Admin action audit trail."""

    entity_type: str = "AuditLog"

    audit_id: str = Field(default_factory=generate_ulid)
    admin_sub: str  # cognito_sub of admin
    admin_username: str

    action: str  # user_created, user_deleted, password_reset, etc.
    target_type: Optional[str] = None  # user, system, etc.
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    details: Optional[str] = None

    created_at: str = Field(default_factory=utcnow_iso)

    def _partition_month(self) -> str:
        """Extract yyyy-mm from created_at for partition key."""
        return self.created_at[:7]  # "2026-01"

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"AUDIT#{self._partition_month()}",
            "SK": f"{self.created_at}#{self.audit_id}",
            "entity_type": self.entity_type,
            "audit_id": self.audit_id,
            "admin_sub": self.admin_sub,
            "admin_username": self.admin_username,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_name": self.target_name,
            "details": self.details,
            "created_at": self.created_at,
            # GSI for browsing all audit logs by date
            "GSI1PK": "AUDIT",
            "GSI1SK": self.created_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> AuditLogEntity:
        sk_parts = item["SK"].rsplit("#", 1)
        audit_id = sk_parts[1] if len(sk_parts) > 1 else generate_ulid()
        return cls(
            audit_id=item.get("audit_id", audit_id),
            admin_sub=item.get("admin_sub", ""),
            admin_username=item.get("admin_username", ""),
            action=item.get("action", ""),
            target_type=item.get("target_type"),
            target_id=item.get("target_id"),
            target_name=item.get("target_name"),
            details=item.get("details"),
            created_at=item.get("created_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# ErrorLog  (PK=ERROR#<yyyy-mm>  SK=<timestamp>#<ulid>)
# -------------------------------------------------------------------

class ErrorLogEntity(DynamoBase):
    """Application error log entry."""

    entity_type: str = "ErrorLog"

    error_id: str = Field(default_factory=generate_ulid)

    error_type: str
    error_message: str
    stack_trace: Optional[str] = None

    page: Optional[str] = None
    function: Optional[str] = None
    user_sub: Optional[str] = None  # cognito_sub
    profile_id: Optional[str] = None

    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    extra_context: Optional[dict[str, Any]] = None

    environment: Optional[str] = None  # production, staging, development

    status: ErrorStatus = ErrorStatus.new
    reviewed_by: Optional[str] = None  # cognito_sub
    reviewed_at: Optional[str] = None
    fix_notes: Optional[str] = None
    email_sent: bool = False

    created_at: str = Field(default_factory=utcnow_iso)

    def _partition_month(self) -> str:
        return self.created_at[:7]

    def to_dynamo(self) -> dict:
        item = {
            "PK": f"ERROR#{self._partition_month()}",
            "SK": f"{self.created_at}#{self.error_id}",
            "entity_type": self.entity_type,
            "error_id": self.error_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "page": self.page,
            "function": self.function,
            "user_sub": self.user_sub,
            "profile_id": self.profile_id,
            "session_id": self.session_id,
            "user_agent": self.user_agent,
            "extra_context": self.extra_context,
            "environment": self.environment,
            "status": self.status,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "fix_notes": self.fix_notes,
            "email_sent": self.email_sent,
            "created_at": self.created_at,
            # GSI for browsing errors by status
            "GSI1PK": f"ERROR#{self.status}",
            "GSI1SK": self.created_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> ErrorLogEntity:
        sk_parts = item["SK"].rsplit("#", 1)
        error_id = sk_parts[1] if len(sk_parts) > 1 else generate_ulid()
        return cls(
            error_id=item.get("error_id", error_id),
            error_type=item.get("error_type", "Unknown"),
            error_message=item.get("error_message", ""),
            stack_trace=item.get("stack_trace"),
            page=item.get("page"),
            function=item.get("function"),
            user_sub=item.get("user_sub"),
            profile_id=item.get("profile_id"),
            session_id=item.get("session_id"),
            user_agent=item.get("user_agent"),
            extra_context=item.get("extra_context"),
            environment=item.get("environment"),
            status=item.get("status", "new"),
            reviewed_by=item.get("reviewed_by"),
            reviewed_at=item.get("reviewed_at"),
            fix_notes=item.get("fix_notes"),
            email_sent=item.get("email_sent", False),
            created_at=item.get("created_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# Feedback  (PK=FEEDBACK  SK=<timestamp>#<ulid>)
# -------------------------------------------------------------------

class FeedbackEntity(DynamoBase):
    """User feedback entry."""

    entity_type: str = "Feedback"

    feedback_id: str = Field(default_factory=generate_ulid)
    user_sub: Optional[str] = None  # cognito_sub, nullable for anonymous

    category: FeedbackCategory
    page: Optional[str] = None
    description: str

    status: FeedbackStatus = FeedbackStatus.new
    created_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": "FEEDBACK",
            "SK": f"{self.created_at}#{self.feedback_id}",
            "entity_type": self.entity_type,
            "feedback_id": self.feedback_id,
            "user_sub": self.user_sub,
            "category": self.category,
            "page": self.page,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            # GSI for filtering by status
            "GSI1PK": f"FEEDBACK#{self.status}",
            "GSI1SK": self.created_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> FeedbackEntity:
        sk_parts = item["SK"].rsplit("#", 1)
        fb_id = sk_parts[1] if len(sk_parts) > 1 else generate_ulid()
        return cls(
            feedback_id=item.get("feedback_id", fb_id),
            user_sub=item.get("user_sub"),
            category=item.get("category", "other"),
            page=item.get("page"),
            description=item.get("description", ""),
            status=item.get("status", "new"),
            created_at=item.get("created_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# AdminMetrics  (PK=METRICS  SK=<date>)
# -------------------------------------------------------------------

class AdminMetricsEntity(DynamoBase):
    """Daily system metrics snapshot."""

    entity_type: str = "AdminMetrics"

    metrics_date: str  # YYYY-MM-DD

    total_users: int = 0
    new_users: int = 0
    active_users: int = 0

    total_profiles: int = 0
    total_heroes_tracked: int = 0
    total_inventory_items: int = 0

    total_logins: int = 0

    created_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        return {
            "PK": "METRICS",
            "SK": self.metrics_date,
            "entity_type": self.entity_type,
            "metrics_date": self.metrics_date,
            "total_users": self.total_users,
            "new_users": self.new_users,
            "active_users": self.active_users,
            "total_profiles": self.total_profiles,
            "total_heroes_tracked": self.total_heroes_tracked,
            "total_inventory_items": self.total_inventory_items,
            "total_logins": self.total_logins,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dynamo(cls, item: dict) -> AdminMetricsEntity:
        return cls(
            metrics_date=item["SK"],
            total_users=item.get("total_users", 0),
            new_users=item.get("new_users", 0),
            active_users=item.get("active_users", 0),
            total_profiles=item.get("total_profiles", 0),
            total_heroes_tracked=item.get("total_heroes_tracked", 0),
            total_inventory_items=item.get("total_inventory_items", 0),
            total_logins=item.get("total_logins", 0),
            created_at=item.get("created_at", utcnow_iso()),
        )


# -------------------------------------------------------------------
# Announcement  (PK=ANNOUNCE  SK=<ulid>)
# -------------------------------------------------------------------

class AnnouncementEntity(DynamoBase):
    """System-wide announcement."""

    entity_type: str = "Announcement"

    announcement_id: str = Field(default_factory=generate_ulid)
    title: str
    message: str
    type: AnnouncementType = AnnouncementType.info

    is_active: bool = True
    show_from: Optional[str] = None
    show_until: Optional[str] = None

    display_type: DisplayType = DisplayType.banner
    inbox_content: Optional[str] = None

    created_by: str  # cognito_sub
    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)

    def to_dynamo(self) -> dict:
        item = {
            "PK": "ANNOUNCE",
            "SK": self.announcement_id,
            "entity_type": self.entity_type,
            "announcement_id": self.announcement_id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "is_active": self.is_active,
            "show_from": self.show_from,
            "show_until": self.show_until,
            "display_type": self.display_type,
            "inbox_content": self.inbox_content,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            # GSI for active announcements sorted by date
            "GSI1PK": f"ANNOUNCE#{'active' if self.is_active else 'inactive'}",
            "GSI1SK": self.created_at,
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> AnnouncementEntity:
        return cls(
            announcement_id=item["SK"],
            title=item.get("title", ""),
            message=item.get("message", ""),
            type=item.get("type", "info"),
            is_active=item.get("is_active", True),
            show_from=item.get("show_from"),
            show_until=item.get("show_until"),
            display_type=item.get("display_type", "banner"),
            inbox_content=item.get("inbox_content"),
            created_by=item.get("created_by", ""),
            created_at=item.get("created_at", utcnow_iso()),
            updated_at=item.get("updated_at", utcnow_iso()),
        )


# ===================================================================
# REFERENCE TABLE ENTITIES
# ===================================================================

# -------------------------------------------------------------------
# Hero  (PK=HERO  SK=<hero_name>)
# -------------------------------------------------------------------

class HeroEntity(DynamoBase):
    """Static hero reference data."""

    entity_type: str = "Hero"

    name: str
    generation: int = Field(ge=1, le=20)
    hero_class: HeroClass
    rarity: Rarity

    tier_overall: Optional[str] = None
    tier_expedition: Optional[str] = None
    tier_exploration: Optional[str] = None

    image_filename: Optional[str] = None

    exploration_skill_1: Optional[str] = None
    exploration_skill_2: Optional[str] = None
    exploration_skill_3: Optional[str] = None
    expedition_skill_1: Optional[str] = None
    expedition_skill_2: Optional[str] = None
    expedition_skill_3: Optional[str] = None

    exploration_skill_1_desc: Optional[str] = None
    exploration_skill_2_desc: Optional[str] = None
    exploration_skill_3_desc: Optional[str] = None
    expedition_skill_1_desc: Optional[str] = None
    expedition_skill_2_desc: Optional[str] = None
    expedition_skill_3_desc: Optional[str] = None

    how_to_obtain: Optional[str] = None
    notes: Optional[str] = None

    def to_dynamo(self) -> dict:
        item = {
            "PK": "HERO",
            "SK": self.name,
            "entity_type": self.entity_type,
            "name": self.name,
            "generation": self.generation,
            "hero_class": self.hero_class,
            "rarity": self.rarity,
            "tier_overall": self.tier_overall,
            "tier_expedition": self.tier_expedition,
            "tier_exploration": self.tier_exploration,
            "image_filename": self.image_filename,
            "exploration_skill_1": self.exploration_skill_1,
            "exploration_skill_2": self.exploration_skill_2,
            "exploration_skill_3": self.exploration_skill_3,
            "expedition_skill_1": self.expedition_skill_1,
            "expedition_skill_2": self.expedition_skill_2,
            "expedition_skill_3": self.expedition_skill_3,
            "exploration_skill_1_desc": self.exploration_skill_1_desc,
            "exploration_skill_2_desc": self.exploration_skill_2_desc,
            "exploration_skill_3_desc": self.exploration_skill_3_desc,
            "expedition_skill_1_desc": self.expedition_skill_1_desc,
            "expedition_skill_2_desc": self.expedition_skill_2_desc,
            "expedition_skill_3_desc": self.expedition_skill_3_desc,
            "how_to_obtain": self.how_to_obtain,
            "notes": self.notes,
            # GSI for filtering by generation
            "GSI1PK": "HERO",
            "GSI1SK": f"GEN#{self.generation:02d}#{self.name}",
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> HeroEntity:
        return cls(
            name=item["SK"],
            generation=item.get("generation", 1),
            hero_class=item.get("hero_class", "Infantry"),
            rarity=item.get("rarity", "Epic"),
            tier_overall=item.get("tier_overall"),
            tier_expedition=item.get("tier_expedition"),
            tier_exploration=item.get("tier_exploration"),
            image_filename=item.get("image_filename"),
            exploration_skill_1=item.get("exploration_skill_1"),
            exploration_skill_2=item.get("exploration_skill_2"),
            exploration_skill_3=item.get("exploration_skill_3"),
            expedition_skill_1=item.get("expedition_skill_1"),
            expedition_skill_2=item.get("expedition_skill_2"),
            expedition_skill_3=item.get("expedition_skill_3"),
            exploration_skill_1_desc=item.get("exploration_skill_1_desc"),
            exploration_skill_2_desc=item.get("exploration_skill_2_desc"),
            exploration_skill_3_desc=item.get("exploration_skill_3_desc"),
            expedition_skill_1_desc=item.get("expedition_skill_1_desc"),
            expedition_skill_2_desc=item.get("expedition_skill_2_desc"),
            expedition_skill_3_desc=item.get("expedition_skill_3_desc"),
            how_to_obtain=item.get("how_to_obtain"),
            notes=item.get("notes"),
        )


# -------------------------------------------------------------------
# Item  (PK=ITEM  SK=<item_name>)
# -------------------------------------------------------------------

class ItemEntity(DynamoBase):
    """Backpack item definition."""

    entity_type: str = "Item"

    name: str
    category: str  # Shard, XP, Material, Gear, etc.
    subcategory: Optional[str] = None
    rarity: Optional[str] = None

    ocr_aliases: Optional[list[str]] = None
    image_filename: Optional[str] = None

    def to_dynamo(self) -> dict:
        item = {
            "PK": "ITEM",
            "SK": self.name,
            "entity_type": self.entity_type,
            "name": self.name,
            "category": self.category,
            "subcategory": self.subcategory,
            "rarity": self.rarity,
            "ocr_aliases": self.ocr_aliases,
            "image_filename": self.image_filename,
            # GSI for filtering by category
            "GSI1PK": "ITEM",
            "GSI1SK": f"CAT#{self.category}#{self.name}",
        }
        return _strip_none(item)

    @classmethod
    def from_dynamo(cls, item: dict) -> ItemEntity:
        return cls(
            name=item["SK"],
            category=item.get("category", ""),
            subcategory=item.get("subcategory"),
            rarity=item.get("rarity"),
            ocr_aliases=item.get("ocr_aliases"),
            image_filename=item.get("image_filename"),
        )


# ===================================================================
# API REQUEST / RESPONSE MODELS
# ===================================================================

# -------------------------------------------------------------------
# Auth
# -------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    username: Optional[str] = None  # Auto-derived from email if not provided

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    """User login request (Cognito handles auth, this is for token exchange)."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response after successful auth."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds


class RefreshTokenRequest(BaseModel):
    """Request to refresh an expired access token."""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class ForgotPasswordRequest(BaseModel):
    """Initiate password reset."""
    email: EmailStr


class ConfirmForgotPasswordRequest(BaseModel):
    """Confirm password reset with code."""
    email: EmailStr
    confirmation_code: str
    new_password: str = Field(min_length=8, max_length=128)


# -------------------------------------------------------------------
# User
# -------------------------------------------------------------------

class UserResponse(BaseModel):
    """User data returned to the client."""
    cognito_sub: str
    username: str
    email: str
    role: str = "user"
    theme: str = "dark"
    is_active: bool = True
    is_verified: bool = False
    is_test_account: bool = False
    ai_access_level: str = "limited"
    ai_daily_limit: Optional[int] = None
    ai_requests_today: int = 0
    created_at: str
    last_login: Optional[str] = None


class UpdateUserRequest(BaseModel):
    """Update user settings."""
    theme: Optional[str] = None
    username: Optional[str] = None


class AdminUpdateUserRequest(BaseModel):
    """Admin-only user update."""
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_test_account: Optional[bool] = None
    ai_access_level: Optional[str] = None
    ai_daily_limit: Optional[int] = None


# -------------------------------------------------------------------
# Profile
# -------------------------------------------------------------------

class CreateProfileRequest(BaseModel):
    """Create a new game profile."""
    name: str = Field(default="Chief", max_length=100)
    is_default: bool = False
    state_number: Optional[int] = None
    server_age_days: int = 0
    furnace_level: int = Field(default=1, ge=1, le=30)
    furnace_fc_level: Optional[str] = None
    spending_profile: SpendingProfile = SpendingProfile.f2p
    priority_focus: PriorityFocus = PriorityFocus.balanced_growth
    alliance_role: AllianceRole = AllianceRole.filler
    priority_pvp_attack: int = Field(default=5, ge=1, le=5)
    priority_defense: int = Field(default=4, ge=1, le=5)
    priority_pve: int = Field(default=3, ge=1, le=5)
    priority_economy: int = Field(default=2, ge=1, le=5)
    is_farm_account: bool = False
    linked_main_profile_id: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    """Update an existing game profile."""
    name: Optional[str] = Field(default=None, max_length=100)
    is_default: Optional[bool] = None
    state_number: Optional[int] = None
    server_age_days: Optional[int] = None
    furnace_level: Optional[int] = Field(default=None, ge=1, le=30)
    furnace_fc_level: Optional[str] = None
    spending_profile: Optional[SpendingProfile] = None
    priority_focus: Optional[PriorityFocus] = None
    alliance_role: Optional[AllianceRole] = None
    priority_pvp_attack: Optional[int] = Field(default=None, ge=1, le=5)
    priority_defense: Optional[int] = Field(default=None, ge=1, le=5)
    priority_pve: Optional[int] = Field(default=None, ge=1, le=5)
    priority_economy: Optional[int] = Field(default=None, ge=1, le=5)
    is_farm_account: Optional[bool] = None
    linked_main_profile_id: Optional[str] = None
    last_svs_date: Optional[str] = None
    svs_wins: Optional[int] = None
    svs_losses: Optional[int] = None


class ProfileResponse(BaseModel):
    """Profile data returned to the client."""
    profile_id: str
    cognito_sub: str
    name: str
    is_default: bool
    state_number: Optional[int] = None
    server_age_days: int
    furnace_level: int
    furnace_fc_level: Optional[str] = None
    spending_profile: str
    priority_focus: str
    alliance_role: str
    priority_pvp_attack: int
    priority_defense: int
    priority_pve: int
    priority_economy: int
    last_svs_date: Optional[str] = None
    svs_wins: int = 0
    svs_losses: int = 0
    is_farm_account: bool = False
    linked_main_profile_id: Optional[str] = None
    created_at: str
    updated_at: str


# -------------------------------------------------------------------
# Hero Tracker
# -------------------------------------------------------------------

class UpdateHeroRequest(BaseModel):
    """Update a user's hero data."""
    level: Optional[int] = Field(default=None, ge=1, le=80)
    stars: Optional[int] = Field(default=None, ge=0, le=5)
    ascension_tier: Optional[int] = Field(default=None, ge=0, le=5)

    exploration_skill_1_level: Optional[int] = Field(default=None, ge=1, le=5)
    exploration_skill_2_level: Optional[int] = Field(default=None, ge=1, le=5)
    exploration_skill_3_level: Optional[int] = Field(default=None, ge=1, le=5)
    expedition_skill_1_level: Optional[int] = Field(default=None, ge=1, le=5)
    expedition_skill_2_level: Optional[int] = Field(default=None, ge=1, le=5)
    expedition_skill_3_level: Optional[int] = Field(default=None, ge=1, le=5)

    gear_slot1_quality: Optional[int] = Field(default=None, ge=0, le=7)
    gear_slot1_level: Optional[int] = Field(default=None, ge=0, le=100)
    gear_slot1_mastery: Optional[int] = Field(default=None, ge=0, le=20)
    gear_slot2_quality: Optional[int] = Field(default=None, ge=0, le=7)
    gear_slot2_level: Optional[int] = Field(default=None, ge=0, le=100)
    gear_slot2_mastery: Optional[int] = Field(default=None, ge=0, le=20)
    gear_slot3_quality: Optional[int] = Field(default=None, ge=0, le=7)
    gear_slot3_level: Optional[int] = Field(default=None, ge=0, le=100)
    gear_slot3_mastery: Optional[int] = Field(default=None, ge=0, le=20)
    gear_slot4_quality: Optional[int] = Field(default=None, ge=0, le=7)
    gear_slot4_level: Optional[int] = Field(default=None, ge=0, le=100)
    gear_slot4_mastery: Optional[int] = Field(default=None, ge=0, le=20)

    mythic_gear_unlocked: Optional[bool] = None
    mythic_gear_quality: Optional[int] = Field(default=None, ge=0, le=7)
    mythic_gear_level: Optional[int] = Field(default=None, ge=0, le=100)
    mythic_gear_mastery: Optional[int] = Field(default=None, ge=0, le=20)
    exclusive_gear_skill_level: Optional[int] = Field(default=None, ge=0, le=10)

    owned: Optional[bool] = None


class HeroResponse(BaseModel):
    """User hero data returned to the client."""
    profile_id: str
    hero_name: str
    level: int
    stars: int
    ascension_tier: int
    exploration_skill_1_level: int
    exploration_skill_2_level: int
    exploration_skill_3_level: int
    expedition_skill_1_level: int
    expedition_skill_2_level: int
    expedition_skill_3_level: int
    gear_slot1_quality: int
    gear_slot1_level: int
    gear_slot1_mastery: int
    gear_slot2_quality: int
    gear_slot2_level: int
    gear_slot2_mastery: int
    gear_slot3_quality: int
    gear_slot3_level: int
    gear_slot3_mastery: int
    gear_slot4_quality: int
    gear_slot4_level: int
    gear_slot4_mastery: int
    mythic_gear_unlocked: bool
    mythic_gear_quality: int
    mythic_gear_level: int
    mythic_gear_mastery: int
    exclusive_gear_skill_level: int
    owned: bool
    created_at: str
    updated_at: str


# -------------------------------------------------------------------
# Chief Gear & Charms
# -------------------------------------------------------------------

class UpdateChiefGearRequest(BaseModel):
    """Update chief gear levels."""
    helmet_quality: Optional[int] = Field(default=None, ge=0, le=7)
    helmet_level: Optional[int] = Field(default=None, ge=0, le=100)
    armor_quality: Optional[int] = Field(default=None, ge=0, le=7)
    armor_level: Optional[int] = Field(default=None, ge=0, le=100)
    gloves_quality: Optional[int] = Field(default=None, ge=0, le=7)
    gloves_level: Optional[int] = Field(default=None, ge=0, le=100)
    boots_quality: Optional[int] = Field(default=None, ge=0, le=7)
    boots_level: Optional[int] = Field(default=None, ge=0, le=100)
    ring_quality: Optional[int] = Field(default=None, ge=0, le=7)
    ring_level: Optional[int] = Field(default=None, ge=0, le=100)
    amulet_quality: Optional[int] = Field(default=None, ge=0, le=7)
    amulet_level: Optional[int] = Field(default=None, ge=0, le=100)


class ChiefGearResponse(BaseModel):
    """Chief gear data returned to the client."""
    profile_id: str
    helmet_quality: int
    helmet_level: int
    armor_quality: int
    armor_level: int
    gloves_quality: int
    gloves_level: int
    boots_quality: int
    boots_level: int
    ring_quality: int
    ring_level: int
    amulet_quality: int
    amulet_level: int
    updated_at: str


class UpdateChiefCharmRequest(BaseModel):
    """Update chief charm levels."""
    cap_slot_1: Optional[str] = None
    cap_slot_2: Optional[str] = None
    cap_slot_3: Optional[str] = None
    watch_slot_1: Optional[str] = None
    watch_slot_2: Optional[str] = None
    watch_slot_3: Optional[str] = None
    coat_slot_1: Optional[str] = None
    coat_slot_2: Optional[str] = None
    coat_slot_3: Optional[str] = None
    pants_slot_1: Optional[str] = None
    pants_slot_2: Optional[str] = None
    pants_slot_3: Optional[str] = None
    belt_slot_1: Optional[str] = None
    belt_slot_2: Optional[str] = None
    belt_slot_3: Optional[str] = None
    weapon_slot_1: Optional[str] = None
    weapon_slot_2: Optional[str] = None
    weapon_slot_3: Optional[str] = None


class ChiefCharmResponse(BaseModel):
    """Chief charm data returned to the client."""
    profile_id: str
    cap_slot_1: str
    cap_slot_2: str
    cap_slot_3: str
    watch_slot_1: str
    watch_slot_2: str
    watch_slot_3: str
    coat_slot_1: str
    coat_slot_2: str
    coat_slot_3: str
    pants_slot_1: str
    pants_slot_2: str
    pants_slot_3: str
    belt_slot_1: str
    belt_slot_2: str
    belt_slot_3: str
    weapon_slot_1: str
    weapon_slot_2: str
    weapon_slot_3: str
    updated_at: str


# -------------------------------------------------------------------
# Inventory
# -------------------------------------------------------------------

class UpdateInventoryRequest(BaseModel):
    """Update inventory item quantity."""
    quantity: int = Field(ge=0)


class InventoryResponse(BaseModel):
    """Inventory item data returned to the client."""
    profile_id: str
    item_name: str
    quantity: int
    updated_at: str


class UpdateInventoryItem(BaseModel):
    """Single item in a bulk inventory update."""
    item_name: str
    quantity: int = Field(ge=0)


class BulkInventoryUpdate(BaseModel):
    """Bulk update multiple inventory items at once."""
    items: list[UpdateInventoryItem]


# -------------------------------------------------------------------
# AI Advisor
# -------------------------------------------------------------------

class AskAdvisorRequest(BaseModel):
    """Ask the AI advisor a question."""
    question: str = Field(max_length=2000)
    profile_id: Optional[str] = None
    source_page: Optional[str] = None
    question_type: Optional[str] = None
    thread_id: Optional[str] = None


class AdvisorResponse(BaseModel):
    """AI advisor response."""
    conversation_id: str
    answer: str
    routed_to: str  # rules, ai, hybrid
    provider: Optional[str] = None
    model: Optional[str] = None
    thread_id: Optional[str] = None
    thread_title: Optional[str] = None


class RateConversationRequest(BaseModel):
    """Rate an AI conversation."""
    is_helpful: Optional[bool] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    user_feedback: Optional[str] = Field(default=None, max_length=500)


# -------------------------------------------------------------------
# Feedback
# -------------------------------------------------------------------

class CreateFeedbackRequest(BaseModel):
    """Submit user feedback."""
    category: FeedbackCategory
    page: Optional[str] = None
    description: str = Field(max_length=2000)


class FeedbackResponse(BaseModel):
    """Feedback data returned to the client."""
    feedback_id: str
    user_sub: Optional[str] = None
    category: str
    page: Optional[str] = None
    description: str
    status: str
    created_at: str


class UpdateFeedbackStatusRequest(BaseModel):
    """Admin: update feedback status."""
    status: FeedbackStatus


# -------------------------------------------------------------------
# Announcements
# -------------------------------------------------------------------

class CreateAnnouncementRequest(BaseModel):
    """Admin: create a new announcement."""
    title: str = Field(max_length=200)
    message: str = Field(max_length=2000)
    type: AnnouncementType = AnnouncementType.info
    display_type: DisplayType = DisplayType.banner
    inbox_content: Optional[str] = Field(default=None, max_length=2000)
    show_from: Optional[str] = None
    show_until: Optional[str] = None


class AnnouncementResponse(BaseModel):
    """Announcement data returned to the client."""
    announcement_id: str
    title: str
    message: str
    type: str
    is_active: bool
    show_from: Optional[str] = None
    show_until: Optional[str] = None
    display_type: str
    inbox_content: Optional[str] = None
    created_by: str
    created_at: str
    updated_at: str


class NotificationResponse(BaseModel):
    """User notification with announcement data."""
    announcement_id: str
    is_read: bool
    read_at: Optional[str] = None
    announcement: Optional[AnnouncementResponse] = None


# -------------------------------------------------------------------
# Messages
# -------------------------------------------------------------------

class CreateThreadRequest(BaseModel):
    """Create a new message thread."""
    subject: str = Field(max_length=200)
    message: str = Field(max_length=5000)


class SendMessageRequest(BaseModel):
    """Send a message in a thread."""
    content: str = Field(max_length=5000)


class ThreadResponse(BaseModel):
    """Message thread data returned to the client."""
    thread_id: str
    cognito_sub: str
    subject: str
    is_closed: bool
    created_at: str
    updated_at: str
    unread_count: int = 0
    last_message: Optional[str] = None


class MessageResponse(BaseModel):
    """Message data returned to the client."""
    message_id: str
    thread_id: str
    sender_sub: str
    content: str
    is_from_admin: bool
    is_read: bool
    read_at: Optional[str] = None
    created_at: str


# -------------------------------------------------------------------
# Admin
# -------------------------------------------------------------------

class AdminAISettingsRequest(BaseModel):
    """Admin: update AI settings."""
    mode: Optional[AIMode] = None
    daily_limit_free: Optional[int] = Field(default=None, ge=0)
    daily_limit_admin: Optional[int] = Field(default=None, ge=0)
    cooldown_seconds: Optional[int] = Field(default=None, ge=0)
    primary_provider: Optional[AIProvider] = None
    fallback_provider: Optional[str] = None
    openai_model: Optional[str] = None
    anthropic_model: Optional[str] = None


class FeatureFlagRequest(BaseModel):
    """Admin: update a feature flag."""
    is_enabled: Optional[bool] = None
    value: Optional[str] = None
    description: Optional[str] = None
    enabled_for_roles: Optional[list[str]] = None
    enabled_for_users: Optional[list[str]] = None


class FeatureFlagResponse(BaseModel):
    """Feature flag data returned to the client."""
    name: str
    description: Optional[str] = None
    is_enabled: bool
    value: Optional[str] = None
    enabled_for_roles: Optional[list[str]] = None
    enabled_for_users: Optional[list[str]] = None
    created_at: str
    updated_at: str


class AuditLogResponse(BaseModel):
    """Audit log entry returned to admin."""
    audit_id: str
    admin_sub: str
    admin_username: str
    action: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    details: Optional[str] = None
    created_at: str


class ErrorLogResponse(BaseModel):
    """Error log entry returned to admin."""
    error_id: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    page: Optional[str] = None
    function: Optional[str] = None
    user_sub: Optional[str] = None
    profile_id: Optional[str] = None
    environment: Optional[str] = None
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    fix_notes: Optional[str] = None
    created_at: str


class AdminMetricsResponse(BaseModel):
    """Daily metrics snapshot returned to admin."""
    metrics_date: str
    total_users: int
    new_users: int
    active_users: int
    total_profiles: int
    total_heroes_tracked: int
    total_inventory_items: int
    total_logins: int


# -------------------------------------------------------------------
# Generic / Common
# -------------------------------------------------------------------

class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses."""
    items: list[Any]
    count: int
    last_evaluated_key: Optional[str] = None  # Base64-encoded DynamoDB pagination token


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    environment: str = "production"


class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str = "OK"
