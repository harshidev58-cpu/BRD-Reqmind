"""Gemini Service for constraint generation from natural language instructions.

This module provides integration with Google's Gemini API to convert
natural language instructions into structured constraints for data filtering.
"""

import json
import logging
import asyncio
from typing import Optional
from google import generativeai as genai
from google.generativeai.types import GenerationConfig

from app.models.constraints import Constraints
from app.utils.exceptions import (
    GeminiAPIError,
    GeminiTimeoutError,
    GeminiRateLimitError,
    ConstraintValidationError
)

# Configure logging
logger = logging.getLogger(__name__)


class GeminiService:
    """Service for generating structured constraints from natural language.
    
    This service uses Google's Gemini API to convert user instructions
    into structured Constraints objects that can be used to filter and
    prioritize ingested data.
    
    Attributes:
        api_key: Google Gemini API key
        model_name: Gemini model to use (default: gemini-pro)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-pro",
        timeout: int = 10,
        max_retries: int = 2
    ):
        """Initialize the Gemini service.
        
        Args:
            api_key: Google Gemini API key for authentication
            model: Gemini model name to use (default: gemini-pro)
            timeout: Request timeout in seconds (default: 10)
            max_retries: Maximum retry attempts (default: 2)
            
        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        self.api_key = api_key
        self.model_name = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        logger.info(
            "GeminiService initialized",
            extra={
                'model': self.model_name,
                'timeout_seconds': self.timeout,
                'max_retries': self.max_retries
            }
        )
    
    async def generate_constraints(
        self,
        instructions: str,
        request_id: Optional[str] = None
    ) -> Optional[Constraints]:
        """Convert natural language instructions to structured constraints.
        
        This method sends instructions to the Gemini API and parses the
        response into a Constraints object. It implements retry logic with
        exponential backoff and comprehensive error handling.
        
        Args:
            instructions: Natural language instructions from user
            request_id: Optional request ID for logging and tracking
            
        Returns:
            Constraints object if successful, None if generation fails
            
        Raises:
            GeminiAPIError: If API call fails after all retries
            GeminiTimeoutError: If request exceeds timeout
            GeminiRateLimitError: If rate limit is exceeded
            ConstraintValidationError: If response validation fails
        """
        if not instructions or not instructions.strip():
            logger.warning(
                "Empty instructions provided, returning None",
                extra={'request_id': request_id or 'N/A'}
            )
            return None
        
        logger.info(
            "Generating constraints from instructions",
            extra={
                'request_id': request_id or 'N/A',
                'instructions_length': len(instructions),
                'instructions_preview': instructions[:100]
            }
        )
        
        # Retry loop with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                # Build prompt
                prompt = self._build_prompt(instructions)
                
                # Call Gemini API with timeout
                response_text = await self._call_gemini_api(prompt, request_id)
                
                # Parse and validate response
                constraints = self._parse_response(response_text, request_id)
                
                logger.info(
                    "Successfully generated constraints",
                    extra={
                        'request_id': request_id or 'N/A',
                        'scope_length': len(constraints.scope) if constraints.scope else 0,
                        'exclude_topics_count': len(constraints.exclude_topics),
                        'has_priority_focus': bool(constraints.priority_focus),
                        'has_deadline_override': bool(constraints.deadline_override)
                    }
                )
                
                return constraints
                
            except GeminiTimeoutError as e:
                logger.warning(
                    "Gemini API timeout",
                    extra={
                        'request_id': request_id or 'N/A',
                        'attempt': attempt + 1,
                        'max_attempts': self.max_retries + 1,
                        'error': str(e)
                    }
                )
                if attempt < self.max_retries:
                    # Exponential backoff: 1s, 2s
                    delay = 2 ** attempt
                    logger.info(
                        "Retrying Gemini API call",
                        extra={'request_id': request_id or 'N/A', 'delay_seconds': delay}
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "Gemini API timeout after all retries",
                        extra={
                            'request_id': request_id or 'N/A',
                            'total_attempts': self.max_retries + 1
                        }
                    )
                    return None
                    
            except GeminiRateLimitError as e:
                logger.warning(
                    "Gemini API rate limit exceeded",
                    extra={
                        'request_id': request_id or 'N/A',
                        'attempt': attempt + 1,
                        'max_attempts': self.max_retries + 1,
                        'error': str(e)
                    }
                )
                if attempt < self.max_retries:
                    # Exponential backoff: 1s, 2s
                    delay = 2 ** attempt
                    logger.info(
                        "Retrying Gemini API call after rate limit",
                        extra={'request_id': request_id or 'N/A', 'delay_seconds': delay}
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "Gemini API rate limit after all retries",
                        extra={
                            'request_id': request_id or 'N/A',
                            'total_attempts': self.max_retries + 1
                        }
                    )
                    return None
                    
            except GeminiAPIError as e:
                logger.error(
                    "Gemini API error",
                    extra={
                        'request_id': request_id or 'N/A',
                        'attempt': attempt + 1,
                        'max_attempts': self.max_retries + 1,
                        'error': str(e)
                    }
                )
                if attempt < self.max_retries:
                    # Exponential backoff: 1s, 2s
                    delay = 2 ** attempt
                    logger.info(
                        "Retrying Gemini API call after error",
                        extra={'request_id': request_id or 'N/A', 'delay_seconds': delay}
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "Gemini API error after all retries",
                        extra={
                            'request_id': request_id or 'N/A',
                            'total_attempts': self.max_retries + 1
                        }
                    )
                    return None
                    
            except ConstraintValidationError as e:
                logger.error(
                    "Constraint validation error",
                    extra={'request_id': request_id or 'N/A', 'error': str(e)}
                )
                return None
                
            except Exception as e:
                logger.error(
                    "Unexpected error during constraint generation",
                    extra={'request_id': request_id or 'N/A', 'error': str(e)},
                    exc_info=True
                )
                return None
        
        # Should not reach here, but return None as fallback
        return None
    
    def _build_prompt(self, instructions: str) -> str:
        """Build prompt for Gemini API.
        
        This method constructs a detailed prompt that instructs Gemini
        to convert natural language instructions into a structured JSON
        object matching the Constraints schema.
        
        Args:
            instructions: Natural language instructions from user
            
        Returns:
            Formatted prompt string for Gemini API
        """
        prompt = f"""You are a constraint extraction system. Convert the following user instructions into a JSON object with this exact structure:

{{
  "scope": "string describing the project scope",
  "exclude_topics": ["list", "of", "topics", "to", "exclude"],
  "priority_focus": "string describing what to prioritize",
  "deadline_override": "string with deadline if mentioned, empty otherwise"
}}

Rules:
- Extract the project scope from the instructions (e.g., "MVP features only", "Phase 1")
- Identify topics to exclude (e.g., "marketing", "internal discussions")
- Determine what should be prioritized (e.g., "core functionality", "mobile features")
- Extract any deadline information mentioned (e.g., "June 2024", "Q2")
- If a field is not mentioned in the instructions, use an empty string or empty list
- Return ONLY the JSON object, no additional text or explanation

User Instructions: {instructions}

JSON Response:"""
        
        return prompt
    
    async def _call_gemini_api(
        self,
        prompt: str,
        request_id: Optional[str] = None
    ) -> str:
        """Call Gemini API with timeout handling.
        
        Args:
            prompt: Prompt to send to Gemini
            request_id: Optional request ID for logging
            
        Returns:
            Response text from Gemini API
            
        Raises:
            GeminiTimeoutError: If request exceeds timeout
            GeminiRateLimitError: If rate limit is exceeded
            GeminiAPIError: If API call fails
        """
        log_prefix = f"[request_id={request_id}]" if request_id else ""
        
        try:
            # Create generation config for JSON output
            generation_config = GenerationConfig(
                temperature=0.1,  # Low temperature for consistent output
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
            )
            
            # Call Gemini API with timeout
            logger.debug(
                "Calling Gemini API",
                extra={'request_id': request_id or 'N/A'}
            )
            
            # Use asyncio.wait_for to enforce timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.model.generate_content,
                    prompt,
                    generation_config=generation_config
                ),
                timeout=self.timeout
            )
            
            # Check if response has text
            if not response or not response.text:
                raise GeminiAPIError("Empty response from Gemini API")
            
            logger.debug(
                "Gemini API response received",
                extra={
                    'request_id': request_id or 'N/A',
                    'response_length': len(response.text)
                }
            )
            
            return response.text
            
        except asyncio.TimeoutError as e:
            raise GeminiTimeoutError(
                f"Gemini API request exceeded timeout of {self.timeout}s"
            ) from e
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for rate limit errors
            if "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
                raise GeminiRateLimitError(f"Gemini API rate limit exceeded: {e}") from e
            
            # Check for authentication errors
            if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg:
                raise GeminiAPIError(f"Gemini API authentication failed: {e}") from e
            
            # Generic API error
            raise GeminiAPIError(f"Gemini API call failed: {e}") from e
    
    def _parse_response(
        self,
        response_text: str,
        request_id: Optional[str] = None
    ) -> Constraints:
        """Parse Gemini response into Constraints object.
        
        This method extracts JSON from the response text and validates
        it against the Constraints schema.
        
        Args:
            response_text: Response text from Gemini API
            request_id: Optional request ID for logging
            
        Returns:
            Validated Constraints object
            
        Raises:
            ConstraintValidationError: If parsing or validation fails
        """
        log_prefix = f"[request_id={request_id}]" if request_id else ""
        
        try:
            # Try to extract JSON from response
            # Gemini might include markdown code blocks or extra text
            json_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if json_text.startswith("```json"):
                json_text = json_text[7:]  # Remove ```json
            elif json_text.startswith("```"):
                json_text = json_text[3:]  # Remove ```
            
            if json_text.endswith("```"):
                json_text = json_text[:-3]  # Remove trailing ```
            
            json_text = json_text.strip()
            
            # Parse JSON
            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as e:
                raise ConstraintValidationError(
                    f"Failed to parse Gemini response as JSON: {e}"
                ) from e
            
            # Validate and convert to Constraints model
            try:
                constraints = Constraints(**data)
            except Exception as e:
                raise ConstraintValidationError(
                    f"Failed to validate constraints schema: {e}"
                ) from e
            
            logger.debug(
                "Successfully parsed constraints",
                extra={
                    'request_id': request_id or 'N/A',
                    'has_scope': bool(constraints.scope),
                    'exclude_topics_count': len(constraints.exclude_topics),
                    'has_priority_focus': bool(constraints.priority_focus),
                    'has_deadline_override': bool(constraints.deadline_override)
                }
            )
            
            return constraints
            
        except ConstraintValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            raise ConstraintValidationError(
                f"Unexpected error parsing Gemini response: {e}"
            ) from e
