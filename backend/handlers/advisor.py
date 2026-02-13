"""AI Advisor Lambda handler."""

import json
import time

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from common.auth import get_effective_user_id
from common.error_capture import capture_error
from common.exceptions import AppError, ValidationError, RateLimitError
from common import ai_repo, profile_repo, hero_repo, user_repo

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
    result = engine.ask(profile=profile, user_heroes=heroes, question=question)
    elapsed_ms = int(time.time() * 1000) - start_ms

    source = result.get("source", "rules")
    answer = result.get("answer", "")
    logger.info("Advisor response", extra={
        "question": question[:100],
        "source": source,
        "elapsed_ms": elapsed_ms,
        "answer_preview": answer[:100] if answer else "",
        "hero_count": len(heroes),
        "profile_furnace": profile.get("furnace_level") if isinstance(profile, dict) else None,
    })
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
        "conversation_id": conversation.get("SK"),
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


@app.delete("/api/advisor/history")
def clear_history():
    user_id = get_effective_user_id(app.current_event.raw_event)
    count = ai_repo.delete_conversation_history(user_id)
    return {"deleted": count}


@app.post("/api/advisor/delete")
def delete_conversation():
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}

    thread_id = body.get("thread_id")
    if thread_id:
        count = ai_repo.delete_thread(user_id, thread_id)
        return {"deleted": count}

    conv_sk = body.get("conversation_sk")
    if not conv_sk:
        raise ValidationError("conversation_sk or thread_id is required")
    ai_repo.delete_conversation(user_id, conv_sk)
    return {"deleted": 1}


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


@app.get("/api/advisor/favorites")
def get_favorites():
    user_id = get_effective_user_id(app.current_event.raw_event)
    params = app.current_event.query_string_parameters or {}
    limit = int(params.get("limit", "20"))

    conversations = ai_repo.get_conversation_history(user_id, limit=limit * 5)
    favorites = [c for c in conversations if c.get("is_favorite")][:limit]
    return {"favorites": favorites}


@app.post("/api/advisor/favorite")
def toggle_favorite():
    user_id = get_effective_user_id(app.current_event.raw_event)
    body = app.current_event.json_body or {}
    conv_sk = body.get("conversation_sk")
    if not conv_sk:
        raise ValidationError("conversation_sk is required")

    # Get current state and toggle
    conversations = ai_repo.get_conversation_history(user_id, limit=200)
    current = next((c for c in conversations if c.get("conversation_id") == conv_sk or c.get("SK") == conv_sk), None)
    new_state = not (current.get("is_favorite", False) if current else False)

    sk = conv_sk if conv_sk.startswith("AICONV#") else f"AICONV#{conv_sk}"
    ai_repo.rate_conversation(user_id, sk, {"is_favorite": new_state})
    return {"is_favorite": new_state}


@app.get("/api/advisor/status")
def get_advisor_status():
    user_id = get_effective_user_id(app.current_event.raw_event)
    user = user_repo.get_user(user_id)
    settings = ai_repo.get_ai_settings()
    allowed, message, remaining = ai_repo.check_rate_limit(user or {}, settings)

    mode = settings.get("mode", "off")
    # Return the actual limit for this user (admin vs free tier)
    role = (user or {}).get("role", "user")
    user_daily_limit = (user or {}).get("ai_daily_limit")
    if user_daily_limit is None:
        user_daily_limit = settings.get("daily_limit_admin", 1000) if role == "admin" else settings.get("daily_limit_free", 20)
    return {
        "ai_enabled": mode != "off",
        "mode": mode,
        "daily_limit": user_daily_limit,
        "requests_today": (user or {}).get("ai_requests_today", 0),
        "requests_remaining": remaining,
        "primary_provider": settings.get("primary_provider", "openai"),
    }


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
    try:
        return app.resolve(event, context)
    except AppError as exc:
        logger.warning("Application error", extra={"error": exc.message, "status": exc.status_code})
        return {"statusCode": exc.status_code, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": exc.message})}
    except Exception as exc:
        logger.exception("Unhandled error in advisor handler")
        capture_error("advisor", event, exc, logger)
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Internal server error"})}
