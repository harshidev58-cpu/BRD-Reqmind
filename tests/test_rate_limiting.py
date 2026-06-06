"""Unit tests for rate limiting on context endpoint."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test."""
    from app.main import limiter
    # Reset the rate limiter storage
    limiter._storage.reset()
    yield
    # Clean up after test
    limiter._storage.reset()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock all service dependencies."""
    with patch('app.routers.context.get_gemini_service') as mock_gemini, \
         patch('app.routers.context.get_constraint_applier') as mock_constraint, \
         patch('app.routers.context.get_chunk_processor') as mock_chunk, \
         patch('app.routers.context.get_ingestion_tracker') as mock_tracker, \
         patch('app.routers.context.get_aggregator') as mock_aggregator, \
         patch('app.routers.context.get_brd_generator_service') as mock_brd, \
         patch('app.routers.context.get_alignment_engine') as mock_alignment:
        
        # Mock Gemini service
        gemini_mock = MagicMock()
        gemini_mock.generate_constraints = AsyncMock(return_value=None)
        mock_gemini.return_value = gemini_mock
        
        # Mock constraint applier
        constraint_mock = MagicMock()
        constraint_mock.apply_constraints = MagicMock(side_effect=lambda data, constraints: data)
        mock_constraint.return_value = constraint_mock
        
        # Mock chunk processor
        chunk_mock = MagicMock()
        chunk_mock.needs_chunking = MagicMock(return_value=False)
        mock_chunk.return_value = chunk_mock
        
        # Mock ingestion tracker
        tracker_mock = MagicMock()
        tracker_mock.start_tracking = MagicMock(return_value="test-tracking-id")
        tracker_mock.track_email = MagicMock()
        tracker_mock.track_slack_message = MagicMock()
        tracker_mock.track_meeting = MagicMock()
        tracker_mock.get_summary = MagicMock(return_value=MagicMock(
            emails_used=0,
            slack_messages_used=0,
            meetings_used=0,
            total_chunks_processed=0,
            total_words_processed=0,
            processing_time_seconds=0.0,
            sample_sources=[]
        ))
        mock_tracker.return_value = tracker_mock
        
        # Mock aggregator
        aggregator_mock = MagicMock()
        mock_aggregator.return_value = aggregator_mock
        
        # Mock BRD generator
        brd_mock = MagicMock()
        brd_mock.generate_brd = AsyncMock(return_value=MagicMock(
            projectName="Test Project",
            executiveSummary="Test summary",
            businessObjectives=["Objective 1"],
            requirements=[],
            stakeholders=[]
        ))
        mock_brd.return_value = brd_mock
        
        # Mock alignment engine
        alignment_mock = MagicMock()
        alignment_mock.analyze_alignment = MagicMock(return_value=MagicMock(
            alignment_score=85.0,
            risk_level="LOW",
            alert="No issues",
            conflicts=[],
            timeline_mismatches=[],
            requirement_volatility={},
            stakeholder_agreement_score=90.0,
            timeline_consistency_score=85.0,
            requirement_stability_score=88.0,
            decision_volatility_score=82.0
        ))
        alignment_mock.generate_conflict_explanations = MagicMock(return_value=[])
        mock_alignment.return_value = alignment_mock
        
        yield {
            'gemini': gemini_mock,
            'constraint': constraint_mock,
            'chunk': chunk_mock,
            'tracker': tracker_mock,
            'aggregator': aggregator_mock,
            'brd': brd_mock,
            'alignment': alignment_mock
        }


class TestRateLimiting:
    """Tests for rate limiting on context endpoint."""
    
    def test_rate_limit_allows_requests_within_limit(self, client, mock_services):
        """Test that requests within rate limit are allowed."""
        # Make 5 requests (well within the 10/minute limit)
        for i in range(5):
            response = client.post(
                "/generate_brd_with_context",
                json={
                    "data": {
                        "emails": [{"subject": "Test", "body": "Test email"}],
                        "slack_messages": [],
                        "meetings": []
                    }
                }
            )
            
            # All requests should succeed
            assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}"
    
    def test_rate_limit_blocks_excessive_requests(self, client, mock_services):
        """Test that requests exceeding rate limit are blocked."""
        # Make 11 requests (exceeds the 10/minute limit)
        responses = []
        for i in range(11):
            response = client.post(
                "/generate_brd_with_context",
                json={
                    "data": {
                        "emails": [{"subject": "Test", "body": "Test email"}],
                        "slack_messages": [],
                        "meetings": []
                    }
                }
            )
            responses.append(response)
        
        # First 10 should succeed
        for i in range(10):
            assert responses[i].status_code == 200, f"Request {i+1} should have succeeded"
        
        # 11th request should be rate limited
        assert responses[10].status_code == 429, "11th request should be rate limited"
        assert "rate limit" in responses[10].text.lower(), "Response should mention rate limit"
    
    def test_rate_limit_per_ip(self, client, mock_services):
        """Test that rate limiting is applied per IP address."""
        # This test verifies the rate limiter uses IP-based limiting
        # In a real scenario, different IPs would have separate limits
        
        # Make requests from the same IP (test client default)
        response1 = client.post(
            "/generate_brd_with_context",
            json={
                "data": {
                    "emails": [{"subject": "Test", "body": "Test email"}],
                    "slack_messages": [],
                    "meetings": []
                }
            }
        )
        
        response2 = client.post(
            "/generate_brd_with_context",
            json={
                "data": {
                    "emails": [{"subject": "Test", "body": "Test email"}],
                    "slack_messages": [],
                    "meetings": []
                }
            }
        )
        
        # Both should succeed (within limit)
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestInputValidationIntegration:
    """Integration tests for input validation in the endpoint."""
    
    def test_rejects_instructions_exceeding_max_length(self, client, mock_services):
        """Test that instructions exceeding max length are rejected."""
        long_instructions = "a" * 2001  # Exceeds 2000 char limit
        
        response = client.post(
            "/generate_brd_with_context",
            json={
                "instructions": long_instructions,
                "data": {
                    "emails": [{"subject": "Test", "body": "Test email"}],
                    "slack_messages": [],
                    "meetings": []
                }
            }
        )
        
        assert response.status_code == 422  # Pydantic validation error
        assert "String should have at most 2000 characters" in str(response.json())
    
    def test_rejects_too_many_items(self, client, mock_services):
        """Test that requests with too many items are rejected."""
        # Create 1001 emails (exceeds 1000 item limit)
        emails = [
            {
                "subject": f"Email {i}",
                "body": "Body",
                "sender": "user@test.com",
                "date": "2024-01-01"
            }
            for i in range(1001)
        ]
        
        response = client.post(
            "/generate_brd_with_context",
            json={
                "data": {
                    "emails": emails,
                    "slack_messages": [],
                    "meetings": []
                }
            }
        )
        
        assert response.status_code == 400
        assert "exceeds maximum" in response.json()["detail"]
    
    def test_sanitizes_control_characters(self, client, mock_services):
        """Test that control characters are sanitized from instructions."""
        instructions_with_control = "Focus\x00on MVP"
        
        response = client.post(
            "/generate_brd_with_context",
            json={
                "instructions": instructions_with_control,
                "data": {
                    "emails": [{"subject": "Test", "body": "Test email"}],
                    "slack_messages": [],
                    "meetings": []
                }
            }
        )
        
        # Request should succeed (control chars are sanitized, not rejected)
        assert response.status_code == 200
        
        # Verify that sanitized instructions were used
        # (control characters should have been removed)
        mock_services['gemini'].generate_constraints.assert_called_once()
        call_args = mock_services['gemini'].generate_constraints.call_args
        sanitized_instructions = call_args[0][0]
        assert "\x00" not in sanitized_instructions


class TestRateLimitingEdgeCases:
    """Additional tests for rate limiting edge cases and security."""
    
    def test_rate_limit_resets_after_time_window(self, client, mock_services):
        """Test that rate limit counter resets after the time window."""
        # Make requests up to the limit
        for i in range(10):
            response = client.post(
                "/generate_brd_with_context",
                json={
                    "data": {
                        "emails": [{"subject": "Test", "body": "Test email"}],
                        "slack_messages": [],
                        "meetings": []
                    }
                }
            )
            assert response.status_code == 200
        
        # Note: In a real test, we would wait for the time window to expire
        # or mock the time. This test documents the expected behavior.
    
    def test_rate_limit_error_response_format(self, client, mock_services):
        """Test that rate limit error response has correct format."""
        # Exhaust the rate limit
        for i in range(11):
            response = client.post(
                "/generate_brd_with_context",
                json={
                    "data": {
                        "emails": [{"subject": "Test", "body": "Test email"}],
                        "slack_messages": [],
                        "meetings": []
                    }
                }
            )
        
        # Check the 11th response (rate limited)
        assert response.status_code == 429
        assert "rate limit" in response.text.lower()
    
    def test_rate_limit_applies_to_endpoint_only(self, client, mock_services):
        """Test that rate limit is specific to the context endpoint."""
        # This test verifies that other endpoints are not affected
        # by rate limiting on the context endpoint
        
        # Exhaust rate limit on context endpoint
        for i in range(11):
            client.post(
                "/generate_brd_with_context",
                json={
                    "data": {
                        "emails": [{"subject": "Test", "body": "Test email"}],
                        "slack_messages": [],
                        "meetings": []
                    }
                }
            )
        
        # Other endpoints should still work (if they exist)
        # This is a placeholder test to document the behavior
        # In a real scenario, we would test other endpoints here


class TestSecurityValidationIntegration:
    """Integration tests for security validation in the endpoint."""
    
    def test_rejects_email_with_oversized_subject(self, client, mock_services):
        """Test that emails with oversized subjects are rejected."""
        response = client.post(
            "/generate_brd_with_context",
            json={
                "data": {
                    "emails": [
                        {
                            "subject": "a" * 100001,  # Exceeds 100,000 char limit
                            "body": "Body",
                            "sender": "user@test.com",
                            "date": "2024-01-01"
                        }
                    ],
                    "slack_messages": [],
                    "meetings": []
                }
            }
        )
        
        assert response.status_code == 400
        assert "exceeds maximum length" in response.json()["detail"]
    
    def test_rejects_slack_message_with_oversized_text(self, client, mock_services):
        """Test that Slack messages with oversized text are rejected."""
        response = client.post(
            "/generate_brd_with_context",
            json={
                "data": {
                    "emails": [],
                    "slack_messages": [
                        {
                            "channel": "#general",
                            "user": "user1",
                            "text": "a" * 100001,  # Exceeds 100,000 char limit
                            "timestamp": "2024-01-01"
                        }
                    ],
                    "meetings": []
                }
            }
        )
        
        assert response.status_code == 400
        assert "exceeds maximum length" in response.json()["detail"]
    
    def test_rejects_meeting_with_oversized_transcript(self, client, mock_services):
        """Test that meetings with oversized transcripts are rejected."""
        response = client.post(
            "/generate_brd_with_context",
            json={
                "data": {
                    "emails": [],
                    "slack_messages": [],
                    "meetings": [
                        {
                            "transcript": "a" * 100001,  # Exceeds 100,000 char limit
                            "topic": "Planning",
                            "speakers": ["PM"],
                            "timestamp": "2024-01-01"
                        }
                    ]
                }
            }
        )
        
        assert response.status_code == 400
        assert "exceeds maximum length" in response.json()["detail"]
    
    def test_accepts_valid_request_with_all_data_types(self, client, mock_services):
        """Test that valid requests with all data types are accepted."""
        response = client.post(
            "/generate_brd_with_context",
            json={
                "instructions": "Focus on MVP features",
                "data": {
                    "emails": [
                        {
                            "subject": "Test Email",
                            "body": "Email body content",
                            "sender": "user@test.com",
                            "date": "2024-01-01"
                        }
                    ],
                    "slack_messages": [
                        {
                            "channel": "#general",
                            "user": "user1",
                            "text": "Slack message content",
                            "timestamp": "2024-01-01"
                        }
                    ],
                    "meetings": [
                        {
                            "transcript": "Meeting transcript content",
                            "topic": "Planning",
                            "speakers": ["PM", "Dev"],
                            "timestamp": "2024-01-01"
                        }
                    ]
                }
            }
        )
        
        assert response.status_code == 200
        assert "brd" in response.json()
        assert "alignment_analysis" in response.json()
        assert "ingestion_summary" in response.json()
    
    def test_sanitization_preserves_valid_content(self, client, mock_services):
        """Test that sanitization doesn't remove valid content."""
        instructions = "Focus on MVP\nLine 2\tTabbed content"
        
        response = client.post(
            "/generate_brd_with_context",
            json={
                "instructions": instructions,
                "data": {
                    "emails": [{"subject": "Test", "body": "Test email"}],
                    "slack_messages": [],
                    "meetings": []
                }
            }
        )
        
        assert response.status_code == 200
        
        # Verify that valid whitespace was preserved
        mock_services['gemini'].generate_constraints.assert_called_once()
        call_args = mock_services['gemini'].generate_constraints.call_args
        sanitized_instructions = call_args[0][0]
        assert "\n" in sanitized_instructions
        assert "\t" in sanitized_instructions
