#!/usr/bin/env python3
"""
Backend client with improved error handling and resilience
Implements retry logic, circuit breaker pattern, and connection pooling
"""

import requests
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failures detected, stop making requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    Prevents cascading failures by stopping requests to failing services
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
        
        Returns:
            Function result
        
        Raises:
            Exception if circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful request"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


class BackendClient:
    """
    Enhanced backend client with retry logic and circuit breaker
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 10,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        allow_http_localhost: bool = True
    ):
        """
        Initialize backend client
        
        Args:
            base_url: Base URL for backend API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
            allow_http_localhost: Allow downgrading HTTPS to HTTP for localhost (default: True)
        """
        # Only downgrade HTTPS to HTTP for localhost if explicitly allowed
        if allow_http_localhost and base_url.startswith("https://localhost"):
            base_url = base_url.replace("https://", "http://", 1)
            logger.warning("Downgraded HTTPS to HTTP for localhost. Set allow_http_localhost=False to prevent this.")
        elif not base_url.startswith("http"):
            base_url = f"http://{base_url}"
        
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Create session for connection pooling
        self.session = requests.Session()
        
        # Circuit breaker for backend resilience
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=requests.exceptions.RequestException
        )
        
        # Cache for health check
        self._health_check_cache = None
        self._health_check_time = None
        self._health_check_ttl = 30  # seconds
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        retry: bool = True,
        **kwargs
    ) -> Dict:
        """
        Make HTTP request with retry logic and error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            retry: Whether to retry on failure
            **kwargs: Additional arguments for requests
        
        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        attempt = 0
        last_exception = None
        
        while attempt <= (self.max_retries if retry else 0):
            try:
                # Use circuit breaker to protect against cascading failures
                response = self.circuit_breaker.call(
                    self.session.request,
                    method,
                    url,
                    **kwargs
                )
                
                response.raise_for_status()
                
                # Return JSON if available
                if response.content:
                    return response.json()
                return {}
            
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
            
            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Timeout (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
            
            except requests.exceptions.HTTPError as e:
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    # Sanitize error message to avoid exposing sensitive information
                    status_code = e.response.status_code
                    error_map = {
                        400: "Solicitud inválida",
                        401: "No autorizado",
                        403: "Acceso denegado",
                        404: "Recurso no encontrado",
                        422: "Datos no válidos"
                    }
                    return {
                        "error": "client_error",
                        "status_code": status_code,
                        "message": error_map.get(status_code, "Error del cliente")
                    }
                last_exception = e
                logger.warning(f"HTTP error (attempt {attempt + 1}/{self.max_retries + 1}): {e}")
            
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error: {e}")
                return {"error": "unexpected_error", "message": str(e)}
            
            attempt += 1
            
            # Exponential backoff
            if attempt <= self.max_retries:
                delay = self.retry_delay * (2 ** (attempt - 1))
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        # All retries exhausted
        logger.error(f"Request failed after {self.max_retries + 1} attempts")
        return {
            "error": "max_retries_exceeded",
            "message": str(last_exception) if last_exception else "Unknown error"
        }
    
    def health_check(self, use_cache: bool = True) -> bool:
        """
        Check if backend is healthy
        
        Args:
            use_cache: Use cached health check result if available
        
        Returns:
            True if backend is healthy
        """
        # Check cache
        if use_cache and self._health_check_cache is not None:
            if self._health_check_time:
                age = (datetime.now() - self._health_check_time).total_seconds()
                if age < self._health_check_ttl:
                    return self._health_check_cache
        
        # Perform health check
        try:
            response = self._make_request("GET", "/health", retry=False)
            is_healthy = (
                response.get("status") == "ok" and
                "error" not in response
            )
            
            # Update cache
            self._health_check_cache = is_healthy
            self._health_check_time = datetime.now()
            
            return is_healthy
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._health_check_cache = False
            self._health_check_time = datetime.now()
            return False
    
    def get_fincas(self, filters: Dict = None) -> List[Dict]:
        """
        Get list of fincas with optional filters
        
        Args:
            filters: Optional filters (e.g., propietario_email)
        
        Returns:
            List of fincas
        """
        params = filters or {}
        response = self._make_request("GET", "/fincas", params=params)
        
        if "error" in response:
            logger.error(f"Failed to get fincas: {response}")
            return []
        
        return response if isinstance(response, list) else []
    
    def create_finca(self, finca_data: Dict) -> Optional[Dict]:
        """
        Create a new finca
        
        Args:
            finca_data: Finca data
        
        Returns:
            Created finca or None if failed
        """
        response = self._make_request("POST", "/fincas", json=finca_data)
        
        if "error" in response:
            logger.error(f"Failed to create finca: {response}")
            return None
        
        return response
    
    def close(self):
        """Close the session and release resources"""
        if self.session:
            self.session.close()


# Global client instance
_global_client = None


def get_backend_client() -> BackendClient:
    """
    Get global backend client instance (singleton pattern)
    
    Returns:
        BackendClient instance
    """
    global _global_client
    if _global_client is None:
        _global_client = BackendClient()
    return _global_client
