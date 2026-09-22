from flask import Blueprint, current_app, jsonify


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "ai-study-assistant",
            "ai_provider": current_app.config["AI_PROVIDER"],
        }
    )
