from fastapi import APIRouter, HTTPException

from app.core.config import settings
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
    try:
        reply, tool_used=(
            await tool_assistant_service.answer(
                message=request.message
            )
        )

        return AssistantResponse(
            reply=reply,
            model=settings.openai_model,
            tool_used=tool_used
        )
    
    except Exception as exc:
        print(f"Tool-enabled assistant failed: {exc}")

        raise HTTPException(
            status_code=502,
            detail=(
                "The tool-enabled assistant could not complete the request"
            ),
        ) from exc
