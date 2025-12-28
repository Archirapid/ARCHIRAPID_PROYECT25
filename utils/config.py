#!/usr/bin/env python3
"""
Configuration management for ARCHIRAPID
Centralizes all configuration settings
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class BackendConfig:
    """Backend API configuration"""
    url: str = "http://localhost:8000"
    timeout: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0
    health_check_ttl: int = 30
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls(
            url=os.getenv("BACKEND_URL", "http://localhost:8000"),
            timeout=int(os.getenv("BACKEND_TIMEOUT", "10")),
            max_retries=int(os.getenv("BACKEND_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("BACKEND_RETRY_DELAY", "1.0")),
            health_check_ttl=int(os.getenv("BACKEND_HEALTH_CHECK_TTL", "30"))
        )


@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes
    max_size: int = 100
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
            max_size=int(os.getenv("CACHE_MAX_SIZE", "100"))
        )


@dataclass
class SecurityConfig:
    """Security configuration"""
    allowed_url_schemes: list = None
    max_file_size_mb: int = 10
    allowed_file_extensions: list = None
    sanitize_html: bool = True
    
    def __post_init__(self):
        if self.allowed_url_schemes is None:
            self.allowed_url_schemes = ['http', 'https', 'data']
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.pdf']
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls(
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "10")),
            sanitize_html=os.getenv("SANITIZE_HTML", "true").lower() == "true"
        )


@dataclass
class UIConfig:
    """UI/UX configuration"""
    items_per_page: int = 10
    map_zoom_default: int = 6
    map_center_lat: float = 40.4168
    map_center_lng: float = -3.7038
    image_placeholder_url: str = "https://via.placeholder.com/320x240?text=No+Photo"
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls(
            items_per_page=int(os.getenv("UI_ITEMS_PER_PAGE", "10")),
            map_zoom_default=int(os.getenv("UI_MAP_ZOOM_DEFAULT", "6")),
            map_center_lat=float(os.getenv("UI_MAP_CENTER_LAT", "40.4168")),
            map_center_lng=float(os.getenv("UI_MAP_CENTER_LNG", "-3.7038")),
            image_placeholder_url=os.getenv(
                "UI_IMAGE_PLACEHOLDER_URL",
                "https://via.placeholder.com/320x240?text=No+Photo"
            )
        )


@dataclass
class AppConfig:
    """Main application configuration"""
    backend: BackendConfig
    cache: CacheConfig
    security: SecurityConfig
    ui: UIConfig
    debug: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls(
            backend=BackendConfig.from_env(),
            cache=CacheConfig.from_env(),
            security=SecurityConfig.from_env(),
            ui=UIConfig.from_env(),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper()
        )


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get global configuration instance (singleton pattern)
    
    Returns:
        AppConfig instance
    """
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def reset_config():
    """Reset configuration (useful for testing)"""
    global _config
    _config = None
