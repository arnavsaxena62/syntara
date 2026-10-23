import secrets

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    func,
    inspect,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.engine import URL

import os

from src.auth import hashPassword

turso_database_url = os.environ.get("TURSO_DATABASE_URL")
turso_auth_token = os.environ.get("TURSO_AUTH_TOKEN")
if not turso_database_url:
    raise RuntimeError("TURSO_DATABASE_URL is not set.")
if not turso_auth_token:
    raise RuntimeError("TURSO_AUTH_TOKEN is not set.")
turso_host = turso_database_url.removeprefix("libsql://")
DATABASE_URL = URL.create(
    drivername="sqlite+libsql",
    host=turso_host,
    query={
        "authToken": turso_auth_token,
    },
)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
Base = declarative_base()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    clerk_user_id = Column(String, unique=True, index=True, nullable=True)


Base.metadata.create_all(bind=engine)


def ensureClerkColumn():
    """Add the clerk_user_id column to an existing database.

    SQLite cannot alter an existing table's constraints, so this is kept
    separate from create_all(), which only creates missing tables.
    """
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    if "clerk_user_id" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN clerk_user_id VARCHAR"))
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_clerk_user_id "
                "ON users (clerk_user_id)"
            )
        )


ensureClerkColumn()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def createUser(db, username, email, password):
    existinguser = (
        db.query(User)
        .filter((User.username == username) | (User.email == email))
        .first()
    )
    if existinguser:
        return None

    hashedPassword = hashPassword(password)

    new_user = User(
        username=username, email=email, hashed_password=hashedPassword, is_active=True
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


def getUserByClerkId(db, clerk_user_id: str):
    """Get user by their Clerk external id"""
    try:
        return db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return None


def getUserByEmail(db, email: str):
    """Get user by email, case insensitive"""
    try:
        return db.query(User).filter(func.lower(User.email) == email.lower()).first()
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return None


def _uniqueUsername(db, base: str) -> str:
    candidate = base
    suffix = 1
    while db.query(User).filter(User.username == candidate).first() is not None:
        suffix += 1
        candidate = f"{base}-{suffix}"
    return candidate


def getOrCreateClerkUser(
    db,
    clerk_user_id: str,
    email: str | None = None,
    username: str | None = None,
):
    """Resolve a Clerk user to a local user row.

    Existing accounts are matched by email so their question history and
    attempt scores stay attached to them.
    """
    user = getUserByClerkId(db, clerk_user_id)
    if user:
        return user

    if email:
        user = getUserByEmail(db, email)
        if user:
            user.clerk_user_id = clerk_user_id
            db.commit()
            db.refresh(user)
            return user

    base_username = username or (email.split("@")[0] if email else None)
    if not base_username:
        base_username = f"user-{clerk_user_id[-8:]}"

    new_user = User(
        username=_uniqueUsername(db, base_username),
        email=email,
        hashed_password=hashPassword(secrets.token_urlsafe(32)),
        clerk_user_id=clerk_user_id,
        is_active=True,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        return getUserByClerkId(db, clerk_user_id)
