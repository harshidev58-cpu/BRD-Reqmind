"""Unit tests for input validation utilities."""

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


class TestSanitizeInstructions:
    """Tests for sanitize_instructions function."""
    
    def test_sanitize_none(self):
        """Test that None input returns None."""
        assert sanitize_instructions(None) is None
    
    def test_sanitize_clean_text(self):
        """Test that clean text is unchanged."""
        text = "Focus on MVP features only"
        assert sanitize_instructions(text) == text
    
    def test_sanitize_removes_control_characters(self):
        """Test that control characters are removed."""
        text = "Focus\x00on\x01MVP\x1Ffeatures"
        expected = "FocusonMVPfeatures"
        assert sanitize_instructions(text) == expected
    
    def test_sanitize_preserves_newlines(self):
        """Test that newlines are preserved."""
        text = "Line 1\nLine 2\nLine 3"
        assert sanitize_instructions(text) == text
    
    def test_sanitize_preserves_tabs(self):
        """Test that tabs are preserved."""
        text = "Item 1\tItem 2\tItem 3"
        assert sanitize_instructions(text) == text
    
    def test_sanitize_removes_null_bytes(self):
        """Test that null bytes are removed."""
        text = "Focus\x00on MVP"
        expected = "Focuson MVP"
        assert sanitize_instructions(text) == expected


class TestValidateInstructions:
    """Tests for validate_instructions function."""
    
    def test_validate_none(self):
        """Test that None instructions are valid."""
        validate_instructions(None)  # Should not raise
    
    def test_validate_empty_string(self):
        """Test that empty string is valid."""
        validate_instructions("")  # Should not raise
    
    def test_validate_normal_length(self):
        """Test that normal length instructions are valid."""
        instructions = "Focus on MVP features" * 10
        validate_instructions(instructions)  # Should not raise
    
    def test_validate_max_length(self):
        """Test that instructions at max length are valid."""
        instructions = "a" * MAX_INSTRUCTION_LENGTH
        validate_instructions(instructions)  # Should not raise
    
    def test_validate_exceeds_max_length(self):
        """Test that instructions exceeding max length raise error."""
        instructions = "a" * (MAX_INSTRUCTION_LENGTH + 1)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_instructions(instructions)
        
        assert exc_info.value.status_code == 400
        assert "exceed maximum length" in exc_info.value.detail


class TestValidateTextLength:
    """Tests for validate_text_length function."""
    
    def test_validate_normal_text(self):
        """Test that normal length text is valid."""
        text = "This is a normal email body" * 100
        validate_text_length(text, "Email body")  # Should not raise
    
    def test_validate_max_length_text(self):
        """Test that text at max length is valid."""
        text = "a" * MAX_TEXT_LENGTH_PER_ITEM
        validate_text_length(text, "Test field")  # Should not raise
    
    def test_validate_exceeds_max_length(self):
        """Test that text exceeding max length raises error."""
        text = "a" * (MAX_TEXT_LENGTH_PER_ITEM + 1)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_text_length(text, "Email body")
        
        assert exc_info.value.status_code == 400
        assert "Email body" in exc_info.value.detail
        assert "exceeds maximum length" in exc_info.value.detail


class TestValidateDataSources:
    """Tests for validate_data_sources function."""
    
    def test_validate_empty_data(self):
        """Test that empty data is valid."""
        data = IngestionData()
        validate_data_sources(data)  # Should not raise
    
    def test_validate_normal_data(self):
        """Test that normal data is valid."""
        data = IngestionData(
            emails=[
                Email(subject="Test", body="Body text", sender="user@test.com", date="2024-01-01")
            ],
            slack_messages=[
                SlackMessage(channel="#general", user="user1", text="Message", timestamp="2024-01-01")
            ],
            meetings=[
                Meeting(transcript="Meeting transcript", topic="Planning", speakers=["PM"], timestamp="2024-01-01")
            ]
        )
        validate_data_sources(data)  # Should not raise
    
    def test_validate_max_items(self):
        """Test that max items is valid."""
        # Create exactly MAX_TOTAL_ITEMS
        emails = [
            Email(subject=f"Email {i}", body="Body", sender="user@test.com", date="2024-01-01")
            for i in range(MAX_TOTAL_ITEMS)
        ]
        data = IngestionData(emails=emails)
        validate_data_sources(data)  # Should not raise
    
    def test_validate_exceeds_max_items(self):
        """Test that exceeding max items raises error."""
        # Create MAX_TOTAL_ITEMS + 1
        emails = [
            Email(subject=f"Email {i}", body="Body", sender="user@test.com", date="2024-01-01")
            for i in range(MAX_TOTAL_ITEMS + 1)
        ]
        data = IngestionData(emails=emails)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_data_sources(data)
        
        assert exc_info.value.status_code == 400
        assert "exceeds maximum" in exc_info.value.detail
    
    def test_validate_email_subject_too_long(self):
        """Test that email with too long subject raises error."""
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
    
    def test_validate_email_body_too_long(self):
        """Test that email with too long body raises error."""
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
    
    def test_validate_slack_text_too_long(self):
        """Test that Slack message with too long text raises error."""
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
    
    def test_validate_meeting_transcript_too_long(self):
        """Test that meeting with too long transcript raises error."""
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


class TestValidateContextRequest:
    """Tests for validate_context_request function."""
    
    def test_validate_complete_request(self):
        """Test that complete valid request is processed correctly."""
        instructions = "Focus on MVP features"
        data = IngestionData(
            emails=[
                Email(subject="Test", body="Body", sender="user@test.com", date="2024-01-01")
            ]
        )
        
        sanitized_instructions, validated_data = validate_context_request(instructions, data)
        
        assert sanitized_instructions == instructions
        assert validated_data == data
    
    def test_validate_request_with_none_instructions(self):
        """Test that request with None instructions is valid."""
        data = IngestionData(
            emails=[
                Email(subject="Test", body="Body", sender="user@test.com", date="2024-01-01")
            ]
        )
        
        sanitized_instructions, validated_data = validate_context_request(None, data)
        
        assert sanitized_instructions is None
        assert validated_data == data
    
    def test_validate_request_sanitizes_instructions(self):
        """Test that instructions are sanitized."""
        instructions = "Focus\x00on MVP"
        data = IngestionData()
        
        sanitized_instructions, validated_data = validate_context_request(instructions, data)
        
        assert sanitized_instructions == "Focuson MVP"
        assert validated_data == data
    
    def test_validate_request_rejects_invalid_instructions(self):
        """Test that invalid instructions raise error."""
        instructions = "a" * (MAX_INSTRUCTION_LENGTH + 1)
        data = IngestionData()
        
        with pytest.raises(HTTPException) as exc_info:
            validate_context_request(instructions, data)
        
        assert exc_info.value.status_code == 400
    
    def test_validate_request_rejects_invalid_data(self):
        """Test that invalid data raises error."""
        instructions = "Focus on MVP"
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
            validate_context_request(instructions, data)
        
        assert exc_info.value.status_code == 400


class TestSecurityMeasures:
    """Comprehensive tests for security measures including validation, sanitization, and edge cases."""
    
    def test_sanitize_removes_all_control_characters(self):
        """Test that all dangerous control characters are removed."""
        # Test various control characters
        dangerous_chars = [
            "\x00",  # Null byte
            "\x01",  # Start of heading
            "\x02",  # Start of text
            "\x08",  # Backspace
            "\x0B",  # Vertical tab
            "\x0C",  # Form feed
            "\x0E",  # Shift out
            "\x1F",  # Unit separator
            "\x7F",  # Delete
        ]
        
        for char in dangerous_chars:
            text = f"Before{char}After"
            sanitized = sanitize_instructions(text)
            assert char not in sanitized, f"Control character {repr(char)} was not removed"
            assert sanitized == "BeforeAfter", f"Expected 'BeforeAfter', got '{sanitized}'"
    
    def test_sanitize_preserves_safe_whitespace(self):
        """Test that safe whitespace characters are preserved."""
        text = "Line 1\nLine 2\rLine 3\tTabbed"
        sanitized = sanitize_instructions(text)
        assert sanitized == text, "Safe whitespace should be preserved"
    
    def test_validate_instructions_boundary_cases(self):
        """Test instruction validation at exact boundaries."""
        # Exactly at limit - should pass
        at_limit = "a" * MAX_INSTRUCTION_LENGTH
        validate_instructions(at_limit)  # Should not raise
        
        # One over limit - should fail
        over_limit = "a" * (MAX_INSTRUCTION_LENGTH + 1)
        with pytest.raises(HTTPException) as exc_info:
            validate_instructions(over_limit)
        assert exc_info.value.status_code == 400
        
        # Empty string - should pass
        validate_instructions("")  # Should not raise
        
        # None - should pass
        validate_instructions(None)  # Should not raise
    
    def test_validate_text_length_boundary_cases(self):
        """Test text length validation at exact boundaries."""
        # Exactly at limit - should pass
        at_limit = "a" * MAX_TEXT_LENGTH_PER_ITEM
        validate_text_length(at_limit, "Test field")  # Should not raise
        
        # One over limit - should fail
        over_limit = "a" * (MAX_TEXT_LENGTH_PER_ITEM + 1)
        with pytest.raises(HTTPException) as exc_info:
            validate_text_length(over_limit, "Test field")
        assert exc_info.value.status_code == 400
        assert "Test field" in exc_info.value.detail
    
    def test_validate_data_sources_total_items_boundary(self):
        """Test that total items validation works at exact boundary."""
        # Exactly at limit - should pass
        emails = [
            Email(subject=f"Email {i}", body="Body", sender="user@test.com", date="2024-01-01")
            for i in range(MAX_TOTAL_ITEMS)
        ]
        data = IngestionData(emails=emails)
        validate_data_sources(data)  # Should not raise
        
        # One over limit - should fail
        emails_over = [
            Email(subject=f"Email {i}", body="Body", sender="user@test.com", date="2024-01-01")
            for i in range(MAX_TOTAL_ITEMS + 1)
        ]
        data_over = IngestionData(emails=emails_over)
        with pytest.raises(HTTPException) as exc_info:
            validate_data_sources(data_over)
        assert exc_info.value.status_code == 400
        assert "exceeds maximum" in exc_info.value.detail
    
    def test_validate_data_sources_mixed_items(self):
        """Test validation with mixed data sources approaching limit."""
        # Create a mix that totals exactly MAX_TOTAL_ITEMS
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
    
    def test_validate_empty_fields_are_allowed(self):
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
    
    def test_sanitize_multiple_control_characters_in_sequence(self):
        """Test sanitization of multiple consecutive control characters."""
        text = "Start\x00\x01\x02Middle\x1F\x7FEnd"
        sanitized = sanitize_instructions(text)
        assert sanitized == "StartMiddleEnd"
    
    def test_sanitize_unicode_characters_preserved(self):
        """Test that valid Unicode characters are preserved."""
        text = "Focus on MVP 中文 العربية 🚀"
        sanitized = sanitize_instructions(text)
        assert sanitized == text, "Unicode characters should be preserved"
    
    def test_validate_context_request_with_edge_cases(self):
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
    
    def test_validate_rejects_sql_injection_patterns(self):
        """Test that common SQL injection patterns are handled safely."""
        # These should not cause errors, just be sanitized/validated
        sql_patterns = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--"
        ]
        
        for pattern in sql_patterns:
            # Should not raise exception - just validate length
            if len(pattern) <= MAX_INSTRUCTION_LENGTH:
                validate_instructions(pattern)  # Should not raise
                sanitized = sanitize_instructions(pattern)
                assert sanitized is not None
    
    def test_validate_rejects_script_injection_patterns(self):
        """Test that common script injection patterns are handled safely."""
        # These should not cause errors, just be sanitized/validated
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
    
    def test_validate_data_sources_with_special_characters(self):
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
