import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
def verifyToken(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")



SECRET_KEY = "85dca03576ec2e60db3504e7a1b7866f415a935bc2be9a712a6ad0895d05acc3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def createAccessToken(subject: int) -> str:
    to_encode = {
        "sub": str(subject),  # subject = user id
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def verify_password(HashedPassword, incomingPassword):
    return pwd_context.verify(incomingPassword, HashedPassword)

def hashPassword(inptPassword):
    return pwd_context.hash(inptPassword)
