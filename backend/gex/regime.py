"""
GEX Regime module for market regime analysis
Identifies market regimes and their characteristics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class RegimeType(Enum):
    """Market regime classifications"""
    BULL = "bull"
    BEAR = "bear"
    RANGING = "ranging"
    TRANSITION = "transition"

@dataclass
class Regime:
    """Represents a market regime"""
    type: RegimeType
    start_idx: int
    end_idx: int
    characteristics: Dict
    confidence: float

class RegimeAnalyzer:
    """Analyzes market regimes in data"""
    
    def __init__(self):
        self.window_size = 20
        self.min_regime_length = 5
    
    def analyze_regime(self, data: pd.DataFrame) -> List[Regime]:
        """
        Analyze market regimes
        
        Args:
            data: OHLC data
            
        Returns:
            List of identified regimes
        """
        regimes = []
        
        if len(data) < self.window_size:
            return regimes
        
        closes = data['close'].values
        volumes = data['volume'].values
        
        # Calculate indicators for regime analysis
        returns = np.diff(closes) / closes[:-1]
        volatility = self._calculate_volatility(closes)
        volume_ma = self._calculate_volume_ma(volumes)
        
        # Identify regime changes
        regimes = self._identify_regimes(
            closes, returns, volatility, volume_ma
        )
        
        return regimes
    
    def _calculate_volatility(self, closes: np.ndarray) -> np.ndarray:
        """Calculate rolling volatility"""
        returns = np.diff(closes) / closes[:-1]
        volatility = np.zeros(len(closes))
        
        for i in range(self.window_size, len(closes)):
            volatility[i] = np.std(returns[i-self.window_size:i])
        
        return volatility
    
    def _calculate_volume_ma(self, volumes: np.ndarray) -> np.ndarray:
        """Calculate moving average of volume"""
        volume_ma = np.zeros(len(volumes))
        
        for i in range(self.window_size, len(volumes)):
            volume_ma[i] = np.mean(volumes[i-self.window_size:i])
        
        return volume_ma
    
    def _identify_regimes(
        self,
        closes: np.ndarray,
        returns: np.ndarray,
        volatility: np.ndarray,
        volume_ma: np.ndarray
    ) -> List[Regime]:
        """Identify regime changes and characteristics"""
        regimes = []
        
        if len(closes) < self.window_size:
            return regimes
        
        current_regime = None
        regime_start = 0
        
        for i in range(self.window_size, len(closes)):
            # Calculate regime indicators
            recent_return = np.mean(returns[max(0, i-self.window_size):i])
            recent_volatility = volatility[i]
            recent_volume = volume_ma[i]
            
            # Determine regime type
            if recent_return > 0.001:
                new_regime = RegimeType.BULL
            elif recent_return < -0.001:
                new_regime = RegimeType.BEAR
            else:
                new_regime = RegimeType.RANGING
            
            # Check for regime change
            if current_regime != new_regime:
                if current_regime is not None:
                    # Save previous regime
                    regime = Regime(
                        type=current_regime,
                        start_idx=regime_start,
                        end_idx=i-1,
                        characteristics={
                            'avg_return': float(np.mean(returns[regime_start:i])),
                            'volatility': float(np.mean(volatility[regime_start:i])),
                            'avg_volume': float(np.mean(volume_ma[regime_start:i]))
                        },
                        confidence=self._calculate_confidence(
                            returns[regime_start:i], volatility[regime_start:i]
                        )
                    )
                    regimes.append(regime)
                
                current_regime = new_regime
                regime_start = i
        
        # Add final regime
        if current_regime is not None:
            regime = Regime(
                type=current_regime,
                start_idx=regime_start,
                end_idx=len(closes)-1,
                characteristics={
                    'avg_return': float(np.mean(returns[regime_start:])),
                    'volatility': float(np.mean(volatility[regime_start:])),
                    'avg_volume': float(np.mean(volume_ma[regime_start:]))
                },
                confidence=self._calculate_confidence(
                    returns[regime_start:], volatility[regime_start:]
                )
            )
            regimes.append(regime)
        
        return regimes
    
    def _calculate_confidence(
        self,
        returns: np.ndarray,
        volatility: np.ndarray
    ) -> float:
        """Calculate confidence in regime identification"""
        if len(returns) == 0:
            return 0.0
        
        # Higher confidence with lower volatility and consistent returns
        volatility_score = 1.0 - min(1.0, np.mean(volatility) * 10)
        consistency_score = abs(np.mean(returns)) / (np.std(returns) + 0.0001)
        
        confidence = (volatility_score + min(1.0, consistency_score)) / 2
        return float(min(1.0, max(0.0, confidence)))
