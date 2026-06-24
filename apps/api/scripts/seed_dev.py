import asyncio
import uuid
import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.core import User, Project
from app.config import get_settings

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        # Create a test user
        test_user_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        user = await session.get(User, test_user_id)
        
        if not user:
            print("Creating test user...")
            user = User(
                id=test_user_id,
                email="test@aura.dev",
                display_name="Test User",
                onboarding_completed=True
            )
            session.add(user)
            await session.commit()
            print(f"Test user created: {user.email}")
        else:
            print("Test user already exists.")
            
        # Create a test project
        test_project_id = uuid.UUID("22222222-2222-2222-2222-222222222222")
        project = await session.get(Project, test_project_id)
        
        if not project:
            print("Creating test project...")
            project = Project(
                id=test_project_id,
                user_id=test_user_id,
                project_name="Aura Development",
                description="The development workspace for Aura.",
                status="active"
            )
            session.add(project)
            await session.commit()
            print(f"Test project created: {project.project_name}")
        else:
            print("Test project already exists.")
            
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(main())
