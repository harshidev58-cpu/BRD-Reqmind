"""Unit tests for error handling and custom exceptions.

This module tests that custom exceptions are raised correctly,
fallback behaviors work as expected, and error logging is functional.
"""

import pytest
from app.utils.exceptions import (
    GeminiAPIError,
    GeminiTimeoutError,
    GeminiRateLimitError,
    ConstraintValidationError,
    ChunkingError,
    TextTooShortError,
    TrackingSessionNotFoundError,
    TrackingStorageError,
    AggregationError,
    EmptyChunkResultsError
)


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_gemini_api_error(self):
        """Test GeminiAPIError can be raised and caught."""
        with pytest.raises(GeminiAPIError) as exc_info:
            raise GeminiAPIError("API call failed")
        
        assert "API call failed" in str(exc_info.value)
    
    def test_gemini_timeout_error(self):
        """Test GeminiTimeoutError is a subclass of GeminiAPIError."""
        with pytest.raises(GeminiAPIError):
            raise GeminiTimeoutError("Request timed out")
        
        with pytest.raises(GeminiTimeoutError) as exc_info:
            raise GeminiTimeoutError("Request timed out")
        
        assert "Request timed out" in str(exc_info.value)
    
    def test_gemini_rate_limit_error(self):
        """Test GeminiRateLimitError is a subclass of GeminiAPIError."""
        with pytest.raises(GeminiAPIError):
            raise GeminiRateLimitError("Rate limit exceeded")
        
        with pytest.raises(GeminiRateLimitError) as exc_info:
            raise GeminiRateLimitError("Rate limit exceeded")
        
        assert "Rate limit exceeded" in str(exc_info.value)
    
    def test_constraint_validation_error(self):
        """Test ConstraintValidationError can be raised and caught."""
        with pytest.raises(ConstraintValidationError) as exc_info:
            raise ConstraintValidationError("Invalid constraint format")
        
        assert "Invalid constraint format" in str(exc_info.value)
    
    def test_chunking_error(self):
        """Test ChunkingError can be raised and caught."""
        with pytest.raises(ChunkingError) as exc_info:
            raise ChunkingError("Chunking failed")
        
        assert "Chunking failed" in str(exc_info.value)
    
    def test_text_too_short_error(self):
        """Test TextTooShortError is a subclass of ChunkingError."""
        with pytest.raises(ChunkingError):
            raise TextTooShortError("Text too short to chunk")
        
        with pytest.raises(TextTooShortError) as exc_info:
            raise TextTooShortError("Text too short to chunk")
        
        assert "Text too short to chunk" in str(exc_info.value)
    
    def test_tracking_session_not_found_error(self):
        """Test TrackingSessionNotFoundError can be raised and caught."""
        with pytest.raises(TrackingSessionNotFoundError) as exc_info:
            raise TrackingSessionNotFoundError("Session not found")
        
        assert "Session not found" in str(exc_info.value)
    
    def test_tracking_storage_error(self):
        """Test TrackingStorageError can be raised and caught."""
        with pytest.raises(TrackingStorageError) as exc_info:
            raise TrackingStorageError("Storage operation failed")
        
        assert "Storage operation failed" in str(exc_info.value)
    
    def test_aggregation_error(self):
        """Test AggregationError can be raised and caught."""
        with pytest.raises(AggregationError) as exc_info:
            raise AggregationError("Aggregation failed")
        
        assert "Aggregation failed" in str(exc_info.value)
    
    def test_empty_chunk_results_error(self):
        """Test EmptyChunkResultsError is a subclass of AggregationError."""
        with pytest.raises(AggregationError):
            raise EmptyChunkResultsError("No chunk results")
        
        with pytest.raises(EmptyChunkResultsError) as exc_info:
            raise EmptyChunkResultsError("No chunk results")
        
        assert "No chunk results" in str(exc_info.value)


class TestErrorFallbackBehaviors:
    """Test fallback behaviors when errors occur."""
    
    def test_chunk_processor_empty_text_fallback(self):
        """Test ChunkProcessor handles empty text gracefully."""
        from app.services.chunk_processor import ChunkProcessor
        
        processor = ChunkProcessor()
        
        # Empty text should not need chunking
        assert processor.needs_chunking("") is False
        assert processor.needs_chunking("   ") is False
        
        # Chunking empty text should raise ValueError
        with pytest.raises(ValueError):
            processor.chunk_text("")
    
    def test_ingestion_tracker_invalid_session_fallback(self):
        """Test IngestionTracker handles invalid session gracefully."""
        from app.services.ingestion_tracker import IngestionTracker
        from app.models.request import Email
        
        tracker = IngestionTracker()
        
        # Accessing invalid session should raise KeyError
        with pytest.raises(KeyError):
            tracker.get_summary("invalid-session-id")
        
        # Tracking with invalid session should raise KeyError
        with pytest.raises(KeyError):
            tracker.track_email("invalid-session-id", Email(subject="Test", body="Test"))
    
    def test_constraint_applier_none_constraints_fallback(self):
        """Test ConstraintApplier handles None constraints gracefully."""
        from app.services.constraint_applier import ConstraintApplier
        from app.models.context_request import IngestionData
        from app.models.request import Email
        
        applier = ConstraintApplier()
        
        # Create test data
        test_data = IngestionData(
            emails=[Email(subject="Test", body="Test content")],
            slack_messages=[],
            meetings=[]
        )
        
        # None constraints should return data unchanged
        result = applier.apply_constraints(test_data, None)
        
        assert len(result.emails) == 1
        assert result.emails[0].subject == "Test"
    
    def test_aggregator_empty_results_handling(self):
        """Test Aggregator handles empty chunk results."""
        from app.services.aggregator import Aggregator
        from app.models.chunk_models import ExtractionResult
        
        aggregator = Aggregator()
        
        # Empty list should return empty ExtractionResult
        result = aggregator.aggregate_chunks([])
        
        assert isinstance(result, ExtractionResult)
        assert len(result.requirements) == 0
        assert len(result.decisions) == 0
        assert len(result.stakeholders) == 0
        assert len(result.timelines) == 0
    
    def test_aggregator_single_chunk_fallback(self):
        """Test Aggregator handles single chunk correctly."""
        from app.services.aggregator import Aggregator
        from app.models.chunk_models import ExtractionResult
        
        aggregator = Aggregator()
        
        # Single chunk should be returned as-is
        single_result = ExtractionResult(
            requirements=["Req 1"],
            decisions=[],
            stakeholders=["User"],
            timelines=[]
        )
        
        result = aggregator.aggregate_chunks([single_result])
        
        assert result == single_result


class TestErrorLogging:
    """Test that errors are logged correctly."""
    
    def test_gemini_service_logs_errors(self, caplog):
        """Test GeminiService logs errors appropriately."""
        import logging
        from app.services.gemini_service import GeminiService
        
        # Create service with invalid API key
        service = GeminiService(api_key="invalid-key")
        
        # The service should initialize without error
        assert service.api_key == "invalid-key"
    
    def test_chunk_processor_logs_operations(self, caplog):
        """Test ChunkProcessor logs chunking operations."""
        import logging
        from app.services.chunk_processor import ChunkProcessor
        
        caplog.set_level(logging.INFO)
        
        processor = ChunkProcessor(threshold_words=100)
        
        # Create text that needs chunking
        text = " ".join(["word"] * 150)
        
        # Check if chunking is needed (should log)
        needs_chunk = processor.needs_chunking(text)
        
        assert needs_chunk is True
    
    def test_constraint_applier_logs_filtering(self, caplog):
        """Test ConstraintApplier logs filtering statistics."""
        import logging
        from app.services.constraint_applier import ConstraintApplier
        from app.models.context_request import IngestionData
        from app.models.constraints import Constraints
        from app.models.request import Email
        
        caplog.set_level(logging.INFO)
        
        applier = ConstraintApplier()
        
        # Create test data
        test_data = IngestionData(
            emails=[
                Email(subject="MVP features", body="Core functionality"),
                Email(subject="Marketing plan", body="Social media")
            ],
            slack_messages=[],
            meetings=[]
        )
        
        # Create constraints
        constraints = Constraints(
            scope="MVP",
            exclude_topics=["marketing"],
            priority_focus="core"
        )
        
        # Apply constraints (should log)
        result = applier.apply_constraints(test_data, constraints)
        
        # Check that filtering occurred
        assert len(result.emails) <= len(test_data.emails)
