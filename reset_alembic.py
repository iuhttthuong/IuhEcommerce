from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection details from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(DATABASE_URL)

# Drop alembic_version table
with engine.connect() as connection:
    connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    connection.commit()

print("Successfully dropped alembic_version table") 