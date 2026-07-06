# Deployment Guide

This project is easiest to share publicly with:

- **Render** for the FastAPI backend and PostgreSQL/pgvector database.
- **Vercel** for the React/Vite frontend.

The backend needs a long-running web service for GitHub webhooks, SSE, OAuth callbacks, and Telegram callbacks. The frontend is a static Vite app, so Vercel is a good fit.

## 1. Push The Repo To GitHub

Make sure these files are committed:

- `README.md`
- `DEPLOYMENT.md`
- `render.yaml`
- `server/Dockerfile`
- `client/Dockerfile`
- `docker-compose.yml`
- `client/.env.example`
- `server/.env.example`

Never commit:

- `server/.env`
- `client/.env`
- API keys
- GitHub OAuth secrets
- Telegram tokens
- ngrok URLs

## 2. Deploy Backend On Render

### Option A: Render Blueprint

1. Go to Render.
2. Create a new **Blueprint**.
3. Select this GitHub repository.
4. Render will read `render.yaml`.
5. Fill every `sync: false` environment variable in the dashboard.

The Blueprint creates:

- `devops-agent-api`: Docker web service.
- `devops-agent-db`: PostgreSQL database.

Render Blueprints support Docker services with `dockerfilePath` and `dockerContext`, and Render Postgres supports pgvector. The app schema already runs:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Option B: Manual Render Web Service

Create a new **Web Service**:

```text
Runtime: Docker
Dockerfile Path: ./server/Dockerfile
Docker Context: .
Health Check Path: /health
```

Create a Render PostgreSQL database and copy its internal connection string into:

```text
DATABASE_URL
```

Required backend environment variables:

```text
APP_ENV=production
LOG_LEVEL=info
DATABASE_URL=<render-postgres-connection-string>
TOKEN_ENCRYPTION_KEY=<generated-fernet-key>
API_BASE_URL=https://your-render-api.onrender.com
FRONTEND_BASE_URL=https://your-vercel-app.vercel.app
CORS_ORIGINS=https://your-vercel-app.vercel.app
WEBHOOK_BASE_URL=https://your-render-api.onrender.com
OPENAI_API_KEY=<your-openai-key>
GITHUB_CLIENT_ID=<your-github-oauth-client-id>
GITHUB_CLIENT_SECRET=<your-github-oauth-client-secret>
GITHUB_WEBHOOK_SECRET=<random-secret>
```

Generate `TOKEN_ENCRYPTION_KEY` locally:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Optional variables:

```text
GITHUB_TOKEN=<fallback-pat>
TELEGRAM_BOT_TOKEN=<telegram-bot-token>
TELEGRAM_WEBHOOK_SECRET=<random-secret>
TELEGRAM_WEBHOOK_URL=https://your-render-api.onrender.com/api/webhooks/telegram
TELEGRAM_ALLOWED_USER_IDS=<comma-separated-user-ids>
CD_WEBHOOK_SECRET=<random-secret>
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_SUBSCRIPTION_ID=
GCP_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=
```

## 3. Deploy Frontend On Vercel

In Vercel, import the same GitHub repo and use:

```text
Root Directory: client
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
```

Add this Vercel environment variable:

```text
VITE_API_BASE_URL=https://your-render-api.onrender.com
```

If you cannot host the backend, deploy the frontend as a self-contained demo instead:

```text
VITE_DEMO_MODE=true
```

In demo mode, the app does not call `localhost:8000` or require GitHub OAuth. It opens a simulated dashboard with sample repositories, CI failure events, RSI ingestion, memory recall, fix PR creation, and PR review output. This is the best option for interviews when Render/backend hosting is unavailable.

The existing `client/vercel.json` handles React Router deep links by rewriting unknown paths to `index.html`.

## 4. Configure GitHub OAuth

Create or update your GitHub OAuth App:

```text
Homepage URL: https://your-vercel-app.vercel.app
Authorization callback URL: https://your-render-api.onrender.com/api/auth/callback
```

Copy the OAuth app values into Render:

```text
GITHUB_CLIENT_ID
GITHUB_CLIENT_SECRET
```

## 5. Configure Webhooks

After deployment:

1. Open the Vercel app link.
2. Log in with GitHub.
3. Initialize a repository from the dashboard.

The backend will create a GitHub webhook using:

```text
WEBHOOK_BASE_URL/api/webhooks/github
```

Events:

- `workflow_run`
- `pull_request`
- `push`

## 6. Resume Links

Use these on your resume/GitHub profile:

```text
Live Demo: https://your-vercel-app.vercel.app
API Health: https://your-render-api.onrender.com/health
Source: https://github.com/<you>/<repo>
```

## 7. Quick Smoke Test

After both deploys:

```bash
curl https://your-render-api.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

Then open the Vercel URL and confirm the GitHub login button redirects to GitHub.
