"""Property-based tests for Aggregator.

This module contains property-based tests using Hypothesis to verify
universal correctness properties of the Aggregator.
"""

import pytest
from hypothesis import given, strategies as st, settings
from app.services.aggregator import Aggregator
from app.models.chunk_models import ExtractionResult, Decision, Timeline


# Strategy for generating requirements
requirements_strategy = st.lists(
    st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))),
    min_size=0,
    max_size=20
)

# Strategy for generating decisions
decisions_strategy = st.lists(
    st.builds(
        Decision,
        description=st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))),
        timestamp=st.sampled_from([
            "2024-02-15 10:00:00",
            "2024-02-16 11:30:00",
            "2024-02-17 14:45:00",
            "2024-02-18 09:15:00"
        ]),
        decision_maker=st.sampled_from(["PM", "Tech Lead", "CTO", "Architect", ""])
    ),
    min_size=0,
    max_size=10
)

# Strategy for generating stakeholders
stakeholders_strategy = st.lists(
    st.sampled_from(["PM", "Tech Lead", "Designer", "Developer", "QA", "Architect", "CTO"]),
    min_size=0,
    max_size=15
)

# Strategy for generating timelines
timelines_strategy = st.lists(
    st.builds(
        Timeline,
        milestone=st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))),
        start_date=st.sampled_from(["2024-01-01", "2024-02-01", "2024-03-01", ""]),
        end_date=st.sampled_from(["2024-06-30", "2024-07-31", "2024-12-31", ""]),
        status=st.sampled_from(["planned", "active", "completed", ""])
    ),
    min_size=0,
    max_size=10
)

# Strategy for generating ExtractionResult
extraction_result_strategy = st.builds(
    ExtractionResult,
    requirements=requirements_strategy,
    decisions=decisions_strategy,
    stakeholders=stakeholders_strategy,
    timelines=timelines_strategy
)


@given(chunk_results=st.lists(extraction_result_strategy, min_size=2, max_size=5))
@settings(max_examples=100, deadline=None)
def test_property_deduplication_effectiveness(chunk_results):
    """Property 11: Deduplication effectiveness.
    
    Feature: production-features, Property 11: Deduplication effectiveness
    Validates: Requirements 2.2.2
    
    For any set of chunk results containing duplicate requirements (>80% similarity),
    the aggregated result should contain fewer total requirements than the sum of
    all chunk results.
    
    This property test verifies that:
    1. Duplicate requirements are identified and removed
    2. The aggregated count is less than or equal to the sum
    3. Deduplication works across multiple chunks
    """
    aggregator = Aggregator()
    
    # Add intentional duplicates to test deduplication
    # Find a chunk with requirements and add duplicates to other chunks
    chunk_with_reqs = None
    for chunk in chunk_results:
        if chunk.requirements:
            chunk_with_reqs = chunk
            break
    
    # If we found a chunk with requirements, add duplicates to at least one other chunk
    duplicates_added = False
    if chunk_with_reqs and chunk_with_reqs.requirements:
        first_req = chunk_with_reqs.requirements[0]
        
        # Add the same requirement to other chunks
        for i, chunk in enumerate(chunk_results):
            if chunk != chunk_with_reqs:
                # Add exact duplicate
                chunk.requirements.append(first_req)
                # Add very similar requirement (should be deduplicated)
                chunk.requirements.append(first_req + ".")
                duplicates_added = True
    
    # Count total requirements before aggregation
    total_requirements_before = sum(len(result.requirements) for result in chunk_results)
    
    # Aggregate
    aggregated = aggregator.aggregate_chunks(chunk_results)
    
    # Property: Aggregated requirements should be <= total (deduplication should occur)
    assert len(aggregated.requirements) <= total_requirements_before, \
        f"Aggregated requirements ({len(aggregated.requirements)}) should be <= " \
        f"total requirements ({total_requirements_before})"
    
    # Property: If we added duplicates, aggregated count should be less than total
    if duplicates_added and total_requirements_before > 0:
        # We added duplicates, so aggregated should be strictly less
        assert len(aggregated.requirements) < total_requirements_before, \
            f"With intentional duplicates, aggregated requirements ({len(aggregated.requirements)}) " \
            f"should be < total requirements ({total_requirements_before})"


@given(chunk_results=st.lists(extraction_result_strategy, min_size=1, max_size=5))
@settings(max_examples=100, deadline=None)
def test_property_extraction_completeness(chunk_results):
    """Property 10: Extraction completeness.
    
    Feature: production-features, Property 10: Extraction completeness
    Validates: Requirements 2.2.1
    
    For any chunk processed through extraction, the resulting ExtractionResult
    should contain all four required fields: requirements, decisions, stakeholders,
    and timelines (even if some are empty lists).
    
    This property test verifies that:
    1. All four fields are present in aggregated result
    2. Fields are of correct type (lists)
    3. No fields are None
    """
    aggregator = Aggregator()
    
    # Aggregate
    aggregated = aggregator.aggregate_chunks(chunk_results)
    
    # Property: All four required fields must be present
    assert hasattr(aggregated, 'requirements'), \
        "Aggregated result must have 'requirements' field"
    assert hasattr(aggregated, 'decisions'), \
        "Aggregated result must have 'decisions' field"
    assert hasattr(aggregated, 'stakeholders'), \
        "Aggregated result must have 'stakeholders' field"
    assert hasattr(aggregated, 'timelines'), \
        "Aggregated result must have 'timelines' field"
    
    # Property: All fields must be lists (not None)
    assert isinstance(aggregated.requirements, list), \
        f"requirements must be a list, got {type(aggregated.requirements)}"
    assert isinstance(aggregated.decisions, list), \
        f"decisions must be a list, got {type(aggregated.decisions)}"
    assert isinstance(aggregated.stakeholders, list), \
        f"stakeholders must be a list, got {type(aggregated.stakeholders)}"
    assert isinstance(aggregated.timelines, list), \
        f"timelines must be a list, got {type(aggregated.timelines)}"
    
    # Property: Fields should not be None
    assert aggregated.requirements is not None, "requirements should not be None"
    assert aggregated.decisions is not None, "decisions should not be None"
    assert aggregated.stakeholders is not None, "stakeholders should not be None"
    assert aggregated.timelines is not None, "timelines should not be None"
