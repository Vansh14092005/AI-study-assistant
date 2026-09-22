import json

from app.db import get_db


def create_plan(title, subjects, minutes_per_day, target_date, plan):
    database = get_db()
    cursor = database.execute(
        """INSERT INTO study_plans
           (title, subjects_json, minutes_per_day, target_date, plan_json)
           VALUES (?, ?, ?, ?, ?)""",
        (title, json.dumps(subjects), minutes_per_day, target_date, json.dumps(plan)),
    )
    database.commit()
    return cursor.lastrowid


def list_plans():
    rows = get_db().execute(
        """SELECT id, title, subjects_json, minutes_per_day, target_date, plan_json, created_at
           FROM study_plans ORDER BY created_at DESC, id DESC"""
    ).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "subjects": json.loads(row["subjects_json"]),
            "minutes_per_day": row["minutes_per_day"],
            "target_date": row["target_date"],
            "plan": json.loads(row["plan_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
