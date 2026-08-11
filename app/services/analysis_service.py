from openai import AsyncOpenAI
from pprint import pprint
import json

from app.core.config import settings
from app.core.logger import logger
from app.models.analysis import TextAnalysis

class AnalysisService:
    def __init__(self) -> None:
        self.client= AsyncOpenAI(api_key=settings.openai_api_key)
        self.model_name= settings.openai_model
        self.instructions= (
            "Analyze the supplied text objectively and provide a structured analysis."
            "Use only the allowed category, difficulty, and sentiment values"
            " and if no follow up is needed, set follow_up_question to null."
        )
        self.max_output_tokens= 200

    async def analyze_text(
            self, 
            text: str
        ) -> TextAnalysis:
        logger.info(
            "Analysis service called",
            extra={"text_length": len(text), "model": self.model_name},
        )

        schema = TextAnalysis.model_json_schema()
        schema["additionalProperties"] = False
        response= await self.client.responses.create(
            model=self.model_name,
            instructions=self.instructions,
            input=text,
            text={
                "format":{
                    "type":"json_schema",
                    "name":"text_analysis",
                    "description":"Structured analysis of the input text.",
                    "strict": True,
                    "schema": schema,
                }
            },
            max_output_tokens=self.max_output_tokens,
        )        

        analysis = TextAnalysis.model_validate_json(response.output_text)
        logger.info("Analysis service completed")
        return analysis

analysis_service = AnalysisService()