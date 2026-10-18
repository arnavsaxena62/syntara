from pydantic import BaseModel, EmailStr

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
    Question: str

class QuestionAPIRequest(BaseModel):
    Userid: int
    diff:int
    UserPrompt: str
    language: str
    model: str

class AnswerAPIResponse(BaseModel):
    Score: int
    remarks: str
    correct: bool

class AnswerAPIRequest(BaseModel):
    Userid: int
    Question:str
    Answer:str
    model:str