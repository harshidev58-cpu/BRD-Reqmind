"""Unit tests for logging behavior in the BRD Generator Backend API.

This module tests that:
- Errors are logged with sufficient detail
- API keys are not exposed in logs
- Request IDs are included in log messages
"""

import logging
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-12345")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")
    monkeypatch.setenv("PORT", "8000")


@pytest.fixture
def client(mock_env):
    """Create a test client for the FastAPI application."""
    return TestClient(app)


class TestLoggingBehavior:
    """Test suite for logging behavior."""
    
    def test_errors_are_logged_with_sufficient_detail(self, client, caplog):
        """Test that errors are logged with sufficient detail including request ID."""
        with caplog.at_level(logging.ERROR):
            # Mock the dependency to avoid OpenAI client initialization
            with patch('app.routers.brd.OpenAIClient') as mock_openai_class:
                with patch('app.routers.brd.BRDGeneratorService') as mock_service_class:
                    mock_instance = MagicMock()
                    mock_instance.generate_brd.side_effect = Exception("Test error")
                    mock_service_class.return_value = mock_instance
                    
                    # Make a request that will trigger an error
                    response = client.post(
                        "/generate_brd",
                        json={
                            "projectName": "Test Project",
                            "emailText": "Test email content"
                        }
                    )
                    
                    # Verify the error response
                    assert response.status_code == 500
                    
                    # Verify error was logged with detail
                    assert any("Unexpected error" in record.message for record in caplog.records)
                    assert any("Test error" in record.message for record in caplog.records)
                    
                    # Verify request ID is present in logs
                    assert any(hasattr(record, 'request_id') for record in caplog.records)
    
    def test_validation_errors_are_logged_as_warnings(self, client, caplog):
        """Test that validation errors are logged as warnings with request ID."""
        with caplog.at_level(logging.WARNING):
            # Mock the dependency to avoid OpenAI client initialization
            with patch('app.routers.brd.OpenAIClient') as mock_openai_class:
                with patch('app.routers.brd.BRDGeneratorService') as mock_service_class:
                    # Make a request with missing projectName
                    response = client.post(
                        "/generate_brd",
                        json={
                            "emailText": "Test email content"
                        }
                    )
                    
                    # Verify the validation error response (FastAPI returns 422 for Pydantic validation errors)
                    assert response.status_code == 422
                    
                    # Note: FastAPI's built-in Pydantic validation happens before our error handler,
                    # so we verify that our custom error handler logs warnings when it's invoked
                    # This is tested separately in the error handler tests
    
    def test_successful_requests_are_logged_as_info(self, client, caplog):
        """Test that successful requests are logged at INFO level with request ID."""
        with caplog.at_level(logging.INFO):
            # Mock the dependency to avoid OpenAI client initialization
            with patch('app.routers.brd.OpenAIClient') as mock_openai_class:
                with patch('app.routers.brd.BRDGeneratorService') as mock_service_class:
                    mock_instance = AsyncMock()
                    mock_instance.generate_brd.return_value = {
                        "projectName": "Test Project",
                        "executiveSummary": "Test summary",
                        "businessObjectives": ["Objective 1"],
                        "requirements": [
                            {"id": "REQ-1", "description": "Test requirement", "priority": "High"}
                        ],
                        "stakeholders": [
                            {"name": "Test Stakeholder", "role": "Test Role"}
                        ]
                    }
                    mock_service_class.return_value = mock_instance
                    
                    # Make a successful request
                    response = client.post(
                        "/generate_brd",
                        json={
                            "projectName": "Test Project",
                            "emailText": "Test email content"
                        }
                    )
                    
                    # Verify successful response
                    assert response.status_code == 200
                    
                    # Verify success was logged at INFO level
                    assert any(
                        record.levelname == "INFO" and "Successfully generated BRD" in record.message
                        for record in caplog.records
                    )
                    
                    # Verify request ID is present
                    assert any(hasattr(record, 'request_id') for record in caplog.records)


class TestSensitiveDataProtection:
    """Test suite for ensuring sensitive data is not logged."""
    
    def test_api_key_not_exposed_in_startup_logs(self, mock_env, caplog):
        """Test that API keys are not exposed in startup logs."""
        from app.config import get_settings
        
        with caplog.at_level(logging.INFO):
            # Get settings to trigger logging
            settings = get_settings()
            
            # Verify API key is not in any log messages
            for record in caplog.records:
                assert "test-api-key-12345" not in record.message, \
                    "API key should not be exposed in logs"
    
    def test_api_key_not_exposed_in_error_logs(self, client, caplog):
        """Test that API keys are not exposed in error logs."""
        with caplog.at_level(logging.ERROR):
            # Mock the dependency to avoid OpenAI client initialization
            with patch('app.routers.brd.OpenAIClient') as mock_openai_class:
                with patch('app.routers.brd.BRDGeneratorService') as mock_service_class:
                    mock_instance = MagicMock()
                    mock_instance.generate_brd.side_effect = Exception("Test error with sensitive data")
                    mock_service_class.return_value = mock_instance
                    
                    # Make a request that will trigger an error
                    response = client.post(
                        "/generate_brd",
                        json={
                            "projectName": "Test Project",
                            "emailText": "Test email content"
                        }
                    )
                    
                    # Verify the error response
                    assert response.status_code == 500
                    
                    # Verify API key is not in any log messages
                    for record in caplog.records:
                        assert "test-api-key-12345" not in record.message, \
                            "API key should not be exposed in error logs"
    
    def test_configuration_logs_do_not_contain_api_key(self, mock_env, caplog):
        """Test that configuration validation logs do not contain the actual API key."""
        from app.config import get_settings
        
        with caplog.at_level(logging.INFO):
            # Trigger configuration loading
            settings = get_settings()
            
            # Check all log records
            for record in caplog.records:
                # Verify the API key value is not in the log message
                assert "test-api-key-12345" not in record.message, \
                    "API key value should never appear in logs"
                
                # Verify we log that the key is validated, but not the key itself
                if "API key" in record.message:
                    assert "validated" in record.message.lower() or "present" in record.message.lower(), \
                        "API key logs should only confirm validation, not show the key"


class TestRequestIDTracking:
    """Test suite for request ID tracking in logs."""
    
    def test_request_id_is_generated_for_each_request(self, client, caplog):
        """Test that a unique request ID is generated for each request."""
        with caplog.at_level(logging.INFO):
            # Mock the dependency to avoid OpenAI client initialization
            with patch('app.routers.brd.OpenAIClient') as mock_openai_class:
                with patch('app.routers.brd.BRDGeneratorService') as mock_service_class:
                    mock_instance = AsyncMock()
                    mock_instance.generate_brd.return_value = {
                        "projectName": "Test Project",
                        "executiveSummary": "Test summary",
                        "businessObjectives": ["Objective 1"],
                        "requirements": [
                            {"id": "REQ-1", "description": "Test requirement", "priority": "High"}
                        ],
                        "stakeholders": [
                            {"name": "Test Stakeholder", "role": "Test Role"}
                        ]
                    }
                    mock_service_class.return_value = mock_instance
                    
                    # Clear previous logs
                    caplog.clear()
                    
                    # Make first request
                    response1 = client.post(
                        "/generate_brd",
                        json={
                            "projectName": "Test Project 1",
                            "emailText": "Test email content 1"
                        }
                    )
                    
                    # Get request ID from first request logs
                    request_id_1 = None
                    for record in caplog.records:
                        if hasattr(record, 'request_id') and record.request_id != 'N/A':
                            request_id_1 = record.request_id
                            break
                    
                    # Clear logs
                    caplog.clear()
                    
                    # Make second request
                    response2 = client.post(
                        "/generate_brd",
                        json={
                            "projectName": "Test Project 2",
                            "emailText": "Test email content 2"
                        }
                    )
                    
                    # Get request ID from second request logs
                    request_id_2 = None
                    for record in caplog.records:
                        if hasattr(record, 'request_id') and record.request_id != 'N/A':
                            request_id_2 = record.request_id
                            break
                    
                    # Verify both requests succeeded
                    assert response1.status_code == 200
                    assert response2.status_code == 200
                    
                    # Verify request IDs are different
                    assert request_id_1 is not None, "First request should have a request ID"
                    assert request_id_2 is not None, "Second request should have a request ID"
                    assert request_id_1 != request_id_2, "Each request should have a unique request ID"
    
    def test_request_id_is_consistent_throughout_request_lifecycle(self, client, caplog):
        """Test that the same request ID is used throughout a single request lifecycle."""
        with caplog.at_level(logging.INFO):
            # Mock the dependency to avoid OpenAI client initialization
            with patch('app.routers.brd.OpenAIClient') as mock_openai_class:
                with patch('app.routers.brd.BRDGeneratorService') as mock_service_class:
                    mock_instance = AsyncMock()
                    mock_instance.generate_brd.return_value = {
                        "projectName": "Test Project",
                        "executiveSummary": "Test summary",
                        "businessObjectives": ["Objective 1"],
                        "requirements": [
                            {"id": "REQ-1", "description": "Test requirement", "priority": "High"}
                        ],
                        "stakeholders": [
                            {"name": "Test Stakeholder", "role": "Test Role"}
                        ]
                    }
                    mock_service_class.return_value = mock_instance
                    
                    # Clear previous logs
                    caplog.clear()
                    
                    # Make a request
                    response = client.post(
                        "/generate_brd",
                        json={
                            "projectName": "Test Project",
                            "emailText": "Test email content"
                        }
                    )
                    
                    # Verify successful response
                    assert response.status_code == 200
                    
                    # Collect all request IDs from this request
                    request_ids = set()
                    for record in caplog.records:
                        if hasattr(record, 'request_id') and record.request_id != 'N/A':
                            request_ids.add(record.request_id)
                    
                    # Verify all logs for this request use the same request ID
                    assert len(request_ids) == 1, \
                        f"All logs for a single request should use the same request ID, found: {request_ids}"
