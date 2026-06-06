"""Unit tests for configuration management.

Tests configuration loading from environment variables, default values,
and validation of required settings.
"""

import pytest
from pydantic import ValidationError
from unittest.mock import patch
from app.config import Settings, get_settings


class TestSettings:
    """Test suite for Settings class."""
    
    def test_load_from_environment_variables(self, monkeypatch):
        """Test that settings are correctly loaded from environment variables.
        
        Validates: Requirements 6.1, 6.2, 6.4
        """
        # Set environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-123")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4-turbo")
        monkeypatch.setenv("PORT", "9000")
        
        # Clear the cache to force reload
        get_settings.cache_clear()
        
        # Load settings
        settings = Settings()
        
        # Verify all values are loaded correctly
        assert settings.openai_api_key == "test-api-key-123"
        assert settings.openai_model == "gpt-4-turbo"
        assert settings.port == 9000
    
    def test_default_values_for_optional_settings(self, monkeypatch):
        """Test that optional settings use default values when not provided.
        
        Validates: Requirements 6.2, 6.4
        """
        # Set only the required environment variable
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key-456")
        # Explicitly unset optional variables to test defaults
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        monkeypatch.delenv("PORT", raising=False)
        # Disable .env file loading for this test
        monkeypatch.setattr("pydantic_settings.BaseSettings.model_config", {"env_file": None})
        
        # Clear the cache to force reload
        get_settings.cache_clear()
        
        # Load settings with env_file disabled
        settings = Settings(_env_file=None)
        
        # Verify required field is set
        assert settings.openai_api_key == "test-api-key-456"
        
        # Verify optional fields use defaults
        assert settings.openai_model == "gpt-4"
        assert settings.port == 8000
    
    def test_startup_failure_when_api_key_missing(self, monkeypatch):
        """Test that application fails to start when OPENAI_API_KEY is missing.
        
        Validates: Requirements 6.1, 6.3
        """
        # Remove OPENAI_API_KEY from environment
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        # Clear the cache to force reload
        get_settings.cache_clear()
        
        # Attempt to load settings should raise ValidationError
        # Disable .env file loading to ensure we test the validation
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)
        
        # Verify the error is about the missing API key
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(
            error["loc"] == ("openai_api_key",) and error["type"] == "missing"
            for error in errors
        )
    
    def test_case_insensitive_environment_variables(self, monkeypatch):
        """Test that environment variables are case-insensitive.
        
        Validates: Requirements 6.1, 6.2
        """
        # Set environment variables with different cases
        monkeypatch.setenv("openai_api_key", "test-key-lowercase")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # Clear the cache to force reload
        get_settings.cache_clear()
        
        # Load settings
        settings = Settings()
        
        # Verify values are loaded correctly regardless of case
        assert settings.openai_api_key == "test-key-lowercase"
        assert settings.openai_model == "gpt-3.5-turbo"
    
    def test_port_type_validation(self, monkeypatch):
        """Test that port value is validated as an integer.
        
        Validates: Requirements 6.4
        """
        # Set valid environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        monkeypatch.setenv("PORT", "8080")
        
        # Clear the cache to force reload
        get_settings.cache_clear()
        
        # Load settings
        settings = Settings()
        
        # Verify port is an integer
        assert isinstance(settings.port, int)
        assert settings.port == 8080


class TestGetSettings:
    """Test suite for get_settings function."""
    
    def test_get_settings_returns_singleton(self, monkeypatch):
        """Test that get_settings returns the same instance on multiple calls.
        
        Validates: Requirements 6.1
        """
        # Set required environment variable
        monkeypatch.setenv("OPENAI_API_KEY", "test-singleton-key")
        
        # Clear the cache to start fresh
        get_settings.cache_clear()
        
        # Get settings multiple times
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Verify they are the same instance
        assert settings1 is settings2
    
    def test_get_settings_raises_on_missing_api_key(self, monkeypatch):
        """Test that get_settings raises ValidationError when API key is missing.
        
        Validates: Requirements 6.1, 6.3
        """
        # Remove OPENAI_API_KEY from environment
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        # Clear the cache to force reload
        get_settings.cache_clear()
        
        # Patch Settings to disable .env file loading
        with patch('app.config.Settings') as MockSettings:
            MockSettings.side_effect = lambda **kwargs: Settings(_env_file=None, **kwargs)
            
            # Attempt to get settings should raise ValidationError
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
            
            # Verify the error is about the missing API key
            errors = exc_info.value.errors()
            assert any(
                error["loc"] == ("openai_api_key",)
                for error in errors
            )
