"""Dependency injection factories for service instances.

This module provides factory functions for creating service instances
with proper configuration. Uses lru_cache to ensure singleton behavior
for stateless services.
"""

from functools import lru_cache

from app.config import get_settings
from app.services.gemini_service import GeminiService
from app.services.chunk_processor import ChunkProcessor
from app.services.ingestion_tracker import IngestionTracker
from app.services.constraint_applier import ConstraintApplier
from app.services.aggregator import Aggregator


@lru_cache()
def get_gemini_service() -> GeminiService:
    """Get GeminiService singleton instance.
    
    Creates a GeminiService configured with settings from environment variables.
    Uses lru_cache to ensure only one instance is created.
    
    Returns:
        GeminiService: Configured Gemini service instance
    """
    settings = get_settings()
    return GeminiService(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        timeout=settings.gemini_timeout,
        max_retries=settings.gemini_max_retries
    )


@lru_cache()
def get_chunk_processor() -> ChunkProcessor:
    """Get ChunkProcessor singleton instance.
    
    Creates a ChunkProcessor configured with chunking settings from
    environment variables. Uses lru_cache to ensure only one instance
    is created.
    
    Returns:
        ChunkProcessor: Configured chunk processor instance
    """
    settings = get_settings()
    return ChunkProcessor(
        threshold_words=settings.chunk_threshold_words,
        chunk_size_min=settings.chunk_size_min,
        chunk_size_max=settings.chunk_size_max,
        overlap=settings.chunk_overlap
    )


@lru_cache()
def get_ingestion_tracker() -> IngestionTracker:
    """Get IngestionTracker singleton instance.
    
    Creates an IngestionTracker configured with tracking settings from
    environment variables. Uses lru_cache to ensure only one instance
    is created.
    
    Returns:
        IngestionTracker: Configured ingestion tracker instance
    """
    settings = get_settings()
    return IngestionTracker(
        sample_count=settings.sample_sources_count,
        session_ttl=settings.tracking_session_ttl
    )


@lru_cache()
def get_constraint_applier() -> ConstraintApplier:
    """Get ConstraintApplier singleton instance.
    
    Creates a ConstraintApplier instance. Uses lru_cache to ensure
    only one instance is created.
    
    Returns:
        ConstraintApplier: Constraint applier instance
    """
    return ConstraintApplier()


@lru_cache()
def get_aggregator() -> Aggregator:
    """Get Aggregator singleton instance.
    
    Creates an Aggregator instance. Uses lru_cache to ensure
    only one instance is created.
    
    Returns:
        Aggregator: Aggregator instance
    """
    return Aggregator()
