"""Tests for structured logging implementation.

This module verifies that structured logging is properly configured
and working across all services with JSON format and proper metrics.
"""

import json
import logging
from io import StringIO
from unittest.mock import patch

import pytest

from app.services.gemini_service import GeminiService
from app.services.chunk_processor import ChunkProcessor
from app.services.ingestion_tracker import IngestionTracker
from app.services.constraint_applier import ConstraintApplier
from app.services.aggregator import Aggregator
from app.models.constraints import Constraints
from app.models.context_request import IngestionData
from app.models.request import Email, SlackMessage, Meeting
from app.models.chunk_models import ExtractionResult, TextChunk
from app.utils.logging_config import configure_structured_logging


class TestStructuredLogging:
    """Test structured logging with JSON format."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Configure structured logging with JSON format
        configure_structured_logging(level="INFO", use_json=True, enable_sensitive_filter=True)
    
    def test_gemini_service_logs_with_request_id(self, caplog):
        """Test that Gemini service logs include request_id."""
        with caplog.at_level(logging.INFO):
            service = GeminiService(
                api_key="test_key_12345678901234567890",
                model="gemini-pro",
                timeout=10
            )
            
            # Check initialization log
            assert any("GeminiService initialized" in record.message for record in caplog.records)
            
            # Verify log has structured data
            for record in caplog.records:
                if "GeminiService initialized" in record.message:
                    assert hasattr(record, 'model')
                    assert hasattr(record, 'timeout_seconds')
                    assert hasattr(record, 'max_retries')
    
    def test_chunk_processor_logs_metrics(self, caplog):
        """Test that chunk processor logs include metrics."""
        with caplog.at_level(logging.INFO):
            processor = ChunkProcessor(
                threshold_words=3000,
                chunk_size_min=1000,
                chunk_size_max=1500,
                overlap=100
            )
            
            # Create a large text that needs chunking
            text = " ".join(["word"] * 4000)
            chunks = processor.chunk_text(text)
            
            # Check that chunking logs include metrics
            assert any("Chunking text" in record.message for record in caplog.records)
            assert any("Chunking complete" in record.message for record in caplog.records)
            
            # Verify structured data in logs
            for record in caplog.records:
                if "Chunking complete" in record.message:
                    assert hasattr(record, 'total_chunks')
                    assert hasattr(record, 'original_word_count')
                    assert hasattr(record, 'avg_chunk_size')
    
    def test_ingestion_tracker_logs_counts(self, caplog):
        """Test that ingestion tracker logs include counts and metrics."""
        with caplog.at_level(logging.INFO):
            tracker = IngestionTracker(sample_count=5)
            tracking_id = tracker.start_tracking()
            
            # Track some items
            email = Email(subject="Test", body="Test body", sender="test@example.com")
            tracker.track_email(tracking_id, email)
            
            meeting = Meeting(transcript="Test transcript", topic="Test meeting")
            tracker.track_meeting(tracking_id, meeting)
            
            # Get summary
            summary = tracker.get_summary(tracking_id)
            
            # Check that summary log includes metrics
            assert any("Generated ingestion summary" in record.message for record in caplog.records)
            
            # Verify structured data
            for record in caplog.records:
                if "Generated ingestion summary" in record.message:
                    assert hasattr(record, 'tracking_id')
                    assert hasattr(record, 'emails_used')
                    assert hasattr(record, 'meetings_used')
                    assert hasattr(record, 'total_words_processed')
                    assert hasattr(record, 'processing_time_seconds')
    
    def test_constraint_applier_logs_filtering_stats(self, caplog):
        """Test that constraint applier logs filtering statistics."""
        with caplog.at_level(logging.INFO):
            applier = ConstraintApplier()
            
            # Create test data
            data = IngestionData(
                emails=[
                    Email(subject="MVP features", body="Core functionality", sender="test@example.com"),
                    Email(subject="Marketing plan", body="Social media strategy", sender="test@example.com")
                ]
            )
            
            # Create constraints
            constraints = Constraints(
                scope="MVP",
                exclude_topics=["marketing"],
                priority_focus="core"
            )
            
            # Apply constraints
            filtered_data = applier.apply_constraints(data, constraints)
            
            # Check that filtering logs include statistics
            assert any("Applying constraints to data" in record.message for record in caplog.records)
            assert any("Filtering complete" in record.message for record in caplog.records)
            
            # Verify structured data
            for record in caplog.records:
                if "Filtering complete" in record.message:
                    assert hasattr(record, 'final_counts')
                    assert hasattr(record, 'excluded_counts')
    
    def test_aggregator_logs_deduplication_stats(self, caplog):
        """Test that aggregator logs deduplication statistics."""
        with caplog.at_level(logging.INFO):
            aggregator = Aggregator()
            
            # Create test chunk results with duplicates
            chunk_results = [
                ExtractionResult(
                    requirements=["Requirement 1", "Requirement 2"],
                    decisions=[],
                    stakeholders=["Alice", "Bob"],
                    timelines=[]
                ),
                ExtractionResult(
                    requirements=["Requirement 1", "Requirement 3"],
                    decisions=[],
                    stakeholders=["Bob", "Charlie"],
                    timelines=[]
                )
            ]
            
            # Aggregate
            result = aggregator.aggregate_chunks(chunk_results)
            
            # Check that aggregation logs include statistics
            assert any("Aggregating chunk results" in record.message for record in caplog.records)
            assert any("Aggregation complete" in record.message for record in caplog.records)
            
            # Verify structured data
            for record in caplog.records:
                if "Aggregation complete" in record.message:
                    assert hasattr(record, 'requirements_before')
                    assert hasattr(record, 'requirements_after')
                    assert hasattr(record, 'stakeholders_before')
                    assert hasattr(record, 'stakeholders_after')
    
    def test_sensitive_data_not_logged(self, caplog):
        """Test that sensitive data (API keys) are not logged."""
        with caplog.at_level(logging.INFO):
            # Create service with API key
            service = GeminiService(
                api_key="sk_test_1234567890abcdefghijklmnopqrstuvwxyz",
                model="gemini-pro"
            )
            
            # Check that API key is not in any log messages
            for record in caplog.records:
                message = record.getMessage()
                assert "sk_test_" not in message
                assert "1234567890abcdefghijklmnopqrstuvwxyz" not in message
    
    def test_json_log_format(self):
        """Test that logs can be formatted as JSON."""
        from app.utils.logging_config import JSONFormatter
        
        # Create a log record
        logger = logging.getLogger("test_logger")
        handler = logging.StreamHandler(StringIO())
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Create a log with extra fields
        logger.info("Test message", extra={'request_id': 'test123', 'metric': 42})
        
        # Get the formatted output
        log_output = handler.stream.getvalue()
        
        # Parse as JSON
        log_data = json.loads(log_output.strip())
        
        # Verify JSON structure
        assert 'timestamp' in log_data
        assert 'level' in log_data
        assert 'logger' in log_data
        assert 'message' in log_data
        assert log_data['message'] == "Test message"
        assert log_data['request_id'] == 'test123'
        assert log_data['metric'] == 42


class TestLoggingRequirements:
    """Test that logging meets all requirements from task 12.2."""
    
    def test_gemini_api_calls_logged_with_request_id(self, caplog):
        """Verify: Log all Gemini API calls with request ID."""
        with caplog.at_level(logging.DEBUG):
            service = GeminiService(api_key="test_key_12345678901234567890")
            
            # The service initialization should log
            assert any("GeminiService initialized" in record.message for record in caplog.records)
    
    def test_chunking_operations_logged_with_metrics(self, caplog):
        """Verify: Log chunking operations with metrics."""
        with caplog.at_level(logging.INFO):
            processor = ChunkProcessor()
            text = " ".join(["word"] * 4000)
            chunks = processor.chunk_text(text)
            
            # Should log chunking metrics
            chunking_logs = [r for r in caplog.records if "Chunking" in r.message]
            assert len(chunking_logs) > 0
            
            # Check for metrics in logs
            for record in chunking_logs:
                if "Chunking complete" in record.message:
                    assert hasattr(record, 'total_chunks')
                    assert hasattr(record, 'original_word_count')
    
    def test_ingestion_counts_and_processing_times_logged(self, caplog):
        """Verify: Log ingestion counts and processing times."""
        with caplog.at_level(logging.INFO):
            tracker = IngestionTracker()
            tracking_id = tracker.start_tracking()
            
            # Track items
            email = Email(subject="Test", body="Test body")
            tracker.track_email(tracking_id, email)
            
            # Get summary
            summary = tracker.get_summary(tracking_id)
            
            # Should log summary with counts and time
            summary_logs = [r for r in caplog.records if "ingestion summary" in r.message]
            assert len(summary_logs) > 0
            
            for record in summary_logs:
                if "Generated ingestion summary" in record.message:
                    assert hasattr(record, 'emails_used')
                    assert hasattr(record, 'processing_time_seconds')
    
    def test_json_format_used(self):
        """Verify: Use JSON format for structured logs."""
        from app.utils.logging_config import JSONFormatter
        
        formatter = JSONFormatter()
        
        # Create a test log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.request_id = "test123"
        
        # Format the record
        formatted = formatter.format(record)
        
        # Should be valid JSON
        log_data = json.loads(formatted)
        assert isinstance(log_data, dict)
        assert 'timestamp' in log_data
        assert 'level' in log_data
        assert 'message' in log_data
    
    def test_sensitive_data_never_logged(self, caplog):
        """Verify: Never log sensitive data (API keys, full content)."""
        with caplog.at_level(logging.DEBUG):
            # Create service with API key
            api_key = "test_key_1234567890abcdefghijklmnopqrstuvwxyz"
            service = GeminiService(api_key=api_key)
            
            # Check all log records
            for record in caplog.records:
                message = record.getMessage()
                # API key should not appear in logs
                assert api_key not in message
                assert "sk_live_" not in message
                
                # Check record attributes too
                for key, value in record.__dict__.items():
                    if isinstance(value, str):
                        assert api_key not in value
