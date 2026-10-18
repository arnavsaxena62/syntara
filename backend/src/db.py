from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.auth import hashPassword

SQLITE_DATABASE_URL = "sqlite:///./db.db"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def createUser(db, username, email, password):
    existinguser = db.query(User).filter(
        (User.username == username) | (User.email == email)).first()
    if existinguser:
        return None

    hashedPassword = hashPassword(password)

    new_user = User(
        username=username,
        email=email,
        hashed_password=hashedPassword,
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    except IntegrityError:
        db.rollback()
        return None
    
    except Exception as e:
        db.rollback()
        raise e


def getUsername(db, username: str):
    """Get user by username from database"""
    try:
        return db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return None
