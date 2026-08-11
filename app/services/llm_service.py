import logging
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import logger

class LLMService:
    def __init__(self) -> None:
        self.client= AsyncOpenAI(api_key=settings.openai_api_key)
        self.model_name= settings.openai_model
        self.instructions= (
            "You are a helpful AI assistant."
            "Explain answers clearly and concisely, and provide examples when appropriate."
        )
        self.max_output_tokens= 200

    async def generate_reply(
            self, 
            message: str, 
            previous_response_id:str | None = None) -> tuple[str, str]:
        logger.info(
            "LLM generate_reply called",
            extra={
                "model": self.model_name,
                "input_length": len(message),
                "previous_response_id": previous_response_id,
            },
        )
        response= await self.client.responses.create(
            model=self.model_name,
            instructions=self.instructions,
            input=message,
            max_output_tokens=self.max_output_tokens,
            previous_response_id=previous_response_id,
        )
        reply, response_id = response.output_text, response.id
        logger.info(
            "LLM generate_reply completed",
            extra={"response_id": response_id},
        )
        return reply, response_id

    async def stream_reply(
            self, 
            message: str, 
            previous_response_id:str | None = None
        ) -> AsyncGenerator[tuple[str,str], None]:
        stream = await self.client.responses.create(
            model=self.model_name,
            instructions=self.instructions,
            input=message,
            max_output_tokens=self.max_output_tokens,
            previous_response_id=previous_response_id,
            stream=True
        )

        async for event in stream:
            if event.type == "response.output_text.delta":
                yield "text", event.delta

            elif event.type == "response.completed":
                yield "completed", event.response.id

            elif event.type == "error":
                error_message = getattr(
                    event, "message", "The AI service returned a streaming error. Please try again later."
                )
                yield "error", error_message

llm_service= LLMService()