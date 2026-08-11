import pytest
from fastapi.testclient import TestClient

from app.services.analysis_service import analysis_service


@pytest.fixture(autouse=True)
def mock_analyze_text(monkeypatch):
    async def fake_analyze_text(text: str):
        return {
            "summary": "This is a test summary.",
            "category": "general",
            "difficulty": "beginner",
            "sentiment": "neutral",
            "keywords": ["test"],
            "requires_follow_up": False,
            "follow_up_question": None,
        }

    monkeypatch.setattr(analysis_service, "analyze_text", fake_analyze_text)


def test_analysis_returns_structured_response(test_client: TestClient):
    payload = {"text": "Analyze this text."}

    response = test_client.post("/analysis", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["analysis"]["summary"] == "This is a test summary."
    assert data["analysis"]["category"] == "general"
    assert data["model"]
