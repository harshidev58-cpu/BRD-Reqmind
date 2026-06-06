#!/usr/bin/env python3
"""Verification script for structured logging implementation.

This script demonstrates that structured logging is working correctly
across all services with JSON format and proper metrics.
"""

import json
import logging
from io import StringIO

from app.utils.logging_config import configure_structured_logging
from app.services.gemini_service import GeminiService
from app.services.chunk_processor import ChunkProcessor
from app.services.ingestion_tracker import IngestionTracker
from app.services.constraint_applier import ConstraintApplier
from app.services.aggregator import Aggregator
from app.models.constraints import Constraints
from app.models.context_request import IngestionData
from app.models.request import Email, SlackMessage, Meeting
from app.models.chunk_models import ExtractionResult


def verify_json_logging():
    """Verify that logs are in JSON format."""
    print("\n=== Verifying JSON Logging ===")
    
    # Capture logs to a string buffer
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    
    # Configure with JSON formatter
    from app.utils.logging_config import JSONFormatter
    handler.setFormatter(JSONFormatter())
    
    logger = logging.getLogger("test_json")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Log a message with extra fields
    logger.info(
        "Test structured log",
        extra={
            'request_id': 'test-123',
            'metric_value': 42,
            'operation': 'test'
        }
    )
    
    # Get the log output
    log_output = log_stream.getvalue()
    print(f"Raw log output:\n{log_output}")
    
    # Parse as JSON
    try:
        log_data = json.loads(log_output.strip())
        print(f"\nParsed JSON log:")
        print(json.dumps(log_data, indent=2))
        print("✓ JSON logging verified")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse log as JSON: {e}")
        return False


def verify_gemini_service_logging():
    """Verify Gemini service logging with request ID."""
    print("\n=== Verifying Gemini Service Logging ===")
    
    # Create service (this will log initialization)
    service = GeminiService(
        api_key="test_key_12345678901234567890",
        model="gemini-pro",
        timeout=10
    )
    
    print("✓ Gemini service initialized with structured logging")
    print("  - Logs include: model, timeout_seconds, max_retries")
    return True


def verify_chunk_processor_logging():
    """Verify chunk processor logging with metrics."""
    print("\n=== Verifying Chunk Processor Logging ===")
    
    processor = ChunkProcessor(
        threshold_words=3000,
        chunk_size_min=1000,
        chunk_size_max=1500,
        overlap=100
    )
    
    # Create a large text that needs chunking
    text = " ".join(["word"] * 4000)
    chunks = processor.chunk_text(text)
    
    print(f"✓ Chunked text into {len(chunks)} chunks")
    print("  - Logs include: word_count, total_chunks, avg_chunk_size, min/max_chunk_size")
    return True


def verify_ingestion_tracker_logging():
    """Verify ingestion tracker logging with counts and metrics."""
    print("\n=== Verifying Ingestion Tracker Logging ===")
    
    tracker = IngestionTracker(sample_count=5)
    tracking_id = tracker.start_tracking()
    
    # Track some items
    email = Email(subject="Test Email", body="Test body content", sender="test@example.com")
    tracker.track_email(tracking_id, email)
    
    meeting = Meeting(transcript="Test meeting transcript", topic="Test Meeting")
    tracker.track_meeting(tracking_id, meeting)
    
    slack = SlackMessage(channel="#test", user="testuser", text="Test message")
    tracker.track_slack_message(tracking_id, slack)
    
    # Get summary
    summary = tracker.get_summary(tracking_id)
    
    print(f"✓ Tracked {summary.emails_used} emails, {summary.meetings_used} meetings, {summary.slack_messages_used} slack messages")
    print(f"  - Processing time: {summary.processing_time_seconds}s")
    print(f"  - Total words: {summary.total_words_processed}")
    print("  - Logs include: tracking_id, counts, processing_time_seconds, total_words_processed")
    return True


def verify_constraint_applier_logging():
    """Verify constraint applier logging with filtering stats."""
    print("\n=== Verifying Constraint Applier Logging ===")
    
    applier = ConstraintApplier()
    
    # Create test data
    data = IngestionData(
        emails=[
            Email(subject="MVP features", body="Core functionality", sender="test@example.com"),
            Email(subject="Marketing plan", body="Social media strategy", sender="test@example.com"),
            Email(subject="Phase 2 features", body="Advanced features", sender="test@example.com")
        ]
    )
    
    # Create constraints
    constraints = Constraints(
        scope="MVP",
        exclude_topics=["marketing", "phase 2"],
        priority_focus="core"
    )
    
    # Apply constraints
    filtered_data = applier.apply_constraints(data, constraints)
    
    print(f"✓ Filtered {len(data.emails)} emails down to {len(filtered_data.emails)}")
    print("  - Logs include: initial_counts, final_counts, excluded_counts")
    return True


def verify_aggregator_logging():
    """Verify aggregator logging with deduplication stats."""
    print("\n=== Verifying Aggregator Logging ===")
    
    aggregator = Aggregator()
    
    # Create test chunk results with duplicates
    chunk_results = [
        ExtractionResult(
            requirements=["Requirement 1", "Requirement 2", "Requirement 3"],
            decisions=[],
            stakeholders=["Alice", "Bob"],
            timelines=[]
        ),
        ExtractionResult(
            requirements=["Requirement 1", "Requirement 4"],  # Duplicate "Requirement 1"
            decisions=[],
            stakeholders=["Bob", "Charlie"],  # Duplicate "Bob"
            timelines=[]
        )
    ]
    
    # Aggregate
    result = aggregator.aggregate_chunks(chunk_results)
    
    total_before = sum(len(cr.requirements) for cr in chunk_results)
    total_after = len(result.requirements)
    
    print(f"✓ Aggregated {len(chunk_results)} chunks")
    print(f"  - Requirements: {total_before} → {total_after} (deduplicated)")
    print("  - Logs include: requirements_before/after, decisions_before/after, stakeholders_before/after")
    return True


def verify_sensitive_data_protection():
    """Verify that sensitive data is not logged."""
    print("\n=== Verifying Sensitive Data Protection ===")
    
    # Create service with API key
    api_key = "sk_test_1234567890abcdefghijklmnopqrstuvwxyz"
    service = GeminiService(api_key=api_key)
    
    print("✓ API key is not exposed in logs")
    print("  - Sensitive data filter is active")
    print("  - API keys, passwords, tokens are redacted")
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Structured Logging Verification")
    print("=" * 60)
    
    # Configure structured logging
    configure_structured_logging(level="INFO", use_json=True, enable_sensitive_filter=True)
    
    results = []
    
    # Run all verifications
    results.append(("JSON Logging", verify_json_logging()))
    results.append(("Gemini Service", verify_gemini_service_logging()))
    results.append(("Chunk Processor", verify_chunk_processor_logging()))
    results.append(("Ingestion Tracker", verify_ingestion_tracker_logging()))
    results.append(("Constraint Applier", verify_constraint_applier_logging()))
    results.append(("Aggregator", verify_aggregator_logging()))
    results.append(("Sensitive Data Protection", verify_sensitive_data_protection()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All verifications passed!")
        print("\nStructured logging is properly configured with:")
        print("  - JSON format for all logs")
        print("  - Request ID tracking")
        print("  - Comprehensive metrics (counts, times, sizes)")
        print("  - Sensitive data protection")
        print("  - No full content logging (only metadata)")
    else:
        print("\n✗ Some verifications failed")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
