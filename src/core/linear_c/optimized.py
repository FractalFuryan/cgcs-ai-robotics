"""
Optimized Linear C Validator - Production Ready

Performance enhancements:
- LRU caching for repeated validations
- Compiled regex patterns
- Thread-safe performance metrics
- Batch validation support
"""
import re
import time
import threading
from functools import lru_cache
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import structlog

from .validator import LinearCValidator, ValidationResult, ValidationLevel
from .patterns import PatternLibrary

logger = structlog.get_logger(__name__)


class PerformanceMetrics:
    """Thread-safe performance metrics collector"""
    
    def __init__(self):
        self.lock = threading.RLock()
        self.validation_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.max_history = 10000
    
    def add_validation_time(self, time_ns: int):
        """Record validation time in nanoseconds"""
        with self.lock:
            self.validation_times.append(time_ns)
            if len(self.validation_times) > self.max_history:
                self.validation_times.pop(0)
    
    def record_cache_hit(self):
        """Record cache hit"""
        with self.lock:
            self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        with self.lock:
            self.cache_misses += 1
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        with self.lock:
            if not self.validation_times:
                return {
                    'total_validations': 0,
                    'avg_time_ns': 0,
                    'p95_time_ns': 0,
                    'max_time_ns': 0,
                    'cache_hit_rate': 0.0,
                    'throughput_per_sec': 0.0
                }
            
            times = sorted(self.validation_times)
            total = len(times)
            avg_time = sum(times) / total
            p95_idx = int(total * 0.95)
            p95_time = times[p95_idx] if p95_idx < total else times[-1]
            max_time = times[-1]
            
            cache_total = self.cache_hits + self.cache_misses
            hit_rate = self.cache_hits / max(1, cache_total)
            
            # Calculate throughput
            total_time_sec = sum(times) / 1e9
            throughput = total / max(total_time_sec, 1e-9)
            
            return {
                'total_validations': total,
                'avg_time_ns': int(avg_time),
                'p95_time_ns': int(p95_time),
                'max_time_ns': int(max_time),
                'cache_hit_rate': hit_rate,
                'throughput_per_sec': throughput,
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses
            }


class OptimizedLinearCValidator(LinearCValidator):
    """
    Production-optimized Linear C validator with caching and metrics
    """
    
    def __init__(self, max_workers: int = 4, cache_size: int = 10000):
        """
        Initialize optimized validator
        
        Args:
            max_workers: Number of worker threads for batch validation
            cache_size: LRU cache size for validation results
        """
        super().__init__()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.metrics = PerformanceMetrics()
        
        # Pre-compile patterns for faster matching
        self._compile_patterns()
        
        # Warm up cache with common patterns
        self._warmup_cache()
        
        logger.info(
            "OptimizedLinearCValidator initialized",
            max_workers=max_workers,
            cache_size=cache_size
        )
    
    def _compile_patterns(self):
        """Pre-compile all regex patterns"""
        # Compile prohibited patterns
        for pattern_def in self.patterns.prohibited_patterns:
            pattern_def['compiled'] = re.compile(pattern_def['pattern'])
        
        # Compile required patterns
        for context, patterns in self.patterns.required_patterns.items():
            for pattern_def in patterns:
                pattern_def['compiled'] = re.compile(pattern_def['pattern'])
        
        logger.debug("Patterns compiled for optimal performance")
    
    def _warmup_cache(self):
        """Warm up cache with common patterns"""
        common_patterns = [
            ("🟢🧠✖️🧍", "human_interaction"),
            ("🔵🧠🚶", "autonomous_movement"),
            ("🟡🧠⚠️", None),
            ("🛡️🔴⛔", None),
            ("🟢🧠✖️🌍", "environment_interaction"),
        ]
        
        for linear_c, context in common_patterns:
            self._validate_cached(linear_c, context)
        
        logger.debug("Cache warmed up with common patterns")
    
    @lru_cache(maxsize=10000)
    def _validate_cached(self, linear_c: str, context: Optional[str]) -> tuple:
        """
        Cached validation implementation
        
        Returns tuple: (is_valid, level, message, patterns_matched, time_ns)
        """
        start_time = time.perf_counter_ns()
        
        # Use parent class validation logic
        result = super().validate(linear_c, context)
        
        validation_time = time.perf_counter_ns() - start_time
        
        # Return tuple for caching (immutable)
        return (
            result.is_valid,
            result.level,
            result.rule_id,
            result.message,
            tuple(result.details.items()),
            validation_time
        )
    
    def validate(self, 
                linear_c: str, 
                context: Optional[str] = None,
                action_name: Optional[str] = None) -> ValidationResult:
        """
        Validate with caching and metrics
        
        Args:
            linear_c: Linear C emoji string
            context: Optional validation context
            action_name: Optional action name
        
        Returns:
            ValidationResult
        """
        # Check cache
        try:
            cached = self._validate_cached(linear_c, context)
            self.metrics.record_cache_hit()
            
            # Reconstruct ValidationResult from cached tuple
            validation_time = cached[5]
            result = ValidationResult(
                is_valid=cached[0],
                level=cached[1],
                rule_id=cached[2],
                message=cached[3],
                details=dict(cached[4]),
                linear_c=linear_c
            )
            
        except Exception as e:
            # Cache miss or error
            self.metrics.record_cache_miss()
            logger.warning("Validation cache miss", error=str(e))
            
            # Fall back to normal validation
            start_time = time.perf_counter_ns()
            result = super().validate(linear_c, context, action_name)
            validation_time = time.perf_counter_ns() - start_time
        
        # Record metrics
        self.metrics.add_validation_time(validation_time)
        
        return result
    
    def validate_batch(self, 
                      linear_c_strings: List[str],
                      contexts: Optional[List[str]] = None,
                      action_names: Optional[List[str]] = None) -> List[ValidationResult]:
        """
        Validate multiple Linear C strings in parallel
        
        Args:
            linear_c_strings: List of Linear C strings
            contexts: Optional list of contexts (one per string)
            action_names: Optional list of action names
        
        Returns:
            List of ValidationResults
        """
        if contexts is None:
            contexts = [None] * len(linear_c_strings)
        if action_names is None:
            action_names = [None] * len(linear_c_strings)
        
        # Submit all validations to thread pool
        futures = []
        for lc, ctx, action in zip(linear_c_strings, contexts, action_names):
            future = self.executor.submit(self.validate, lc, ctx, action)
            futures.append(future)
        
        # Collect results
        results = []
        for future in futures:
            try:
                result = future.result(timeout=1.0)
                results.append(result)
            except Exception as e:
                logger.error("Batch validation error", error=str(e))
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.BLOCK,
                    rule_id="ERROR",
                    message=f"Validation error: {str(e)}",
                    linear_c=""
                ))
        
        return results
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        return self.metrics.get_stats()
    
    def clear_cache(self):
        """Clear validation cache"""
        self._validate_cached.cache_clear()
        logger.info("Validation cache cleared")
    
    def __del__(self):
        """Cleanup executor on deletion"""
        try:
            self.executor.shutdown(wait=False)
        except:
            pass
