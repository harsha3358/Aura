import pytest
from app.dependencies import engine

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(autouse=True)
async def dispose_engine():
    yield
    # Dispose the engine to close connections before the loop is destroyed
    await engine.dispose()
