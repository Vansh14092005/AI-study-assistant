from app import create_app
from app.db import init_db
from app.services.ai_provider import AIProviderError, create_provider


def make_app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(tmp_path / "study_assistant.sqlite3"),
            "AI_PROVIDER": "mock",
        }
    )
    with app.app_context():
        init_db()
    return app


def test_chat_returns_mock_response_and_conversation_id(tmp_path):
    app = make_app(tmp_path)
    response = app.test_client().post(
        "/api/chat",
        json={
            "message": "Explain fractions",
            "education_level": "middle_school",
            "action": "chat",
        },
    )

    body = response.get_json()
    assert response.status_code == 200
    assert body["conversation_id"] == 1
    assert body["message"]["role"] == "assistant"
    assert "Explain fractions" in body["message"]["content"]


def test_chat_rejects_empty_message(tmp_path):
    app = make_app(tmp_path)
    response = app.test_client().post("/api/chat", json={"message": ""})

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_gemini_requires_server_side_key():
    try:
        create_provider({"AI_PROVIDER": "gemini"})
    except AIProviderError as error:
        assert str(error) == "GEMINI_API_KEY is not configured."
    else:
        raise AssertionError("Gemini provider should require an API key")
