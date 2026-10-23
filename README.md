# Syntara

Type a topic, get an interview-style coding question, write your answer in the browser, and get a score out of 100 with notes on what to fix.

Live: https://syntara-bice.vercel.app/

![Syntara demo](docs/demo.gif)

You choose the topic, language and one of three difficulty levels. Almost any language works. There is no question bank, every question is generated. When you submit, the solution is graded on correctness, efficiency and coding practices, and you get a score, a correct/incorrect verdict and written remarks.

The prompts ask the model for JSON only, and the backend parses every response into a Pydantic model before sending it on. If the model returns something malformed, the request fails there instead of breaking the UI. Models go through LiteLLM, so switching models is a config change.

---

## Features

- Question generation from a topic, difficulty and language
- Monaco editor in the browser with a three-pane layout (question, solution, results)
- AI grading with a 0 to 100 score, a correct verdict and written remarks
- Strict JSON-only LLM prompts validated into Pydantic models
- Rate limiting on the API
- Sign in and sign up through Clerk, with `/chatbot` protected on the server
- Swagger UI and ReDoc at `/docs` and `/redoc`

---

## Tech Stack

| Backend | Frontend |
|---|---|
| Python 3.11+ | Next.js 16 (App Router, Turbopack) |
| FastAPI, Uvicorn | React 19 |
| SQLAlchemy with SQLite | TypeScript (strict) |
| Pydantic v2 | Tailwind CSS v4 |
| PyJWT (RS256) for Clerk token verification | shadcn/ui |
| LiteLLM with OpenRouter | Monaco Editor |

---

## Authentication

Clerk handles sign-in, sign-up, sessions, token refresh and account management. The frontend sends the session token to the backend as `Authorization: Bearer <token>`, and the backend verifies it against the Clerk instance JWKS.

The backend maps the caller to a local `users` row:

1. Look up `users.clerk_user_id`.
2. Otherwise match an existing account by email and attach the Clerk id, so existing data stays with the user.
3. Otherwise create a row with a random unusable password hash.

The acting user always comes from the token. The `Userid` field in the request body was removed because it let any authenticated caller act as any user.

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

Imports inside `backend/` are package-absolute (`from src.clerk.tokens import ...`), so uvicorn must be started from the `backend/` directory.

The LLM request and response shapes are duplicated across the stack. When the contract changes, update `prompts/`, `schemas.py`, `llm.py` and `lib/api.ts` together.

---

## Roadmap

- [x] Rate limiting
- [ ] Interview type questions
- [ ] File upload for example questions
- [ ] Persist question history and attempt scores per user
- [ ] Enable Clerk social providers and organizations (needs a claimed application)
- [ ] Dark mode

---

## License

Proprietary. All rights reserved. This project is not open for contributions.

## Acknowledgements

FastAPI, LiteLLM, OpenRouter, Next.js, Clerk, shadcn/ui, Monaco Editor, Tailwind CSS, uv
