EDUCATION_LEVELS = {
    "middle_school": "middle school student",
    "high_school": "high school student",
    "undergraduate": "undergraduate student",
    "graduate": "graduate student",
}

ACTIONS = {
    "chat": "Explain the topic clearly with a useful example.",
    "summary_short": "Give a concise summary in 3 to 5 bullet points.",
    "summary_detailed": "Give a structured, detailed summary with headings and key terms.",
    "mcq": "Create 5 multiple-choice questions with four options and an answer key.",
    "practice": "Create 5 practice questions, ordered from easier to harder, without solutions unless requested.",
    "solution": "Give a step-by-step solution and briefly explain why each step works.",
}


def build_prompt(message, education_level, action):
    learner = EDUCATION_LEVELS[education_level]
    instruction = ACTIONS[action]
    return f"""You are a careful AI study assistant helping a {learner}.
Use simple language, define important terms, and show reasoning rather than only giving an answer.
If the question is ambiguous or you are not confident, say what is uncertain and suggest how to verify it.
Do not claim to have completed actions or consulted sources you did not use.

Requested format: {instruction}

Student request:
{message}
"""
