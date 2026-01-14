"""
Test module for Pattern Detection
Tests for patterns.py functionality
"""

import pytest
import numpy as np
import pandas as pd
from backend.gex.patterns import PatternDetector, PatternType

class TestPatternDetector:
    """Test Pattern Detector functionality"""
    
    @pytest.fixture
    def detector(self):
        """Create pattern detector instance"""
        return PatternDetector()
    
    @pytest.fixture
    def sample_ohlc_data(self):
        """Create sample OHLC data"""
        data = {
            'open': [100, 101, 102, 103, 104, 105, 104, 103, 102, 101],
            'high': [102, 103, 104, 105, 106, 107, 106, 105, 104, 103],
            'low': [99, 100, 101, 102, 103, 104, 103, 102, 101, 100],
            'close': [101, 102, 103, 104, 105, 106, 105, 104, 103, 102],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1400, 1300, 1200, 1100]
        }
        return pd.DataFrame(data)
    
    def test_detector_initialization(self, detector):
        """Test detector initialization"""
        assert detector is not None
        assert detector.min_pattern_length == 2
        assert detector.max_pattern_length == 50
    
    def test_detect_patterns(self, detector, sample_ohlc_data):
        """Test pattern detection"""
        patterns = detector.detect_patterns(sample_ohlc_data)
        
        assert isinstance(patterns, list)
        # Should detect at least one pattern
        assert len(patterns) > 0
    
    def test_pattern_attributes(self, detector, sample_ohlc_data):
        """Test pattern object attributes"""
        patterns = detector.detect_patterns(sample_ohlc_data)
        
        if patterns:
            pattern = patterns[0]
            assert hasattr(pattern, 'type')
            assert hasattr(pattern, 'strength')
            assert hasattr(pattern, 'confidence')
            assert hasattr(pattern, 'description')
    
    def test_uptrend_detection(self, detector):
        """Test uptrend detection"""
        # Create uptrend data
        data = {
            'open': [100, 101, 102, 103, 104],
            'high': [102, 103, 104, 105, 106],
            'low': [99, 100, 101, 102, 103],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1000, 1000, 1000, 1000]
        }
        df = pd.DataFrame(data)
        
        patterns = detector.detect_patterns(df)
        
        # Should contain bullish patterns
        bullish_patterns = [p for p in patterns if 'BULLISH' in str(p.type)]
        assert len(bullish_patterns) > 0
    
    def test_downtrend_detection(self, detector):
        """Test downtrend detection"""
        # Create downtrend data
        data = {
            'open': [105, 104, 103, 102, 101],
            'high': [106, 105, 104, 103, 102],
            'low': [104, 103, 102, 101, 100],
            'close': [104, 103, 102, 101, 100],
            'volume': [1000, 1000, 1000, 1000, 1000]
        }
        df = pd.DataFrame(data)
        
        patterns = detector.detect_patterns(df)
        
        # Should contain bearish patterns
        bearish_patterns = [p for p in patterns if 'BEARISH' in str(p.type)]
        assert len(bearish_patterns) > 0
    
    def test_pattern_classification(self, detector, sample_ohlc_data):
        """Test pattern classification"""
        patterns = detector.detect_patterns(sample_ohlc_data)
        
        if patterns:
            pattern = patterns[0]
            classification = detector.classify_pattern(pattern)
            
            assert 'type' in classification
            assert 'strength' in classification
            assert 'confidence' in classification
            assert 'recommendation' in classification
    
    def test_confidence_bounds(self, detector, sample_ohlc_data):
        """Test that confidence is within valid bounds"""
        patterns = detector.detect_patterns(sample_ohlc_data)
        
        for pattern in patterns:
            assert 0.0 <= pattern.confidence <= 1.0
            assert 0.0 <= pattern.strength <= 100.0
    
    def test_empty_data_handling(self, detector):
        """Test handling of empty data"""
        empty_df = pd.DataFrame({
            'open': [], 'high': [], 'low': [], 'close': [], 'volume': []
        })
        
        patterns = detector.detect_patterns(empty_df)
        
        assert patterns == []

class TestPatternTypes:
    """Test different pattern types"""
    
    def test_pattern_type_enum(self):
        """Test pattern type enumeration"""
        assert PatternType.BULLISH.value == "bullish"
        assert PatternType.BEARISH.value == "bearish"
        assert PatternType.NEUTRAL.value == "neutral"
        assert PatternType.DIVERGENCE.value == "divergence"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
