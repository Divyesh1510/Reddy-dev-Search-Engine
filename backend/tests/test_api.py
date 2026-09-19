import pytest
import os
import shutil
import tempfile
from fastapi.testclient import TestClient

def test_api_endpoints_and_job_queue():
    # Set a temporary DATA_DIR for isolated test
    temp_dir = tempfile.mkdtemp()
    os.environ["DATA_DIR"] = temp_dir

    from app.main import app
    from app.jobs import job_store

    client = TestClient(app)

    # 1. Test root endpoint
    root_resp = client.get("/")
    assert root_resp.status_code == 200
    assert root_resp.json()["status"] == "online"

    # 2. Test /stats endpoint
    stats_resp = client.get("/stats")
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert "index" in stats_data
    assert "storage" in stats_data

    # 3. Test POST /crawl returns 202 Accepted and job_id
    crawl_resp = client.post("/crawl", json={"urls": ["https://example.com"], "max_pages": 1})
    assert crawl_resp.status_code == 202
    job_payload = crawl_resp.json()
    assert "job_id" in job_payload
    job_id = job_payload["job_id"]
    assert job_payload["status"] == "queued"

    # 4. Test GET /crawl/status/{job_id}
    status_resp = client.get(f"/crawl/status/{job_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["job_id"] == job_id
    assert status_data["status"] in ("queued", "running", "completed", "failed")

    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)
