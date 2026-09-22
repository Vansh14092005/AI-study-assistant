from app import create_app
from app.db import init_db


def test_saved_conversation_can_be_loaded(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(tmp_path / "study_assistant.sqlite3"),
            "AI_PROVIDER": "mock",
        }
    )
    with app.app_context():
        init_db()

    client = app.test_client()
    chat_response = client.post("/api/chat", json={"message": "Explain atoms"})
    conversation_id = chat_response.get_json()["conversation_id"]
    response = client.get(f"/api/conversations/{conversation_id}")

    assert response.status_code == 200
    assert len(response.get_json()["messages"]) == 2
