from fastapi import FastAPI
from app.routers import users, conversations
from pydantic import BaseModel

app = FastAPI(title="AURA API", version="0.1.0")

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(users.router, prefix="/api/v1", tags=["Current User"]) # For /api/v1/me
app.include_router(conversations.router, prefix="/api/v1", tags=["Conversations"])

class HealthResponse(BaseModel):
    status: str
    version: str

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/version")
async def get_version():
    return {"version": "0.1.0"}

@app.get("/ready")
async def ready_check():
    return {"status": "ready"}
