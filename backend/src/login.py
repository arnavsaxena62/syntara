from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import cast

from src.schemas import *
from src.auth import verify_password, createAccessToken, verifyToken
from src.db import getUsername, get_db, createUser

loginRoute = APIRouter()

@loginRoute.get("/")
async def root():
    return {"message": "Welcome to Syntara"}


@loginRoute.post("/register", response_model=TokenResponse)
async def register(formdata: UserCreate, db: Session = Depends(get_db)):
    print(formdata.password)
    print(len(formdata.password.encode("utf-8")))
    newuser = createUser(
        db,
        formdata.username,
        formdata.email,
        formdata.password
    )
    if not newuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    return TokenResponse(
        access_token=createAccessToken(cast(int, newuser.id)),
        token_type="bearer",
        expires_in=30 * 60,
    )


@loginRoute.post("/login", response_model=TokenResponse)
async def login(
    formdata: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    print(formdata.username)
    print(formdata.password)
    user = getUsername(db, formdata.username)
    if not user or not verify_password(user.hashed_password, formdata.password):
        raise HTTPException(
            status_code=401, detail="Incorrect username or password")
    return TokenResponse(
        access_token=createAccessToken(cast(int, user.id)),
        token_type="bearer",
        expires_in=30 * 60,
    )
