from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

class AnalysisRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=2000,
        description="The text should be analyzed by AI."
    )

class TextAnalysis(BaseModel):

    summary: str = Field(
        description="A concise summary of the input text."
    )

    category: Literal["software", "healthcare", "career", "education", "general"]

    difficulty: Literal["beginner", "intermediate", "advanced"]

    sentiment: Literal["positive", "negative", "neutral", "mixed"]

    keywords: list[str] = Field(
        min_length=1,
        max_length=5,
        description="one to five keywords that capture the essence of the input text."
    )

    requires_follow_up: bool

    follow_up_question: str | None = Field(
        description = (
            "A useful follow up question when additional information is needed."
        )
    )

class AnalysisResponse(BaseModel):
    analysis: TextAnalysis
    model: str
