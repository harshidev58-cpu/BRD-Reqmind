"""Input validation utilities for security measures.

This module provides validation functions for user inputs to ensure
security and prevent malicious or invalid data from being processed.
"""

import re
from typing import Optional
from fastapi import HTTPException

from app.models.context_request import IngestionData


# Validation constants
MAX_INSTRUCTION_LENGTH = 2000
MAX_TEXT_LENGTH_PER_ITEM = 100000
MAX_TOTAL_ITEMS = 1000


def sanitize_instructions(instructions: Optional[str]) -> Optional[str]:
    """Sanitize instructions by removing control characters.
    
    Removes control characters (ASCII 0-31 except newline, tab, carriage return)
    and other potentially dangerous characters from the instructions string.
    
    Args:
        instructions: Raw instruction string from user
        
    Returns:
        Sanitized instruction string or None if input is None
    """
    if instructions is None:
        return None
    
    # Remove control characters except \n, \t, \r
    # Control characters are ASCII 0-31 and 127
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', instructions)
    
    return sanitized


def validate_instructions(instructions: Optional[str]) -> None:
    """Validate instructions length and content.
    
    Args:
        instructions: Instruction string to validate
        
    Raises:
        HTTPException: If validation fails (400 Bad Request)
    """
    if instructions is None:
        return
    
    if len(instructions) > MAX_INSTRUCTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Instructions exceed maximum length of {MAX_INSTRUCTION_LENGTH} characters"
        )


def validate_text_length(text: str, field_name: str) -> None:
    """Validate that a text field doesn't exceed maximum length.
    
    Args:
        text: Text content to validate
        field_name: Name of the field for error messages
        
    Raises:
        HTTPException: If text exceeds maximum length (400 Bad Request)
    """
    if len(text) > MAX_TEXT_LENGTH_PER_ITEM:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} exceeds maximum length of {MAX_TEXT_LENGTH_PER_ITEM} characters"
        )


def validate_data_sources(data: IngestionData) -> None:
    """Validate data source structure and limits.
    
    Validates:
    - Total number of items doesn't exceed maximum
    - Each text field doesn't exceed maximum length
    - Data structure is valid
    
    Args:
        data: IngestionData to validate
        
    Raises:
        HTTPException: If validation fails (400 Bad Request)
    """
    # Count total items
    total_items = len(data.emails) + len(data.slack_messages) + len(data.meetings)
    
    if total_items > MAX_TOTAL_ITEMS:
        raise HTTPException(
            status_code=400,
            detail=f"Total items ({total_items}) exceeds maximum of {MAX_TOTAL_ITEMS} per request"
        )
    
    # Validate email text lengths
    for idx, email in enumerate(data.emails):
        if email.subject:
            validate_text_length(email.subject, f"Email {idx + 1} subject")
        if email.body:
            validate_text_length(email.body, f"Email {idx + 1} body")
    
    # Validate Slack message text lengths
    for idx, slack_msg in enumerate(data.slack_messages):
        if slack_msg.text:
            validate_text_length(slack_msg.text, f"Slack message {idx + 1} text")
    
    # Validate meeting transcript lengths
    for idx, meeting in enumerate(data.meetings):
        if meeting.transcript:
            validate_text_length(meeting.transcript, f"Meeting {idx + 1} transcript")


def validate_context_request(instructions: Optional[str], data: IngestionData) -> tuple[Optional[str], IngestionData]:
    """Validate and sanitize a complete context request.
    
    This is the main validation function that should be called for all
    context requests. It performs all necessary validation and sanitization.
    
    Args:
        instructions: Optional user instructions
        data: Ingestion data to validate
        
    Returns:
        Tuple of (sanitized_instructions, validated_data)
        
    Raises:
        HTTPException: If any validation fails (400 Bad Request)
    """
    # Validate instructions
    validate_instructions(instructions)
    
    # Sanitize instructions
    sanitized_instructions = sanitize_instructions(instructions)
    
    # Validate data sources
    validate_data_sources(data)
    
    return sanitized_instructions, data
