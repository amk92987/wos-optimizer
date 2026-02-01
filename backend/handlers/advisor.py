"""AI Advisor Lambda handler."""

import json
import time

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from backend.common.auth import get_effective_user_id
from backend.common.exceptions import AppError, ValidationError, RateLimitError
from backend.common import ai_repo, profile_repo, hero_repo, user_repo

app = APIGatewayHttpResolver()
logger = Logger()


@app.post("/api/advisor/ask")
def ask_advisor():
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}

    question = body.get("question", "").strip()
    if not question:
        raise ValidationError("Question is required")

    thread_id = body.get("thread_id")

    # Check rate limits
    user = user_repo.get_user(user_id)
    settings = ai_repo.get_ai_settings()
    allowed, message, remaining = ai_repo.check_rate_limit(user or {}, settings)
    if not allowed:
        raise RateLimitError(message)

    # Load user context
    profile = profile_repo.get_or_create_profile(user_id)
    profile_id = profile["profile_id"]
    heroes = hero_repo.get_heroes(profile_id)

    # Try rules engine first, fall back to AI
    from engine.recommendation_engine import get_engine
    engine = get_engine()

    start_ms = int(time.time() * 1000)
    result = engine.ask(question=question, profile=profile, heroes=heroes)
    elapsed_ms = int(time.time() * 1000) - start_ms

    source = result.get("source", "rules")
    answer = result.get("answer", "")
    provider = result.get("provider", "rules")
    model = result.get("model", "rule_engine")
    tokens_in = result.get("tokens_input", 0)
    tokens_out = result.get("tokens_output", 0)

    # Log conversation
    conversation = ai_repo.log_conversation(
        user_id=user_id,
        profile_id=profile_id,
        question=question,
        answer=answer,
        source=source,
        provider=provider,
        model=model,
        tokens_input=tokens_in,
        tokens_output=tokens_out,
        response_time_ms=elapsed_ms,
        thread_id=thread_id,
    )

    # Increment AI request counter if AI was used
    if source == "ai":
        user_repo.increment_ai_requests(user_id)

    return {
        "answer": answer,
        "source": source,
        "conversation_id": conversation.get("conversation_id"),
        "thread_id": thread_id,
        "remaining_requests": remaining - (1 if source == "ai" else 0),
    }


@app.get("/api/advisor/history")
def get_history():
    user_id = get_effective_user_id(app.current_event.raw_event)
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "10"))

    conversations = ai_repo.get_conversation_history(user_id, limit=limit)
    return {"conversations": conversations}


@app.post("/api/advisor/rate")
def rate_conversation():
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}

    conversation_sk = body.get("conversation_sk")
    if not conversation_sk:
        raise ValidationError("conversation_sk is required")

    allowed_fields = {"rating", "is_helpful", "user_feedback", "is_favorite"}
    updates = {k: v for k, v in body.items() if k in allowed_fields}

    if not updates:
        raise ValidationError("No valid rating fields provided")

    result = ai_repo.rate_conversation(user_id, conversation_sk, updates)
    return {"conversation": result}


@app.get("/api/advisor/threads")
def get_threads():
    user_id = get_effective_user_id(app.current_event.raw_event)
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "10"))

    # Get recent conversations and group by thread_id
    conversations = ai_repo.get_conversation_history(user_id, limit=limit * 5)

    threads = {}
    for conv in conversations:
        tid = conv.get("thread_id") or conv.get("conversation_id")
        if tid not in threads:
            threads[tid] = {
                "thread_id": tid,
                "last_question": conv.get("question", ""),
                "last_answer": conv.get("answer", ""),
                "created_at": conv.get("created_at", ""),
                "message_count": 0,
            }
        threads[tid]["message_count"] += 1

    thread_list = sorted(threads.values(), key=lambda t: t["created_at"], reverse=True)[:limit]
    return {"threads": thread_list}


@app.get("/api/advisor/threads/<threadId>")
def get_thread_messages(threadId: str):
    user_id = get_effective_user_id(app.current_event.raw_event)

    # Get all conversations and filter by thread_id
    conversations = ai_repo.get_conversation_history(user_id, limit=100)
    messages = [c for c in conversations if c.get("thread_id") == threadId or c.get("conversation_id") == threadId]

    # Sort oldest first for chat display
    messages.sort(key=lambda m: m.get("created_at", ""))
    return {"thread_id": threadId, "messages": messages}


def lambda_handler(event, context):
    return app.resolve(event, context)
