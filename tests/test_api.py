

from http import client

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
def test_ask_rejects_missing_question():
    """POST /ask without a Question, should get an error response"""
    response = client.post("/ask", json={})
    assert response.status_code == 422
    body = response.json()
    detail_text = str(body.get("detail", ""))
    assert "question" in detail_text.lower()
    
    
    
def test_health_returns_ok():
    """GET /health should return a 200 OK response"""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"