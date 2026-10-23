from typing import Any, Dict, Optional

import httpx
import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

from src.clerk.config import (
    CLERK_API_URL,
    CLERK_AUDIENCE,
    CLERK_AUTHORIZED_PARTIES,
    CLERK_FRONTEND_API,
    CLERK_JWKS_URL,
    CLERK_SECRET_KEY,
)

_jwks_client: Optional[PyJWKClient] = None


def _getJwksClient() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        if not CLERK_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Clerk is not configured on this server",
            )
        _jwks_client = PyJWKClient(
            CLERK_JWKS_URL,
            headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"},
        )
    return _jwks_client


def verifyClerkToken(token: str) -> Dict[str, Any]:
    """Verify a Clerk session token and return its claims."""
    try:
        signing_key = _getJwksClient().get_signing_key_from_jwt(token)


    except HTTPException:
        raise
    except Exception as exc:
        print(
            "Clerk signing-key lookup failed: %s: %s",
            type(exc).__name__,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify this token",
        ) from exc

    try:
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=CLERK_AUDIENCE,
            options={
                "verify_aud": CLERK_AUDIENCE is not None,
                "verify_iss": False,
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    if CLERK_FRONTEND_API:
        expected_issuer = f"https://{CLERK_FRONTEND_API}"
        if payload.get("iss") != expected_issuer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token was issued for a different application",
            )

    if CLERK_AUTHORIZED_PARTIES:
        authorized_party = payload.get("azp")
        if (
            authorized_party is not None
            and authorized_party not in CLERK_AUTHORIZED_PARTIES
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token was issued to an unauthorized party",
            )

    if payload.get("sts") == "pending":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session setup is not complete",
        )

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing a subject",
        )

    return payload


def getClerkUser(clerk_user_id: str) -> Dict[str, Any]:
    """Fetch a user from the Clerk Backend API."""
    if not CLERK_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Clerk is not configured on this server",
        )

    try:
        response = httpx.get(
            f"{CLERK_API_URL}/v1/users/{clerk_user_id}",
            headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not load the user from Clerk",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach Clerk",
        ) from exc
