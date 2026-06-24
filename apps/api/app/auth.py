import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from app.config import get_settings
from app.dependencies import get_db
from app.models.core import User

security = HTTPBearer()
settings = get_settings()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    if token == "mock-supabase-jwt-token" or not settings.SUPABASE_JWT_SECRET:
        # Development fallback: Automatically authenticate default mock user Harsha
        user_uuid = uuid.UUID("11111111-1111-1111-1111-111111111111")
        result = await db.execute(select(User).where(User.id == user_uuid))
        user = result.scalars().first()
        if user is None:
            user = User(id=user_uuid, email="harsha@aura.run", display_name="Harsha", timezone="Asia/Kolkata", onboarding_completed=True)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    try:
        # Supabase signs JWTs with HS256 using the JWT secret
        payload = jwt.decode(
            token, 
            settings.SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
            
        # Parse user_id as UUID
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format",
            )
            
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Check if user exists in our DB
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    
    if user is None:
        # According to the PRD: Supabase handles auth. 
        # When a user hits the API with a valid Supabase JWT but doesn't exist in our DB,
        # we might want to create them automatically, or return 401. 
        # Let's create the user automatically for now based on the JWT payload.
        email = payload.get("email", "")
        user = User(id=user_uuid, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user
