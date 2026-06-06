"""Configuration management for the BRD Generator Backend API.

This module handles loading and validating configuration from environment variables.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    Attributes:
        openai_api_key: OpenAI API key for authentication (required)
        openai_model: OpenAI model to use for BRD generation (default: gpt-4)
        openai_base_url: Base URL for OpenAI-compatible API (optional, for Groq/other providers)
        port: Server port number (default: 8000)
        dataset_mode_enabled: Enable dataset-based ingestion (default: False)
        email_dataset_path: Path to email dataset file
        meeting_dataset_path: Path to meeting dataset directory
        max_dataset_emails: Maximum emails to load from dataset (default: 1000)
        max_dataset_meetings: Maximum meetings to load from dataset (default: 100)
        dataset_sample_size: Sample size for BRD generation (default: 50)
    """
    
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for authentication"
    )
    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use for BRD generation"
    )
    openai_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for OpenAI-compatible API (optional)"
    )
    port: int = Field(
        default=8000,
        description="Server port number"
    )
    
    # Dataset configuration
    dataset_mode_enabled: bool = Field(
        default=False,
        description="Enable dataset-based ingestion"
    )
    email_dataset_path: Optional[str] = Field(
        default=None,
        description="Path to email dataset CSV file"
    )
    meeting_dataset_path: Optional[str] = Field(
        default=None,
        description="Path to meeting dataset directory"
    )
    max_dataset_emails: int = Field(
        default=1000,
        description="Maximum emails to load from dataset"
    )
    max_dataset_meetings: int = Field(
        default=100,
        description="Maximum meetings to load from dataset"
    )
    dataset_sample_size: int = Field(
        default=50,
        description="Sample size for BRD generation from dataset"
    )
    
    # Gemini configuration
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for constraint generation"
    )
    gemini_model: str = Field(
        default="gemini-pro",
        description="Gemini model to use for constraint generation"
    )
    gemini_timeout: int = Field(
        default=10,
        description="Gemini API request timeout in seconds"
    )
    gemini_max_retries: int = Field(
        default=2,
        description="Maximum retries for Gemini API calls"
    )
    
    # Chunking configuration
    chunk_threshold_words: int = Field(
        default=3000,
        description="Word count threshold for text chunking"
    )
    chunk_size_min: int = Field(
        default=1000,
        description="Minimum chunk size in words"
    )
    chunk_size_max: int = Field(
        default=1500,
        description="Maximum chunk size in words"
    )
    chunk_overlap: int = Field(
        default=100,
        description="Overlap between chunks in words"
    )
    
    # Tracking configuration
    sample_sources_count: int = Field(
        default=5,
        description="Number of sample sources to include in ingestion summary"
    )
    tracking_session_ttl: int = Field(
        default=3600,
        description="Tracking session time-to-live in seconds (1 hour)"
    )
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """Get application settings singleton.
    
    This function uses lru_cache to ensure settings are loaded only once
    and reused across the application.
    
    Returns:
        Settings: Application settings instance
        
    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    return Settings()
