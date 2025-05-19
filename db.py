from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app_environment import AppEnvironment
from env import env

# Construct database URL from individual components
SQLALCHEMY_DATABASE_URL = f"postgresql://{env.DB_USER}:{env.DB_PASSWORD}@{env.DB_HOST}:{env.DB_PORT}/{env.DB_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Export Session for backward compatibility
Session = SessionLocal

# Create base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Vector database connection string
vectordb_conn_str = f"postgresql+psycopg://{env.DB_USER}:{env.DB_PASSWORD}@{env.DB_HOST}:{env.DB_PORT}/{env.DB_NAME}"