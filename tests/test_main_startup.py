"""Tests for application startup and cleanup task initialization.

This module tests that the cleanup task is properly started during
application startup.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestApplicationStartup:
    """Test application startup behavior."""
    
    def test_cleanup_task_started_on_startup(self):
        """Test that cleanup task is started during application startup."""
        # Mock the ingestion tracker to verify start_cleanup_task is called
        with patch('app.main.get_ingestion_tracker') as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker
            
            # Import app after mocking to trigger startup
            from app.main import app
            
            # Create test client (this triggers the lifespan startup)
            with TestClient(app) as client:
                # Verify the tracker was retrieved
                mock_get_tracker.assert_called_once()
                
                # Verify start_cleanup_task was called with correct interval
                mock_tracker.start_cleanup_task.assert_called_once_with(cleanup_interval=600)
                
                # Verify the app is running
                response = client.get("/")
                assert response.status_code == 200
                assert "BRD Generator Backend API is running" in response.json()["message"]
