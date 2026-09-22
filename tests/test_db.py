from app import create_app
from app.db import get_db, init_db


def test_init_db_creates_tables(tmp_path):
    database_path = tmp_path / "study_assistant.sqlite3"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(database_path),
        }
    )

    with app.app_context():
        init_db()
        table_names = {
            row["name"]
            for row in get_db().execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        foreign_keys_enabled = get_db().execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0]

    assert {"conversations", "messages", "study_plans"}.issubset(table_names)
    assert foreign_keys_enabled == 1
