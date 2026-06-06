"""
E2E Tests for INTENT-ITERATIVE Web GUI
Uses pytest and httpx for async API testing.
"""

import pytest
import sys
from pathlib import Path
from httpx import AsyncClient, ASGITransport

# Add parent to path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web.app import app


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.anyio
    async def test_health_check(self, client):
        """Test that health endpoint returns healthy status."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestIntentsCRUD:
    """Test intents CRUD operations."""
    
    @pytest.mark.anyio
    async def test_list_intents_empty(self, client):
        """Test listing intents when none exist."""
        response = await client.get("/api/intents")
        assert response.status_code == 200
        data = response.json()
        assert "intents" in data
        assert isinstance(data["intents"], list)
    
    @pytest.mark.anyio
    async def test_parse_valid_dsl(self, client):
        """Test parsing valid DSL content."""
        dsl_content = """
INTENT:
  name: web-test-api
  goal: Test API creation

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose GET /health

EXECUTION:
  mode: dry-run
"""
        response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data
        assert data["intent"]["intent"]["name"] == "web-test-api"
        
        return data["id"]
    
    @pytest.mark.anyio
    async def test_parse_invalid_dsl(self, client):
        """Test parsing invalid DSL content."""
        response = await client.post(
            "/api/intents/parse",
            json={"content": "invalid: [yaml: syntax"}
        )
        
        assert response.status_code == 400
    
    @pytest.mark.anyio
    async def test_parse_missing_intent_section(self, client):
        """Test parsing DSL without INTENT section."""
        dsl_content = """
ENVIRONMENT:
  runtime: docker

IMPLEMENTATION:
  language: python
  actions:
    - api.expose GET /ping
"""
        response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        
        assert response.status_code == 400
        assert "INTENT" in response.json()["detail"]
    
    @pytest.mark.anyio
    async def test_get_intent(self, client):
        """Test getting intent by ID."""
        # First create an intent
        dsl_content = """
INTENT:
  name: get-test
  goal: Test get endpoint

IMPLEMENTATION:
  language: python
  actions:
    - api.expose GET /test
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        # Then get it
        response = await client.get(f"/api/intents/{intent_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["intent"]["name"] == "get-test"
    
    @pytest.mark.anyio
    async def test_get_nonexistent_intent(self, client):
        """Test getting non-existent intent."""
        response = await client.get("/api/intents/nonexistent-id")
        assert response.status_code == 404
    
    @pytest.mark.anyio
    async def test_delete_intent(self, client):
        """Test deleting an intent."""
        # First create
        dsl_content = """
INTENT:
  name: delete-test
  goal: Test deletion

IMPLEMENTATION:
  language: python
  actions:
    - api.expose GET /test
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        # Then delete
        response = await client.delete(f"/api/intents/{intent_id}")
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify it's gone
        get_response = await client.get(f"/api/intents/{intent_id}")
        assert get_response.status_code == 404


class TestPlanningEndpoint:
    """Test dry-run planning endpoint."""
    
    @pytest.mark.anyio
    async def test_plan_intent(self, client):
        """Test running dry-run plan."""
        # Create intent
        dsl_content = """
INTENT:
  name: plan-test
  goal: Test planning

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
    - api.expose POST /users

EXECUTION:
  mode: dry-run
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        # Run plan
        response = await client.post(f"/api/intents/{intent_id}/plan")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "logs" in data
        assert len(data["logs"]) > 0
        assert "generated_code" in data
        assert "fastapi" in data["generated_code"].lower()
        assert "dockerfile" in data
        assert "FROM python:3.12-slim" in data["dockerfile"]
        assert "estimated_resources" in data
    
    @pytest.mark.anyio
    async def test_plan_express(self, client):
        """Test planning for Express.js project."""
        dsl_content = """
INTENT:
  name: express-plan-test
  goal: Test Express planning

ENVIRONMENT:
  runtime: docker
  base_image: node:20

IMPLEMENTATION:
  language: node
  framework: express
  actions:
    - api.expose GET /health
    - api.expose POST /data

EXECUTION:
  mode: dry-run
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        response = await client.post(f"/api/intents/{intent_id}/plan")
        assert response.status_code == 200
        
        data = response.json()
        assert "express" in data["generated_code"].lower()
        assert "app.get" in data["generated_code"]


class TestIterationEndpoint:
    """Test iteration endpoint."""
    
    @pytest.mark.anyio
    async def test_iterate_add_action(self, client):
        """Test adding action via iteration."""
        # Create intent
        dsl_content = """
INTENT:
  name: iterate-test
  goal: Test iteration

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        initial_actions = len(create_response.json()["intent"]["implementation"]["actions"])
        
        # Iterate
        response = await client.post(
            f"/api/intents/{intent_id}/iterate",
            json={
                "changes": {"action": "api.expose POST /users"},
                "source": "test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["iteration_count"] == 1
        assert len(data["intent"]["implementation"]["actions"]) == initial_actions + 1
    
    @pytest.mark.anyio
    async def test_iterate_change_framework(self, client):
        """Test changing framework via iteration."""
        dsl_content = """
INTENT:
  name: framework-test
  goal: Test framework change

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        response = await client.post(
            f"/api/intents/{intent_id}/iterate",
            json={
                "changes": {"framework": "flask"},
                "source": "test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["intent"]["implementation"]["framework"] == "flask"
    
    @pytest.mark.anyio
    async def test_multiple_iterations(self, client):
        """Test multiple iterations tracking."""
        dsl_content = """
INTENT:
  name: multi-iter-test
  goal: Test multiple iterations

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        # First iteration
        await client.post(
            f"/api/intents/{intent_id}/iterate",
            json={"changes": {"action": "api.expose POST /users"}, "source": "test"}
        )
        
        # Second iteration
        response = await client.post(
            f"/api/intents/{intent_id}/iterate",
            json={"changes": {"framework": "flask"}, "source": "test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["iteration_count"] == 2
        assert len(data["intent"]["iteration_history"]) == 2


class TestAmenAndExecution:
    """Test AMEN approval and execution endpoints."""
    
    @pytest.mark.anyio
    async def test_amen_approval(self, client):
        """Test AMEN approval endpoint."""
        dsl_content = """
INTENT:
  name: amen-test
  goal: Test AMEN approval

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        # Approve AMEN
        response = await client.post(f"/api/intents/{intent_id}/amen")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["amen_approved"] is True
        assert data["execution_mode"] == "transactional"
    
    @pytest.mark.anyio
    async def test_execute_without_amen(self, client):
        """Test that execution auto-approves AMEN when skipped."""
        dsl_content = """
INTENT:
  name: no-amen-test
  goal: Test execution without AMEN

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        # Execute without explicit AMEN - should auto-approve
        response = await client.post(f"/api/intents/{intent_id}/execute")
        # Should return 200 with auto-approval (execution may fail without Docker)
        assert response.status_code == 200
        assert "logs" in response.json()


class TestGeneratedCodeEndpoint:
    """Test generated code endpoint."""
    
    @pytest.mark.anyio
    async def test_get_generated_code(self, client):
        """Test getting generated code."""
        dsl_content = """
INTENT:
  name: code-test
  goal: Test code retrieval

ENVIRONMENT:
  runtime: docker

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping
"""
        create_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        intent_id = create_response.json()["id"]
        
        # Run plan first to generate code
        await client.post(f"/api/intents/{intent_id}/plan")
        
        # Get generated code
        response = await client.get(f"/api/intents/{intent_id}/code")
        assert response.status_code == 200
        
        data = response.json()
        assert "generated_code" in data
        assert "dockerfile" in data


class TestEndToEndWorkflow:
    """Complete end-to-end workflow tests."""
    
    @pytest.mark.anyio
    async def test_complete_workflow(self, client):
        """Test complete workflow: parse → plan → iterate → amen."""
        # 1. Parse DSL
        dsl_content = """
INTENT:
  name: e2e-workflow
  goal: Complete E2E test

ENVIRONMENT:
  runtime: docker
  base_image: python:3.12-slim

IMPLEMENTATION:
  language: python
  framework: fastapi
  actions:
    - api.expose GET /ping

EXECUTION:
  mode: dry-run
"""
        parse_response = await client.post(
            "/api/intents/parse",
            json={"content": dsl_content}
        )
        assert parse_response.status_code == 200
        intent_id = parse_response.json()["id"]
        
        # 2. Run plan
        plan_response = await client.post(f"/api/intents/{intent_id}/plan")
        assert plan_response.status_code == 200
        assert plan_response.json()["success"]
        
        # 3. Iterate - add endpoint
        iter_response = await client.post(
            f"/api/intents/{intent_id}/iterate",
            json={
                "changes": {"action": "api.expose POST /users"},
                "source": "e2e-test"
            }
        )
        assert iter_response.status_code == 200
        assert iter_response.json()["iteration_count"] == 1
        
        # 4. Re-plan after iteration
        plan_response2 = await client.post(f"/api/intents/{intent_id}/plan")
        assert plan_response2.status_code == 200
        assert "@app.post" in plan_response2.json()["generated_code"]
        
        # 5. Approve AMEN
        amen_response = await client.post(f"/api/intents/{intent_id}/amen")
        assert amen_response.status_code == 200
        assert amen_response.json()["amen_approved"]
        
        # 6. Verify final state
        final_response = await client.get(f"/api/intents/{intent_id}")
        assert final_response.status_code == 200
        final_data = final_response.json()
        assert final_data["amen_approved"] is True
        assert final_data["execution_mode"] == "transactional"
        assert final_data["iteration_count"] == 1


class TestHomePage:
    """Test home page rendering."""
    
    @pytest.mark.anyio
    async def test_home_page_renders(self, client):
        """Test that home page renders HTML."""
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "INTENT-ITERATIVE" in response.text


def run_tests():
    """Run all tests."""
    pytest.main([__file__, "-v", "--tb=short", "-x"])


if __name__ == "__main__":
    run_tests()
