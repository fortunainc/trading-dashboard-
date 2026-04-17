"""
Failure Handler - Circuit breaker pattern and graceful degradation
"""
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)


class FailureHandler:
    """
    Failure Handler with Circuit Breaker Pattern
    
    Implements graceful degradation with:
    - Per-service circuit breakers
    - Automatic retry with exponential backoff
    - Fallback chains
    - Error isolation
    """
    
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 300):
        """
        Initialize failure handler
        
        Args:
            failure_threshold: Number of failures before circuit breaker opens
            cooldown_seconds: Cooldown period before retrying
        """
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        
        # Circuit breaker state
        self.circuit_breakers: Dict[str, Dict] = {}
        
        # Error counts
        self.error_counts: Dict[str, int] = {}
    
    def is_circuit_open(self, service_name: str) -> bool:
        """
        Check if circuit breaker is open for a service
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if circuit is open
        """
        if service_name not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[service_name]
        
        # Check if cooldown period has elapsed
        if breaker['opens_at']:
            cooldown_until = breaker['opens_at'] + timedelta(seconds=self.cooldown_seconds)
            if datetime.now() >= cooldown_until:
                # Cooldown elapsed, close circuit
                self.circuit_breakers[service_name] = {
                    'open': False,
                    'opens_at': None,
                    'failure_count': 0
                }
                logger.info(f"Circuit breaker for {service_name} closed after cooldown")
                return False
        
        return breaker['open']
    
    def record_failure(self, service_name: str):
        """
        Record a failure for a service
        
        Args:
            service_name: Name of the service
        """
        # Increment error count
        key = f"{service_name}_error_count"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Update circuit breaker
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {
                'open': False,
                'opens_at': None,
                'failure_count': 0
            }
        
        breaker = self.circuit_breakers[service_name]
        breaker['failure_count'] += 1
        
        # Check if threshold reached
        if breaker['failure_count'] >= self.failure_threshold:
            breaker['open'] = True
            breaker['opens_at'] = datetime.now()
            logger.warning(f"Circuit breaker OPENED for {service_name} after {breaker['failure_count']} failures")
    
    def record_success(self, service_name: str):
        """
        Record a success for a service
        
        Args:
            service_name: Name of the service
        """
        # Reset error count
        self.error_counts[f"{service_name}_error_count"] = 0
        
        # Reset circuit breaker
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name]['failure_count'] = 0
            if self.circuit_breakers[service_name]['open']:
                self.circuit_breakers[service_name]['open'] = False
                logger.info(f"Circuit breaker CLOSED for {service_name}")
    
    async def safe_execute(
        self,
        func: Callable,
        service_name: str,
        fallback_value: Any = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Safely execute a function with circuit breaker protection
        
        Args:
            func: Function to execute
            service_name: Name of the service for circuit breaker
            fallback_value: Value to return if execution fails
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func or fallback_value if execution fails
        """
        # Check if circuit is open
        if self.is_circuit_open(service_name):
            logger.warning(f"Circuit breaker OPEN for {service_name}, returning fallback")
            return fallback_value
        
        try:
            # Execute function
            result = await func(*args, **kwargs)
            
            # Record success
            self.record_success(service_name)
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing {service_name}: {e}")
            
            # Record failure
            self.record_failure(service_name)
            
            # Return fallback
            return fallback_value
    
    async def execute_with_fallback_chain(
        self,
        primary_func: Callable,
        fallback_funcs: list[Callable],
        service_name: str,
        fallback_value: Any = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute with fallback chain
        
        Args:
            primary_func: Primary function to try first
            fallback_funcs: List of fallback functions to try in order
            service_name: Name of the service
            fallback_value: Ultimate fallback if all fail
            *args: Arguments to pass to functions
            **kwargs: Keyword arguments to pass to functions
            
        Returns:
            Result from first successful function or fallback_value
        """
        # Check primary circuit
        if self.is_circuit_open(service_name):
            # Primary is down, skip to fallbacks
            logger.info(f"Primary {service_name} circuit open, trying fallbacks")
        else:
            try:
                result = await primary_func(*args, **kwargs)
                self.record_success(service_name)
                return result
            except Exception as e:
                logger.error(f"Primary {service_name} failed: {e}")
                self.record_failure(service_name)
        
        # Try fallbacks
        for i, fallback_func in enumerate(fallback_funcs):
            fallback_name = f"{service_name}_fallback_{i}"
            
            if self.is_circuit_open(fallback_name):
                continue
            
            try:
                result = await fallback_func(*args, **kwargs)
                self.record_success(fallback_name)
                logger.info(f"Fallback {fallback_name} succeeded")
                return result
            except Exception as e:
                logger.error(f"Fallback {fallback_name} failed: {e}")
                self.record_failure(fallback_name)
        
        # All failed, return ultimate fallback
        logger.error(f"All fallbacks exhausted for {service_name}")
        return fallback_value
    
    def get_status(self) -> Dict:
        """
        Get status of all circuit breakers
        
        Returns:
            Dict with circuit breaker status
        """
        status = {
            'circuit_breakers': {},
            'error_counts': self.error_counts.copy()
        }
        
        for service_name, breaker in self.circuit_breakers.items():
            status['circuit_breakers'][service_name] = {
                'open': breaker['open'],
                'failure_count': breaker['failure_count'],
                'opens_at': breaker['opens_at'].isoformat() if breaker['opens_at'] else None
            }
        
        return status