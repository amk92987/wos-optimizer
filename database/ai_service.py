"""
AI Service - Rate limiting, logging, and settings management for AI features.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any, List
from sqlalchemy.orm import Session

from database.models import User, UserProfile, UserHero, UserChiefGear, UserChiefCharm, AIConversation, AISettings


def get_ai_settings(db: Session) -> AISettings:
    """Get or create the global AI settings (singleton)."""
    settings = db.query(AISettings).first()
    if not settings:
        settings = AISettings(mode='off')
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def get_ai_mode(db: Session) -> str:
    """Get current AI mode: 'off', 'on', or 'unlimited'."""
    settings = get_ai_settings(db)
    return settings.mode


def set_ai_mode(db: Session, mode: str, admin_id: int = None) -> AISettings:
    """Set the AI mode. Mode must be 'off', 'on', or 'unlimited'."""
    if mode not in ('off', 'on', 'unlimited'):
        raise ValueError(f"Invalid AI mode: {mode}. Must be 'off', 'on', or 'unlimited'.")

    settings = get_ai_settings(db)
    settings.mode = mode
    settings.updated_at = datetime.utcnow()
    if admin_id:
        settings.updated_by = admin_id
    db.commit()
    return settings


def check_rate_limit(db: Session, user: User) -> Tuple[bool, str, int]:
    """
    Check if user can make an AI request.

    Returns:
        Tuple of (allowed: bool, message: str, remaining: int)
    """
    settings = get_ai_settings(db)

    # Check mode
    if settings.mode == 'off':
        return False, "AI features are currently disabled.", 0

    if settings.mode == 'unlimited':
        return True, "Unlimited mode", -1  # -1 means unlimited

    # Mode is 'on' - check rate limits
    is_admin = user.role == 'admin'
    daily_limit = settings.daily_limit_admin if is_admin else settings.daily_limit_free

    # Reset daily count if needed
    today = datetime.utcnow().date()
    if user.ai_request_reset_date is None or user.ai_request_reset_date.date() < today:
        user.ai_requests_today = 0
        user.ai_request_reset_date = datetime.utcnow()
        db.commit()

    # Check daily limit
    remaining = daily_limit - user.ai_requests_today
    if remaining <= 0:
        return False, f"Daily limit reached ({daily_limit} requests). Resets at midnight UTC.", 0

    # Check cooldown
    if user.last_ai_request and settings.cooldown_seconds > 0:
        cooldown_end = user.last_ai_request + timedelta(seconds=settings.cooldown_seconds)
        if datetime.utcnow() < cooldown_end:
            wait_seconds = (cooldown_end - datetime.utcnow()).seconds
            return False, f"Please wait {wait_seconds} seconds before your next request.", remaining

    return True, f"{remaining} requests remaining today", remaining


def record_ai_request(db: Session, user: User) -> None:
    """Record that a user made an AI request (for rate limiting)."""
    user.ai_requests_today = (user.ai_requests_today or 0) + 1
    user.last_ai_request = datetime.utcnow()
    db.commit()


def build_user_snapshot(db: Session, profile_id: int) -> Optional[str]:
    """
    Build a JSON snapshot of user's state at time of question.
    Captures profile, top heroes, gear, and charms for training data context.

    Returns JSON string or None if profile not found.
    """
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile:
        return None

    # Get top 10 heroes by level
    heroes = db.query(UserHero).filter(
        UserHero.profile_id == profile_id
    ).order_by(UserHero.level.desc()).limit(10).all()

    # Get chief gear
    chief_gear = db.query(UserChiefGear).filter(
        UserChiefGear.profile_id == profile_id
    ).first()

    # Get chief charms
    chief_charms = db.query(UserChiefCharm).filter(
        UserChiefCharm.profile_id == profile_id
    ).first()

    snapshot = {
        'timestamp': datetime.utcnow().isoformat(),
        'profile': {
            'name': profile.name,
            'furnace_level': profile.furnace_level,
            'server_age_days': profile.server_age_days,
            'spending_profile': profile.spending_profile,
            'alliance_role': profile.alliance_role,
            'state_number': profile.state_number,
            'is_farm_account': profile.is_farm_account,
            'priorities': {
                'svs': profile.priority_svs,
                'rally': profile.priority_rally,
                'castle': profile.priority_castle_battle,
                'exploration': profile.priority_exploration,
                'gathering': profile.priority_gathering,
            }
        },
        'heroes': [
            {
                'name': h.hero.name if h.hero else 'Unknown',
                'level': h.level,
                'stars': h.stars,
                'exp_skills': [h.expedition_skill_1_level, h.expedition_skill_2_level, h.expedition_skill_3_level],
                'expl_skills': [h.exploration_skill_1_level, h.exploration_skill_2_level, h.exploration_skill_3_level],
            }
            for h in heroes
        ],
        'chief_gear': {
            'ring': chief_gear.ring_quality if chief_gear else 1,
            'amulet': chief_gear.amulet_quality if chief_gear else 1,
            'helmet': chief_gear.helmet_quality if chief_gear else 1,
            'armor': chief_gear.armor_quality if chief_gear else 1,
            'gloves': chief_gear.gloves_quality if chief_gear else 1,
            'boots': chief_gear.boots_quality if chief_gear else 1,
        } if chief_gear else None,
        'chief_charms': {
            'cap': [chief_charms.cap_protection, chief_charms.cap_keenness, chief_charms.cap_vision],
            'watch': [chief_charms.watch_protection, chief_charms.watch_keenness, chief_charms.watch_vision],
        } if chief_charms else None,
        'hero_count': len(heroes),
    }

    return json.dumps(snapshot)


def log_ai_conversation(
    db: Session,
    user_id: int,
    question: str,
    answer: str,
    provider: str,
    model: str,
    profile_id: int = None,
    context_summary: str = None,
    user_snapshot: str = None,
    routed_to: str = None,
    rule_ids_matched: str = None,
    tokens_input: int = None,
    tokens_output: int = None,
    response_time_ms: int = None,
    source_page: str = None,
    question_type: str = None,
    thread_id: str = None,
    thread_title: str = None
) -> AIConversation:
    """
    Log an AI conversation for training data collection.

    Args:
        profile_id: Which profile was active when question was asked
        user_snapshot: JSON blob of user's state (call build_user_snapshot)
        routed_to: 'rules', 'ai', or 'hybrid'
        rule_ids_matched: Comma-separated list of rule IDs that matched

    Returns the created AIConversation object.
    """
    # Auto-build snapshot if profile_id provided but no snapshot
    if profile_id and not user_snapshot:
        user_snapshot = build_user_snapshot(db, profile_id)

    conversation = AIConversation(
        user_id=user_id,
        profile_id=profile_id,
        question=question,
        answer=answer,
        provider=provider,
        model=model,
        context_summary=context_summary,
        user_snapshot=user_snapshot,
        routed_to=routed_to,
        rule_ids_matched=rule_ids_matched,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        response_time_ms=response_time_ms,
        source_page=source_page,
        question_type=question_type,
        thread_id=thread_id,
        thread_title=thread_title
    )
    db.add(conversation)

    # Update global stats
    settings = get_ai_settings(db)
    settings.total_requests = (settings.total_requests or 0) + 1
    if tokens_input and tokens_output:
        settings.total_tokens_used = (settings.total_tokens_used or 0) + tokens_input + tokens_output

    db.commit()
    db.refresh(conversation)
    return conversation


def rate_conversation(
    db: Session,
    conversation_id: int,
    is_helpful: bool = None,
    rating: int = None,
    user_feedback: str = None
) -> Optional[AIConversation]:
    """
    Rate an AI conversation (user feedback).

    Args:
        conversation_id: The conversation to rate
        is_helpful: True for thumbs up, False for thumbs down
        rating: 1-5 rating
        user_feedback: Optional text feedback

    Returns the updated conversation or None if not found.
    """
    conversation = db.query(AIConversation).filter(AIConversation.id == conversation_id).first()
    if not conversation:
        return None

    if is_helpful is not None:
        conversation.is_helpful = is_helpful
    if rating is not None:
        conversation.rating = max(1, min(5, rating))  # Clamp to 1-5
    if user_feedback is not None:
        conversation.user_feedback = user_feedback[:500]  # Limit length

    db.commit()
    return conversation


def curate_conversation(
    db: Session,
    conversation_id: int,
    is_good_example: bool = None,
    is_bad_example: bool = None,
    admin_notes: str = None
) -> Optional[AIConversation]:
    """
    Admin curation of conversation for training data.

    Args:
        conversation_id: The conversation to curate
        is_good_example: Mark as good training data
        is_bad_example: Mark as bad (hallucination, wrong info)
        admin_notes: Admin notes

    Returns the updated conversation or None if not found.
    """
    conversation = db.query(AIConversation).filter(AIConversation.id == conversation_id).first()
    if not conversation:
        return None

    if is_good_example is not None:
        conversation.is_good_example = is_good_example
    if is_bad_example is not None:
        conversation.is_bad_example = is_bad_example
    if admin_notes is not None:
        conversation.admin_notes = admin_notes[:500]

    db.commit()
    return conversation


def get_training_data(db: Session, good_only: bool = True) -> list:
    """
    Export conversations for training data.

    Args:
        good_only: If True, only return conversations marked as good examples

    Returns list of dicts with question/answer pairs.
    """
    query = db.query(AIConversation)

    if good_only:
        query = query.filter(AIConversation.is_good_example == True)
    else:
        # Exclude bad examples
        query = query.filter(AIConversation.is_bad_example != True)

    conversations = query.order_by(AIConversation.created_at.desc()).all()

    return [
        {
            'question': c.question,
            'answer': c.answer,
            'context': c.context_summary,
            'user_snapshot': json.loads(c.user_snapshot) if c.user_snapshot else None,
            'routed_to': c.routed_to,
            'rule_ids_matched': c.rule_ids_matched,
            'rating': c.rating,
            'is_helpful': c.is_helpful,
            'admin_notes': c.admin_notes
        }
        for c in conversations
    ]


def get_recent_conversations(db: Session, user_id: int, limit: int = 5) -> List[AIConversation]:
    """
    Get recent AI conversations for a user.

    Args:
        db: Database session
        user_id: The user's ID
        limit: Maximum number of conversations to return

    Returns:
        List of recent AIConversation objects, most recent first.
    """
    return db.query(AIConversation).filter(
        AIConversation.user_id == user_id
    ).order_by(AIConversation.created_at.desc()).limit(limit).all()


def toggle_favorite(db: Session, conversation_id: int, user_id: int) -> bool:
    """
    Toggle the favorite status of a conversation.

    Args:
        db: Database session
        conversation_id: The conversation ID
        user_id: The user's ID (for security - only owner can favorite)

    Returns:
        New favorite status (True if now favorited, False if unfavorited)
    """
    conv = db.query(AIConversation).filter(
        AIConversation.id == conversation_id,
        AIConversation.user_id == user_id
    ).first()

    if conv:
        conv.is_favorite = not (conv.is_favorite or False)
        db.commit()
        return conv.is_favorite
    return False


def get_favorite_conversations(db: Session, user_id: int, limit: int = 20) -> List[AIConversation]:
    """
    Get favorited conversations for a user.

    Args:
        db: Database session
        user_id: The user's ID
        limit: Maximum number to return

    Returns:
        List of favorited AIConversation objects, most recent first.
    """
    return db.query(AIConversation).filter(
        AIConversation.user_id == user_id,
        AIConversation.is_favorite == True
    ).order_by(AIConversation.created_at.desc()).limit(limit).all()


def get_ai_stats(db: Session) -> Dict[str, Any]:
    """Get AI usage statistics for admin dashboard."""
    settings = get_ai_settings(db)

    # Count conversations
    total_conversations = db.query(AIConversation).count()
    good_examples = db.query(AIConversation).filter(AIConversation.is_good_example == True).count()
    bad_examples = db.query(AIConversation).filter(AIConversation.is_bad_example == True).count()
    rated_conversations = db.query(AIConversation).filter(AIConversation.rating != None).count()

    # Average rating
    from sqlalchemy import func
    avg_rating = db.query(func.avg(AIConversation.rating)).filter(AIConversation.rating != None).scalar()

    # Helpful ratio
    helpful_count = db.query(AIConversation).filter(AIConversation.is_helpful == True).count()
    unhelpful_count = db.query(AIConversation).filter(AIConversation.is_helpful == False).count()

    # Routing stats
    rules_count = db.query(AIConversation).filter(AIConversation.routed_to == 'rules').count()
    ai_count = db.query(AIConversation).filter(AIConversation.routed_to == 'ai').count()
    hybrid_count = db.query(AIConversation).filter(AIConversation.routed_to == 'hybrid').count()

    return {
        'mode': settings.mode,
        'total_requests': settings.total_requests or 0,
        'total_tokens': settings.total_tokens_used or 0,
        'daily_limit_free': settings.daily_limit_free,
        'daily_limit_admin': settings.daily_limit_admin,
        'cooldown_seconds': settings.cooldown_seconds,
        'primary_provider': settings.primary_provider,
        'openai_model': settings.openai_model,
        'anthropic_model': settings.anthropic_model,
        'total_conversations': total_conversations,
        'good_examples': good_examples,
        'bad_examples': bad_examples,
        'rated_conversations': rated_conversations,
        'average_rating': round(avg_rating, 2) if avg_rating else None,
        'helpful_count': helpful_count,
        'unhelpful_count': unhelpful_count,
        # Routing stats
        'routed_to_rules': rules_count,
        'routed_to_ai': ai_count,
        'routed_to_hybrid': hybrid_count,
        'rules_percentage': round(rules_count / total_conversations * 100, 1) if total_conversations > 0 else 0,
    }


# ============================================
# CONVERSATION THREADING
# ============================================

def create_thread_id() -> str:
    """Generate a new unique thread ID."""
    import uuid
    return str(uuid.uuid4())


def generate_thread_title(question: str) -> str:
    """Generate a thread title from the first question (truncated)."""
    # Clean up and truncate
    title = question.strip()
    if len(title) > 60:
        title = title[:57] + "..."
    return title


def get_user_threads(db: Session, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get conversation threads for a user, grouped by thread_id.

    Returns list of thread summaries with:
    - thread_id
    - thread_title (from first message or auto-generated)
    - message_count
    - last_message_time
    - first_question_preview
    """
    from sqlalchemy import func, desc

    # Get threads with their stats
    threads = db.query(
        AIConversation.thread_id,
        AIConversation.thread_title,
        func.count(AIConversation.id).label('message_count'),
        func.max(AIConversation.created_at).label('last_message'),
        func.min(AIConversation.created_at).label('first_message')
    ).filter(
        AIConversation.user_id == user_id,
        AIConversation.thread_id != None
    ).group_by(
        AIConversation.thread_id
    ).order_by(desc('last_message')).limit(limit).all()

    result = []
    for thread in threads:
        # Get first question for preview
        first_conv = db.query(AIConversation).filter(
            AIConversation.thread_id == thread.thread_id
        ).order_by(AIConversation.created_at.asc()).first()

        result.append({
            'thread_id': thread.thread_id,
            'title': thread.thread_title or (first_conv.question[:50] + "..." if first_conv and len(first_conv.question) > 50 else first_conv.question if first_conv else "Chat"),
            'message_count': thread.message_count,
            'last_message': thread.last_message,
            'first_question': first_conv.question if first_conv else None
        })

    return result


def get_thread_conversations(db: Session, thread_id: str, user_id: int) -> List[AIConversation]:
    """
    Get all conversations in a thread, ordered by creation time.

    Args:
        db: Database session
        thread_id: The thread UUID
        user_id: User ID for security (only return threads owned by this user)

    Returns:
        List of AIConversation objects in chronological order.
    """
    return db.query(AIConversation).filter(
        AIConversation.thread_id == thread_id,
        AIConversation.user_id == user_id
    ).order_by(AIConversation.created_at.asc()).all()


def get_standalone_conversations(db: Session, user_id: int, limit: int = 10) -> List[AIConversation]:
    """
    Get recent conversations that are NOT part of a thread (single Q&A).

    Args:
        db: Database session
        user_id: The user's ID
        limit: Maximum number to return

    Returns:
        List of AIConversation objects without a thread_id.
    """
    return db.query(AIConversation).filter(
        AIConversation.user_id == user_id,
        AIConversation.thread_id == None
    ).order_by(AIConversation.created_at.desc()).limit(limit).all()
