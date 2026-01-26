"""
AI Advisor routes for the API.
Handles chat functionality with the recommendation engine and AI fallback.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import get_db, init_db
from database.models import User, UserProfile, UserHero, AIConversation, AISettings
from database.ai_service import (
    get_ai_settings,
    check_rate_limit,
    record_ai_request,
    log_ai_conversation
)
from api.routes.auth import get_current_user
from engine.recommendation_engine import get_engine

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    force_ai: bool = False


class AskResponse(BaseModel):
    answer: str
    source: str  # 'rules', 'ai', 'error'
    category: Optional[str] = None
    recommendations: List[dict] = []
    lineup: Optional[dict] = None
    conversation_id: Optional[int] = None


class ConversationResponse(BaseModel):
    id: int
    question: str
    answer: str
    source: str
    created_at: datetime
    rating: Optional[int] = None
    is_helpful: Optional[bool] = None


class RateRequest(BaseModel):
    conversation_id: int
    rating: Optional[int] = None
    is_helpful: Optional[bool] = None


@router.post("/ask", response_model=AskResponse)
def ask_advisor(
    request: AskRequest,
    current_user: User = Depends(get_current_user)
):
    """Ask the AI advisor a question."""
    init_db()
    db = get_db()

    try:
        # Get AI settings
        settings = get_ai_settings(db)

        # Check if AI is enabled (for AI fallback)
        ai_mode = settings.mode if settings else "on"

        # Get user's profile
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found. Please set up your profile first.")

        # Get user's heroes
        user_heroes = db.query(UserHero).filter(
            UserHero.profile_id == profile.id
        ).all()

        # Build user snapshot for logging
        user_snapshot = {
            "profile": {
                "furnace_level": profile.furnace_level,
                "spending_profile": profile.spending_profile,
                "priority_focus": profile.priority_focus,
                "alliance_role": profile.alliance_role,
                "is_farm_account": profile.is_farm_account
            },
            "hero_count": len(user_heroes)
        }

        # Get engine and ask
        engine = get_engine()

        # Check rate limit for AI-only requests
        if request.force_ai:
            if ai_mode == "off":
                raise HTTPException(status_code=400, detail="AI is currently disabled")

            if ai_mode != "unlimited":
                allowed, message, remaining = check_rate_limit(db, current_user)
                if not allowed:
                    raise HTTPException(status_code=429, detail=message)

        # Ask the engine
        result = engine.ask(
            profile=profile,
            user_heroes=user_heroes,
            question=request.question,
            force_ai=request.force_ai
        )

        answer = result.get("answer", "I couldn't process your question.")
        source = result.get("source", "rules")
        category = result.get("category")
        recommendations = result.get("recommendations", [])
        lineup = result.get("lineup")

        # Log the conversation
        conversation = AIConversation(
            user_id=current_user.id,
            profile_id=profile.id,
            question=request.question,
            answer=answer,
            context_summary=f"F{profile.furnace_level}, {profile.spending_profile}, {len(user_heroes)} heroes",
            user_snapshot=json.dumps(user_snapshot),
            provider="rules" if source == "rules" else (settings.primary_provider if settings else "openai"),
            model="rule_engine" if source == "rules" else (settings.primary_model if settings else "gpt-4o-mini"),
            routed_to=source,
            created_at=datetime.utcnow()
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # Record usage if AI was used
        if source == "ai":
            record_ai_request(db, current_user)

        return {
            "answer": answer,
            "source": source,
            "category": category,
            "recommendations": recommendations,
            "lineup": lineup,
            "conversation_id": conversation.id
        }

    finally:
        db.close()


@router.get("/history", response_model=List[ConversationResponse])
def get_conversation_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get user's recent conversation history."""
    init_db()
    db = get_db()

    try:
        conversations = db.query(AIConversation).filter(
            AIConversation.user_id == current_user.id
        ).order_by(AIConversation.created_at.desc()).limit(limit).all()

        result = []
        for conv in conversations:
            result.append({
                "id": conv.id,
                "question": conv.question,
                "answer": conv.answer,
                "source": conv.routed_to or "rules",
                "created_at": conv.created_at,
                "rating": conv.rating,
                "is_helpful": conv.is_helpful
            })

        return result

    finally:
        db.close()


@router.post("/rate")
def rate_conversation(
    request: RateRequest,
    current_user: User = Depends(get_current_user)
):
    """Rate a conversation (thumbs up/down or 1-5 stars)."""
    init_db()
    db = get_db()

    try:
        conversation = db.query(AIConversation).filter(
            AIConversation.id == request.conversation_id,
            AIConversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if request.rating is not None:
            conversation.rating = request.rating
        if request.is_helpful is not None:
            conversation.is_helpful = request.is_helpful

        db.commit()

        return {"status": "success", "message": "Rating saved"}

    finally:
        db.close()


@router.get("/status")
def get_advisor_status(current_user: User = Depends(get_current_user)):
    """Get AI advisor status and usage info."""
    init_db()
    db = get_db()

    try:
        settings = get_ai_settings(db)

        if not settings:
            return {
                "ai_enabled": False,
                "mode": "off",
                "daily_limit": 0,
                "requests_today": 0,
                "requests_remaining": 0
            }

        # Get user's usage
        user = db.query(User).filter(User.id == current_user.id).first()
        requests_today = user.ai_requests_today if user else 0

        daily_limit = settings.daily_limit_admin if current_user.role == "admin" else settings.daily_limit_free

        if settings.mode == "unlimited":
            requests_remaining = 999
        else:
            requests_remaining = max(0, daily_limit - requests_today)

        return {
            "ai_enabled": settings.mode != "off",
            "mode": settings.mode,
            "daily_limit": daily_limit,
            "requests_today": requests_today,
            "requests_remaining": requests_remaining,
            "primary_provider": settings.primary_provider
        }

    finally:
        db.close()
