"""SQLAlchemy models for Whiteout Survival Optimizer."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User account for authentication. AWS-ready design."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash

    # Role: 'admin' or 'user'
    role = Column(String(20), default='user', nullable=False)

    # User preferences
    theme = Column(String(20), default='dark', nullable=False)  # 'dark' (Arctic Night) or 'light' (Arctic Day)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # For email verification (AWS SES)
    is_test_account = Column(Boolean, default=False)  # Flag for test/demo accounts

    # AWS Cognito compatibility fields (for future migration)
    cognito_sub = Column(String(100), unique=True, nullable=True)  # Cognito user ID

    # AI Rate Limiting
    ai_requests_today = Column(Integer, default=0)
    ai_request_reset_date = Column(DateTime, nullable=True)  # Date when count resets
    last_ai_request = Column(DateTime, nullable=True)  # For cooldown
    ai_access_level = Column(String(20), default='limited')  # 'off', 'limited', 'unlimited'

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships - cascade delete all child data when user is permanently deleted
    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    """User's game profile and preferences."""
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable for migration
    name = Column(String(100), default="Chief")
    is_default = Column(Boolean, default=False)  # True = auto-load this profile on login
    state_number = Column(Integer, nullable=True)  # Game state/server number (e.g., 123, 456)
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

    # Farm account settings
    is_farm_account = Column(Boolean, default=False)  # True if this is a farm/alt account
    linked_main_profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=True)  # Link to main account

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete - profile hidden but recoverable for 30 days

    # Relationships - cascade delete all child data when profile is deleted
    user = relationship("User", back_populates="profiles")
    heroes = relationship("UserHero", back_populates="profile", cascade="all, delete-orphan")
    inventory = relationship("UserInventory", back_populates="profile", cascade="all, delete-orphan")

    # Farm account relationships (self-referential)
    linked_main_profile = relationship("UserProfile", remote_side=[id], foreign_keys=[linked_main_profile_id], backref="farm_accounts")


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

    # Relationship - cascade delete when profile is deleted
    profile = relationship("UserProfile", backref=backref("chief_gear", cascade="all, delete-orphan"))


class UserChiefCharm(Base):
    """User's Chief Charm levels - 18 charm slots (6 gear pieces × 3 slots per gear).

    Each gear piece has 3 charms of the SAME type based on troop category:
    - Cap/Watch (Lancer gear) → 3 Keenness charms each
    - Coat/Pants (Infantry gear) → 3 Protection charms each
    - Belt/Weapon (Marksman gear) → 3 Vision charms each

    Levels 1-3 are simple, but 4+ have sub-levels like FC construction (e.g., "4-1", "4-2", "4-3").
    Stored as strings to support sub-level format.
    """
    __tablename__ = 'user_chief_charms'

    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)

    # Cap charms - 3 Keenness slots (Lancer gear)
    # Levels: "1" through "16", with sub-levels at 4+: "4-1", "4-2", "4-3", "5", etc.
    cap_slot_1 = Column(String(10), default="1")
    cap_slot_2 = Column(String(10), default="1")
    cap_slot_3 = Column(String(10), default="1")

    # Watch charms - 3 Keenness slots (Lancer gear)
    watch_slot_1 = Column(String(10), default="1")
    watch_slot_2 = Column(String(10), default="1")
    watch_slot_3 = Column(String(10), default="1")

    # Coat charms - 3 Protection slots (Infantry gear)
    coat_slot_1 = Column(String(10), default="1")
    coat_slot_2 = Column(String(10), default="1")
    coat_slot_3 = Column(String(10), default="1")

    # Pants charms - 3 Protection slots (Infantry gear)
    pants_slot_1 = Column(String(10), default="1")
    pants_slot_2 = Column(String(10), default="1")
    pants_slot_3 = Column(String(10), default="1")

    # Belt charms - 3 Vision slots (Marksman gear)
    belt_slot_1 = Column(String(10), default="1")
    belt_slot_2 = Column(String(10), default="1")
    belt_slot_3 = Column(String(10), default="1")

    # Weapon charms - 3 Vision slots (Marksman gear)
    weapon_slot_1 = Column(String(10), default="1")
    weapon_slot_2 = Column(String(10), default="1")
    weapon_slot_3 = Column(String(10), default="1")

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship - cascade delete when profile is deleted
    profile = relationship("UserProfile", backref=backref("chief_charms", cascade="all, delete-orphan"))


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


class Feedback(Base):
    """User feedback and suggestions."""
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable for anonymous feedback

    category = Column(String(50), nullable=False)  # bug, feature, data_error, other
    page = Column(String(100), nullable=True)  # Which page the feedback is about
    description = Column(String(2000), nullable=False)

    # Status for admin review
    # new = freshly submitted
    # pending_fix = bug marked for development
    # pending_update = feature marked for development
    # completed = fixed/implemented
    # archive = dismissed/not needed
    status = Column(String(20), default='new')

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="feedback")


class AdminMetrics(Base):
    """Daily snapshots of system metrics for analytics charts."""
    __tablename__ = 'admin_metrics'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)

    # User metrics (excludes admins)
    total_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)  # Logged in that day

    # Content metrics
    total_profiles = Column(Integer, default=0)
    total_heroes_tracked = Column(Integer, default=0)
    total_inventory_items = Column(Integer, default=0)

    # Engagement metrics
    total_logins = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Track admin actions for accountability."""
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    admin_username = Column(String(50), nullable=False)

    action = Column(String(50), nullable=False)  # user_created, user_deleted, password_reset, role_changed, impersonation_started
    target_type = Column(String(50), nullable=True)  # user, system, etc.
    target_id = Column(Integer, nullable=True)
    target_name = Column(String(100), nullable=True)
    details = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Announcement(Base):
    """System-wide announcements for users."""
    __tablename__ = 'announcements'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    message = Column(String(2000), nullable=False)
    type = Column(String(20), default='info')  # info, warning, success, error

    # Display settings
    is_active = Column(Boolean, default=True)
    show_from = Column(DateTime, nullable=True)
    show_until = Column(DateTime, nullable=True)

    # Who created it
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FeatureFlag(Base):
    """Feature flags for controlling app features."""
    __tablename__ = 'feature_flags'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    is_enabled = Column(Boolean, default=False)

    # For multi-state flags like AI mode (off/on/unlimited)
    value = Column(String(50), nullable=True)  # Optional string value for complex flags

    # Optional: limit to specific roles or users
    enabled_for_roles = Column(JSON, nullable=True)  # ["admin", "user"] or None for all
    enabled_for_users = Column(JSON, nullable=True)  # [user_id, ...] or None for all

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIConversation(Base):
    """Log AI conversations for training data collection."""
    __tablename__ = 'ai_conversations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=True)  # Which profile was active

    # The conversation
    question = Column(String(2000), nullable=False)
    answer = Column(String(5000), nullable=False)
    context_summary = Column(String(1000), nullable=True)  # Summary of user's profile/heroes for context

    # Full user snapshot at time of question (JSON blob for training data context)
    # Contains: profile, heroes (top 10), chief_gear, chief_charms, spending_profile, priorities
    user_snapshot = Column(Text, nullable=True)

    # AI metadata
    provider = Column(String(20), nullable=False)  # openai, anthropic
    model = Column(String(50), nullable=False)  # gpt-4o-mini, claude-sonnet-4-20250514, etc.
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)  # How long the API call took

    # Routing info - did this go to rules or AI?
    routed_to = Column(String(20), nullable=True)  # 'rules', 'ai', 'hybrid'
    rule_ids_matched = Column(String(500), nullable=True)  # Which rules were matched (comma-separated)

    # User feedback for training
    rating = Column(Integer, nullable=True)  # 1-5 or null if not rated
    is_helpful = Column(Boolean, nullable=True)  # Thumbs up/down
    user_feedback = Column(String(500), nullable=True)  # Optional text feedback

    # Admin curation for training data
    is_good_example = Column(Boolean, default=False)  # Admin marks as good training data
    is_bad_example = Column(Boolean, default=False)  # Admin marks as bad (hallucination, wrong info)
    admin_notes = Column(String(500), nullable=True)  # Admin notes about this conversation

    # Source tracking
    source_page = Column(String(50), nullable=True)  # Which page the question came from
    question_type = Column(String(50), nullable=True)  # quick_question, custom, recommendations, etc.

    # User favorites
    is_favorite = Column(Boolean, default=False)  # User bookmarked this conversation

    # Conversation threading
    thread_id = Column(String(36), nullable=True, index=True)  # UUID to group related conversations
    thread_title = Column(String(100), nullable=True)  # Auto-generated from first question

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="ai_conversations")
    profile = relationship("UserProfile", backref="ai_conversations")


class AISettings(Base):
    """Global AI settings (singleton - only one row)."""
    __tablename__ = 'ai_settings'

    id = Column(Integer, primary_key=True)

    # AI Mode: off, on, unlimited
    mode = Column(String(20), default='off', nullable=False)

    # Rate limits (when mode='on')
    daily_limit_free = Column(Integer, default=20)  # Requests per day for free users
    daily_limit_admin = Column(Integer, default=1000)  # Requests per day for admins (effectively unlimited)
    cooldown_seconds = Column(Integer, default=30)  # Seconds between requests

    # Provider settings
    primary_provider = Column(String(20), default='openai')  # openai or anthropic
    fallback_provider = Column(String(20), nullable=True)  # Use this if primary fails

    # Model settings
    openai_model = Column(String(50), default='gpt-4o-mini')
    anthropic_model = Column(String(50), default='claude-sonnet-4-20250514')

    # Cost tracking
    total_requests = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)


class PendingEmailChange(Base):
    """Pending email change requests awaiting verification."""
    __tablename__ = 'pending_email_changes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)

    # New email to change to
    new_email = Column(String(255), nullable=False)

    # 6-digit verification code
    verification_code = Column(String(6), nullable=False)

    # Expiration (15 minutes from creation)
    expires_at = Column(DateTime, nullable=False)

    # Attempts tracking (max 3 attempts)
    attempts = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref=backref("pending_email_change", uselist=False, cascade="all, delete-orphan"))


class LineupTestRun(Base):
    """Groups results from a single lineup test execution."""
    __tablename__ = 'lineup_test_runs'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))  # "Gen Coverage Run 1", "Gear Impact Test"
    description = Column(String(500), nullable=True)

    # Test configuration
    total_profiles = Column(Integer, default=0)
    total_scenarios = Column(Integer, default=0)
    test_groups = Column(Text, nullable=True)  # JSON: which test groups were included

    # Status
    status = Column(String(20), default='pending')  # pending, running, completed, failed

    # Cost tracking
    openai_tokens_input = Column(Integer, default=0)
    openai_tokens_output = Column(Integer, default=0)
    openai_cost_usd = Column(Float, default=0.0)

    # Summary stats (populated after completion)
    avg_engine_vs_openai = Column(Float, nullable=True)
    avg_engine_vs_claude = Column(Float, nullable=True)
    avg_openai_vs_claude = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    results = relationship("LineupTestResult", back_populates="test_run", cascade="all, delete-orphan")


class LineupTestResult(Base):
    """Individual lineup test result for one profile + scenario."""
    __tablename__ = 'lineup_test_results'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('lineup_test_runs.id'), nullable=False)

    # Profile context
    profile_name = Column(String(100))  # e.g., "Gen10_Developed_A"
    profile_snapshot = Column(Text, nullable=False)  # Full JSON snapshot sent to AI
    generation = Column(Integer)
    test_group = Column(String(50))  # "generation", "level_impact", "gear_impact", etc.

    # Scenario
    scenario = Column(String(50), nullable=False)  # bear_trap, rally_lead, etc.

    # TRAINING DATA: Store exact prompt sent to AI
    prompt_sent = Column(Text, nullable=True)  # Full prompt for reproducibility and training

    # Our engine results
    engine_lineup = Column(Text)  # JSON: [{"slot": 1, "hero": "Natalia", "reason": "..."}]
    engine_troop_ratio = Column(String(50))  # "30/20/50" (infantry/lancer/marksman)
    engine_reasoning = Column(Text)
    engine_time_ms = Column(Integer, nullable=True)

    # OpenAI results
    openai_model = Column(String(50))
    openai_lineup = Column(Text)  # JSON
    openai_troop_ratio = Column(String(50))
    openai_reasoning = Column(Text)
    openai_tokens_input = Column(Integer, nullable=True)
    openai_tokens_output = Column(Integer, nullable=True)
    openai_time_ms = Column(Integer, nullable=True)
    openai_raw_response = Column(Text, nullable=True)  # Full API response for debugging

    # Claude results
    claude_model = Column(String(50))
    claude_lineup = Column(Text)  # JSON
    claude_troop_ratio = Column(String(50))
    claude_reasoning = Column(Text)
    claude_time_ms = Column(Integer, nullable=True)
    claude_raw_response = Column(Text, nullable=True)

    # Comparison metrics
    engine_vs_openai_score = Column(Float, nullable=True)  # 0.0-1.0
    engine_vs_claude_score = Column(Float, nullable=True)
    openai_vs_claude_score = Column(Float, nullable=True)

    # Detailed comparison
    hero_overlap_openai = Column(Integer, nullable=True)  # 0-5 heroes matching
    hero_overlap_claude = Column(Integer, nullable=True)
    slot1_match_openai = Column(Boolean, nullable=True)  # For rally scenarios - leftmost hero matches?
    slot1_match_claude = Column(Boolean, nullable=True)

    # Flags for review
    needs_review = Column(Boolean, default=False)  # True if big discrepancy
    review_notes = Column(Text, nullable=True)  # Manual notes after review

    # Quality annotations for training data
    quality_flag = Column(String(50), nullable=True)  # gold_standard, valid_alternative, claude_correct, parser_false_positive, needs_review
    quality_notes = Column(Text, nullable=True)  # Human-readable explanation of quality flag

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("LineupTestRun", back_populates="results")


class LineupEngineImprovement(Base):
    """Track suggested improvements to the lineup engine based on test results."""
    __tablename__ = 'lineup_engine_improvements'

    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey('lineup_test_runs.id'), nullable=True)

    # What scenario/pattern this addresses
    scenario = Column(String(50), nullable=True)  # bear_trap, rally_lead, or None for general
    pattern_description = Column(Text)  # "AI consistently picks Sergey for garrison defense"

    # The suggested change
    suggestion_source = Column(String(20))  # openai, claude, manual
    suggestion = Column(Text, nullable=False)  # Detailed suggestion
    affected_code = Column(Text, nullable=True)  # Which file/function to change
    code_diff = Column(Text, nullable=True)  # Suggested code changes

    # Status
    status = Column(String(20), default='pending')  # pending, approved, implemented, rejected
    priority = Column(String(20), default='medium')  # low, medium, high, critical

    # Implementation tracking
    implemented_at = Column(DateTime, nullable=True)
    implemented_by = Column(String(50), nullable=True)
    verification_result = Column(Text, nullable=True)  # Did re-test show improvement?

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserDailyLogin(Base):
    """Track daily logins for usage analytics."""
    __tablename__ = 'user_daily_logins'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    login_date = Column(DateTime, nullable=False, index=True)  # Date only (time set to midnight)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref=backref("daily_logins", cascade="all, delete-orphan"))


class ErrorLog(Base):
    """Application error logging for debugging and monitoring."""
    __tablename__ = 'error_logs'

    id = Column(Integer, primary_key=True)

    # Error details
    error_type = Column(String(100), nullable=False, index=True)  # Exception class name
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)

    # Context
    page = Column(String(100), nullable=True, index=True)  # Which page/module
    function = Column(String(100), nullable=True)  # Function name if available
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    profile_id = Column(Integer, nullable=True)

    # Request context
    session_id = Column(String(100), nullable=True)  # Streamlit session ID
    user_agent = Column(String(500), nullable=True)
    extra_context = Column(JSON, nullable=True)  # Any additional debug info

    # Environment
    environment = Column(String(20), nullable=True)  # production, staging, development

    # Status tracking
    status = Column(String(20), default='new', index=True)  # new, reviewed, fixed, ignored
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    fix_notes = Column(Text, nullable=True)

    # Email notification
    email_sent = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="errors")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
