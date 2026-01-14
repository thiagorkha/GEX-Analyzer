"""
GEX Calculator module for technical indicators
Core analysis engine for GEX indicator calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CalculatorResult:
    """Result of GEX calculation"""
    gex_long: float
    gex_short: float
    net_gex: float
    strike_prices: List[float]
    gamma_exposure: List[float]
    data: Dict[str, Any]

class GexCalculator:
    """
    GEX (Gamma Exposure) Calculator
    Calculates gamma exposure from options data
    """
    
    def __init__(self):
        self.spot_price = None
        self.volatility = 0.2
        self.risk_free_rate = 0.05
        self.time_to_expiry = 1.0
    
    def calculate_gex(
        self,
        spot_price: float,
        strike_prices: List[float],
        gamma_values: List[float],
        open_interest: List[float]
    ) -> CalculatorResult:
        """
        Calculate GEX from options data
        
        Args:
            spot_price: Current spot price
            strike_prices: List of strike prices
            gamma_values: Gamma values per strike
            open_interest: Open interest per strike
            
        Returns:
            CalculatorResult with GEX calculations
        """
        self.spot_price = spot_price
        
        if not strike_prices or not gamma_values or not open_interest:
            return self._create_empty_result()
        
        # Calculate gamma exposure
        gamma_exposure = self._calculate_gamma_exposure(
            strike_prices, gamma_values, open_interest, spot_price
        )
        
        # Separate long and short gamma
        gex_long = sum(ge for ge in gamma_exposure if ge > 0)
        gex_short = abs(sum(ge for ge in gamma_exposure if ge < 0))
        net_gex = gex_long - gex_short
        
        result = CalculatorResult(
            gex_long=gex_long,
            gex_short=gex_short,
            net_gex=net_gex,
            strike_prices=strike_prices,
            gamma_exposure=gamma_exposure,
            data={
                'calculation_method': 'standard',
                'timestamp': pd.Timestamp.now().isoformat(),
                'spot_price': spot_price
            }
        )
        
        return result
    
    def _calculate_gamma_exposure(
        self,
        strike_prices: List[float],
        gamma_values: List[float],
        open_interest: List[float],
        spot_price: float
    ) -> List[float]:
        """
        Calculate gamma exposure for each strike
        
        Args:
            strike_prices: List of strike prices
            gamma_values: Gamma values
            open_interest: Open interest
            spot_price: Current spot price
            
        Returns:
            List of gamma exposures
        """
        gamma_exposure = []
        
        for i, strike in enumerate(strike_prices):
            if i >= len(gamma_values) or i >= len(open_interest):
                continue
            
            gamma = gamma_values[i]
            oi = open_interest[i]
            
            # Adjust for distance from spot
            distance_factor = abs(strike - spot_price) / spot_price if spot_price != 0 else 1
            weight = 1.0 / (1.0 + distance_factor)
            
            # Calculate exposure
            exposure = gamma * oi * weight
            gamma_exposure.append(exposure)
        
        return gamma_exposure
    
    def calculate_implied_volatility(
        self,
        option_price: float,
        strike: float,
        spot: float,
        time_to_expiry: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson method
        
        Args:
            option_price: Market price of option
            strike: Strike price
            spot: Spot price
            time_to_expiry: Time to expiry in years
            option_type: 'call' or 'put'
            
        Returns:
            Implied volatility estimate
        """
        try:
            from scipy.optimize import newton
            
            def objective(vol):
                return self._black_scholes_price(
                    spot, strike, time_to_expiry, vol, self.risk_free_rate, option_type
                ) - option_price
            
            # Initial guess
            iv = newton(objective, 0.2, maxiter=100)
            return max(0.001, min(2.0, iv))
        except Exception as e:
            logger.error(f"Error calculating IV: {e}")
            return 0.2
    
    def _black_scholes_price(
        self,
        spot: float,
        strike: float,
        time: float,
        volatility: float,
        rate: float,
        option_type: str = 'call'
    ) -> float:
        """
        Calculate Black-Scholes option price
        
        Args:
            spot: Spot price
            strike: Strike price
            time: Time to expiry
            volatility: Volatility
            rate: Risk-free rate
            option_type: 'call' or 'put'
            
        Returns:
            Option price
        """
        from scipy.stats import norm
        
        if time <= 0 or volatility <= 0:
            return 0.0
        
        d1 = (
            (np.log(spot / strike) + (rate + 0.5 * volatility**2) * time) /
            (volatility * np.sqrt(time))
        )
        d2 = d1 - volatility * np.sqrt(time)
        
        if option_type.lower() == 'call':
            return spot * norm.cdf(d1) - strike * np.exp(-rate * time) * norm.cdf(d2)
        else:
            return strike * np.exp(-rate * time) * norm.cdf(-d2) - spot * norm.cdf(-d1)
    
    def calculate_delta(
        self,
        strike: float,
        spot: float,
        time_to_expiry: float,
        volatility: float,
        option_type: str = 'call'
    ) -> float:
        """Calculate option delta"""
        from scipy.stats import norm
        
        d1 = (
            (np.log(spot / strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) /
            (volatility * np.sqrt(time_to_expiry) + 1e-10)
        )
        
        if option_type.lower() == 'call':
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1
    
    def calculate_gamma(
        self,
        strike: float,
        spot: float,
        time_to_expiry: float,
        volatility: float
    ) -> float:
        """Calculate option gamma"""
        from scipy.stats import norm
        
        d1 = (
            (np.log(spot / strike) + (self.risk_free_rate + 0.5 * volatility**2) * time_to_expiry) /
            (volatility * np.sqrt(time_to_expiry) + 1e-10)
        )
        
        return norm.pdf(d1) / (spot * volatility * np.sqrt(time_to_expiry) + 1e-10)
    
    def _create_empty_result(self) -> CalculatorResult:
        """Create empty result for invalid inputs"""
        return CalculatorResult(
            gex_long=0.0,
            gex_short=0.0,
            net_gex=0.0,
            strike_prices=[],
            gamma_exposure=[],
            data={'error': 'Invalid input data'}
        )
    
    def analyze_gex_levels(
        self,
        gex_values: List[float],
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Analyze GEX levels for significant barriers
        
        Args:
            gex_values: List of GEX values
            threshold: Threshold for significance
            
        Returns:
            Analysis dictionary
        """
        if not gex_values:
            return {}
        
        gex_array = np.array(gex_values)
        mean = np.mean(gex_array)
        std = np.std(gex_array)
        
        return {
            'mean': float(mean),
            'std': float(std),
            'max': float(np.max(gex_array)),
            'min': float(np.min(gex_array)),
            'percentile_75': float(np.percentile(gex_array, 75)),
            'percentile_25': float(np.percentile(gex_array, 25)),
            'significant_barriers': int(np.sum(np.abs(gex_array) > threshold))
        }
