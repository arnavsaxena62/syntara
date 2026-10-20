# Syntara

**AI-powered coding practice platform.** Describe a topic, get a generated interview-style question, write your solution in an in-browser Monaco editor, and get an AI score with feedback.

- **Frontend** — Next.js 16 (App Router) + React 19 + Tailwind v4 + shadcn/ui + Monaco Editor
- **Backend** — FastAPI + SQLAlchemy + SQLite + JWT auth, with an LLM gateway (LiteLLM → OpenRouter)

---

## Features

- Register/login with bcrypt-hashed passwords and stateless JWT bearer tokens (30-min expiry)
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
| python-jose (HS256) + passlib/bcrypt | `>= 3.5.0` / `4.0.1` | ESLint 9 | `9.39.5` |
| LiteLLM → OpenRouter | `>= 1.106.0` | npm | lockfile committed |

---

## Quick Start

**Prerequisites:** [uv](https://docs.astral.sh/uv/), Python 3.11, Node 20+, and a free [OpenRouter](https://openrouter.ai/) API key.

### Backend

```bash
cd backend
uv sync
cat > src/.env <<'EOF'
OPENROUTER_API_KEY=sk-or-v1-your-key-here
EOF
uv run uvicorn src.main:app --reload --port 8000
```

API on **http://localhost:8000** — Swagger at `/docs`. Tables are created automatically on startup; no migration step needed.

> Run uvicorn from `backend/`. The SQLite URL is relative (`sqlite:///./db.db`) and LiteLLM resolves `.env` from the working directory.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**. The root route checks `localStorage` for a token and redirects to `/chatbot` or `/login`.

---

## Environment Variables

**Backend** (`backend/src/.env`)

| Variable | Required | Notes |
|---|---|---|
| `OPENROUTER_API_KEY` | **Yes** | Read automatically by LiteLLM for `openrouter/...` models |
| `SECRET_KEY` | Recommended | JWT signing secret — currently hardcoded in `src/auth.py` |
| `DATABASE_URL` | Optional | Currently hardcoded to `sqlite:///./db.db` |

> The committed `.env` names the key `openrouter` (lowercase). LiteLLM expects `OPENROUTER_API_KEY`, so it's ignored and the LLM routes fail with a 502.

**Frontend** — the API base URL is currently hardcoded as `http://100.66.224.73:8000` in `lib/api.ts:1` and duplicated in `components/login-form.tsx:35` and `components/register-form.tsx:22`. `NEXT_PUBLIC_API_BASE` is the natural fix but isn't wired up yet.

---

## Project Layout

```
backend/src/
  main.py        FastAPI app, CORS, lifespan (create_all)
  login.py       /register, /login
  llm.py         /newquestion, /checkAnswer, callLLM
  auth.py        JWT encode/verify, bcrypt hashing
  db.py          engine, User model, CRUD
  schemas.py     Pydantic request/response models
  prompts/       newquestion.txt, CheckAnswer.txt

frontend/
  app/           layout, page (auth redirect), login/, register/, chatbot/
  components/    login-form, register-form, ui/ (shadcn primitives)
  lib/           api.ts (client + token), utils.ts
```

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
```

---

## Roadmap

- [ ] Move `SECRET_KEY`/`DATABASE_URL` to env vars; rotate the committed secret and API keys
- [ ] Remove plaintext password logging
- [ ] Wire up `NEXT_PUBLIC_API_BASE`; delete the hardcoded URLs
- [ ] Fix the `Score`/`score` key mismatch and honour the request's `model`
- [ ] Add a client-side guard for `/chatbot`; decode the real user id from the JWT
- [ ] Add `pytest` + `httpx` coverage for auth and LLM routes (LLM mocked)
- [ ] Add Alembic migrations, refresh tokens, rate limiting, `is_active` checks
- [ ] Persist question history and attempt scores per user

---

## Contributing

Fork, branch, and keep both sides clean before opening a PR (`npm run lint`, `npx tsc --noEmit`). If you change the LLM contract, update `prompts/`, `schemas.py`, `llm.py`, and `lib/api.ts` together — the request/response shapes are duplicated across the stack.

## License

No license file yet — the code is proprietary to the project owner. Add a `LICENSE` before distributing externally.

## Acknowledgements

FastAPI · LiteLLM · OpenRouter · Next.js · shadcn/ui · Monaco Editor · Tailwind CSS · uv
