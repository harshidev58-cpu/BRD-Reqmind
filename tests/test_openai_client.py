"""Unit tests for OpenAI client.

Tests the OpenAI client's ability to generate completions, handle errors,
and configure JSON response formats.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from openai import OpenAIError, APIError, RateLimitError, APIConnectionError
from app.services.openai_client import OpenAIClient
from app.utils.exceptions import OpenAIServiceError


class TestOpenAIClient:
    """Test suite for OpenAIClient class."""
    
    def test_initialization(self):
        """Test that OpenAI client initializes correctly with api_key and model.
        
        Validates: Requirements 3.1
        """
        api_key = "test-api-key-123"
        model = "gpt-4-turbo"
        
        # Mock the OpenAI client to avoid initialization issues
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            client = OpenAIClient(api_key=api_key, model=model)
            
            assert client.api_key == api_key
            assert client.model == model
            assert client.client is not None
            mock_openai.assert_called_once_with(api_key=api_key)
    
    def test_initialization_with_default_model(self):
        """Test that OpenAI client uses default model when not specified.
        
        Validates: Requirements 3.1
        """
        api_key = "test-api-key-456"
        
        # Mock the OpenAI client to avoid initialization issues
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            client = OpenAIClient(api_key=api_key)
            
            assert client.api_key == api_key
            assert client.model == "gpt-4"
            assert client.client is not None
            mock_openai.assert_called_once_with(api_key=api_key)
    
    @pytest.mark.asyncio
    async def test_successful_completion_generation(self):
        """Test successful completion generation with mocked OpenAI API.
        
        Validates: Requirements 3.1, 3.3
        """
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Generated BRD content"
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.return_value = mock_response
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Call generate_completion
            result = await client.generate_completion("Test prompt")
        
        assert result == "Generated BRD content"
    
    @pytest.mark.asyncio
    async def test_completion_with_json_format(self):
        """Test that JSON format is correctly configured in the request.
        
        Validates: Requirements 3.5
        """
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"key": "value"}'
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.return_value = mock_response
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Call generate_completion with JSON format
            response_format = {"type": "json_object"}
            result = await client.generate_completion("Test prompt", response_format=response_format)
            
            # Verify the method was called with correct parameters
            mock_client_instance.chat.completions.create.assert_called_once()
            call_args = mock_client_instance.chat.completions.create.call_args[1]
            
            assert call_args["model"] == "gpt-4"
            assert call_args["messages"] == [{"role": "user", "content": "Test prompt"}]
            assert call_args["response_format"] == {"type": "json_object"}
        
        assert result == '{"key": "value"}'
    
    @pytest.mark.asyncio
    async def test_completion_without_json_format(self):
        """Test that request works without response_format parameter.
        
        Validates: Requirements 3.1, 3.3
        """
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Plain text response"
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.return_value = mock_response
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Call generate_completion without response_format
            result = await client.generate_completion("Test prompt")
            
            # Verify the method was called without response_format
            mock_client_instance.chat.completions.create.assert_called_once()
            call_args = mock_client_instance.chat.completions.create.call_args[1]
            
            assert "response_format" not in call_args
            assert call_args["model"] == "gpt-4"
            assert call_args["messages"] == [{"role": "user", "content": "Test prompt"}]
        
        assert result == "Plain text response"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test that OpenAI API errors are caught and wrapped in OpenAIServiceError.
        
        Validates: Requirements 3.4
        """
        # Mock an API error
        error_message = "Invalid API key provided"
        mock_error = APIError(
            message=error_message,
            request=Mock(),
            body=None
        )
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.side_effect = mock_error
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Verify error is caught and wrapped
            with pytest.raises(OpenAIServiceError) as exc_info:
                await client.generate_completion("Test prompt")
            
            # Verify the error message includes details
            assert "OpenAI API error" in str(exc_info.value)
            assert error_message in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self):
        """Test that rate limit errors are caught and wrapped in OpenAIServiceError.
        
        Validates: Requirements 3.4
        """
        # Mock a rate limit error
        error_message = "Rate limit exceeded"
        mock_error = RateLimitError(
            message=error_message,
            response=Mock(),
            body=None
        )
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.side_effect = mock_error
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Verify error is caught and wrapped
            with pytest.raises(OpenAIServiceError) as exc_info:
                await client.generate_completion("Test prompt")
            
            # Verify the error message includes details
            assert "OpenAI API error" in str(exc_info.value)
            assert error_message in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test that connection errors are caught and wrapped in OpenAIServiceError.
        
        Validates: Requirements 3.4
        """
        # Mock a connection error
        error_message = "Connection timeout"
        mock_error = APIConnectionError(
            message=error_message,
            request=Mock()
        )
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.side_effect = mock_error
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Verify error is caught and wrapped
            with pytest.raises(OpenAIServiceError) as exc_info:
                await client.generate_completion("Test prompt")
            
            # Verify the error message includes details
            assert "OpenAI API error" in str(exc_info.value)
            assert error_message in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_generic_openai_error_handling(self):
        """Test that generic OpenAI errors are caught and wrapped in OpenAIServiceError.
        
        Validates: Requirements 3.4
        """
        # Mock a generic OpenAI error
        error_message = "Service temporarily unavailable"
        mock_error = OpenAIError(error_message)
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.side_effect = mock_error
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Verify error is caught and wrapped
            with pytest.raises(OpenAIServiceError) as exc_info:
                await client.generate_completion("Test prompt")
            
            # Verify the error message includes details
            assert "OpenAI API error" in str(exc_info.value)
            assert error_message in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self):
        """Test that unexpected errors are caught and wrapped in OpenAIServiceError.
        
        Validates: Requirements 3.4
        """
        # Mock an unexpected error
        error_message = "Unexpected internal error"
        mock_error = Exception(error_message)
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.side_effect = mock_error
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Verify error is caught and wrapped
            with pytest.raises(OpenAIServiceError) as exc_info:
                await client.generate_completion("Test prompt")
            
            # Verify the error message includes details
            assert "Unexpected error calling OpenAI API" in str(exc_info.value)
            assert error_message in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_custom_model_used_in_request(self):
        """Test that custom model is used in API requests.
        
        Validates: Requirements 3.1
        """
        # Custom model
        custom_model = "gpt-3.5-turbo"
        
        # Mock the OpenAI API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Response"
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.return_value = mock_response
            
            # Create client with custom model
            client = OpenAIClient(api_key="test-key", model=custom_model)
            
            # Call generate_completion
            await client.generate_completion("Test prompt")
            
            # Verify the custom model was used
            call_args = mock_client_instance.chat.completions.create.call_args[1]
            assert call_args["model"] == custom_model


# Property-Based Tests

def test_property_openai_error_handling():
    """Property test: For any OpenAI API error, OpenAIServiceError is raised with error details.
    
    Feature: brd-generator-backend, Property 6: OpenAI error handling
    
    This property test verifies that all types of OpenAI API errors are properly
    caught and wrapped in OpenAIServiceError with the original error details preserved.
    
    Validates: Requirements 3.4
    """
    from hypothesis import given, strategies as st, settings
    import asyncio
    
    # Define error types and their constructors
    error_types = [
        ("APIError", lambda msg: APIError(message=msg, request=Mock(), body=None)),
        ("RateLimitError", lambda msg: RateLimitError(message=msg, response=Mock(), body=None)),
        ("APIConnectionError", lambda msg: APIConnectionError(message=msg, request=Mock())),
        ("OpenAIError", lambda msg: OpenAIError(msg)),
        ("Exception", lambda msg: Exception(msg))
    ]
    
    @given(
        error_message=st.text(min_size=1, max_size=200),
        error_type_index=st.integers(min_value=0, max_value=len(error_types) - 1),
        prompt=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100)
    def property_test(error_message, error_type_index, prompt):
        """Test that any OpenAI error is properly wrapped."""
        error_type_name, error_constructor = error_types[error_type_index]
        mock_error = error_constructor(error_message)
        
        # Mock the OpenAI client
        with patch('app.services.openai_client.OpenAI') as mock_openai:
            mock_client_instance = Mock()
            mock_openai.return_value = mock_client_instance
            mock_client_instance.chat.completions.create.side_effect = mock_error
            
            # Create client
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            
            # Verify error is caught and wrapped (run async function synchronously)
            with pytest.raises(OpenAIServiceError) as exc_info:
                asyncio.run(client.generate_completion(prompt))
            
            # Verify the error message includes details
            error_str = str(exc_info.value)
            assert len(error_str) > 0, "Error message should not be empty"
            
            # For OpenAI errors, check for "OpenAI API error" prefix
            # For generic exceptions, check for "Unexpected error" prefix
            if error_type_name == "Exception":
                assert "Unexpected error calling OpenAI API" in error_str
            else:
                assert "OpenAI API error" in error_str
            
            # Verify original error message is preserved
            assert error_message in error_str
    
    # Run the property test
    property_test()
