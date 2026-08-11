from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.core.config import settings
from app.core.logger import logger
from app.models.analysis import TextAnalysis, AnalysisRequest, AnalysisResponse
from app.services.analysis_service import analysis_service

router= APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)

@router.post("", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest)->AnalysisResponse:
    logger.info(
        "Analysis request received",
        extra={"text_length": len(request.text)}
    )
    try:
        analysis= await analysis_service.analyze_text(request.text)

        logger.info("Analysis request completed")

        return AnalysisResponse(
            analysis=analysis,
            model=settings.openai_model,
        )

    except ValidationError as exc:
        logger.exception("Analysis request failed due to validation error", exc_info=exc)

        raise HTTPException(
            status_code=502,
            detail="The AI service returned an invalid response. Please try again later."
        ) from exc

    except Exception as exc:
        logger.exception("Analysis request failed", exc_info=exc)

        raise HTTPException(
            status_code=502,
            detail="The AI service is currently unavailable. Please try again later."
        ) from exc
    