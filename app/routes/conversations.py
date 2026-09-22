from flask import Blueprint, jsonify

from app.db import get_db


conversations_bp = Blueprint("conversations", __name__)


@conversations_bp.get("/conversations/<int:conversation_id>")
def get_conversation(conversation_id):
    database = get_db()
    conversation = database.execute(
        "SELECT id, title, education_level, created_at, updated_at FROM conversations WHERE id = ?",
        (conversation_id,),
    ).fetchone()
    if conversation is None:
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Conversation was not found."}}), 404

    messages = database.execute(
        """SELECT role, content, action, created_at FROM messages
           WHERE conversation_id = ? ORDER BY id""",
        (conversation_id,),
    ).fetchall()
    return jsonify(
        {
            "conversation": dict(conversation),
            "messages": [dict(message) for message in messages],
        }
    )
