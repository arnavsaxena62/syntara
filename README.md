# Syntara

**AI-powered coding practice platform.** Describe a topic, get a generated interview-style question, write your solution in an in-browser Monaco editor, and get an AI score with feedback.

- **Frontend** — Next.js 16 (App Router) + React 19 + Tailwind v4 + shadcn/ui + Monaco Editor
- **Backend** — FastAPI + SQLAlchemy + SQLite + Clerk auth, with an LLM gateway (LiteLLM → OpenRouter)

---

## Features

- Sign in and sign up with Clerk, including social providers and account management
- Server-side route protection — `/chatbot` requires a session before it renders
- Prompt-driven question generation — topic, difficulty, and language in, one clean question out
- In-browser Monaco editor with a three-pane layout (question / solution / results)
- AI grading that returns a `0–100` score, a `correct` verdict, and written remarks
- Strict JSON-only LLM prompts, validated into Pydantic models before reaching the client
- Auto-generated Swagger UI and ReDoc at `/docs` and `/redoc`

---

## Tech Stack

| Backend | Version | Frontend | Version |
|---|---|---|---|
| Python | `>= 3.11` | Next.js (App Router, Turbopack) | `16.4.2` |
| FastAPI | `>= 0.143.3` | React / React DOM | `19.3.0` |
| Uvicorn | `>= 0.54.0` | TypeScript (`strict`) | `5.9.3` |
| SQLAlchemy | `>= 2.1.5` | Tailwind CSS v4 | `4.3.3` |
| SQLite | file `backend/db.db` | shadcn/ui (Base UI) | `4.22.1` |
| Pydantic v2 | `>= 2.14.1` | Monaco Editor | `0.57.0` |
| PyJWT (RS256) + passlib/bcrypt | `>= 2.10.1` / `4.0.1` | ESLint 9 | `9.39.5` |
| LiteLLM → OpenRouter | `>= 1.106.0` | npm | lockfile committed |

Authentication is handled by [Clerk](https://clerk.com). The frontend uses `@clerk/nextjs` v7, and the backend verifies Clerk session tokens (RS256) against the instance JWKS.

---

## Quick Start

**Prerequisites:** [uv](https://docs.astral.sh/uv/), Python 3.11, Node 20.9+, and a free [OpenRouter](https://openrouter.ai/) API key.

### Backend

```bash
cd backend
uv sync
cat > src/.env <<'EOF'
OPENROUTER_API_KEY=sk-or-v1-your-key-here
EOF
cat > .env <<'EOF'
CLERK_SECRET_KEY=sk_test_...
CLERK_FRONTEND_API=your-instance.clerk.accounts.dev
CLERK_AUTHORIZED_PARTIES=http://localhost:3000,http://localhost:3001
AUTH_PROVIDER=clerk
EOF
uv run uvicorn src.main:app --reload --port 8000
```

API on **http://localhost:8000** — Swagger at `/docs`. Tables are created automatically on startup; the `users.clerk_user_id` column is added by an idempotent migration if it is missing.

> Run uvicorn from `backend/`. The SQLite URL is relative (`sqlite:///./db.db`) and LiteLLM resolves `.env` from the working directory.

### Frontend

```bash
cd frontend
npm install
npx clerk@latest init          # or copy the keys from the Clerk dashboard
npm run dev
```

Open **http://localhost:3000**. The root route reads the Clerk session and redirects to `/chatbot` or `/sign-in`.

> The Clerk keys live in `frontend/.env.local` (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`).

---

## Environment Variables

**Backend** (`backend/.env` — gitignored)

| Variable | Required | Notes |
|---|---|---|
| `OPENROUTER_API_KEY` | **Yes** | Read automatically by LiteLLM for `openrouter/...` models. A lowercase `openrouter` key is also accepted. |
| `CLERK_SECRET_KEY` | **Yes** | Clerk instance secret key, used to fetch JWKS and user records |
| `CLERK_FRONTEND_API` | Recommended | Instance host, e.g. `your-instance.clerk.accounts.dev`. Used to build the JWKS URL and to check the token issuer |
| `CLERK_AUTHORIZED_PARTIES` | Recommended | Comma-separated app origins allowed to present a token, e.g. `http://localhost:3000`. Matches the token's `azp` claim |
| `CLERK_JWKS_URL` | Optional | Overrides the JWKS endpoint |
| `CLERK_AUDIENCE` | Optional | Verify the token `aud` claim when the instance uses a custom session token template |
| `AUTH_PROVIDER` | Optional | `clerk` (default) or `legacy` to re-enable the old password endpoints |
| `API_ALLOWED_ORIGINS` | Optional | Comma-separated CORS allowlist |

**Frontend** (`frontend/.env.local` — gitignored)

| Variable | Notes |
|---|---|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk publishable key |
| `CLERK_SECRET_KEY` | Clerk secret key |
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` / `_SIGN_UP_URL` | Where the auth controls link to (default `/sign-in`, `/sign-up`) |
| `NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL` | Where a signed-in user lands (default `/`) |
| `NEXT_PUBLIC_API_BASE` | Base URL of the FastAPI backend (default `http://100.66.224.73:8000`) |

---

## Authentication

Clerk owns sign-in, sign-up, sessions, and account management. The frontend keeps the session in an httpOnly cookie managed by Clerk and sends the session token to the backend as `Authorization: Bearer <token>`.

The backend resolves the caller to a local `users` row:

1. Look up `users.clerk_user_id`.
2. Otherwise match an existing account by email and attach the Clerk id — so existing question history and scores stay with the user.
3. Otherwise create a row with a random unusable password hash.

The acting user always comes from the token. The `Userid` field in the request body was removed, since it let any authenticated caller act as any user.

### Rolling back

Set `AUTH_PROVIDER=legacy` in `backend/.env` to re-enable the old `/login` and `/register` password endpoints. The Clerk routes stay disabled in that mode.

---

## Project Layout

```
backend/src/
  main.py        FastAPI app, CORS, lifespan (create_all)
  login.py       /register, /login (legacy mode only)
  llm.py         /newquestion, /checkAnswer, callLLM
  auth.py        legacy JWT encode/verify, bcrypt hashing
  db.py          engine, User model, CRUD, clerk_user_id migration
  schemas.py     Pydantic request/response models
  prompts/       newquestion.txt, CheckAnswer.txt
  clerk/
    config.py    env loading, AUTH_PROVIDER, CORS allowlist
    tokens.py    session token verification (JWKS), Clerk user lookup
    deps.py      currentUser dependency (Clerk or legacy)

frontend/
  app/           layout, page (auth redirect), sign-in/, sign-up/, chatbot/
  components/    chatbot-view, ui/ (shadcn primitives)
  lib/           api.ts (backend calls), utils.ts
  proxy.ts       clerkMiddleware
```

> Imports inside `backend/` are package-absolute (`from src.clerk.tokens import ...`), so uvicorn must be started from the `backend/` directory.

---

## Commands

```bash
# Backend
cd backend && uv sync
uv run uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend && npm install
npm run dev        # dev server on :3000
npm run build      # production build
npm run start      # serve the build
npm run lint       # ESLint
npx tsc --noEmit   # type check

# Clerk
npx clerk@latest doctor
```

---

## Roadmap

- [ ] Move `DATABASE_URL` to an env var; add Alembic migrations
- [ ] Add `pytest` + `httpx` coverage for auth and LLM routes (LLM mocked)
- [ ] Rate limiting and refresh token handling
- [ ] Persist question history and attempt scores per user
- [ ] Enable Clerk social providers and organizations (needs a claimed application)

---

## Contributing

Fork, branch, and keep both sides clean before opening a PR (`npm run lint`, `npx tsc --noEmit`). If you change the LLM contract, update `prompts/`, `schemas.py`, `llm.py`, and `lib/api.ts` together — the request/response shapes are duplicated across the stack.

## License

No license file yet — the code is proprietary to the project owner. Add a `LICENSE` before distributing externally.

## Acknowledgements

FastAPI · LiteLLM · OpenRouter · Next.js · Clerk · shadcn/ui · Monaco Editor · Tailwind CSS · uv
