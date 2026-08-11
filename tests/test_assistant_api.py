import pytest
from fastapi.testclient import TestClient

from app.services.tool_assistant_service import tool_assistant_service


@pytest.fixture(autouse=True)
def mock_tool_assistant(monkeypatch):
    async def fake_answer(message: str):
        return "Tool reply", []

    monkeypatch.setattr(tool_assistant_service, "answer", fake_answer)


def test_assistant_returns_reply(test_client: TestClient):
    payload = {"message": "Find policy info."}

    response = test_client.post("/assistant", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Tool reply"
    assert data["model"]
    assert isinstance(data["tools_used"], list)
