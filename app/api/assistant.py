from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.logger import logger
from app.models.assistant import (
    AssistantRequest,
    AssistantResponse
)
from app.services.tool_assistant_service import tool_assistant_service

router = APIRouter(
    prefix="/assistant",
    tags=["Tool-enabled assistant"]
)

@router.post("", response_model=AssistantResponse)
async def ask_assistant(request:AssistantRequest)-> AssistantResponse:
    logger.info(
        "Tool-enabled assistant request received",
        extra={"message_length": len(request.message)}
    )
    try:
        reply, tool_used=(
            await tool_assistant_service.answer(
                message=request.message
            )
        )

        logger.info(
            "Tool-enabled assistant request completed",
            extra={"tool_count": len(tool_used)}
        )

        return AssistantResponse(
            reply=reply,
            model=settings.openai_model,
            tools_used=tool_used
        )
    
    except Exception as exc:
        logger.exception("Tool-enabled assistant failed", exc_info=exc)

        raise HTTPException(
            status_code=502,
            detail=(
                "The tool-enabled assistant could not complete the request"
            ),
        ) from exc
