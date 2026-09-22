from flask import Blueprint, current_app, jsonify, request

from app.repositories.conversations import (
    add_message,
    conversation_exists,
    create_conversation,
)
from app.services.ai_provider import AIProviderError, create_provider
from app.services.prompts import ACTIONS, EDUCATION_LEVELS, build_prompt


chat_bp = Blueprint("chat", __name__)


def error_response(code, message, status):
    return jsonify({"error": {"code": code, "message": message}}), status


@chat_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_JSON", "Request body must be a JSON object.", 400)

    message = payload.get("message", "")
    education_level = payload.get("education_level", "high_school")
    action = payload.get("action", "chat")
    conversation_id = payload.get("conversation_id")

    if not isinstance(message, str) or not message.strip():
        return error_response("VALIDATION_ERROR", "Please provide a message.", 400)
    if len(message) > 4000:
        return error_response("VALIDATION_ERROR", "Message must be 4000 characters or fewer.", 400)
    if education_level not in EDUCATION_LEVELS:
        return error_response("VALIDATION_ERROR", "Choose a supported education level.", 400)
    if action not in ACTIONS:
        return error_response("VALIDATION_ERROR", "Choose a supported study action.", 400)

    if conversation_id is not None:
        if not isinstance(conversation_id, int) or not conversation_exists(conversation_id):
            return error_response("NOT_FOUND", "Conversation was not found.", 404)
    else:
        conversation_id = create_conversation(education_level)

    add_message(conversation_id, "user", message.strip(), action)
    prompt = build_prompt(message.strip(), education_level, action)

    try:
        provider = create_provider(current_app.config)
        provider_response = provider.generate(prompt)
    except AIProviderError as error:
        return error_response("PROVIDER_ERROR", str(error), 502)

    add_message(conversation_id, "assistant", provider_response.content, action)
    return jsonify(
        {
            "conversation_id": conversation_id,
            "message": {
                "role": "assistant",
                "content": provider_response.content,
                "action": action,
            },
            "uncertainty_notice": provider_response.uncertainty_notice,
        }
    )
