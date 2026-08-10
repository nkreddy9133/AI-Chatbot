from pydantic import BaseModel, Field

class AssistantRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="The text to be analyzed by the AI assistant.")

class ToolExecution(BaseModel):
    tool_name: str
    arguments: dict[str, object]
    result: dict[str, object]

class AssistantResponse(BaseModel):
    reply: str
    model: str
    tools_used: list[ToolExecution]
