"""Property-based tests for BRD Generator Service.

This module contains property-based tests using Hypothesis to verify
the correctness of the BRD generator service, particularly the prompt
construction logic.
"""

import json
import pytest
from unittest.mock import Mock
from hypothesis import given, strategies as st, settings
from app.models.request import BRDRequest
from app.services.brd_generator import BRDGeneratorService
from app.services.openai_client import OpenAIClient
from app.utils.exceptions import BRDGenerationError, OpenAIServiceError


# Custom strategy for generating valid BRDRequest objects
@st.composite
def valid_brd_request(draw):
    """Generate a valid BRDRequest with random data.
    
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
    
    return BRDRequest(
        projectName=project_name,
        emailText=email_text,
        slackText=slack_text,
        meetingText=meeting_text
    )


class TestBRDGeneratorPromptConstruction:
    """Test suite for BRD generator prompt construction."""
    
    @given(request=valid_brd_request())
    @settings(max_examples=100)
    def test_property_prompt_includes_project_information(self, request):
        """Property 5: Prompt includes project information.
        
        Feature: brd-generator-backend, Property 5: Prompt includes project information
        
        Validates: Requirements 3.2
        
        For any valid BRD request, the prompt sent to OpenAI should contain
        the projectName and all non-empty text fields (emailText, slackText,
        meetingText) from the request.
        """
        # Create a mock OpenAI client (we don't need it for prompt testing)
        mock_client = Mock(spec=OpenAIClient)
        service = BRDGeneratorService(openai_client=mock_client)
        
        # Build the prompt
        prompt = service._build_prompt(request)
        
        # Verify projectName is in the prompt
        assert request.projectName in prompt, \
            f"Prompt should contain projectName '{request.projectName}'"
        
        # Verify all non-empty text fields are in the prompt
        if request.emailText and request.emailText.strip():
            assert request.emailText.strip() in prompt, \
                "Prompt should contain non-empty emailText"
        
        if request.slackText and request.slackText.strip():
            assert request.slackText.strip() in prompt, \
                "Prompt should contain non-empty slackText"
        
        if request.meetingText and request.meetingText.strip():
            assert request.meetingText.strip() in prompt, \
                "Prompt should contain non-empty meetingText"
        
        # Verify the prompt contains the expected structure instructions
        assert "Business Requirements Document" in prompt or "BRD" in prompt, \
            "Prompt should mention BRD or Business Requirements Document"
        assert "JSON" in prompt, \
            "Prompt should request JSON format"



class TestBRDGeneratorService:
    """Unit tests for BRD generator service."""
    
    @pytest.mark.asyncio
    async def test_successful_brd_generation(self):
        """Test successful BRD generation with mocked OpenAI client."""
        # Create a mock OpenAI client
        mock_client = Mock(spec=OpenAIClient)
        
        # Mock the OpenAI response
        mock_response = json.dumps({
            "projectName": "Test Project",
            "executiveSummary": "This is a test project summary.",
            "businessObjectives": ["Objective 1", "Objective 2"],
            "requirements": [
                {"id": "REQ-1", "description": "First requirement", "priority": "High"},
                {"id": "REQ-2", "description": "Second requirement", "priority": "Medium"}
            ],
            "stakeholders": [
                {"name": "John Doe", "role": "Product Manager"},
                {"name": "Jane Smith", "role": "Developer"}
            ]
        })
        
        # Create async mock
        async def mock_generate(*args, **kwargs):
            return mock_response
        
        mock_client.generate_completion = Mock(side_effect=mock_generate)
        
        # Create service and request
        service = BRDGeneratorService(openai_client=mock_client)
        request = BRDRequest(
            projectName="Test Project",
            emailText="This is an email about the project."
        )
        
        # Generate BRD
        result = await service.generate_brd(request)
        
        # Verify the result
        assert result.projectName == "Test Project"
        assert result.executiveSummary == "This is a test project summary."
        assert len(result.businessObjectives) == 2
        assert len(result.requirements) == 2
        assert len(result.stakeholders) == 2
        assert result.requirements[0].id == "REQ-1"
        assert result.requirements[0].priority == "High"
        
        # Verify OpenAI client was called
        mock_client.generate_completion.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_json_response(self):
        """Test error handling when OpenAI returns invalid JSON."""
        # Create a mock OpenAI client that returns invalid JSON
        mock_client = Mock(spec=OpenAIClient)
        
        async def mock_generate(*args, **kwargs):
            return "This is not valid JSON"
        
        mock_client.generate_completion = Mock(side_effect=mock_generate)
        
        # Create service and request
        service = BRDGeneratorService(openai_client=mock_client)
        request = BRDRequest(
            projectName="Test Project",
            emailText="Test email content"
        )
        
        # Verify that BRDGenerationError is raised
        with pytest.raises(BRDGenerationError) as exc_info:
            await service.generate_brd(request)
        
        assert "Failed to parse OpenAI response as JSON" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_response_structure(self):
        """Test error handling when OpenAI returns JSON with invalid structure."""
        # Create a mock OpenAI client that returns JSON with missing fields
        mock_client = Mock(spec=OpenAIClient)
        mock_response = json.dumps({
            "projectName": "Test Project",
            # Missing required fields like executiveSummary, businessObjectives, etc.
        })
        
        async def mock_generate(*args, **kwargs):
            return mock_response
        
        mock_client.generate_completion = Mock(side_effect=mock_generate)
        
        # Create service and request
        service = BRDGeneratorService(openai_client=mock_client)
        request = BRDRequest(
            projectName="Test Project",
            slackText="Test slack content"
        )
        
        # Verify that BRDGenerationError is raised
        with pytest.raises(BRDGenerationError) as exc_info:
            await service.generate_brd(request)
        
        assert "Failed to validate BRD response structure" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_error_handling_openai_service_error(self):
        """Test that OpenAI service errors are propagated correctly."""
        # Create a mock OpenAI client that raises an error
        mock_client = Mock(spec=OpenAIClient)
        mock_client.generate_completion = Mock(side_effect=OpenAIServiceError("API rate limit exceeded"))
        
        # Create service and request
        service = BRDGeneratorService(openai_client=mock_client)
        request = BRDRequest(
            projectName="Test Project",
            meetingText="Test meeting notes"
        )
        
        # Verify that OpenAIServiceError is propagated
        with pytest.raises(OpenAIServiceError) as exc_info:
            await service.generate_brd(request)
        
        assert "API rate limit exceeded" in str(exc_info.value)
    
    def test_prompt_construction_with_email_only(self):
        """Test prompt construction with only email text."""
        mock_client = Mock(spec=OpenAIClient)
        service = BRDGeneratorService(openai_client=mock_client)
        
        request = BRDRequest(
            projectName="Email Project",
            emailText="Email content here"
        )
        
        prompt = service._build_prompt(request)
        
        assert "Email Project" in prompt
        assert "Email content here" in prompt
        assert "Email Content:" in prompt
        assert "Slack Messages:" not in prompt
        assert "Meeting Notes:" not in prompt
    
    def test_prompt_construction_with_slack_only(self):
        """Test prompt construction with only Slack text."""
        mock_client = Mock(spec=OpenAIClient)
        service = BRDGeneratorService(openai_client=mock_client)
        
        request = BRDRequest(
            projectName="Slack Project",
            slackText="Slack messages here"
        )
        
        prompt = service._build_prompt(request)
        
        assert "Slack Project" in prompt
        assert "Slack messages here" in prompt
        assert "Slack Messages:" in prompt
        assert "Email Content:" not in prompt
        assert "Meeting Notes:" not in prompt
    
    def test_prompt_construction_with_meeting_only(self):
        """Test prompt construction with only meeting text."""
        mock_client = Mock(spec=OpenAIClient)
        service = BRDGeneratorService(openai_client=mock_client)
        
        request = BRDRequest(
            projectName="Meeting Project",
            meetingText="Meeting notes here"
        )
        
        prompt = service._build_prompt(request)
        
        assert "Meeting Project" in prompt
        assert "Meeting notes here" in prompt
        assert "Meeting Notes:" in prompt
        assert "Email Content:" not in prompt
        assert "Slack Messages:" not in prompt
    
    def test_prompt_construction_with_all_sources(self):
        """Test prompt construction with all text sources."""
        mock_client = Mock(spec=OpenAIClient)
        service = BRDGeneratorService(openai_client=mock_client)
        
        request = BRDRequest(
            projectName="Complete Project",
            emailText="Email content",
            slackText="Slack messages",
            meetingText="Meeting notes"
        )
        
        prompt = service._build_prompt(request)
        
        assert "Complete Project" in prompt
        assert "Email content" in prompt
        assert "Slack messages" in prompt
        assert "Meeting notes" in prompt
        assert "Email Content:" in prompt
        assert "Slack Messages:" in prompt
        assert "Meeting Notes:" in prompt
    
    def test_prompt_construction_ignores_empty_strings(self):
        """Test that prompt construction ignores empty or whitespace-only strings."""
        mock_client = Mock(spec=OpenAIClient)
        service = BRDGeneratorService(openai_client=mock_client)
        
        request = BRDRequest(
            projectName="Test Project",
            emailText="Valid email content",
            slackText="   ",  # Whitespace only
            meetingText=""    # Empty string
        )
        
        prompt = service._build_prompt(request)
        
        assert "Test Project" in prompt
        assert "Valid email content" in prompt
        assert "Email Content:" in prompt
        # Empty/whitespace fields should not appear
        assert "Slack Messages:" not in prompt
        assert "Meeting Notes:" not in prompt
