# AI Study Assistant Chatbot

## 1. Project Overview

The AI Study Assistant is a web application for students. It combines a simple chat interface with focused study tools:

- Ask academic questions in natural language.
- Receive explanations adjusted to the student's education level.
- Request short or detailed summaries.
- Generate multiple-choice questions and practice questions.
- Build a study plan from subjects, deadline, and available study time.
- Receive step-by-step solutions while being reminded to understand the method.
- Store useful conversations and study plans locally in SQLite.

The first release is intentionally small enough for a student project. It will use a single Flask application, a browser client, SQLite, and an LLM API accessed only by the server.

## 2. Problem Statement

Students often need immediate explanations, revision material, and planning support, but information is scattered across notes, search results, and separate tools. They need one approachable assistant that can adapt explanations to their level and provide structured study support.

The application must also be honest about uncertainty. AI-generated answers can be incomplete or incorrect, so the interface will encourage students to verify important information with class materials or a teacher.

## 3. Objectives

### Primary objectives

1. Build a usable chat interface for academic questions.
2. Adapt responses to a selected education level.
3. Provide structured study actions: summary, quiz, practice, solution, and study plan.
4. Persist conversations and plans in SQLite.
5. Handle missing configuration, invalid input, API failures, and uncertain answers gracefully.
6. Keep the code understandable and deployable by a student.

### Out of scope for version 1

- User accounts and multi-user permissions.
- File upload and document retrieval.
- Automatic grading of student answers.
- Voice input or output.
- A custom-trained machine-learning model.
- High-scale production hosting.

These can become future enhancements after the core workflow is stable.

## 4. Requirements

### Functional requirements

- **FR1:** A student can choose an education level.
- **FR2:** A student can submit a natural-language message.
- **FR3:** The assistant returns a readable answer with a confidence/verification notice when appropriate.
- **FR4:** A student can request a short or detailed summary of supplied text or a topic.
- **FR5:** A student can generate MCQs and practice questions.
- **FR6:** A student can request a step-by-step solution.
- **FR7:** A student can create a study plan from subjects, available minutes per day, and target date.
- **FR8:** Chat messages and study plans can be saved in SQLite.
- **FR9:** The UI shows loading, validation, empty, and error states.
- **FR10:** The server never sends the AI API key to the browser.

### Non-functional requirements

- **Usability:** A first-time student can start a chat without training.
- **Accessibility:** Keyboard-friendly controls, labels, readable contrast, and semantic HTML.
- **Security:** Secrets come from environment variables; inputs are validated and output is escaped by the frontend.
- **Reliability:** Provider failures return useful messages instead of a blank page.
- **Maintainability:** Routes, database access, prompts, and AI provider logic remain separate.
- **Performance:** Normal requests should avoid unnecessary database work and show progress while waiting for the provider.
- **Portability:** The project runs locally on Windows, macOS, and Linux with Python 3.11 or newer.

## 5. Recommended System Architecture

```text
Browser (HTML/CSS/JavaScript)
        |
        | JSON over HTTP
        v
Flask routes (/api/chat, /api/plans, /api/health)
        |
        +--> Validation and error handling
        +--> SQLite repository
        +--> Prompt builder
        +--> AI provider adapter
                    |
                    v
              OpenAI-compatible LLM API
```

### Request flow

1. The browser sends a request containing the message, education level, and optional action.
2. Flask validates the request and limits input size.
3. The service builds a focused prompt with the education level and requested output format.
4. The provider adapter calls the LLM using a server-side environment variable.
5. The service stores the user message and assistant response in SQLite.
6. Flask returns structured JSON.
7. The browser renders the response and any verification notice.

### Design decision: provider adapter

Use a small `AIProvider` interface rather than calling a vendor SDK directly from every route. This makes the project easier to test and lets the provider be changed later. The initial implementation can target the OpenAI API, but the rest of the application should not depend on OpenAI-specific objects.

## 6. Database Design

SQLite is sufficient for a local student project. Use parameterized queries and enable foreign keys.

### `conversations`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `title` | TEXT | Optional short label |
| `education_level` | TEXT | Example: high_school |
| `created_at` | TEXT | UTC timestamp |
| `updated_at` | TEXT | UTC timestamp |

### `messages`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `conversation_id` | INTEGER | Foreign key |
| `role` | TEXT | `user` or `assistant` |
| `content` | TEXT | Message text |
| `action` | TEXT | chat, summary, quiz, practice, solution |
| `created_at` | TEXT | UTC timestamp |

### `study_plans`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `title` | TEXT | Plan label |
| `subjects_json` | TEXT | JSON array of subjects |
| `minutes_per_day` | INTEGER | Validated positive integer |
| `target_date` | TEXT | ISO date |
| `plan_json` | TEXT | Generated plan as JSON |
| `created_at` | TEXT | UTC timestamp |

### Initial indexes

- `messages(conversation_id, created_at)`
- `study_plans(created_at)`

## 7. API Contract

All endpoints return JSON. Errors use the shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Please provide a message."
  }
}
```

### `GET /api/health`

Returns application and provider configuration status. It must not return the API key.

### `POST /api/chat`

Request:

```json
{
  "message": "Explain photosynthesis",
  "education_level": "high_school",
  "action": "chat",
  "conversation_id": null
}
```

Allowed actions: `chat`, `summary_short`, `summary_detailed`, `mcq`, `practice`, `solution`.

Response:

```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "...",
    "action": "chat"
  },
  "uncertainty_notice": "Verify important details with your course materials."
}
```

### `GET /api/conversations/<id>`

Returns the conversation and its messages.

### `POST /api/plans`

Request:

```json
{
  "subjects": ["Mathematics", "Biology"],
  "minutes_per_day": 60,
  "target_date": "2026-10-15",
  "education_level": "high_school"
}
```

Response contains the saved plan and its database ID.

### `GET /api/plans`

Returns saved plans, newest first.

## 8. UI Design

The first screen should be a focused study workspace rather than a marketing page.

### Layout

- **Header:** App name, education-level selector, connection status.
- **Main area:** Scrollable chat transcript with distinct user and assistant messages.
- **Composer:** Multiline input, send button, and action selector.
- **Quick actions:** Summary, detailed summary, MCQ, practice, solution, and study plan.
- **Secondary panel:** Saved plans and recent conversations on larger screens; collapses below the chat on small screens.
- **Feedback states:** Loading indicator, retry action, validation message, and verification notice.

### Visual and interaction principles

- Use plain language and short labels.
- Keep the send action available by keyboard.
- Preserve the selected education level across requests.
- Never display raw HTML from an AI response without sanitization; render plain text or a safe markdown subset.
- Make the uncertainty notice visible but non-alarming.
- Use responsive CSS so the chat remains usable on a phone.

## 9. Folder and Project Structure

```text
ai-study-assistant/
|-- app/
|   |-- __init__.py              # Flask app factory
|   |-- config.py                # Environment-backed configuration
|   |-- db.py                    # SQLite connection and initialization
|   |-- routes/
|   |   |-- chat.py              # Chat and conversation endpoints
|   |   |-- plans.py             # Study-plan endpoints
|   |   |-- health.py             # Health endpoint
|   |-- services/
|   |   |-- ai_provider.py       # Provider interface and implementation
|   |   |-- prompts.py            # Prompt construction
|   |   |-- study_plans.py       # Plan validation and formatting
|   |-- repositories/
|   |   |-- conversations.py     # Conversation persistence
|   |   |-- plans.py              # Plan persistence
|   |-- templates/
|   |   |-- index.html
|   |-- static/
|       |-- css/style.css
|       |-- js/app.js
|-- tests/
|   |-- test_health.py
|   |-- test_chat.py
|   |-- test_plans.py
|   |-- fakes.py
|-- instance/
|   |-- .gitkeep
|-- .env.example
|-- .gitignore
|-- requirements.txt
|-- run.py
|-- README.md
|-- PROJECT_ROADMAP.md
```

## 10. Development Roadmap

### Phase 0: Environment setup

- Install Python 3.11+.
- Create and activate a virtual environment.
- Add Flask, `python-dotenv`, the selected provider SDK, and pytest.
- Create `.env.example` without real secrets.
- Confirm the Flask health endpoint runs.

**Checkpoint:** `GET /api/health` returns JSON locally.

### Phase 1: Application shell

- Create the Flask app factory.
- Add configuration and error handlers.
- Add the static frontend and a basic responsive layout.
- Add a health route.

**Checkpoint:** The browser loads the study workspace without an API key.

### Phase 2: SQLite persistence

- Create schema initialization.
- Add conversation and message repositories.
- Add study-plan repository.
- Write repository tests using a temporary database.

**Checkpoint:** A test can save and retrieve a conversation and plan.

### Phase 3: AI provider integration

- Define the provider interface.
- Read the API key from `.env` or deployment environment.
- Implement timeout and exception handling.
- Add a fake provider for tests.
- Add prompts for each supported action.

**Checkpoint:** Tests run without network calls; a configured local run can answer one question.

### Phase 4: Chat workflow

- Implement `POST /api/chat`.
- Validate message size, education level, action, and conversation ID.
- Save user and assistant messages.
- Render responses in the browser.
- Add loading, retry, and uncertainty states.

**Checkpoint:** A student can complete a full question-and-answer cycle.

### Phase 5: Study tools

- Add summary and question-generation actions.
- Add study-plan validation and generation.
- Render plans as readable daily tasks.
- Save and reload plans.

**Checkpoint:** Each core feature works from the UI with a fake provider test and one manual provider check.

### Phase 6: Testing and hardening

- Add route tests for valid and invalid requests.
- Test provider timeouts and missing configuration.
- Test browser behavior manually at desktop and mobile widths.
- Check accessibility basics with keyboard navigation.
- Review logs to ensure secrets and full sensitive prompts are not written.

**Checkpoint:** `pytest` passes and common failure states are understandable to a user.

### Phase 7: Documentation and deployment

- Complete the README with setup instructions.
- Add screenshots only after the UI is stable.
- Document environment variables and limitations.
- Deploy to a small Python-compatible host.
- Configure a production secret outside source control.
- Use a production WSGI server and HTTPS.

**Checkpoint:** A clean machine can follow the README and run the application.

## 11. Environment Configuration

Create `.env` locally from `.env.example`. Never commit `.env`.

```text
FLASK_ENV=development
SECRET_KEY=replace-with-a-long-random-value
DATABASE_PATH=instance/study_assistant.sqlite3
AI_PROVIDER=openai
OPENAI_API_KEY=add-your-key-locally
OPENAI_MODEL=choose-a-supported-model
AI_REQUEST_TIMEOUT_SECONDS=30
```

The exact model name depends on the provider account and current API availability. Keep it configurable rather than embedding it in code.

## 12. Testing Strategy

### Unit tests

- Prompt construction includes the education level and action.
- Validation rejects empty or oversized messages.
- Plan validation rejects invalid dates, subjects, and study time.
- Repositories correctly save and retrieve records.
- Provider errors are converted to application-level errors.

### API tests

- Health endpoint does not expose secrets.
- Chat endpoint returns a conversation ID.
- Invalid JSON and missing fields return `400`.
- Provider failure returns a controlled `502` or equivalent application error.
- Plan creation returns a saved plan.

### Manual tests

- Send a normal question.
- Try each quick action.
- Refresh and reload a conversation.
- Disconnect or misconfigure the provider.
- Use the app with keyboard only.
- Check phone-sized layout.

Do not claim tests pass until they have actually been run.

## 13. Security and Responsible AI

- Store keys only in environment variables or the deployment secret manager.
- Add `.env` and the SQLite database to `.gitignore`.
- Validate request bodies and cap message length.
- Use parameterized SQLite queries.
- Escape or safely render assistant output.
- Do not log API keys, authorization headers, or unnecessary student content.
- Add request rate limiting before public deployment.
- Use HTTPS in production.
- Do not present generated answers as guaranteed facts.
- Encourage checking important answers against textbooks, teachers, and official sources.
- Avoid collecting personal information that the feature does not need.
- Explain that the assistant supports learning and should not replace academic integrity or teacher guidance.

## 14. Deployment Plan

For a student demonstration, deploy the Flask app to a Python-compatible service such as Render, Railway, or another approved host.

1. Put the project in a Git repository without `.env` or the local database.
2. Define the build command from `requirements.txt`.
3. Use a production start command such as `gunicorn run:app` after adding Gunicorn to dependencies.
4. Add `SECRET_KEY`, database path, provider name, model name, and API key as host environment variables.
5. Use a persistent disk or managed database if plans must survive redeployments.
6. Set `FLASK_ENV=production` and disable debug mode.
7. Verify health, chat errors, and secret masking after deployment.

SQLite is acceptable for a demo or single-instance deployment. For multiple instances or heavier usage, migrate the repository layer to PostgreSQL.

## 15. Documentation and Report Deliverables

The final project report should contain:

1. Title page and abstract.
2. Introduction and problem statement.
3. Objectives and scope.
4. Requirement analysis.
5. Related systems or background research.
6. Architecture and database design.
7. UI design and screenshots.
8. Implementation details.
9. Testing approach and actual results.
10. Security, privacy, and responsible-AI considerations.
11. Limitations and future enhancements.
12. Conclusion and references.

The README should include prerequisites, setup, environment variables, run commands, test commands, API overview, troubleshooting, and deployment notes.

## 16. PowerPoint Presentation Outline

1. Title: AI Study Assistant Chatbot.
2. Problem: Students need explainable, structured study support.
3. Proposed solution and target users.
4. Core features.
5. System architecture diagram.
6. Database design.
7. UI walkthrough.
8. AI prompt and provider approach.
9. Error handling and responsible AI.
10. Testing evidence and limitations.
11. Deployment and future improvements.
12. Conclusion and live demo.

Use actual screenshots and test evidence from the completed application. Do not present planned features as completed features.

## 17. Viva Questions and Short Answers

### Why did you choose Flask?

Flask is lightweight, easy to understand, and sufficient for a small REST API and server-rendered or static frontend.

### Why use SQLite?

SQLite has no separate database server, is easy to test, and is appropriate for a local or single-instance student project.

### Where is the API key stored?

Only on the server, in an environment variable or deployment secret. It is never sent to the browser or committed to source control.

### How does the assistant adapt to students?

The selected education level is validated and included in the prompt so the provider can adjust vocabulary, depth, and examples.

### How do you handle incorrect AI answers?

The UI includes a verification notice, the prompt asks the model to acknowledge uncertainty, and important information should be checked against trusted course sources.

### What happens if the provider is unavailable?

The backend catches provider errors, logs only safe diagnostic information, and returns a controlled error that the frontend can display with a retry option.

### Why use a provider adapter?

It separates application logic from vendor-specific SDK code, which improves testing and makes changing providers easier.

### How would you scale the system?

Move from SQLite to PostgreSQL, add authentication and rate limiting, use a background job for long requests, and deploy multiple stateless application instances.

### How do you protect against prompt injection?

Treat user input as untrusted content, keep system instructions separate, limit tool access, avoid exposing internal prompts, and never let model output directly execute code or database queries.

## 18. First Implementation Order

The next practical coding session should implement these files in order:

1. `requirements.txt` and `.env.example`.
2. `run.py`, `app/__init__.py`, and `app/config.py`.
3. `app/db.py` and the initial schema.
4. `app/routes/health.py`.
5. `app/templates/index.html`, `app/static/css/style.css`, and `app/static/js/app.js`.
6. Provider interface and fake provider.
7. Chat route and repositories.
8. Study-plan route and UI actions.
9. Tests and README setup instructions.

This order creates a runnable checkpoint early, then adds persistence and AI behavior behind small, testable boundaries.
