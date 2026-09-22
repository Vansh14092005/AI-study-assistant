from datetime import date

from flask import Blueprint, current_app, jsonify, request

from app.repositories.plans import create_plan, list_plans
from app.services.ai_provider import AIProviderError, create_provider
from app.services.prompts import EDUCATION_LEVELS


plans_bp = Blueprint("plans", __name__)


def error_response(code, message, status):
    return jsonify({"error": {"code": code, "message": message}}), status


def build_plan_prompt(subjects, minutes_per_day, target_date, education_level):
    subjects_text = ", ".join(subjects)
    return f"""Create a practical study plan for a {EDUCATION_LEVELS[education_level]}.
Subjects: {subjects_text}
Available study time: {minutes_per_day} minutes per day
Target date: {target_date}

Return a concise daily plan in plain text. Include time allocations, review sessions,
and one small measurable goal for each day. Do not invent course-specific deadlines.
"""


@plans_bp.post("/plans")
def create_study_plan():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("INVALID_JSON", "Request body must be a JSON object.", 400)

    subjects = payload.get("subjects")
    minutes_per_day = payload.get("minutes_per_day")
    target_date = payload.get("target_date")
    education_level = payload.get("education_level", "high_school")

    if (
        not isinstance(subjects, list)
        or not subjects
        or len(subjects) > 10
        or any(not isinstance(subject, str) or not subject.strip() for subject in subjects)
    ):
        return error_response("VALIDATION_ERROR", "Provide 1 to 10 subject names.", 400)
    if not isinstance(minutes_per_day, int) or not 15 <= minutes_per_day <= 720:
        return error_response("VALIDATION_ERROR", "Study time must be between 15 and 720 minutes.", 400)
    if not isinstance(target_date, str):
        return error_response("VALIDATION_ERROR", "Provide a target date.", 400)
    try:
        parsed_target = date.fromisoformat(target_date)
    except ValueError:
        return error_response("VALIDATION_ERROR", "Target date must use YYYY-MM-DD format.", 400)
    if parsed_target < date.today():
        return error_response("VALIDATION_ERROR", "Target date cannot be in the past.", 400)
    if education_level not in EDUCATION_LEVELS:
        return error_response("VALIDATION_ERROR", "Choose a supported education level.", 400)

    clean_subjects = [subject.strip() for subject in subjects]
    prompt = build_plan_prompt(clean_subjects, minutes_per_day, target_date, education_level)
    try:
        provider_response = create_provider(current_app.config).generate(prompt)
    except AIProviderError as error:
        return error_response("PROVIDER_ERROR", str(error), 502)

    title = f"Study plan: {', '.join(clean_subjects[:2])}"
    plan_id = create_plan(
        title,
        clean_subjects,
        minutes_per_day,
        target_date,
        {"content": provider_response.content, "uncertainty_notice": provider_response.uncertainty_notice},
    )
    return jsonify(
        {
            "id": plan_id,
            "title": title,
            "subjects": clean_subjects,
            "minutes_per_day": minutes_per_day,
            "target_date": target_date,
            "plan": {"content": provider_response.content, "uncertainty_notice": provider_response.uncertainty_notice},
        }
    ), 201


@plans_bp.get("/plans")
def get_study_plans():
    return jsonify({"plans": list_plans()})
