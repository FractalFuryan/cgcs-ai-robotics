"""
Tests for optimized Linear C validator
"""
import time
import pytest
from src.core.linear_c.optimized import OptimizedLinearCValidator, PerformanceMetrics
from src.core.linear_c.validator import ValidationLevel


class TestPerformanceMetrics:
    """Test performance metrics collection"""
    
    def test_metrics_initialization(self):
        """Test metrics collector initializes correctly"""
        metrics = PerformanceMetrics()
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert len(metrics.validation_times) == 0
    
    def test_add_validation_time(self):
        """Test adding validation times"""
        metrics = PerformanceMetrics()
        metrics.add_validation_time(1000000)  # 1ms
        metrics.add_validation_time(2000000)  # 2ms
        
        assert len(metrics.validation_times) == 2
    
    def test_cache_hit_recording(self):
        """Test cache hit recording"""
        metrics = PerformanceMetrics()
        metrics.record_cache_hit()
        metrics.record_cache_hit()
        
        assert metrics.cache_hits == 2
        assert metrics.cache_misses == 0
    
    def test_get_stats(self):
        """Test statistics calculation"""
        metrics = PerformanceMetrics()
        
        # Empty stats
        stats = metrics.get_stats()
        assert stats['total_validations'] == 0
        assert stats['avg_time_ns'] == 0
        
        # Add some data
        for i in range(100):
            metrics.add_validation_time(1000000 + i * 1000)
        
        stats = metrics.get_stats()
        assert stats['total_validations'] == 100
        assert stats['avg_time_ns'] > 0
        assert stats['p95_time_ns'] > stats['avg_time_ns']
    
    def test_cache_hit_rate(self):
        """Test cache hit rate calculation"""
        metrics = PerformanceMetrics()
        
        # Add some validation times (required for stats)
        for _ in range(10):
            metrics.add_validation_time(1000000)
        
        # 7 hits, 3 misses = 70% hit rate
        for _ in range(7):
            metrics.record_cache_hit()
        for _ in range(3):
            metrics.record_cache_miss()
        
        stats = metrics.get_stats()
        assert stats['cache_hit_rate'] == 0.7


class TestOptimizedValidator:
    """Test optimized Linear C validator"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return OptimizedLinearCValidator(max_workers=2, cache_size=100)
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly"""
        assert validator.max_workers == 2
        assert validator.metrics is not None
        assert validator.executor is not None
    
    def test_basic_validation(self, validator):
        """Test basic validation works"""
        # Test a valid pattern
        result = validator.validate("🔵🧠🚶", "autonomous_movement")
        assert result is not None
        assert hasattr(result, 'is_valid')
        
        # Test validation with prohibited pattern
        result2 = validator.validate("🟢🧠✖️🧍", "human_interaction")
        assert result2 is not None
    
    def test_validation_caching(self, validator):
        """Test validation results are cached"""
        linear_c = "🔵🧠🚶"
        
        # First validation (cache miss)
        result1 = validator.validate(linear_c, "autonomous_movement")
        
        # Second validation (cache hit)
        result2 = validator.validate(linear_c, "autonomous_movement")
        
        assert result1.is_valid == result2.is_valid
        assert result1.message == result2.message
        
        # Check cache was used
        stats = validator.get_performance_metrics()
        assert stats['cache_hits'] > 0
    
    def test_cache_different_contexts(self, validator):
        """Test cache distinguishes contexts"""
        linear_c = "🔵🧠🚶"
        
        # Same linear_c, different contexts
        result1 = validator.validate(linear_c, "autonomous_movement")
        result2 = validator.validate(linear_c, "human_interaction")
        
        # Results may differ based on context
        assert result1 is not None
        assert result2 is not None
    
    def test_batch_validation(self, validator):
        """Test batch validation"""
        linear_c_strings = [
            "🔵🧠🚶",
            "🟡🧠⚠️",
            "🛡️🔴⛔",
            "🟢🧠✖️🧍"
        ]
        
        results = validator.validate_batch(linear_c_strings)
        
        assert len(results) == 4
        for result in results:
            assert result is not None
            assert hasattr(result, 'is_valid')
    
    def test_batch_with_contexts(self, validator):
        """Test batch validation with contexts"""
        linear_c_strings = [
            "🔵🧠🚶",
            "🟢🧠✖️🧍"
        ]
        contexts = [
            "autonomous_movement",
            "human_interaction"
        ]
        
        results = validator.validate_batch(linear_c_strings, contexts)
        
        assert len(results) == 2
        assert results[0] is not None
        assert results[1] is not None
    
    def test_performance_metrics(self, validator):
        """Test performance metrics are recorded"""
        # Run some validations
        for _ in range(10):
            validator.validate("🔵🧠🚶", "autonomous_movement")
        
        metrics = validator.get_performance_metrics()
        
        assert metrics['total_validations'] > 0
        assert metrics['avg_time_ns'] > 0
        assert 'cache_hit_rate' in metrics
    
    def test_cache_clear(self, validator):
        """Test cache clearing"""
        # Populate cache
        validator.validate("🔵🧠🚶", "autonomous_movement")
        validator.validate("🟡🧠⚠️", None)
        
        # Get stats before clear
        stats_before = validator.get_performance_metrics()
        
        # Clear cache
        validator.clear_cache()
        
        # Validate again - should populate cache again
        validator.validate("🔵🧠🚶", "autonomous_movement")
        stats_after = validator.get_performance_metrics()
        
        # Total validations should have increased
        assert stats_after['total_validations'] >= stats_before['total_validations']
    
    @pytest.mark.benchmark
    def test_validation_performance(self, validator):
        """Test validation performance"""
        linear_c = "🔵🧠🚶"
        iterations = 1000
        
        start = time.perf_counter()
        for _ in range(iterations):
            validator.validate(linear_c, "autonomous_movement")
        elapsed = time.perf_counter() - start
        
        avg_time_ms = (elapsed / iterations) * 1000
        
        print(f"\nAverage validation time: {avg_time_ms:.3f} ms")
        
        # Should be fast due to caching
        assert avg_time_ms < 1.0  # Less than 1ms per validation
    
    @pytest.mark.benchmark
    def test_cache_effectiveness(self, validator):
        """Test cache effectiveness"""
        # Repeat same validations
        patterns = [
            "🔵🧠🚶",
            "🟡🧠⚠️",
            "🛡️🔴⛔"
        ]
        
        # Run multiple times to populate cache
        for _ in range(100):
            for pattern in patterns:
                validator.validate(pattern, None)
        
        metrics = validator.get_performance_metrics()
        
        # Cache hit rate should be high for repeated validations
        assert metrics['cache_hit_rate'] > 0.9  # >90% cache hits
        
        print(f"\nCache hit rate: {metrics['cache_hit_rate']:.1%}")
        print(f"Cache hits: {metrics['cache_hits']}")
        print(f"Cache misses: {metrics['cache_misses']}")


class TestCompilationOptimization:
    """Test pattern compilation optimization"""
    
    def test_patterns_are_compiled(self):
        """Test that patterns are pre-compiled"""
        validator = OptimizedLinearCValidator()
        
        # Check prohibited patterns
        for pattern_def in validator.patterns.prohibited_patterns:
            assert 'compiled' in pattern_def
            assert pattern_def['compiled'] is not None
        
        # Check required patterns
        for context, patterns in validator.patterns.required_patterns.items():
            for pattern_def in patterns:
                assert 'compiled' in pattern_def
                assert pattern_def['compiled'] is not None
    
    def test_compiled_pattern_matching(self):
        """Test compiled patterns work correctly"""
        validator = OptimizedLinearCValidator()
        
        # Test validation works with compiled patterns
        result = validator.validate("🔵🧠🚶", "autonomous_movement")
        assert result is not None
        assert hasattr(result, 'is_valid')


class TestThreadSafety:
    """Test thread safety of optimized validator"""
    
    @pytest.mark.slow
    def test_concurrent_validation(self):
        """Test concurrent validation is thread-safe"""
        import concurrent.futures
        
        validator = OptimizedLinearCValidator(max_workers=4)
        
        def validate_pattern(pattern):
            return validator.validate(pattern, None)
        
        patterns = ["🔵🧠🚶", "🟡🧠⚠️", "🛡️🔴⛔"] * 100
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(validate_pattern, patterns))
        
        assert len(results) == 300
        assert all(r is not None for r in results)
    
    @pytest.mark.slow
    def test_metrics_thread_safety(self):
        """Test metrics collection is thread-safe"""
        import concurrent.futures
        
        validator = OptimizedLinearCValidator(max_workers=4)
        
        def run_validations():
            for _ in range(100):
                validator.validate("🔵🧠🚶", "autonomous_movement")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_validations) for _ in range(5)]
            concurrent.futures.wait(futures)
        
        metrics = validator.get_performance_metrics()
        
        # Should have recorded all validations
        assert metrics['total_validations'] >= 500
