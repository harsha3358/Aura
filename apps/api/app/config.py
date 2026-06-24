from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_JWT_SECRET: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://aura:password@127.0.0.1:5433/aura_db"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
