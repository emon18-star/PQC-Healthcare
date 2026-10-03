from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Please configure the Supabase PostgreSQL connection string in your .env file."
    )

# Normalize legacy postgres:// scheme to postgresql:// (required by SQLAlchemy 2.0)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Supabase / PostgreSQL configuration with optimized connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=False,
    pool_size=20,
    max_overflow=30,
    pool_recycle=300,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

Base = declarative_base()