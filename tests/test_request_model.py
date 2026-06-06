"""Property-based tests for BRD request validation.

Tests request validation logic using property-based testing with Hypothesis
to verify that invalid inputs are properly rejected.
"""

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError
from app.models.request import BRDRequest


# Feature: brd-generator-backend, Property 1: Request validation rejects invalid inputs
# Validates: Requirements 1.2, 1.3, 2.2, 2.6


# Strategy for generating empty or whitespace-only strings
empty_or_whitespace = st.one_of(
    st.just(""),
    st.just("   "),
    st.just("\t"),
    st.just("\n"),
    st.just("  \t\n  ")
)


# Strategy for generating invalid projectName values
invalid_project_names = st.one_of(
    st.just(""),
    st.just("   "),
    st.just("\t"),
    st.just("\n"),
    st.just("  \t\n  "),
    st.just("\t\t\t"),
    st.just("     ")
)


# Strategy for generating all empty text fields
all_empty_text_fields = st.fixed_dictionaries({
    'emailText': st.one_of(st.none(), empty_or_whitespace),
    'slackText': st.one_of(st.none(), empty_or_whitespace),
    'meetingText': st.one_of(st.none(), empty_or_whitespace)
})


class TestRequestValidationProperty:
    """Property-based tests for request validation."""
    
    @settings(max_examples=100)
    @given(project_name=invalid_project_names)
    def test_property_empty_project_name_rejected(self, project_name):
        """Property 1a: Requests with empty or whitespace-only projectName are rejected.
        
        For any request with an empty or whitespace-only projectName,
        the validation should raise a ValidationError.
        
        Validates: Requirements 1.2, 1.3, 2.2
        """
        # Attempt to create a request with invalid projectName
        with pytest.raises(ValidationError) as exc_info:
            BRDRequest(
                projectName=project_name,
                emailText="Some email content"
            )
        
        # Verify that the error is related to projectName validation
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(
            'projectName' in str(error.get('loc', ''))
            for error in errors
        )
    
    @settings(max_examples=100)
    @given(
        project_name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        text_fields=all_empty_text_fields
    )
    def test_property_all_text_fields_empty_rejected(self, project_name, text_fields):
        """Property 1b: Requests with all text fields empty are rejected.
        
        For any request with a valid projectName but all text fields
        (emailText, slackText, meetingText) empty or None, the validation
        should raise a ValidationError.
        
        Validates: Requirements 2.6
        """
        # Ensure at least one text field is actually empty/None
        # (the strategy should guarantee this, but we verify)
        has_content = any(
            text_fields.get(field) and text_fields.get(field).strip()
            for field in ['emailText', 'slackText', 'meetingText']
        )
        
        # Skip if somehow we got valid content (shouldn't happen with our strategy)
        if has_content:
            return
        
        # Attempt to create a request with all empty text fields
        with pytest.raises(ValidationError) as exc_info:
            BRDRequest(
                projectName=project_name,
                **text_fields
            )
        
        # Verify that the error is about missing text sources
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # The error should mention the validation failure
        error_messages = [str(error) for error in errors]
        assert any(
            'emailText' in msg or 'slackText' in msg or 'meetingText' in msg
            for msg in error_messages
        )
    
    @settings(max_examples=100)
    @given(
        project_name=invalid_project_names,
        text_fields=all_empty_text_fields
    )
    def test_property_both_invalid_project_and_empty_fields_rejected(
        self, project_name, text_fields
    ):
        """Property 1c: Requests with both invalid projectName and empty text fields are rejected.
        
        For any request with an invalid projectName AND all text fields empty,
        the validation should raise a ValidationError.
        
        Validates: Requirements 1.2, 1.3, 2.2, 2.6
        """
        # Attempt to create a completely invalid request
        with pytest.raises(ValidationError) as exc_info:
            BRDRequest(
                projectName=project_name,
                **text_fields
            )
        
        # Verify that validation errors are raised
        errors = exc_info.value.errors()
        assert len(errors) > 0


# Feature: brd-generator-backend, Property 8: Optional fields are truly optional
# Validates: Requirements 2.3, 2.4, 2.5


# Strategy for generating valid non-empty text
valid_text = st.text(min_size=1, max_size=200).filter(lambda x: x.strip())


# Strategy for generating at least one optional field with content
def optional_fields_with_at_least_one():
    """Generate combinations of optional fields with at least one present."""
    return st.fixed_dictionaries({
        'emailText': st.one_of(st.none(), valid_text),
        'slackText': st.one_of(st.none(), valid_text),
        'meetingText': st.one_of(st.none(), valid_text)
    }).filter(
        lambda fields: any(
            fields.get(field) and fields.get(field).strip()
            for field in ['emailText', 'slackText', 'meetingText']
        )
    )


class TestOptionalFieldsProperty:
    """Property-based tests for optional field handling."""
    
    @settings(max_examples=100)
    @given(
        project_name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        optional_fields=optional_fields_with_at_least_one()
    )
    def test_property_optional_fields_are_optional(self, project_name, optional_fields):
        """Property 8: Optional fields are truly optional.
        
        For any valid request with a non-empty projectName and at least one
        non-empty text field, omitting any combination of the optional fields
        (emailText, slackText, meetingText) should not cause a validation error.
        
        Validates: Requirements 2.3, 2.4, 2.5
        """
        # Attempt to create a request with various combinations of optional fields
        try:
            request = BRDRequest(
                projectName=project_name,
                **optional_fields
            )
            
            # Verify the request was created successfully
            assert request.projectName == project_name.strip()
            
            # Verify that at least one text field has content
            has_content = any(
                getattr(request, field) and getattr(request, field).strip()
                for field in ['emailText', 'slackText', 'meetingText']
            )
            assert has_content, "At least one text field should have content"
            
            # Verify that None values are preserved for omitted fields
            for field in ['emailText', 'slackText', 'meetingText']:
                field_value = getattr(request, field)
                if optional_fields.get(field) is None:
                    assert field_value is None, f"{field} should be None when not provided"
                else:
                    assert field_value == optional_fields.get(field), f"{field} should match input"
            
        except ValidationError as e:
            # If validation fails, this is a test failure
            pytest.fail(
                f"Valid request with optional fields was rejected: {e}\n"
                f"projectName: {project_name}\n"
                f"optional_fields: {optional_fields}"
            )
