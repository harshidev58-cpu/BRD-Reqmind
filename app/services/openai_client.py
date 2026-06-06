"""OpenAI API client for the BRD Generator Backend API.

This module provides a client for interacting with OpenAI's API to generate
completions for BRD generation.
"""

from openai import OpenAI, OpenAIError
from app.utils.exceptions import OpenAIServiceError


class OpenAIClient:
    """Client for interacting with OpenAI's API.
    
    This class handles all communication with OpenAI's API, including
    authentication, request formatting, and error handling.
    
    Attributes:
        api_key: The OpenAI API key for authentication
        model: The OpenAI model to use for completions
        client: The OpenAI SDK client instance
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: str = None):
        """Initialize the OpenAI client.
        
        Args:
            api_key: The OpenAI API key for authentication
            model: The OpenAI model to use (default: "gpt-4")
            base_url: Optional base URL for OpenAI-compatible APIs (e.g., Groq)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
        # Initialize client with base_url if provided (for Groq or other providers)
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
    
    async def generate_completion(self, prompt: str, response_format: dict = None) -> str:
        """Call OpenAI API to generate a completion.
        
        This method sends a prompt to OpenAI's API and returns the generated
        completion. It handles JSON response formatting and error handling.
        
        Args:
            prompt: The prompt to send to OpenAI
            response_format: Optional format specification for structured output
                           (e.g., {"type": "json_object"} for JSON responses)
        
        Returns:
            The generated text response from OpenAI
        
        Raises:
            OpenAIServiceError: When the API call fails due to authentication,
                              rate limiting, network errors, or service unavailability
        """
        try:
            # Build the request parameters
            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Add response format if specified
            if response_format:
                request_params["response_format"] = response_format
            
            # Make the API call
            response = self.client.chat.completions.create(**request_params)
            
            # Extract and return the completion text
            return response.choices[0].message.content
            
        except OpenAIError as e:
            # Catch all OpenAI SDK errors and wrap them in our custom exception
            raise OpenAIServiceError(f"OpenAI API error: {str(e)}") from e
        except Exception as e:
            # Catch any unexpected errors
            raise OpenAIServiceError(f"Unexpected error calling OpenAI API: {str(e)}") from e

