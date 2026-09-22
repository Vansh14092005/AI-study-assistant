from app import create_app


def test_health_endpoint():
    app = create_app({"TESTING": True, "AI_PROVIDER": "mock"})
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "service": "ai-study-assistant",
        "ai_provider": "mock",
    }
