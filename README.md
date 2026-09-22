# AI Study Assistant

A Flask, SQLite, and Gemini/OpenAI study assistant for students.

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Open http://127.0.0.1:5000.

Set the provider in `.env`:

```text
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key-from-google-ai-studio
GEMINI_MODEL=gemini-flash-lite-latest
```

Never commit `.env` or paste an API key into source control.

## Test

```powershell
python -m pytest -q
```

## Deploy to Vercel

1. Push this repository to GitHub.
2. In Vercel, choose **Add New Project** and import `Vansh14092005/AI-study-assistant`.
3. Keep the detected Python settings and deploy.
4. Add these Environment Variables in the Vercel project settings for the Production environment:

```text
SECRET_KEY=<long-random-value>
AI_PROVIDER=gemini
GEMINI_API_KEY=<Gemini API key>
GEMINI_MODEL=gemini-flash-lite-latest
AI_REQUEST_TIMEOUT_SECONDS=30
```

5. Redeploy after adding variables.

`api/index.py` is the Vercel WSGI entry point and `vercel.json` routes requests to it. Vercel's serverless filesystem is temporary, so the SQLite database is suitable for a demo only and should be replaced with PostgreSQL or another hosted database for durable conversations and plans.
