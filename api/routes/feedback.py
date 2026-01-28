"""
User Feedback Routes - Submit and manage feedback.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database.db import init_db, get_db
from database.models import User, Feedback
from api.routes.auth import get_current_user

router = APIRouter()


class FeedbackCreate(BaseModel):
    category: str  # bug, feature, bad_recommendation, data_error, other
    description: str
    page: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    category: str
    description: str
    page: Optional[str]
    status: str
    created_at: datetime


@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    request: FeedbackCreate,
    current_user: User = Depends(get_current_user)
):
    """Submit user feedback."""
    init_db()
    db = get_db()

    try:
        # Validate category
        valid_categories = ['bug', 'feature', 'bad_recommendation', 'data_error', 'other']
        if request.category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {valid_categories}")

        # Validate description
        if not request.description or len(request.description.strip()) < 10:
            raise HTTPException(status_code=400, detail="Description must be at least 10 characters")

        # Determine initial status based on category
        if request.category == 'bug':
            status = 'pending_fix'
        elif request.category in ['feature', 'bad_recommendation']:
            status = 'pending_update'
        else:
            status = 'new'

        feedback = Feedback(
            user_id=current_user.id,
            category=request.category,
            description=request.description.strip(),
            page=request.page,
            status=status,
            created_at=datetime.utcnow()
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return {
            "id": feedback.id,
            "category": feedback.category,
            "description": feedback.description,
            "page": feedback.page,
            "status": feedback.status,
            "created_at": feedback.created_at
        }

    finally:
        db.close()
