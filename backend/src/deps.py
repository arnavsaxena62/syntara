from typing import Annotated, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.auth import verifyLegacyToken
from src.clerk import getClerkUser, verifyClerkToken
from src.config import AUTH_PROVIDER
from src.db import get_db, getOrCreateClerkUser

bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def _clerkUserFromToken(token: str, db: Session) -> int:
    claims = verifyClerkToken(token)
    clerk_user_id = claims["sub"]

    email = claims.get("email")
    username = claims.get("username") or claims.get("full_name")

    if not email or not username:
        clerk_user = getClerkUser(clerk_user_id)
        email = email or _primaryEmail(clerk_user)
        username = username or clerk_user.get("username")

    user = getOrCreateClerkUser(db, clerk_user_id, email=email, username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not provision the user",
        )
    if not cast(bool, user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is disabled",
        )
    return cast(int, user.id)


def _primaryEmail(clerk_user: dict) -> str | None:
    emails = clerk_user.get("email_addresses") or []
    primary_id = clerk_user.get("primary_email_address_id")
    for email_address in emails:
        if email_address.get("id") == primary_id:
            return email_address.get("email_address")
    for email_address in emails:
        if email_address.get("email_address"):
            return email_address["email_address"]
    return None


def currentUser(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DbSession,
) -> int:
    """Return the local user id for the authenticated caller.

    With AUTH_PROVIDER=clerk the caller must present a Clerk session token.
    With AUTH_PROVIDER=legacy the old HS256 token is accepted instead.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = credentials.credentials

    if AUTH_PROVIDER == "legacy":
        return verifyLegacyToken(token)

    return _clerkUserFromToken(token, db)
