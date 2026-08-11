import uuid

import pytest
from fastapi.testclient import TestClient

from app.services.llm_service import llm_service


@pytest.fixture(autouse=True)
def mock_generate_reply(monkeypatch):
    async def fake_generate_reply(message: str, previous_response_id=None):
        return f"Echo: {message}", str(uuid.uuid4())

    async def fake_stream_reply(message: str, previous_response_id=None):
        yield "text", "Hello"
        yield "completed", str(uuid.uuid4())

    monkeypatch.setattr(llm_service, "generate_reply", fake_generate_reply)
    monkeypatch.setattr(llm_service, "stream_reply", fake_stream_reply)


def test_chat_returns_response(test_client: TestClient):
    payload = {"message": "Hello"}

    response = test_client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Echo: Hello"
    assert data["model"]
    assert data["conversation_id"]


def test_chat_returns_same_conversation_id(test_client: TestClient):
    conversation_id = str(uuid.uuid4())
    payload = {"message": "Hello again", "conversation_id": conversation_id}

    response = test_client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == conversation_id


def test_stream_chat_event_stream(test_client: TestClient):
    payload = {"message": "Stream me"}

    with test_client.stream("POST", "/chat/stream", json=payload) as response:
        assert response.status_code == 200
        content = b"".join(response.iter_bytes()).decode("utf-8")

    assert "event: conversation" in content
    assert "event: text" in content
    assert "event: completed" in content


def test_delete_conversation_not_found(test_client: TestClient):
    response = test_client.delete("/chat/does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found."
