from fastapi import FastAPI, Request

from app.api.chat import router as chat_router
from app.api.analysis import router as analysis_router
from app.api.assistant import router as assistant_router
from app.core.logger import logger

app = FastAPI(
    title="AI Chat Project",
    description="A beginner-friendly AI chat backend with conversation history",
    version="1.0.0",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(
            f"Request completed: {request.method} {request.url} -> {response.status_code}"
        )
        return response
    except Exception:
        logger.exception(
            f"Unhandled exception while processing request: {request.method} {request.url}"
        )
        raise


@app.get("/health")
async def health_check()-> dict[str,str]:
    return {"status": "healthy"}

app.include_router(chat_router)
app.include_router(analysis_router)
app.include_router(assistant_router)