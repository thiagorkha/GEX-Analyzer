"""
Test module for GEX Calculator
Tests for calculator.py functionality
"""

import pytest
import numpy as np
import pandas as pd
from backend.gex.calculator import GexCalculator

class TestGexCalculator:
    """Test GEX Calculator functionality"""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator instance"""
        return GexCalculator()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return {
            'spot_price': 100.0,
            'strike_prices': [95, 100, 105, 110],
            'gamma_values': [0.01, 0.015, 0.012, 0.008],
            'open_interest': [1000, 5000, 4000, 1000]
        }
    
    def test_calculator_initialization(self, calculator):
        """Test calculator initialization"""
        assert calculator is not None
        assert calculator.volatility == 0.2
        assert calculator.risk_free_rate == 0.05
    
    def test_calculate_gex(self, calculator, sample_data):
        """Test GEX calculation"""
        result = calculator.calculate_gex(
            sample_data['spot_price'],
            sample_data['strike_prices'],
            sample_data['gamma_values'],
            sample_data['open_interest']
        )
        
        assert result is not None
        assert hasattr(result, 'gex_long')
        assert hasattr(result, 'gex_short')
        assert hasattr(result, 'net_gex')
        assert len(result.gamma_exposure) == len(sample_data['strike_prices'])
    
    def test_gamma_exposure_calculation(self, calculator, sample_data):
        """Test gamma exposure calculation"""
        result = calculator.calculate_gex(
            sample_data['spot_price'],
            sample_data['strike_prices'],
            sample_data['gamma_values'],
            sample_data['open_interest']
        )
        
        # Gamma exposure should be non-empty
        assert len(result.gamma_exposure) > 0
        
        # Should have same length as strikes
        assert len(result.gamma_exposure) == len(sample_data['strike_prices'])
    
    def test_empty_input(self, calculator):
        """Test with empty input"""
        result = calculator.calculate_gex(100, [], [], [])
        
        assert result.gex_long == 0.0
        assert result.gex_short == 0.0
        assert result.net_gex == 0.0
    
    def test_delta_calculation(self, calculator):
        """Test delta calculation"""
        delta = calculator.calculate_delta(
            strike=100,
            spot=100,
            time_to_expiry=1.0,
            volatility=0.2,
            option_type='call'
        )
        
        # Delta should be between 0 and 1 for call
        assert 0 <= delta <= 1
    
    def test_gamma_calculation(self, calculator):
        """Test gamma calculation"""
        gamma = calculator.calculate_gamma(
            strike=100,
            spot=100,
            time_to_expiry=1.0,
            volatility=0.2
        )
        
        # Gamma should be positive
        assert gamma > 0
    
    def test_gex_levels_analysis(self, calculator):
        """Test GEX levels analysis"""
        gex_values = [100, 200, 150, 300, 250, 180, 220]
        
        analysis = calculator.analyze_gex_levels(gex_values)
        
        assert 'mean' in analysis
        assert 'std' in analysis
        assert 'max' in analysis
        assert 'min' in analysis
        assert 'significant_barriers' in analysis
        
        # Verify calculations
        assert analysis['mean'] == np.mean(gex_values)
        assert analysis['max'] == max(gex_values)
        assert analysis['min'] == min(gex_values)

class TestBlackScholes:
    """Test Black-Scholes calculations"""
    
    @pytest.fixture
    def calculator(self):
        return GexCalculator()
    
    def test_bs_call_price(self, calculator):
        """Test Black-Scholes call price"""
        price = calculator._black_scholes_price(
            spot=100,
            strike=100,
            time=1.0,
            volatility=0.2,
            rate=0.05,
            option_type='call'
        )
        
        # Call price should be positive
        assert price > 0
        
        # ATM call should be approximately 10 (rule of thumb)
        assert 5 < price < 15
    
    def test_bs_put_price(self, calculator):
        """Test Black-Scholes put price"""
        price = calculator._black_scholes_price(
            spot=100,
            strike=100,
            time=1.0,
            volatility=0.2,
            rate=0.05,
            option_type='put'
        )
        
        # Put price should be positive
        assert price > 0
    
    def test_itm_call_vs_otm(self, calculator):
        """Test ITM vs OTM call pricing"""
        itm_call = calculator._black_scholes_price(
            spot=110,
            strike=100,
            time=1.0,
            volatility=0.2,
            rate=0.05,
            option_type='call'
        )
        
        otm_call = calculator._black_scholes_price(
            spot=90,
            strike=100,
            time=1.0,
            volatility=0.2,
            rate=0.05,
            option_type='call'
        )
        
        # ITM call should be more expensive than OTM
        assert itm_call > otm_call

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
