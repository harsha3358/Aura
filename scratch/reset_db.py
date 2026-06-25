import argparse
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

# Adjust this path if alembic.ini is elsewhere
ALEMBIC_INI_PATH = "c:/Aura/alembic.ini"

def get_sync_engine(database_url: str):
    # Convert async URL to sync for drop/create
    sync_url = database_url.replace("+asyncpg", "")
    return create_engine(sync_url)

def drop_all(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if tables:
        with engine.begin() as conn:
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS \"{table}\" CASCADE;"))
    print(f"Dropped tables: {', '.join(tables) if tables else 'none'}")

def create_all(engine):
    # Run Alembic migrations to recreate schema
    alembic_cfg = Config(ALEMBIC_INI_PATH)
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied (schema recreated).")

def seed_data(async_engine, seed: bool):
    if not seed:
        return
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async def run():
        async with async_session() as session:
            # Seed default user (match auth.py expectations)
            await session.execute(text("""
                INSERT INTO "user" (email, hashed_password, is_active)
                VALUES ('harsha@aura.run', 'placeholder_hashed', true)
                ON CONFLICT (email) DO NOTHING;
            """))
            # Seed a sample project named 'AURA'
            await session.execute(text("""
                INSERT INTO "project" (name, description)
                VALUES ('AURA', 'Demo project for validation')
                ON CONFLICT (name) DO NOTHING;
            """))
            await session.commit()
        print("Seed data inserted (default user and sample project).")
    import asyncio
    asyncio.run(run())

def main():
    parser = argparse.ArgumentParser(description="Reset the development database.")
    parser.add_argument("--seed", action="store_true", help="Drop tables, recreate schema, run migrations, and seed default data.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without making changes.")
    args = parser.parse_args()

    # Load DB URL from config file (same as apps/api/app/config.py)
    # We duplicate minimal parsing to avoid importing the FastAPI config directly.
    import os
    from pathlib import Path
    env_path = Path("c:/Aura/.env")
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                database_url = line.split("=", 1)[1].strip()
                break
        else:
            database_url = "postgresql+asyncpg://aura:password@127.0.0.1:5433/aura_db"
    else:
        database_url = "postgresql+asyncpg://aura:password@127.0.0.1:5433/aura_db"

    if args.dry_run:
        sync_engine = get_sync_engine(database_url)
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        print("[DRY RUN] Tables that would be dropped:")
        for t in tables:
            print(f" - {t}")
        sys.exit(0)

    # Actual reset
    sync_engine = get_sync_engine(database_url)
    drop_all(sync_engine)
    create_all(sync_engine)
    # Seed if requested
    if args.seed:
        async_engine = create_async_engine(database_url, echo=False)
        seed_data(async_engine, seed=True)
    print("Database reset complete.")

if __name__ == "__main__":
    main()
