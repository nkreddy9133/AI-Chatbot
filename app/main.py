from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.analysis import router as analysis_router
from app.api.assistant import router as assistant_router

app = FastAPI(
    title="AI Chat Project",
    description="A beginner-friendly AI chat backend with conversation history",
    version="1.0.0",
)


@app.get("/health")
async def health_check()-> dict[str,str]:
    return {"status": "healthy"}

app.include_router(chat_router)
app.include_router(analysis_router)
app.include_router(assistant_router)