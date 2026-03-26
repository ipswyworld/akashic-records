import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ONLINE", "system": "Akasha Universal Library"}

def test_get_analytics():
    response = client.get("/analytics?user_id=system_user")
    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "category_distribution" in data
    assert "system_status" in data

def test_get_psychology_no_profile():
    # Test with a non-existent user
    response = client.get("/user/psychology?user_id=non_existent_user")
    assert response.status_code == 200
    assert response.json() == {"status": "NO_PROFILE"}

def test_get_artifacts():
    response = client.get("/artifacts?user_id=system_user")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_translate_fail_no_payload():
    response = client.post("/translate", json={})
    # FastAPI should return 422 Unprocessable Entity due to missing required fields
    assert response.status_code == 422
