from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.core.config import settings
from app.models.analysis import TextAnalysis, AnalysisRequest, AnalysisResponse
from app.services.analysis_service import analysis_service

router= APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)

@router.post("", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest)->AnalysisResponse:
    try:
        analysis= await analysis_service.analyze_text(request.text)

        return AnalysisResponse(
            analysis=analysis,
            model=settings.openai_model,
        )

    except ValidationError as exc:
        print(f"Analysis request failed: {exc}")

        raise HTTPException(
            status_code=502,
            detail="The AI service returned an invalid response. Please try again later."
        ) from exc

    except Exception as exc:
        print(f"Analysis request failed: {exc}")

        raise HTTPException(
            status_code=502,
            detail="The AI service is currently unavailable. Please try again later."
        ) from exc
    