import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")


def _csv(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


AUTH_PROVIDER = os.getenv("AUTH_PROVIDER", "clerk").strip().lower()

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "").strip()
CLERK_FRONTEND_API = os.getenv("CLERK_FRONTEND_API", "").strip()
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "").strip() or (
    f"https://{CLERK_FRONTEND_API}/.well-known/jwks.json"
    if CLERK_FRONTEND_API
    else "https://api.clerk.com/v1/jwks"
)
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE", "").strip() or None
CLERK_AUTHORIZED_PARTIES = _csv("CLERK_AUTHORIZED_PARTIES")
CLERK_API_URL = os.getenv("CLERK_API_URL", "https://api.clerk.com").strip()

API_ALLOWED_ORIGINS = _csv("API_ALLOWED_ORIGINS") or [
    "http://192.168.1.17:3001",
    "http://localhost:3000",
    "http://localhost:3001",
]


def _normalizeApiKeys():
    """LiteLLM only reads OPENROUTER_API_KEY, the env file uses a lowercase key."""
    if not os.getenv("OPENROUTER_API_KEY") and os.getenv("openrouter"):
        os.environ["OPENROUTER_API_KEY"] = os.environ["openrouter"]


_normalizeApiKeys()
