"""
AI Service - Rate limiting, logging, and settings management for AI features.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session

from database.models import User, AIConversation, AISettings


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


def log_ai_conversation(
    db: Session,
    user_id: int,
    question: str,
    answer: str,
    provider: str,
    model: str,
    context_summary: str = None,
    tokens_input: int = None,
    tokens_output: int = None,
    response_time_ms: int = None,
    source_page: str = None,
    question_type: str = None
) -> AIConversation:
    """
    Log an AI conversation for training data collection.

    Returns the created AIConversation object.
    """
    conversation = AIConversation(
        user_id=user_id,
        question=question,
        answer=answer,
        provider=provider,
        model=model,
        context_summary=context_summary,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        response_time_ms=response_time_ms,
        source_page=source_page,
        question_type=question_type
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
            'rating': c.rating,
            'is_helpful': c.is_helpful,
            'admin_notes': c.admin_notes
        }
        for c in conversations
    ]


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
        'unhelpful_count': unhelpful_count
    }
