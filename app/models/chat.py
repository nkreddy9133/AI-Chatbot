from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="The message to send to the AI model."
    )

    conversation_id: str | None = Field(
        default=None,
        description=(
            "Existing Conversation Identifier."
            "Leave empty to start a new conversation."
        ),
    )

class ChatResponse(BaseModel):
    reply: str
    model: str
    conversation_id: str