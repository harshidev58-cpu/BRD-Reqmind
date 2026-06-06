"""Request models for the BRD Generator Backend API.

This module defines the Pydantic models for validating incoming API requests.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator


class Email(BaseModel):
    """Model for an email message.
    
    Represents an email message with subject, body, and optional metadata.
    
    Attributes:
        subject: Email subject line
        body: Email body content
        sender: Email sender address (optional)
        date: Email date (optional)
    """
    
    subject: str
    body: str
    sender: str = ""
    date: str = ""


class SlackMessage(BaseModel):
    """Model for a Slack message.
    
    Represents a Slack message with channel, user, and content information.
    
    Attributes:
        channel: Slack channel name (e.g., "#project-alpha")
        user: Username of the message sender
        text: Message content
        timestamp: Message timestamp (optional)
    """
    
    channel: str
    user: str
    text: str
    timestamp: str = ""


class Meeting(BaseModel):
    """Model for a meeting transcript.
    
    Represents a meeting with transcript, topic, and participant information.
    
    Attributes:
        transcript: Full meeting transcript text
        topic: Meeting topic or title (optional)
        speakers: List of speaker names (optional)
        timestamp: Meeting timestamp (optional)
    """
    
    transcript: str
    topic: str = ""
    speakers: List[str] = []
    timestamp: str = ""


class BRDRequest(BaseModel):
    """Request model for BRD generation.
    
    This model validates incoming requests to ensure they contain all required
    information for generating a Business Requirements Document.
    
    Attributes:
        projectName: Name of the project (required, non-empty)
        emailText: Optional email content about the project
        slackText: Optional Slack messages about the project
        meetingText: Optional meeting notes about the project
        
    Validation Rules:
        - projectName must be non-empty and not just whitespace
        - At least one of emailText, slackText, or meetingText must be provided
    """
    
    projectName: str = Field(..., min_length=1, description="Name of the project")
    emailText: Optional[str] = Field(None, description="Email content about the project")
    slackText: Optional[str] = Field(None, description="Slack messages about the project")
    meetingText: Optional[str] = Field(None, description="Meeting notes about the project")
    
    @field_validator('projectName')
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """Ensure project name is not just whitespace.
        
        Args:
            v: The project name value to validate
            
        Returns:
            str: The trimmed project name
            
        Raises:
            ValueError: If project name is empty or only whitespace
        """
        if not v or not v.strip():
            raise ValueError('projectName cannot be empty or whitespace')
        return v.strip()
    
    @model_validator(mode='after')
    def validate_at_least_one_source(self) -> 'BRDRequest':
        """Ensure at least one text source is provided.
        
        Validates that at least one of the optional text fields (emailText,
        slackText, meetingText) contains non-empty content.
        
        Returns:
            BRDRequest: The validated request instance
            
        Raises:
            ValueError: If all text sources are empty or None
        """
        sources = [self.emailText, self.slackText, self.meetingText]
        if not any(source and source.strip() for source in sources):
            raise ValueError('At least one of emailText, slackText, or meetingText must be provided')
        return self
