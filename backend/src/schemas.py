from pydantic import BaseModel, EmailStr
from fastapi import UploadFile, File, Form, Depends
from typing import Annotated

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class QuestionAPIResponse(BaseModel):
    question: str


class QuestionAPIRequest(BaseModel):
    diff: int
    UserPrompt: str
    language: str
    model: str

class QuestionAPIRequestExamples(BaseModel):
    diff: int
    UserPrompt: str
    language: str
    model: str
    @classmethod
    def as_form(
        cls,
        diff: Annotated[int, Form(...)],
        UserPrompt: Annotated[str, Form(...)],
        language: Annotated[str, Form(...)],
        model: Annotated[str, Form(...)],
    ):
        return cls(
            diff=diff,
            UserPrompt=UserPrompt,
            language=language,
            model=model,
        )


class AnswerAPIResponse(BaseModel):
    score: int
    remarks: str
    correct: bool


class AnswerAPIRequest(BaseModel):
    Question: str
    Answer: str
    model: str
