from sqlalchemy import create_engine, text

# Create database connection
engine = create_engine('postgresql://postgres:postgres@localhost:5432/shop_db')

# Update alembic version
with engine.connect() as conn:
    conn.execute(text("UPDATE alembic_version SET version_num = 'reset_migration_base'"))
    conn.commit()

print("Successfully updated alembic version to reset_migration_base") 