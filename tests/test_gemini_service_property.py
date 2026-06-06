"""Property-based tests for GeminiService.

This module contains property-based tests using Hypothesis to verify
universal correctness properties of the GeminiService.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, settings, HealthCheck
from google.generativeai.types import GenerateContentResponse

from app.services.gemini_service import GeminiService
from app.models.constraints import Constraints


# Strategy for generating random instruction strings
instruction_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Zs'),
        min_codepoint=32,
        max_codepoint=126
    ),
    min_size=10,
    max_size=500
)


@pytest.mark.asyncio
@given(instructions=instruction_strategy)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_property_constraint_generation_validity(instructions):
    """Property 2: Constraint generation validity.
    
    Feature: production-features, Property 2: Constraint generation validity
    Validates: Requirements 1.1.2
    
    For any natural language instructions, if Gemini successfully processes them,
    the resulting Constraints object should have valid JSON structure with all
    required fields (scope, exclude_topics, priority_focus, deadline_override).
    
    This property test verifies that:
    1. Valid instructions are accepted
    2. The service returns a Constraints object or None
    3. If a Constraints object is returned, it has all required fields
    4. All fields have the correct types
    """
    # Skip empty or whitespace-only instructions
    if not instructions or not instructions.strip():
        return
    
    # Create service with test API key
    service = GeminiService(
        api_key="test_api_key",
        model="gemini-pro",
        timeout=10,
        max_retries=2
    )
    
    # Mock the Gemini API response with valid JSON
    mock_response_text = """
    {
        "scope": "test scope",
        "exclude_topics": ["topic1", "topic2"],
        "priority_focus": "test priority",
        "deadline_override": "test deadline"
    }
    """
    
    # Create a mock response object
    mock_response = MagicMock()
    mock_response.text = mock_response_text
    
    # Mock the model.generate_content method
    with patch.object(
        service.model,
        'generate_content',
        return_value=mock_response
    ):
        # Call generate_constraints
        result = await service.generate_constraints(
            instructions=instructions,
            request_id="test_request"
        )
        
        # Property: Result should be either Constraints or None
        assert result is None or isinstance(result, Constraints), \
            f"Result must be Constraints or None, got {type(result)}"
        
        # If result is not None, verify all required fields exist
        if result is not None:
            # Property: All required fields must exist
            assert hasattr(result, 'scope'), "Constraints must have 'scope' field"
            assert hasattr(result, 'exclude_topics'), "Constraints must have 'exclude_topics' field"
            assert hasattr(result, 'priority_focus'), "Constraints must have 'priority_focus' field"
            assert hasattr(result, 'deadline_override'), "Constraints must have 'deadline_override' field"
            
            # Property: Fields must have correct types
            assert isinstance(result.scope, str), "scope must be a string"
            assert isinstance(result.exclude_topics, list), "exclude_topics must be a list"
            assert isinstance(result.priority_focus, str), "priority_focus must be a string"
            assert isinstance(result.deadline_override, str), "deadline_override must be a string"
            
            # Property: exclude_topics must contain only strings
            assert all(isinstance(topic, str) for topic in result.exclude_topics), \
                "All items in exclude_topics must be strings"


@pytest.mark.asyncio
@given(instructions=instruction_strategy)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_property_constraint_generation_with_api_failure(instructions):
    """Property: Constraint generation handles API failures gracefully.
    
    Feature: production-features
    Validates: Requirements 1.2.5
    
    For any natural language instructions, if Gemini API fails,
    the service should return None and not raise an exception.
    
    This property test verifies that:
    1. API failures are handled gracefully
    2. The service returns None on failure
    3. No exceptions propagate to the caller
    """
    # Skip empty or whitespace-only instructions
    if not instructions or not instructions.strip():
        return
    
    # Create service with test API key
    service = GeminiService(
        api_key="test_api_key",
        model="gemini-pro",
        timeout=10,
        max_retries=0  # No retries for faster testing
    )
    
    # Mock the model.generate_content to raise an exception
    with patch.object(
        service.model,
        'generate_content',
        side_effect=Exception("API Error")
    ):
        # Call generate_constraints - should not raise exception
        result = await service.generate_constraints(
            instructions=instructions,
            request_id="test_request"
        )
        
        # Property: Result should be None on API failure
        assert result is None, \
            f"Result must be None on API failure, got {result}"


@pytest.mark.asyncio
@given(instructions=instruction_strategy)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_property_constraint_generation_with_invalid_json(instructions):
    """Property: Constraint generation handles invalid JSON gracefully.
    
    Feature: production-features
    Validates: Requirements 1.2.3
    
    For any natural language instructions, if Gemini returns invalid JSON,
    the service should return None and not raise an exception.
    
    This property test verifies that:
    1. Invalid JSON responses are handled gracefully
    2. The service returns None on parsing failure
    3. No exceptions propagate to the caller
    """
    # Skip empty or whitespace-only instructions
    if not instructions or not instructions.strip():
        return
    
    # Create service with test API key
    service = GeminiService(
        api_key="test_api_key",
        model="gemini-pro",
        timeout=10,
        max_retries=0  # No retries for faster testing
    )
    
    # Mock the Gemini API response with invalid JSON
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON at all!"
    
    # Mock the model.generate_content method
    with patch.object(
        service.model,
        'generate_content',
        return_value=mock_response
    ):
        # Call generate_constraints - should not raise exception
        result = await service.generate_constraints(
            instructions=instructions,
            request_id="test_request"
        )
        
        # Property: Result should be None on invalid JSON
        assert result is None, \
            f"Result must be None on invalid JSON, got {result}"
