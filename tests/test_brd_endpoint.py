"""Property-based and integration tests for BRD endpoint.

This module contains property-based tests using Hypothesis to verify
the correctness of the /generate_brd endpoint, particularly that valid
requests are accepted and invalid requests are properly rejected.
"""

import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from hypothesis import given, strategies as st, settings
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.brd import router, get_brd_generator_service
from app.models.request import BRDRequest
from app.models.response import BRDResponse, Requirement, Stakeholder
from app.services.brd_generator import BRDGeneratorService
from app.services.openai_client import OpenAIClient
from app.utils.exceptions import OpenAIServiceError, BRDGenerationError
from app.main import app as main_app


# Create a test FastAPI app
app = FastAPI()
app.include_router(router)


# Custom strategy for generating valid BRDRequest objects
@st.composite
def valid_brd_request_dict(draw):
    """Generate a valid BRDRequest dictionary with random data.
    
    Ensures at least one text field is non-empty to satisfy validation.
    """
    project_name = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    
    # Generate optional text fields, ensuring at least one is non-empty
    email_text = draw(st.one_of(st.none(), st.text(min_size=0, max_size=500)))
    slack_text = draw(st.one_of(st.none(), st.text(min_size=0, max_size=500)))
    meeting_text = draw(st.one_of(st.none(), st.text(min_size=0, max_size=500)))
    
    # Ensure at least one text field has content
    sources = [email_text, slack_text, meeting_text]
    if not any(source and source.strip() for source in sources):
        # Force at least one field to have content
        choice = draw(st.integers(min_value=0, max_value=2))
        non_empty_text = draw(st.text(min_size=1, max_size=500).filter(lambda x: x.strip()))
        if choice == 0:
            email_text = non_empty_text
        elif choice == 1:
            slack_text = non_empty_text
        else:
            meeting_text = non_empty_text
    
    # Build the request dictionary
    request_dict = {"projectName": project_name}
    if email_text is not None:
        request_dict["emailText"] = email_text
    if slack_text is not None:
        request_dict["slackText"] = slack_text
    if meeting_text is not None:
        request_dict["meetingText"] = meeting_text
    
    return request_dict


class TestBRDEndpointValidRequestAcceptance:
    """Property-based tests for valid request acceptance."""
    
    @given(request_data=valid_brd_request_dict())
    @settings(max_examples=100)
    def test_property_valid_requests_are_accepted(self, request_data):
        """Property 2: Valid requests are accepted.
        
        Feature: brd-generator-backend, Property 2: Valid requests are accepted
        
        Validates: Requirements 1.4, 1.5
        
        For any request with a non-empty projectName and at least one non-empty
        text field, the API should accept the request and return either a 200
        status code (success) or a 5xx status code (server error), but never
        a 400 status code (validation error).
        """
        # Create a mock BRD response
        mock_brd_response = {
            "projectName": request_data["projectName"],
            "executiveSummary": "Test executive summary",
            "businessObjectives": ["Objective 1", "Objective 2"],
            "requirements": [
                {"id": "REQ-1", "description": "Test requirement", "priority": "High"}
            ],
            "stakeholders": [
                {"name": "Test Stakeholder", "role": "Test Role"}
            ]
        }
        
        # Mock the BRD generator service
        mock_service = Mock(spec=BRDGeneratorService)
        
        # Create an async mock for generate_brd
        async def mock_generate_brd(*args, **kwargs):
            from app.models.response import BRDResponse, Requirement, Stakeholder
            return BRDResponse(
                projectName=mock_brd_response["projectName"],
                executiveSummary=mock_brd_response["executiveSummary"],
                businessObjectives=mock_brd_response["businessObjectives"],
                requirements=[
                    Requirement(**req) for req in mock_brd_response["requirements"]
                ],
                stakeholders=[
                    Stakeholder(**sh) for sh in mock_brd_response["stakeholders"]
                ]
            )
        
        mock_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        # Override the dependency
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_service
        
        try:
            # Create test client and make request
            client = TestClient(app)
            response = client.post("/generate_brd", json=request_data)
            
            # Verify that the response is NOT a 400 (validation error)
            assert response.status_code != 400, (
                f"Valid request was rejected with 400 status code. "
                f"Request: {request_data}, Response: {response.json()}"
            )
            
            # The response should be either 200 (success) or 5xx (server error)
            assert response.status_code == 200 or response.status_code >= 500, (
                f"Unexpected status code {response.status_code} for valid request. "
                f"Expected 200 or 5xx. Request: {request_data}"
            )
            
            # If successful (200), verify the response structure
            if response.status_code == 200:
                response_data = response.json()
                assert "projectName" in response_data
                assert "executiveSummary" in response_data
                assert "businessObjectives" in response_data
                assert "requirements" in response_data
                assert "stakeholders" in response_data
        
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()


# ============================================================================
# Integration Tests for Complete API
# ============================================================================


class TestBRDEndpointIntegration:
    """Integration tests for the complete BRD API.
    
    These tests verify end-to-end functionality including:
    - Successful BRD generation with mocked OpenAI
    - Error scenarios (missing projectName, OpenAI unavailable, invalid response)
    - API documentation endpoints
    """
    
    def test_generate_brd_success_end_to_end(self):
        """Test /generate_brd endpoint end-to-end with mocked OpenAI.
        
        Validates: Requirements 1.1, 1.3
        
        Verifies that a valid request flows through the entire stack
        (router -> service -> OpenAI client) and returns a properly
        structured BRD response.
        """
        # Create a valid request
        request_data = {
            "projectName": "E-commerce Platform",
            "emailText": "We need to build an online store with payment processing.",
            "slackText": "The team discussed adding a shopping cart feature.",
            "meetingText": "Meeting notes: Focus on user authentication and product catalog."
        }
        
        # Mock OpenAI response
        mock_openai_response = {
            "projectName": "E-commerce Platform",
            "executiveSummary": "An online e-commerce platform with payment processing capabilities.",
            "businessObjectives": [
                "Enable online sales",
                "Provide secure payment processing",
                "Improve customer experience"
            ],
            "requirements": [
                {
                    "id": "REQ-1",
                    "description": "Implement user authentication system",
                    "priority": "High"
                },
                {
                    "id": "REQ-2",
                    "description": "Create product catalog with search functionality",
                    "priority": "High"
                },
                {
                    "id": "REQ-3",
                    "description": "Integrate payment gateway",
                    "priority": "High"
                }
            ],
            "stakeholders": [
                {"name": "Product Manager", "role": "Project Owner"},
                {"name": "Development Team", "role": "Implementation"},
                {"name": "End Users", "role": "Primary Users"}
            ]
        }
        
        # Mock the BRD generator service
        mock_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd(*args, **kwargs):
            return BRDResponse(
                projectName=mock_openai_response["projectName"],
                executiveSummary=mock_openai_response["executiveSummary"],
                businessObjectives=mock_openai_response["businessObjectives"],
                requirements=[Requirement(**req) for req in mock_openai_response["requirements"]],
                stakeholders=[Stakeholder(**sh) for sh in mock_openai_response["stakeholders"]]
            )
        
        mock_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        # Override the dependency
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_service
        
        try:
            # Create test client and make request
            client = TestClient(app)
            response = client.post("/generate_brd", json=request_data)
            
            # Verify successful response
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            
            # Verify response structure
            response_data = response.json()
            assert response_data["projectName"] == "E-commerce Platform"
            assert "executiveSummary" in response_data
            assert len(response_data["businessObjectives"]) == 3
            assert len(response_data["requirements"]) == 3
            assert len(response_data["stakeholders"]) == 3
            
            # Verify requirement structure
            req = response_data["requirements"][0]
            assert "id" in req
            assert "description" in req
            assert "priority" in req
            
            # Verify stakeholder structure
            stakeholder = response_data["stakeholders"][0]
            assert "name" in stakeholder
            assert "role" in stakeholder
            
        finally:
            app.dependency_overrides.clear()
    
    def test_generate_brd_missing_project_name(self):
        """Test error handling when projectName is missing.
        
        Validates: Requirements 1.3, 5.1
        
        Verifies that requests without a projectName are rejected
        with a 422 validation error.
        """
        # Request missing projectName
        request_data = {
            "emailText": "Some project information"
        }
        
        # Mock the dependency
        mock_service = Mock(spec=BRDGeneratorService)
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post("/generate_brd", json=request_data)
            
            # Verify validation error response
            assert response.status_code == 422, f"Expected 422, got {response.status_code}"
            
            response_data = response.json()
            assert "detail" in response_data
            
        finally:
            app.dependency_overrides.clear()
    
    def test_generate_brd_openai_unavailable(self):
        """Test error handling when OpenAI service is unavailable.
        
        Validates: Requirements 5.2
        
        Verifies that OpenAI service errors are properly handled
        and return a 503 status code.
        """
        request_data = {
            "projectName": "Test Project",
            "emailText": "Test content"
        }
        
        # Mock service to raise OpenAIServiceError
        mock_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd_error(*args, **kwargs):
            raise OpenAIServiceError("OpenAI API is currently unavailable")
        
        mock_service.generate_brd = AsyncMock(side_effect=mock_generate_brd_error)
        
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post("/generate_brd", json=request_data)
            
            # Verify service unavailable response
            assert response.status_code == 503, f"Expected 503, got {response.status_code}"
            
            response_data = response.json()
            assert "detail" in response_data
            assert "unavailable" in response_data["detail"].lower()
            
        finally:
            app.dependency_overrides.clear()
    
    def test_generate_brd_invalid_openai_response(self):
        """Test error handling when OpenAI returns an invalid response.
        
        Validates: Requirements 5.3
        
        Verifies that invalid OpenAI responses are properly handled
        and return a 500 status code.
        """
        request_data = {
            "projectName": "Test Project",
            "emailText": "Test content"
        }
        
        # Mock service to raise BRDGenerationError
        mock_service = Mock(spec=BRDGeneratorService)
        
        async def mock_generate_brd_error(*args, **kwargs):
            raise BRDGenerationError("Failed to parse OpenAI response")
        
        mock_service.generate_brd = AsyncMock(side_effect=mock_generate_brd_error)
        
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post("/generate_brd", json=request_data)
            
            # Verify internal server error response
            assert response.status_code == 500, f"Expected 500, got {response.status_code}"
            
            response_data = response.json()
            assert "detail" in response_data
            
        finally:
            app.dependency_overrides.clear()
    
    def test_docs_endpoint_returns_openapi_documentation(self):
        """Test /docs endpoint returns OpenAPI documentation.
        
        Validates: Requirements 7.1, 7.2
        
        Verifies that the Swagger UI documentation endpoint is accessible
        and returns HTML content.
        """
        # Use the main app which includes all routers and configuration
        client = TestClient(main_app)
        response = client.get("/docs")
        
        # Verify successful response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify HTML content is returned
        assert "text/html" in response.headers.get("content-type", "")
        
        # Verify it contains Swagger UI elements
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_redoc_endpoint_returns_documentation(self):
        """Test /redoc endpoint returns ReDoc documentation.
        
        Validates: Requirements 7.1, 7.2
        
        Verifies that the ReDoc documentation endpoint is accessible
        and returns HTML content.
        """
        # Use the main app which includes all routers and configuration
        client = TestClient(main_app)
        response = client.get("/redoc")
        
        # Verify successful response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify HTML content is returned
        assert "text/html" in response.headers.get("content-type", "")
        
        # Verify it contains ReDoc elements
        assert "redoc" in response.text.lower()


# Custom strategy for generating invalid BRDRequest dictionaries
@st.composite
def invalid_brd_request_dict(draw):
    """Generate an invalid BRDRequest dictionary that should fail validation.

    Generates requests with one of the following validation failures:
    1. Missing projectName
    2. Empty projectName
    3. Whitespace-only projectName
    4. All text fields empty or missing
    """
    # Choose which validation failure to generate
    failure_type = draw(st.integers(min_value=0, max_value=3))

    if failure_type == 0:
        # Missing projectName entirely
        request_dict = {}
        # Add at least one text field
        email_text = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
        request_dict["emailText"] = email_text

    elif failure_type == 1:
        # Empty projectName
        request_dict = {"projectName": ""}
        # Add at least one text field
        slack_text = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
        request_dict["slackText"] = slack_text

    elif failure_type == 2:
        # Whitespace-only projectName
        whitespace = draw(st.text(alphabet=" \t\n\r", min_size=1, max_size=10))
        request_dict = {"projectName": whitespace}
        # Add at least one text field
        meeting_text = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
        request_dict["meetingText"] = meeting_text

    else:  # failure_type == 3
        # Valid projectName but all text fields empty or missing
        project_name = draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
        request_dict = {"projectName": project_name}

        # Randomly include empty/whitespace text fields
        include_email = draw(st.booleans())
        include_slack = draw(st.booleans())
        include_meeting = draw(st.booleans())

        if include_email:
            request_dict["emailText"] = draw(st.text(max_size=10).filter(lambda x: not x.strip()))
        if include_slack:
            request_dict["slackText"] = draw(st.text(max_size=10).filter(lambda x: not x.strip()))
        if include_meeting:
            request_dict["meetingText"] = draw(st.text(max_size=10).filter(lambda x: not x.strip()))

    return request_dict


class TestBRDEndpointResponseStructure:
    """Property-based tests for response structure completeness."""
    
    @given(request_data=valid_brd_request_dict())
    @settings(max_examples=100)
    def test_property_response_structure_completeness(self, request_data):
        """Property 3: Response structure completeness.
        
        Feature: brd-generator-backend, Property 3: Response structure completeness
        
        Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
        
        For any successful BRD generation, the response JSON should contain all
        required fields: projectName (string), executiveSummary (string),
        businessObjectives (array), requirements (array), and stakeholders (array).
        """
        # Create a mock BRD response with all required fields
        mock_brd_response = {
            "projectName": request_data["projectName"],
            "executiveSummary": "Generated executive summary for the project",
            "businessObjectives": [
                "Business objective 1",
                "Business objective 2",
                "Business objective 3"
            ],
            "requirements": [
                {
                    "id": "REQ-1",
                    "description": "First requirement description",
                    "priority": "High"
                },
                {
                    "id": "REQ-2",
                    "description": "Second requirement description",
                    "priority": "Medium"
                }
            ],
            "stakeholders": [
                {
                    "name": "Stakeholder 1",
                    "role": "Project Manager"
                },
                {
                    "name": "Stakeholder 2",
                    "role": "Developer"
                }
            ]
        }
        
        # Mock the BRD generator service
        mock_service = Mock(spec=BRDGeneratorService)
        
        # Create an async mock for generate_brd
        async def mock_generate_brd(*args, **kwargs):
            return BRDResponse(
                projectName=mock_brd_response["projectName"],
                executiveSummary=mock_brd_response["executiveSummary"],
                businessObjectives=mock_brd_response["businessObjectives"],
                requirements=[
                    Requirement(**req) for req in mock_brd_response["requirements"]
                ],
                stakeholders=[
                    Stakeholder(**sh) for sh in mock_brd_response["stakeholders"]
                ]
            )
        
        mock_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)
        
        # Override the dependency
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_service
        
        try:
            # Create test client and make request
            client = TestClient(app)
            response = client.post("/generate_brd", json=request_data)
            
            # Verify successful response
            assert response.status_code == 200, (
                f"Expected 200 status code, got {response.status_code}. "
                f"Request: {request_data}, Response: {response.text}"
            )
            
            # Parse response JSON
            response_data = response.json()
            
            # Verify all required fields are present
            assert "projectName" in response_data, (
                f"Response missing 'projectName' field. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            assert "executiveSummary" in response_data, (
                f"Response missing 'executiveSummary' field. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            assert "businessObjectives" in response_data, (
                f"Response missing 'businessObjectives' field. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            assert "requirements" in response_data, (
                f"Response missing 'requirements' field. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            assert "stakeholders" in response_data, (
                f"Response missing 'stakeholders' field. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            # Verify field types
            assert isinstance(response_data["projectName"], str), (
                f"'projectName' should be a string, got {type(response_data['projectName'])}. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            assert isinstance(response_data["executiveSummary"], str), (
                f"'executiveSummary' should be a string, got {type(response_data['executiveSummary'])}. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            assert isinstance(response_data["businessObjectives"], list), (
                f"'businessObjectives' should be a list, got {type(response_data['businessObjectives'])}. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            assert isinstance(response_data["requirements"], list), (
                f"'requirements' should be a list, got {type(response_data['requirements'])}. "
                f"Request: {request_data}, Response: {response_data}"
            )
            
            assert isinstance(response_data["stakeholders"], list), (
                f"'stakeholders' should be a list, got {type(response_data['stakeholders'])}. "
                f"Request: {request_data}, Response: {response_data}"
            )
        
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()


class TestBRDEndpointValidationErrors:
    """Property-based tests for validation error responses."""

    @given(request_data=invalid_brd_request_dict())
    @settings(max_examples=100)
    def test_property_validation_error_responses(self, request_data):
        """Property 7: Validation error responses.

        Feature: brd-generator-backend, Property 7: Validation error responses

        Validates: Requirements 5.1

        For any validation failure, the API should return a 400 or 422 status code
        with a JSON response containing an error message that describes what
        validation failed.
        
        Note: FastAPI returns 422 (Unprocessable Entity) for Pydantic validation errors,
        which is semantically equivalent to 400 (Bad Request) for validation failures.
        """
        # Mock the dependency to avoid needing real OpenAI credentials
        # This is necessary even though validation happens before dependency injection,
        # because FastAPI may still try to resolve dependencies in some cases
        mock_service = Mock(spec=BRDGeneratorService)
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_service
        
        try:
            # Create test client
            client = TestClient(app)

            # Make request with invalid data
            response = client.post("/generate_brd", json=request_data)

            # Verify that the response is a 400 or 422 (validation error)
            # FastAPI uses 422 for Pydantic validation errors
            assert response.status_code in [400, 422], (
                f"Expected 400 or 422 status code for invalid request, got {response.status_code}. "
                f"Request: {request_data}, Response: {response.text}"
            )

            # Verify the response is JSON
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                pytest.fail(
                    f"Response is not valid JSON. "
                    f"Request: {request_data}, Response: {response.text}"
                )

            # Verify the response contains an error message
            assert "detail" in response_data, (
                f"Response does not contain 'detail' field. "
                f"Request: {request_data}, Response: {response_data}"
            )

            # Verify the error message is descriptive (non-empty string)
            detail = response_data["detail"]
            assert isinstance(detail, (str, list)), (
                f"Error detail should be a string or list, got {type(detail)}. "
                f"Request: {request_data}, Response: {response_data}"
            )

            # If detail is a string, verify it's not empty
            if isinstance(detail, str):
                assert len(detail) > 0, (
                    f"Error detail is empty. "
                    f"Request: {request_data}, Response: {response_data}"
                )

            # If detail is a list (Pydantic validation errors), verify it's not empty
            if isinstance(detail, list):
                assert len(detail) > 0, (
                    f"Error detail list is empty. "
                    f"Request: {request_data}, Response: {response_data}"
                )
        
        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()



class TestBRDEndpointRequirementStructure:
    """Property-based tests for requirement object structure."""

    @given(request_data=valid_brd_request_dict())
    @settings(max_examples=100)
    def test_property_requirement_object_structure(self, request_data):
        """Property 4: Requirement object structure.

        Feature: brd-generator-backend, Property 4: Requirement object structure

        Validates: Requirements 4.6

        For any requirement in the requirements array of a generated BRD,
        the requirement object should contain id (string), description (string),
        and priority (string) fields.
        """
        # Create a mock BRD response with requirements
        mock_brd_response = {
            "projectName": request_data["projectName"],
            "executiveSummary": "Generated executive summary",
            "businessObjectives": ["Objective 1", "Objective 2"],
            "requirements": [
                {
                    "id": "REQ-1",
                    "description": "First requirement",
                    "priority": "High"
                },
                {
                    "id": "REQ-2",
                    "description": "Second requirement",
                    "priority": "Medium"
                },
                {
                    "id": "REQ-3",
                    "description": "Third requirement",
                    "priority": "Low"
                }
            ],
            "stakeholders": [
                {"name": "Stakeholder", "role": "Role"}
            ]
        }

        # Mock the BRD generator service
        mock_service = Mock(spec=BRDGeneratorService)

        # Create an async mock for generate_brd
        async def mock_generate_brd(*args, **kwargs):
            return BRDResponse(
                projectName=mock_brd_response["projectName"],
                executiveSummary=mock_brd_response["executiveSummary"],
                businessObjectives=mock_brd_response["businessObjectives"],
                requirements=[
                    Requirement(**req) for req in mock_brd_response["requirements"]
                ],
                stakeholders=[
                    Stakeholder(**sh) for sh in mock_brd_response["stakeholders"]
                ]
            )

        mock_service.generate_brd = AsyncMock(side_effect=mock_generate_brd)

        # Override the dependency
        app.dependency_overrides[get_brd_generator_service] = lambda: mock_service

        try:
            # Create test client and make request
            client = TestClient(app)
            response = client.post("/generate_brd", json=request_data)

            # Verify successful response
            assert response.status_code == 200, (
                f"Expected 200 status code, got {response.status_code}. "
                f"Request: {request_data}, Response: {response.text}"
            )

            # Parse response JSON
            response_data = response.json()

            # Verify requirements array exists
            assert "requirements" in response_data, (
                f"Response missing 'requirements' field. "
                f"Request: {request_data}, Response: {response_data}"
            )

            requirements = response_data["requirements"]
            assert isinstance(requirements, list), (
                f"'requirements' should be a list, got {type(requirements)}. "
                f"Request: {request_data}, Response: {response_data}"
            )

            # Verify each requirement has the required fields
            for idx, requirement in enumerate(requirements):
                # Verify 'id' field exists and is a string
                assert "id" in requirement, (
                    f"Requirement at index {idx} missing 'id' field. "
                    f"Requirement: {requirement}, Request: {request_data}"
                )
                assert isinstance(requirement["id"], str), (
                    f"Requirement 'id' at index {idx} should be a string, got {type(requirement['id'])}. "
                    f"Requirement: {requirement}, Request: {request_data}"
                )

                # Verify 'description' field exists and is a string
                assert "description" in requirement, (
                    f"Requirement at index {idx} missing 'description' field. "
                    f"Requirement: {requirement}, Request: {request_data}"
                )
                assert isinstance(requirement["description"], str), (
                    f"Requirement 'description' at index {idx} should be a string, got {type(requirement['description'])}. "
                    f"Requirement: {requirement}, Request: {request_data}"
                )

                # Verify 'priority' field exists and is a string
                assert "priority" in requirement, (
                    f"Requirement at index {idx} missing 'priority' field. "
                    f"Requirement: {requirement}, Request: {request_data}"
                )
                assert isinstance(requirement["priority"], str), (
                    f"Requirement 'priority' at index {idx} should be a string, got {type(requirement['priority'])}. "
                    f"Requirement: {requirement}, Request: {request_data}"
                )

        finally:
            # Clean up dependency override
            app.dependency_overrides.clear()

