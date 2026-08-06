import uuid
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import llm_service


router= APIRouter(
    prefix="/chat",
    tags=["chat"],
)

conversation_store: dict[str, str] = {}

def create_sse_message(
        event_name: str,
        data: dict[str,object],
)-> str:
    json_data = json.dumps(data)

    return f"event: {event_name}\ndata: {json_data}\n\n"


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest)->ChatResponse:
    try:
        conversation_id=request.conversation_id

        if conversation_id is None:
            conversation_id= str(uuid.uuid4())

        previous_response_id= conversation_store.get(conversation_id)

        reply, response_id= await llm_service.generate_reply(
            message=request.message,
            previous_response_id=previous_response_id,
        )

        conversation_store[conversation_id]= response_id

        return ChatResponse(
            reply=reply,
            model=settings.openai_model,
            conversation_id=conversation_id,
        )

    except Exception as exc:
        print(f"Chat request failed: {exc}")

        raise HTTPException(
            status_code=502,
            detail="The AI service is currently unavailable. Please try again later."
        ) from exc


@router.post("/stream")
async def stream_chat(request: ChatRequest)-> StreamingResponse:
            
    conversation_id= request.conversation_id

    if conversation_id is None:
        conversation_id= str(uuid.uuid4())

    previous_response_id= conversation_store.get(conversation_id)

    async def event_generator()-> AsyncGenerator[str, None]:
        yield create_sse_message("conversation", {"conversation_id": conversation_id, "model": settings.openai_model})

        try:
            async for event_type, value in llm_service.stream_reply(
                message=request.message,
                previous_response_id=previous_response_id,
            ):
                if event_type == "text":
                    yield create_sse_message("text", {"delta": value})

                elif event_type == "completed":
                    conversation_store[conversation_id]= value
                    yield create_sse_message("completed", {"conversation_id": conversation_id, "response_id": value})

                elif event_type == "error":
                    yield create_sse_message("error", {"message": value})

        except Exception as exc:
            print(f"Streaming chat request failed: {exc}")
            yield create_sse_message(
                "error",
                {"message": "The AI service is currently unavailable. Please try again later."}
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str)-> dict[str, str]:
    if conversation_id not in conversation_store:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )
    del conversation_store[conversation_id]

    return {
        "message": "Conversation deleted successfully.",
        "conversation_id": conversation_id  
    }