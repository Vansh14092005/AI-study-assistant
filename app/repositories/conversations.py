from app.db import get_db


def create_conversation(education_level, title=None):
    database = get_db()
    cursor = database.execute(
        "INSERT INTO conversations (education_level, title) VALUES (?, ?)",
        (education_level, title),
    )
    database.commit()
    return cursor.lastrowid


def add_message(conversation_id, role, content, action):
    database = get_db()
    cursor = database.execute(
        """INSERT INTO messages (conversation_id, role, content, action)
           VALUES (?, ?, ?, ?)""",
        (conversation_id, role, content, action),
    )
    database.execute(
        "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (conversation_id,),
    )
    database.commit()
    return cursor.lastrowid


def conversation_exists(conversation_id):
    row = get_db().execute(
        "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
    ).fetchone()
    return row is not None
