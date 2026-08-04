import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()   

api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL", "gpt-5-nano")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Please set it in your environment variables or in a .env file."
    )

openai_client = OpenAI(api_key=api_key)

app = FastAPI(
    title="AI Chat API",
    description="A simple API to interact with OpenAI's GPT model.",
    version="1.0.0",
)

class ChatRequest(BaseModel):
    message: str= Field(
        min_length=1, 
        max_length=2000, 
        description="The message to send to the AI model."
    )

class ChatResponse(BaseModel):
    reply: str
    model: str

@app.get("/health")
async def health_check()-> dict[str,str]:
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest)->ChatResponse:
    try:
        response= openai_client.responses.create(
            model=model_name,
            instructions=(
                "You are a helpful assistant."
                "Explain answers clearly and concisely, and provide examples when appropriate."
            ),
            input=request.message,
            max_output_tokens=200
        )

        return ChatResponse(reply=response.output_text, model=model_name)
    except Exception as exc:
        print(f"OpenAI request failed: {exc}")

        raise HTTPException(status_code=502, detail="The AI service is currently unavailable. Please try again later.") from exc