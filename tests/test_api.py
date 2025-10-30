import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

from excel_engine import schema_extractor, prompt_builder, llm_client
from excel_engine.interpreter import PlanInterpreter

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Excel AI Engine!"}

def test_analyse_file_not_found(client, monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    response = client.post(
        "/api/analyse",
        json={"file_path": "fake/file/that/does/not/exist.xlsx", "query": "test query"}
    )

    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]

def test_analyse_empty_query(client, monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    
    response = client.post(
        "/api/analyse", 
        json={"file_path": "fake/file.xlsx", "query": ""}
    )

    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]

def test_anaylse_proper_path(client, monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda path: True)

    monkeypatch.setattr(
        "app.routes.get_excel_schema", 
        lambda path: {"fake_schema": ["col1"]}
    )

    monkeypatch.setattr(
        "app.routes.build_analysis_prompt", 
        lambda schema, query: "fake_prompt_string"
    )

    monkeypatch.setattr(
        "app.routes.get_llm_json_response", 
        lambda prompt: {"target_sheet": "fake", "operations": []}
    )
    def mock_init(self, file_path: str):
        print(f"MockInterpreter initialized with {file_path}")
        self.dataframes = {}
    
    def mock_execute(self, plan: dict):
        return {"result": "success"}
    

    class MockInterpreter:
        pass 
    MockInterpreter.__init__ = mock_init
    MockInterpreter.execute_plan = mock_execute
    monkeypatch.setattr("app.routes.PlanInterpreter", MockInterpreter)
    
    response = client.post(
        "/api/analyse",
        json={"file_path": "real/file.xlsx", "query": "What is the average?"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["result"] == {"result": "success"}