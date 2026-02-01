"""Migrate data from PostgreSQL (Lightsail) to DynamoDB (serverless).

Reads all tables from the production PostgreSQL database via SQLAlchemy
and writes items to DynamoDB MainTable and AdminTable following the
single-table design defined in backend/common/ repos.

Usage:
    python scripts/migrate_data.py \
        --db-url "postgresql://user:pass@host:5432/wos" \
        --region us-east-1 \
        --stage dev

    # Preview without writing:
    python scripts/migrate_data.py --db-url "..." --dry-run
"""

import argparse
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so we can import models
# ---------------------------------------------------------------------------
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.models import (
    User, UserProfile, Hero, UserHero, UserChiefGear, UserChiefCharm,
    UserInventory, Item, AIConversation, AISettings, Feedback,
    FeatureFlag, Announcement, AuditLog, AdminMetrics, ErrorLog,
    UserNotification, UserDailyLogin, MessageThread, Message,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_ulid() -> str:
    """Generate a ULID-like sortable unique ID (matches repo convention)."""
    ts = int(time.time() * 1000)
    rand = uuid.uuid4().hex[:16]
    return f"{ts:012x}{rand}"


def _ts(dt) -> str:
    """Convert a datetime (or None) to ISO-8601 string."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _strip_none(d: dict) -> dict:
    """Remove keys with None or empty-string values for DynamoDB."""
    return {k: v for k, v in d.items() if v is not None and v != ""}


def _to_decimal(value):
    """Convert Python numerics to Decimal for DynamoDB."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, int) and not isinstance(value, bool):
        return Decimal(value)
    if isinstance(value, dict):
        return {k: _to_decimal(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_decimal(v) for v in value]
    return value


def _prepare(item: dict) -> dict:
    return _to_decimal(_strip_none(item))


# ---------------------------------------------------------------------------
# DynamoDB table name helpers
# ---------------------------------------------------------------------------

def _table_name(base: str, stage: str) -> str:
    """Return stage-prefixed table name, e.g. wos-main-dev."""
    return f"wos-{base}-{stage}"


# ---------------------------------------------------------------------------
# ID mapping  --  old integer PK  -->  new string ID
# ---------------------------------------------------------------------------

class IdMapper:
    """Generates deterministic string IDs for old integer PKs.

    For users that already have a cognito_sub we reuse it.
    For profiles we generate ULID-like strings.
    """

    def __init__(self):
        self._user_map: dict[int, str] = {}
        self._profile_map: dict[int, str] = {}
        self._hero_name_map: dict[int, str] = {}   # hero.id -> hero.name

    def user_id(self, old_id: int, cognito_sub: str | None = None) -> str:
        if old_id not in self._user_map:
            self._user_map[old_id] = cognito_sub or str(uuid.uuid4())
        return self._user_map[old_id]

    def profile_id(self, old_id: int) -> str:
        if old_id not in self._profile_map:
            self._profile_map[old_id] = _generate_ulid()
        return self._profile_map[old_id]

    def set_hero_name(self, hero_id: int, name: str):
        self._hero_name_map[hero_id] = name

    def hero_name(self, hero_id: int) -> str:
        return self._hero_name_map.get(hero_id, f"Unknown#{hero_id}")


# ---------------------------------------------------------------------------
# Migration functions
# ---------------------------------------------------------------------------

def migrate_users(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate users -> MainTable USER# items + uniqueness guards."""
    users = session.query(User).all()
    count = 0
    items = []

    for u in users:
        uid = ids.user_id(u.id, u.cognito_sub)

        user_item = _prepare({
            "PK": f"USER#{uid}",
            "SK": "METADATA",
            "entity_type": "USER",
            "user_id": uid,
            "old_pg_id": u.id,
            "email": u.email or "",
            "username": u.username,
            "password_hash": u.password_hash or "",
            "role": u.role or "user",
            "theme": u.theme or "dark",
            "is_active": u.is_active if u.is_active is not None else True,
            "is_verified": u.is_verified if u.is_verified is not None else False,
            "is_test_account": u.is_test_account if u.is_test_account is not None else False,
            "cognito_sub": u.cognito_sub or "",
            "ai_requests_today": u.ai_requests_today or 0,
            "ai_access_level": u.ai_access_level or "limited",
            "ai_daily_limit": u.ai_daily_limit,
            "created_at": _ts(u.created_at),
            "updated_at": _ts(u.updated_at),
            "last_login": _ts(u.last_login),
        })
        items.append(user_item)

        # Email uniqueness guard
        if u.email:
            items.append(_prepare({
                "PK": "UNIQUE#EMAIL",
                "SK": u.email.lower(),
                "user_id": uid,
            }))

        # Username uniqueness guard
        items.append(_prepare({
            "PK": "UNIQUE#USERNAME",
            "SK": u.username.lower(),
            "user_id": uid,
        }))
        count += 1

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  Users: {count} users ({len(items)} items including guards)")
    return count


def migrate_profiles(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate user_profile -> MainTable USER#/PROFILE# items."""
    profiles = session.query(UserProfile).all()
    items = []

    for p in profiles:
        if p.user_id is None:
            continue
        uid = ids.user_id(p.user_id)
        pid = ids.profile_id(p.id)

        linked_main = None
        if p.linked_main_profile_id:
            linked_main = ids.profile_id(p.linked_main_profile_id)

        item = _prepare({
            "PK": f"USER#{uid}",
            "SK": f"PROFILE#{pid}",
            "profile_id": pid,
            "user_id": uid,
            "old_pg_id": p.id,
            "name": p.name or "Chief",
            "is_default": p.is_default if p.is_default is not None else False,
            "state_number": p.state_number,
            "server_age_days": p.server_age_days or 0,
            "furnace_level": p.furnace_level or 1,
            "furnace_fc_level": p.furnace_fc_level,
            "spending_profile": p.spending_profile or "f2p",
            "priority_focus": p.priority_focus or "balanced_growth",
            "alliance_role": p.alliance_role or "filler",
            "priority_svs": p.priority_svs if p.priority_svs is not None else 5,
            "priority_rally": p.priority_rally if p.priority_rally is not None else 4,
            "priority_castle_battle": p.priority_castle_battle if p.priority_castle_battle is not None else 4,
            "priority_exploration": p.priority_exploration if p.priority_exploration is not None else 3,
            "priority_gathering": p.priority_gathering if p.priority_gathering is not None else 2,
            "svs_wins": p.svs_wins or 0,
            "svs_losses": p.svs_losses or 0,
            "last_svs_date": _ts(p.last_svs_date),
            "is_farm_account": p.is_farm_account if p.is_farm_account is not None else False,
            "linked_main_profile_id": linked_main,
            "created_at": _ts(p.created_at),
            "updated_at": _ts(p.updated_at),
            "deleted_at": _ts(p.deleted_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  Profiles: {len(items)} profiles")
    return len(items)


def migrate_heroes(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate user_heroes -> MainTable PROFILE#/HERO# items."""
    # Pre-load hero names from the Hero reference table
    for hero in session.query(Hero).all():
        ids.set_hero_name(hero.id, hero.name)

    user_heroes = session.query(UserHero).all()
    items = []

    for uh in user_heroes:
        pid = ids.profile_id(uh.profile_id)
        hero_name = ids.hero_name(uh.hero_id)

        item = _prepare({
            "PK": f"PROFILE#{pid}",
            "SK": f"HERO#{hero_name}",
            "hero_name": hero_name,
            "profile_id": pid,
            "level": uh.level or 1,
            "stars": uh.stars or 0,
            "ascension_tier": uh.ascension_tier or 0,
            # Exploration skills
            "exploration_skill_1_level": uh.exploration_skill_1_level or 1,
            "exploration_skill_2_level": uh.exploration_skill_2_level or 1,
            "exploration_skill_3_level": uh.exploration_skill_3_level or 1,
            # Expedition skills
            "expedition_skill_1_level": uh.expedition_skill_1_level or 1,
            "expedition_skill_2_level": uh.expedition_skill_2_level or 1,
            "expedition_skill_3_level": uh.expedition_skill_3_level or 1,
            # Gear slots
            "gear_slot1_quality": uh.gear_slot1_quality or 0,
            "gear_slot1_level": uh.gear_slot1_level or 0,
            "gear_slot1_mastery": uh.gear_slot1_mastery or 0,
            "gear_slot2_quality": uh.gear_slot2_quality or 0,
            "gear_slot2_level": uh.gear_slot2_level or 0,
            "gear_slot2_mastery": uh.gear_slot2_mastery or 0,
            "gear_slot3_quality": uh.gear_slot3_quality or 0,
            "gear_slot3_level": uh.gear_slot3_level or 0,
            "gear_slot3_mastery": uh.gear_slot3_mastery or 0,
            "gear_slot4_quality": uh.gear_slot4_quality or 0,
            "gear_slot4_level": uh.gear_slot4_level or 0,
            "gear_slot4_mastery": uh.gear_slot4_mastery or 0,
            # Mythic gear
            "mythic_gear_unlocked": uh.mythic_gear_unlocked if uh.mythic_gear_unlocked is not None else False,
            "mythic_gear_quality": uh.mythic_gear_quality or 0,
            "mythic_gear_level": uh.mythic_gear_level or 0,
            "mythic_gear_mastery": uh.mythic_gear_mastery or 0,
            "exclusive_gear_skill_level": uh.exclusive_gear_skill_level or 0,
            # Metadata
            "owned": True,
            "created_at": _ts(uh.created_at),
            "updated_at": _ts(uh.updated_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  Heroes: {len(items)} user heroes")
    return len(items)


def migrate_chief_gear(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate user_chief_gear -> MainTable PROFILE#/CHIEFGEAR items."""
    gear_rows = session.query(UserChiefGear).all()
    items = []

    for g in gear_rows:
        pid = ids.profile_id(g.profile_id)
        item = _prepare({
            "PK": f"PROFILE#{pid}",
            "SK": "CHIEFGEAR",
            "profile_id": pid,
            "helmet_quality": g.helmet_quality or 1,
            "helmet_level": g.helmet_level or 1,
            "armor_quality": g.armor_quality or 1,
            "armor_level": g.armor_level or 1,
            "gloves_quality": g.gloves_quality or 1,
            "gloves_level": g.gloves_level or 1,
            "boots_quality": g.boots_quality or 1,
            "boots_level": g.boots_level or 1,
            "ring_quality": g.ring_quality or 1,
            "ring_level": g.ring_level or 1,
            "amulet_quality": g.amulet_quality or 1,
            "amulet_level": g.amulet_level or 1,
            "updated_at": _ts(g.updated_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  Chief gear: {len(items)} gear sets")
    return len(items)


def migrate_chief_charms(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate user_chief_charms -> MainTable PROFILE#/CHIEFCHARM items."""
    charm_rows = session.query(UserChiefCharm).all()
    items = []

    for c in charm_rows:
        pid = ids.profile_id(c.profile_id)
        item = _prepare({
            "PK": f"PROFILE#{pid}",
            "SK": "CHIEFCHARM",
            "profile_id": pid,
            "cap_slot_1": c.cap_slot_1 or "1",
            "cap_slot_2": c.cap_slot_2 or "1",
            "cap_slot_3": c.cap_slot_3 or "1",
            "watch_slot_1": c.watch_slot_1 or "1",
            "watch_slot_2": c.watch_slot_2 or "1",
            "watch_slot_3": c.watch_slot_3 or "1",
            "coat_slot_1": c.coat_slot_1 or "1",
            "coat_slot_2": c.coat_slot_2 or "1",
            "coat_slot_3": c.coat_slot_3 or "1",
            "pants_slot_1": c.pants_slot_1 or "1",
            "pants_slot_2": c.pants_slot_2 or "1",
            "pants_slot_3": c.pants_slot_3 or "1",
            "belt_slot_1": c.belt_slot_1 or "1",
            "belt_slot_2": c.belt_slot_2 or "1",
            "belt_slot_3": c.belt_slot_3 or "1",
            "weapon_slot_1": c.weapon_slot_1 or "1",
            "weapon_slot_2": c.weapon_slot_2 or "1",
            "weapon_slot_3": c.weapon_slot_3 or "1",
            "updated_at": _ts(c.updated_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  Chief charms: {len(items)} charm sets")
    return len(items)


def migrate_inventory(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate user_inventory -> MainTable PROFILE#/ITEM# items."""
    inv_rows = session.query(UserInventory).all()
    # Pre-load item names
    item_names = {i.id: i.name for i in session.query(Item).all()}
    items = []

    for inv in inv_rows:
        pid = ids.profile_id(inv.profile_id)
        item_name = item_names.get(inv.item_id, f"Unknown#{inv.item_id}")
        item = _prepare({
            "PK": f"PROFILE#{pid}",
            "SK": f"ITEM#{item_name}",
            "item_name": item_name,
            "profile_id": pid,
            "quantity": inv.quantity or 0,
            "updated_at": _ts(inv.updated_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  Inventory: {len(items)} items")
    return len(items)


def migrate_daily_logins(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate user_daily_logins -> MainTable USER#/LOGIN# items."""
    logins = session.query(UserDailyLogin).all()
    items = []

    for login in logins:
        uid = ids.user_id(login.user_id)
        login_date = login.login_date.strftime("%Y-%m-%d") if login.login_date else ""
        if not login_date:
            continue
        item = _prepare({
            "PK": f"USER#{uid}",
            "SK": f"LOGIN#{login_date}",
            "login_date": login_date,
            "created_at": _ts(login.created_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  Daily logins: {len(items)} records")
    return len(items)


def migrate_ai_conversations(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate ai_conversations -> MainTable USER#/AICONV# items."""
    convos = session.query(AIConversation).all()
    items = []

    for c in convos:
        uid = ids.user_id(c.user_id)
        ulid = _generate_ulid()
        created = _ts(c.created_at) or datetime.now(timezone.utc).isoformat()
        profile_id = ids.profile_id(c.profile_id) if c.profile_id else None

        item = _prepare({
            "PK": f"USER#{uid}",
            "SK": f"AICONV#{created}#{ulid}",
            "conversation_id": ulid,
            "user_id": uid,
            "profile_id": profile_id,
            "question": c.question or "",
            "answer": c.answer or "",
            "context_summary": c.context_summary,
            "user_snapshot": c.user_snapshot,
            "provider": c.provider or "unknown",
            "model": c.model or "unknown",
            "tokens_input": c.tokens_input or 0,
            "tokens_output": c.tokens_output or 0,
            "response_time_ms": c.response_time_ms or 0,
            "routed_to": c.routed_to,
            "rule_ids_matched": c.rule_ids_matched,
            "rating": c.rating,
            "is_helpful": c.is_helpful,
            "user_feedback": c.user_feedback,
            "is_good_example": c.is_good_example if c.is_good_example is not None else False,
            "is_bad_example": c.is_bad_example if c.is_bad_example is not None else False,
            "admin_notes": c.admin_notes,
            "source_page": c.source_page,
            "question_type": c.question_type,
            "is_favorite": c.is_favorite if c.is_favorite is not None else False,
            "thread_id": c.thread_id,
            "thread_title": c.thread_title,
            "created_at": created,
        })
        items.append(item)

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  AI conversations: {len(items)} conversations")
    return len(items)


def migrate_message_threads(session, main_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate message_threads + messages -> MainTable USER#/THREAD# items."""
    threads = session.query(MessageThread).all()
    items = []

    for t in threads:
        uid = ids.user_id(t.user_id)
        thread_ulid = _generate_ulid()

        # Thread metadata
        items.append(_prepare({
            "PK": f"USER#{uid}",
            "SK": f"THREAD#{thread_ulid}",
            "thread_id": thread_ulid,
            "user_id": uid,
            "subject": t.subject or "",
            "is_closed": t.is_closed if t.is_closed is not None else False,
            "created_at": _ts(t.created_at),
            "updated_at": _ts(t.updated_at),
        }))

        # Messages within thread
        for m in t.messages:
            msg_ulid = _generate_ulid()
            sender_uid = ids.user_id(m.sender_id)
            items.append(_prepare({
                "PK": f"THREAD#{thread_ulid}",
                "SK": f"MSG#{_ts(m.created_at)}#{msg_ulid}",
                "message_id": msg_ulid,
                "thread_id": thread_ulid,
                "sender_id": sender_uid,
                "content": m.content or "",
                "is_from_admin": m.is_from_admin if m.is_from_admin is not None else False,
                "is_read": m.is_read if m.is_read is not None else False,
                "read_at": _ts(m.read_at),
                "created_at": _ts(m.created_at),
            }))

    if not dry_run:
        _batch_write(main_table, items)

    print(f"  Message threads: {len(threads)} threads ({len(items)} items)")
    return len(items)


# ---------------------------------------------------------------------------
# Admin table migrations
# ---------------------------------------------------------------------------

def migrate_feature_flags(session, admin_table, dry_run: bool) -> int:
    """Migrate feature_flags -> AdminTable FLAG# items."""
    flags = session.query(FeatureFlag).all()
    items = []

    for f in flags:
        item = _prepare({
            "PK": "FLAG",
            "SK": f.name,
            "name": f.name,
            "description": f.description,
            "is_enabled": f.is_enabled if f.is_enabled is not None else False,
            "value": f.value,
            "enabled_for_roles": json.dumps(f.enabled_for_roles) if f.enabled_for_roles else None,
            "enabled_for_users": json.dumps(f.enabled_for_users) if f.enabled_for_users else None,
            "created_at": _ts(f.created_at),
            "updated_at": _ts(f.updated_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(admin_table, items)

    print(f"  Feature flags: {len(items)} flags")
    return len(items)


def migrate_announcements(session, admin_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate announcements -> AdminTable ANNOUNCE# items."""
    anns = session.query(Announcement).all()
    items = []

    for a in anns:
        ulid = _generate_ulid()
        created_by_uid = ids.user_id(a.created_by) if a.created_by else "unknown"

        item = _prepare({
            "PK": "ANNOUNCE",
            "SK": ulid,
            "announcement_id": ulid,
            "title": a.title or "",
            "message": a.message or "",
            "type": a.type or "info",
            "display_type": a.display_type or "banner",
            "inbox_content": a.inbox_content,
            "is_active": a.is_active if a.is_active is not None else True,
            "show_from": _ts(a.show_from),
            "show_until": _ts(a.show_until),
            "created_by": created_by_uid,
            "created_at": _ts(a.created_at),
            "updated_at": _ts(a.updated_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(admin_table, items)

    print(f"  Announcements: {len(items)} announcements")
    return len(items)


def migrate_feedback(session, admin_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate feedback -> AdminTable FEEDBACK# items."""
    feedback_rows = session.query(Feedback).all()
    items = []

    for f in feedback_rows:
        ulid = _generate_ulid()
        created = _ts(f.created_at) or datetime.now(timezone.utc).isoformat()
        user_uid = ids.user_id(f.user_id) if f.user_id else "anonymous"

        item = _prepare({
            "PK": "FEEDBACK",
            "SK": f"{created}#{ulid}",
            "feedback_id": ulid,
            "user_id": user_uid,
            "category": f.category or "other",
            "description": f.description or "",
            "page": f.page,
            "status": f.status or "new",
            "created_at": created,
        })
        items.append(item)

    if not dry_run:
        _batch_write(admin_table, items)

    print(f"  Feedback: {len(items)} items")
    return len(items)


def migrate_audit_logs(session, admin_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate audit_log -> AdminTable AUDIT#YYYY-MM items."""
    logs = session.query(AuditLog).all()
    items = []

    for log in logs:
        ulid = _generate_ulid()
        created = log.created_at or datetime.now(timezone.utc)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        month = created.strftime("%Y-%m")
        admin_uid = ids.user_id(log.admin_id) if log.admin_id else "unknown"

        item = _prepare({
            "PK": f"AUDIT#{month}",
            "SK": f"{created.isoformat()}#{ulid}",
            "admin_id": admin_uid,
            "admin_username": log.admin_username or "unknown",
            "action": log.action or "",
            "target_type": log.target_type,
            "target_id": str(log.target_id) if log.target_id else None,
            "target_name": log.target_name,
            "details": log.details,
            "created_at": created.isoformat(),
        })
        items.append(item)

    if not dry_run:
        _batch_write(admin_table, items)

    print(f"  Audit logs: {len(items)} entries")
    return len(items)


def migrate_ai_settings(session, admin_table, dry_run: bool) -> int:
    """Migrate ai_settings -> AdminTable SETTINGS/AI item."""
    settings = session.query(AISettings).first()
    if not settings:
        print("  AI settings: no settings found, skipping")
        return 0

    item = _prepare({
        "PK": "SETTINGS",
        "SK": "AI",
        "mode": settings.mode or "on",
        "daily_limit_free": settings.daily_limit_free or 20,
        "daily_limit_admin": settings.daily_limit_admin or 1000,
        "cooldown_seconds": settings.cooldown_seconds or 30,
        "primary_provider": settings.primary_provider or "openai",
        "fallback_provider": settings.fallback_provider,
        "openai_model": settings.openai_model or "gpt-4o-mini",
        "anthropic_model": settings.anthropic_model or "claude-sonnet-4-20250514",
        "total_requests": settings.total_requests or 0,
        "total_tokens_used": settings.total_tokens_used or 0,
        "updated_at": _ts(settings.updated_at),
    })

    if not dry_run:
        admin_table.put_item(Item=item)

    print("  AI settings: 1 item")
    return 1


def migrate_admin_metrics(session, admin_table, dry_run: bool) -> int:
    """Migrate admin_metrics -> AdminTable METRICS/YYYY-MM-DD items."""
    metrics = session.query(AdminMetrics).all()
    items = []

    for m in metrics:
        date_str = m.date.strftime("%Y-%m-%d") if m.date else ""
        if not date_str:
            continue

        item = _prepare({
            "PK": "METRICS",
            "SK": date_str,
            "date": date_str,
            "total_users": m.total_users or 0,
            "new_users": m.new_users or 0,
            "active_users": m.active_users or 0,
            "total_profiles": m.total_profiles or 0,
            "total_heroes_tracked": m.total_heroes_tracked or 0,
            "total_inventory_items": m.total_inventory_items or 0,
            "total_logins": m.total_logins or 0,
            "created_at": _ts(m.created_at),
        })
        items.append(item)

    if not dry_run:
        _batch_write(admin_table, items)

    print(f"  Admin metrics: {len(items)} daily snapshots")
    return len(items)


def migrate_error_logs(session, admin_table, ids: IdMapper, dry_run: bool) -> int:
    """Migrate error_logs -> AdminTable ERROR#YYYY-MM items."""
    errors = session.query(ErrorLog).all()
    items = []

    for e in errors:
        ulid = _generate_ulid()
        created = e.created_at or datetime.now(timezone.utc)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        month = created.strftime("%Y-%m")

        user_uid = ids.user_id(e.user_id) if e.user_id else None

        item = _prepare({
            "PK": f"ERROR#{month}",
            "SK": f"{created.isoformat()}#{ulid}",
            "error_type": e.error_type or "Unknown",
            "error_message": e.error_message or "",
            "stack_trace": e.stack_trace,
            "page": e.page,
            "function": e.function,
            "user_id": user_uid,
            "environment": e.environment,
            "status": e.status or "new",
            "created_at": created.isoformat(),
        })
        items.append(item)

    if not dry_run:
        _batch_write(admin_table, items)

    print(f"  Error logs: {len(items)} entries")
    return len(items)


# ---------------------------------------------------------------------------
# Batch write helper
# ---------------------------------------------------------------------------

def _batch_write(table, items: list[dict]) -> None:
    """Write items using batch_writer (auto-handles 25-item batches)."""
    if not items:
        return
    with table.batch_writer() as writer:
        for item in items:
            writer.put_item(Item=item)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Migrate PostgreSQL data to DynamoDB for the WoS serverless backend."
    )
    parser.add_argument("--db-url", required=True,
                        help="PostgreSQL connection URL (e.g. postgresql://user:pass@host:5432/wos)")
    parser.add_argument("--region", default="us-east-1",
                        help="AWS region for DynamoDB (default: us-east-1)")
    parser.add_argument("--stage", choices=["dev", "live"], default="dev",
                        help="Target stage (determines table name prefix)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Read from PostgreSQL but do not write to DynamoDB")

    args = parser.parse_args()

    # ---- Connect to PostgreSQL ----
    print(f"\n{'='*60}")
    print(f"WoS Data Migration: PostgreSQL -> DynamoDB")
    print(f"{'='*60}")
    print(f"Source:  {args.db_url.split('@')[-1] if '@' in args.db_url else args.db_url}")
    print(f"Target:  wos-main-{args.stage} / wos-admin-{args.stage}")
    print(f"Region:  {args.region}")
    print(f"Dry run: {args.dry_run}")
    print(f"{'='*60}\n")

    engine = create_engine(args.db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # ---- Connect to DynamoDB ----
    dynamodb = boto3.resource("dynamodb", region_name=args.region)
    main_table_name = f"wos-main-{args.stage}"
    admin_table_name = f"wos-admin-{args.stage}"

    main_tbl = dynamodb.Table(main_table_name)
    admin_tbl = dynamodb.Table(admin_table_name)

    if not args.dry_run:
        # Verify tables exist
        try:
            main_tbl.table_status
            admin_tbl.table_status
        except Exception as e:
            print(f"ERROR: Could not access DynamoDB tables. Ensure they exist.")
            print(f"  Main:  {main_table_name}")
            print(f"  Admin: {admin_table_name}")
            print(f"  Error: {e}")
            sys.exit(1)

    ids = IdMapper()
    total = 0

    try:
        print("Migrating MainTable data...")
        print("-" * 40)
        total += migrate_users(session, main_tbl, ids, args.dry_run)
        total += migrate_profiles(session, main_tbl, ids, args.dry_run)
        total += migrate_heroes(session, main_tbl, ids, args.dry_run)
        total += migrate_chief_gear(session, main_tbl, ids, args.dry_run)
        total += migrate_chief_charms(session, main_tbl, ids, args.dry_run)
        total += migrate_inventory(session, main_tbl, ids, args.dry_run)
        total += migrate_daily_logins(session, main_tbl, ids, args.dry_run)
        total += migrate_ai_conversations(session, main_tbl, ids, args.dry_run)
        total += migrate_message_threads(session, main_tbl, ids, args.dry_run)

        print()
        print("Migrating AdminTable data...")
        print("-" * 40)
        total += migrate_feature_flags(session, admin_tbl, args.dry_run)
        total += migrate_announcements(session, admin_tbl, ids, args.dry_run)
        total += migrate_feedback(session, admin_tbl, ids, args.dry_run)
        total += migrate_audit_logs(session, admin_tbl, ids, args.dry_run)
        total += migrate_ai_settings(session, admin_tbl, args.dry_run)
        total += migrate_admin_metrics(session, admin_tbl, args.dry_run)
        total += migrate_error_logs(session, admin_tbl, ids, args.dry_run)

        print()
        print(f"{'='*60}")
        action = "would be written" if args.dry_run else "written"
        print(f"Migration complete! {total} items {action}.")
        print(f"{'='*60}")

        # Save ID mapping for reference (useful for Cognito setup)
        mapping_file = PROJECT_ROOT / "scripts" / f"id_mapping_{args.stage}.json"
        mapping_data = {
            "users": {str(k): v for k, v in ids._user_map.items()},
            "profiles": {str(k): v for k, v in ids._profile_map.items()},
        }
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(mapping_data, f, indent=2)
        print(f"ID mapping saved to: {mapping_file}")

    except Exception as e:
        print(f"\nERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
