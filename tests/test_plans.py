from datetime import date, timedelta

from app import create_app
from app.db import init_db


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


def test_create_and_list_study_plan(tmp_path):
    app = make_app(tmp_path)
    target_date = (date.today() + timedelta(days=7)).isoformat()
    client = app.test_client()

    response = client.post(
        "/api/plans",
        json={
            "subjects": ["Mathematics", "Biology"],
            "minutes_per_day": 60,
            "target_date": target_date,
            "education_level": "high_school",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["id"] == 1
    assert client.get("/api/plans").get_json()["plans"][0]["subjects"] == ["Mathematics", "Biology"]


def test_plan_rejects_past_date(tmp_path):
    app = make_app(tmp_path)
    response = app.test_client().post(
        "/api/plans",
        json={
            "subjects": ["History"],
            "minutes_per_day": 30,
            "target_date": "2000-01-01",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"
