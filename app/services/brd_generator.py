"""BRD Generator Service for the BRD Generator Backend API.

This module provides the core business logic for generating Business Requirements
Documents from project information using OpenAI's API.
"""

import json
from app.models.request import BRDRequest
from app.models.response import BRDResponse
from app.services.openai_client import OpenAIClient
from app.utils.exceptions import BRDGenerationError, OpenAIServiceError


class BRDGeneratorService:
    """Service for generating Business Requirements Documents.
    
    This service orchestrates the BRD generation process by constructing
    prompts from request data, calling OpenAI's API, and parsing the
    response into structured BRD data.
    
    Attributes:
        openai_client: The OpenAI client for API communication
    """
    
    def __init__(self, openai_client: OpenAIClient):
        """Initialize the BRD generator service.
        
        Args:
            openai_client: The OpenAI client instance for API communication
        """
        self.openai_client = openai_client
    
    async def generate_brd(self, request: BRDRequest) -> BRDResponse:
        """Generate a structured BRD from project information.
        
        This method orchestrates the entire BRD generation process:
        1. Builds a prompt from the request data
        2. Calls OpenAI API to generate the BRD content
        3. Parses the JSON response into a BRDResponse model
        
        Args:
            request: BRDRequest containing project information
            
        Returns:
            BRDResponse with structured BRD data
            
        Raises:
            OpenAIServiceError: When OpenAI API fails
            BRDGenerationError: When BRD generation or parsing fails
        """
        try:
            # Build the prompt from request data
            prompt = self._build_prompt(request)
            
            # Call OpenAI API with JSON response format
            response_text = await self.openai_client.generate_completion(
                prompt=prompt,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            try:
                response_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                raise BRDGenerationError(f"Failed to parse OpenAI response as JSON: {str(e)}") from e
            
            # Validate and convert to BRDResponse model
            try:
                brd_response = BRDResponse(**response_data)
            except Exception as e:
                raise BRDGenerationError(f"Failed to validate BRD response structure: {str(e)}") from e
            
            return brd_response
            
        except OpenAIServiceError:
            # Re-raise OpenAI errors as-is
            raise
        except BRDGenerationError:
            # Re-raise BRD generation errors as-is
            raise
        except Exception as e:
            # Wrap any unexpected errors
            raise BRDGenerationError(f"Unexpected error during BRD generation: {str(e)}") from e
    
    def _build_prompt(self, request: BRDRequest) -> str:
        """Build the prompt for OpenAI API from request data.
        
        This method constructs a detailed prompt that includes the project name
        and all provided text sources (email, Slack, meeting notes). The prompt
        instructs OpenAI to generate a structured BRD in JSON format.
        
        Args:
            request: BRDRequest containing project information
            
        Returns:
            Formatted prompt string for OpenAI API
        """
        # Start with the base instruction
        prompt_parts = [
            "You are a business analyst creating a Business Requirements Document.",
            f"\nProject Name: {request.projectName}",
            "\nSource Information:"
        ]
        
        # Add each non-empty text source
        if request.emailText and request.emailText.strip():
            prompt_parts.append(f"\nEmail Content:\n{request.emailText.strip()}")
        
        if request.slackText and request.slackText.strip():
            prompt_parts.append(f"\nSlack Messages:\n{request.slackText.strip()}")
        
        if request.meetingText and request.meetingText.strip():
            prompt_parts.append(f"\nMeeting Notes:\n{request.meetingText.strip()}")
        
        # Add the JSON structure instruction
        prompt_parts.append("""

Generate a comprehensive BRD in JSON format with the following structure:
{
  "projectName": "string",
  "executiveSummary": "string",
  "businessObjectives": ["string"],
  "requirements": [
    {
      "id": "string",
      "description": "string",
      "priority": "High|Medium|Low"
    }
  ],
  "stakeholders": [
    {
      "name": "string",
      "role": "string"
    }
  ]
}

Ensure the response is valid JSON and includes all required fields.""")
        
        return "".join(prompt_parts)
