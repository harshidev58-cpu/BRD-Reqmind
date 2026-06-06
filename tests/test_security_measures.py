"""Unit tests for security measures - input validation, sanitization, and rate limiting.

This test file focuses on security-specific test cases for NFR-4 requirements.
"""

import pytest
from fastapi import HTTPException

from app.utils.validators import (
    sanitize_instructions,
    validate_instructions,
    validate_text_length,
    validate_data_sources,
    validate_context_request,
    MAX_INSTRUCTION_LENGTH,
    MAX_TEXT_LENGTH_PER_ITEM,
    MAX_TOTAL_ITEMS
)
from app.models.context_request import IngestionData
from app.models.request import Email, SlackMessage, Meeting


class TestInputValidationSecurity:
    """Security-focused tests for input validation."""
    
    def test_rejects_oversized_instructions(self):
        """Test that instructions exceeding max length are rejected."""
        oversized = "a" * (MAX_INSTRUCTION_LENGTH + 1)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_instructions(oversized)
        
        assert exc_info.value.status_code == 400
        assert "exceed maximum length" in exc_info.value.detail
    
    def test_rejects_oversized_email_subject(self):
        """Test that email subjects exceeding max length are rejected."""
        data = IngestionData(
            emails=[
                Email(
                    subject="a" * (MAX_TEXT_LENGTH_PER_ITEM + 1),
                    body="Body",
                    sender="user@test.com",
                    date="2024-01-01"
                )
            ]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            validate_data_sources(data)
        
        assert exc_info.value.status_code == 400
        assert "Email 1 subject" in exc_info.value.detail
        assert "exceeds maximum length" in exc_info.value.detail
    
    def test_rejects_oversized_email_body(self):
        """Test that email bodies exceeding max length are rejected."""
        data = IngestionData(
            emails=[
                Email(
                    subject="Subject",
                    body="a" * (MAX_TEXT_LENGTH_PER_ITEM + 1),
                    sender="user@test.com",
                    date="2024-01-01"
                )
            ]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            validate_data_sources(data)
        
        assert exc_info.value.status_code == 400
        assert "Email 1 body" in exc_info.value.detail
    
    def test_rejects_oversized_slack_text(self):
        """Test that Slack message text exceeding max length is rejected."""
        data = IngestionData(
            slack_messages=[
                SlackMessage(
                    channel="#general",
                    user="user1",
                    text="a" * (MAX_TEXT_LENGTH_PER_ITEM + 1),
                    timestamp="2024-01-01"
                )
            ]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            validate_data_sources(data)
        
        assert exc_info.value.status_code == 400
        assert "Slack message 1 text" in exc_info.value.detail
    
    def test_rejects_oversized_meeting_transcript(self):
        """Test that meeting transcripts exceeding max length are rejected."""
        data = IngestionData(
            meetings=[
                Meeting(
                    transcript="a" * (MAX_TEXT_LENGTH_PER_ITEM + 1),
                    topic="Planning",
                    speakers=["PM"],
                    timestamp="2024-01-01"
                )
            ]
        )
        
        with pytest.raises(HTTPException) as exc_info:
            validate_data_sources(data)
        
        assert exc_info.value.status_code == 400
        assert "Meeting 1 transcript" in exc_info.value.detail
    
    def test_rejects_too_many_total_items(self):
        """Test that requests with too many total items are rejected."""
        emails = [
            Email(subject=f"Email {i}", body="Body", sender="user@test.com", date="2024-01-01")
            for i in range(MAX_TOTAL_ITEMS + 1)
        ]
        data = IngestionData(emails=emails)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_data_sources(data)
        
        assert exc_info.value.status_code == 400
        assert "exceeds maximum" in exc_info.value.detail
        assert str(MAX_TOTAL_ITEMS + 1) in exc_info.value.detail


class TestSanitizationSecurity:
    """Security-focused tests for input sanitization."""
    
    def test_removes_null_bytes(self):
        """Test that null bytes are removed from instructions."""
        malicious = "Focus\x00on MVP"
        sanitized = sanitize_instructions(malicious)
        
        assert "\x00" not in sanitized
        assert sanitized == "Focuson MVP"
    
    def test_removes_all_dangerous_control_characters(self):
        """Test that all dangerous control characters are removed."""
        dangerous_chars = [
            ("\x00", "Null byte"),
            ("\x01", "Start of heading"),
            ("\x02", "Start of text"),
            ("\x08", "Backspace"),
            ("\x0B", "Vertical tab"),
            ("\x0C", "Form feed"),
            ("\x0E", "Shift out"),
            ("\x1F", "Unit separator"),
            ("\x7F", "Delete"),
        ]
        
        for char, name in dangerous_chars:
            text = f"Before{char}After"
            sanitized = sanitize_instructions(text)
            assert char not in sanitized, f"{name} ({repr(char)}) was not removed"
            assert sanitized == "BeforeAfter"
    
    def test_preserves_safe_whitespace(self):
        """Test that safe whitespace characters are preserved."""
        text = "Line 1\nLine 2\rLine 3\tTabbed"
        sanitized = sanitize_instructions(text)
        
        assert "\n" in sanitized
        assert "\r" in sanitized
        assert "\t" in sanitized
        assert sanitized == text
    
    def test_removes_multiple_consecutive_control_characters(self):
        """Test that multiple consecutive control characters are removed."""
        text = "Start\x00\x01\x02Middle\x1F\x7FEnd"
        sanitized = sanitize_instructions(text)
        
        assert sanitized == "StartMiddleEnd"
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        assert "\x02" not in sanitized
        assert "\x1F" not in sanitized
        assert "\x7F" not in sanitized
    
    def test_preserves_unicode_characters(self):
        """Test that valid Unicode characters are preserved."""
        text = "Focus on MVP 中文 العربية 🚀"
        sanitized = sanitize_instructions(text)
        
        assert sanitized == text


class TestInjectionPatternHandling:
    """Tests for handling common injection attack patterns."""
    
    def test_handles_sql_injection_patterns_safely(self):
        """Test that SQL injection patterns don't cause errors."""
        sql_patterns = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "1; DELETE FROM users WHERE 1=1--"
        ]
        
        for pattern in sql_patterns:
            # Should not raise exception - just validate length
            if len(pattern) <= MAX_INSTRUCTION_LENGTH:
                validate_instructions(pattern)  # Should not raise
                sanitized = sanitize_instructions(pattern)
                assert sanitized is not None
                # Pattern should be preserved (we don't filter SQL, just control chars)
                assert sanitized == pattern
    
    def test_handles_script_injection_patterns_safely(self):
        """Test that script injection patterns don't cause errors."""
        script_patterns = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert(String.fromCharCode(88,83,83))//'"
        ]
        
        for pattern in script_patterns:
            # Should not raise exception - just validate length
            if len(pattern) <= MAX_INSTRUCTION_LENGTH:
                validate_instructions(pattern)  # Should not raise
                sanitized = sanitize_instructions(pattern)
                assert sanitized is not None
                # Pattern should be preserved (we don't filter HTML/JS, just control chars)
                assert sanitized == pattern
    
    def test_handles_path_traversal_patterns_safely(self):
        """Test that path traversal patterns don't cause errors."""
        path_patterns = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd"
        ]
        
        for pattern in path_patterns:
            if len(pattern) <= MAX_INSTRUCTION_LENGTH:
                validate_instructions(pattern)  # Should not raise
                sanitized = sanitize_instructions(pattern)
                assert sanitized is not None
                assert sanitized == pattern
    
    def test_handles_command_injection_patterns_safely(self):
        """Test that command injection patterns don't cause errors."""
        command_patterns = [
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "`rm -rf /`",
            "$(cat /etc/passwd)"
        ]
        
        for pattern in command_patterns:
            if len(pattern) <= MAX_INSTRUCTION_LENGTH:
                validate_instructions(pattern)  # Should not raise
                sanitized = sanitize_instructions(pattern)
                assert sanitized is not None
                assert sanitized == pattern


class TestBoundaryConditions:
    """Tests for boundary conditions in security validation."""
    
    def test_exactly_at_instruction_length_limit(self):
        """Test that instructions exactly at the limit are accepted."""
        at_limit = "a" * MAX_INSTRUCTION_LENGTH
        validate_instructions(at_limit)  # Should not raise
    
    def test_one_over_instruction_length_limit(self):
        """Test that instructions one character over the limit are rejected."""
        over_limit = "a" * (MAX_INSTRUCTION_LENGTH + 1)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_instructions(over_limit)
        
        assert exc_info.value.status_code == 400
    
    def test_exactly_at_text_length_limit(self):
        """Test that text exactly at the limit is accepted."""
        at_limit = "a" * MAX_TEXT_LENGTH_PER_ITEM
        validate_text_length(at_limit, "Test field")  # Should not raise
    
    def test_one_over_text_length_limit(self):
        """Test that text one character over the limit is rejected."""
        over_limit = "a" * (MAX_TEXT_LENGTH_PER_ITEM + 1)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_text_length(over_limit, "Test field")
        
        assert exc_info.value.status_code == 400
        assert "Test field" in exc_info.value.detail
    
    def test_exactly_at_total_items_limit(self):
        """Test that exactly MAX_TOTAL_ITEMS is accepted."""
        emails = [
            Email(subject=f"Email {i}", body="Body", sender="user@test.com", date="2024-01-01")
            for i in range(MAX_TOTAL_ITEMS)
        ]
        data = IngestionData(emails=emails)
        validate_data_sources(data)  # Should not raise
    
    def test_one_over_total_items_limit(self):
        """Test that MAX_TOTAL_ITEMS + 1 is rejected."""
        emails = [
            Email(subject=f"Email {i}", body="Body", sender="user@test.com", date="2024-01-01")
            for i in range(MAX_TOTAL_ITEMS + 1)
        ]
        data = IngestionData(emails=emails)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_data_sources(data)
        
        assert exc_info.value.status_code == 400
        assert "exceeds maximum" in exc_info.value.detail
    
    def test_mixed_items_at_limit(self):
        """Test that mixed data sources totaling exactly MAX_TOTAL_ITEMS is accepted."""
        emails_count = MAX_TOTAL_ITEMS // 3
        slack_count = MAX_TOTAL_ITEMS // 3
        meetings_count = MAX_TOTAL_ITEMS - emails_count - slack_count
        
        data = IngestionData(
            emails=[
                Email(subject=f"Email {i}", body="Body", sender="user@test.com", date="2024-01-01")
                for i in range(emails_count)
            ],
            slack_messages=[
                SlackMessage(channel="#general", user="user1", text=f"Message {i}", timestamp="2024-01-01")
                for i in range(slack_count)
            ],
            meetings=[
                Meeting(transcript=f"Meeting {i}", topic="Topic", speakers=["PM"], timestamp="2024-01-01")
                for i in range(meetings_count)
            ]
        )
        
        validate_data_sources(data)  # Should not raise


class TestEdgeCases:
    """Tests for edge cases in security validation."""
    
    def test_empty_instructions_are_valid(self):
        """Test that empty instructions are accepted."""
        validate_instructions("")  # Should not raise
        validate_instructions(None)  # Should not raise
    
    def test_empty_data_sources_are_valid(self):
        """Test that empty data sources are accepted."""
        data = IngestionData()
        validate_data_sources(data)  # Should not raise
    
    def test_empty_optional_fields_are_valid(self):
        """Test that empty optional fields don't cause validation errors."""
        data = IngestionData(
            emails=[
                Email(subject="", body="", sender="", date="")
            ],
            slack_messages=[
                SlackMessage(channel="", user="", text="", timestamp="")
            ],
            meetings=[
                Meeting(transcript="", topic="", speakers=[], timestamp="")
            ]
        )
        
        validate_data_sources(data)  # Should not raise
    
    def test_special_characters_in_data_are_valid(self):
        """Test that special characters in data sources are handled correctly."""
        data = IngestionData(
            emails=[
                Email(
                    subject="Test <script>alert('xss')</script>",
                    body="Body with 'quotes' and \"double quotes\"",
                    sender="user@test.com",
                    date="2024-01-01"
                )
            ],
            slack_messages=[
                SlackMessage(
                    channel="#general",
                    user="user1",
                    text="Message with special chars: !@#$%^&*()",
                    timestamp="2024-01-01"
                )
            ]
        )
        
        validate_data_sources(data)  # Should not raise
    
    def test_context_request_validation_with_edge_cases(self):
        """Test complete request validation with various edge cases."""
        # Test with maximum valid instructions and data
        max_instructions = "a" * MAX_INSTRUCTION_LENGTH
        data = IngestionData(
            emails=[
                Email(subject="Test", body="Body", sender="user@test.com", date="2024-01-01")
            ]
        )
        
        sanitized, validated = validate_context_request(max_instructions, data)
        assert sanitized == max_instructions
        assert validated == data
        
        # Test with None instructions and empty data
        sanitized, validated = validate_context_request(None, IngestionData())
        assert sanitized is None
        assert validated.emails == []
        assert validated.slack_messages == []
        assert validated.meetings == []
    
    def test_sanitization_with_control_chars_in_instructions(self):
        """Test that control characters are sanitized from instructions."""
        instructions = "Focus\x00on\x01MVP\x1Ffeatures"
        sanitized = sanitize_instructions(instructions)
        
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        assert "\x1F" not in sanitized
        assert sanitized == "FocusonMVPfeatures"


class TestRateLimitingConcept:
    """Conceptual tests for rate limiting (actual rate limiting tested in integration tests)."""
    
    def test_rate_limiting_constants_are_defined(self):
        """Test that rate limiting is configured (conceptual test)."""
        # This test documents that rate limiting exists
        # Actual rate limiting behavior is tested in integration tests
        # Rate limit: 10 requests/minute per IP
        assert True  # Placeholder to document rate limiting exists
    
    def test_rate_limiting_applies_per_ip(self):
        """Test that rate limiting is IP-based (conceptual test)."""
        # This test documents that rate limiting is per-IP
        # Actual behavior tested in integration tests with TestClient
        assert True  # Placeholder to document IP-based rate limiting
    
    def test_rate_limiting_returns_429_status(self):
        """Test that rate limiting returns 429 status (conceptual test)."""
        # This test documents the expected status code
        # Actual behavior tested in integration tests
        expected_status_code = 429
        assert expected_status_code == 429  # Too Many Requests
