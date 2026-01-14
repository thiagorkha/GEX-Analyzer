"""
GEX Patterns module for technical analysis
Identifies and classifies GEX patterns in market data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """GEX pattern classifications"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    DIVERGENCE = "divergence"

@dataclass
class Pattern:
    """Represents a detected pattern"""
    type: PatternType
    strength: float  # 0-100
    confidence: float  # 0-1
    start_idx: int
    end_idx: int
    description: str
    signals: Dict

class PatternDetector:
    """Detects GEX patterns in market data"""
    
    def __init__(self):
        self.min_pattern_length = 2
        self.max_pattern_length = 50
    
    def detect_patterns(self, data: pd.DataFrame) -> List[Pattern]:
        """
        Detect all patterns in the data
        
        Args:
            data: OHLC data
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        if len(data) < self.min_pattern_length:
            return patterns
        
        # Detect various pattern types
        patterns.extend(self._detect_gex_resistance(data))
        patterns.extend(self._detect_gex_support(data))
        patterns.extend(self._detect_volatility_patterns(data))
        patterns.extend(self._detect_trend_patterns(data))
        
        return sorted(patterns, key=lambda p: p.confidence, reverse=True)
    
    def _detect_gex_resistance(self, data: pd.DataFrame) -> List[Pattern]:
        """Detect GEX resistance patterns"""
        patterns = []
        
        try:
            closes = data['close'].values
            highs = data['high'].values
            
            for i in range(self.min_pattern_length, len(closes)):
                # Look for resistance formation
                if i >= 5:
                    recent_high = np.max(highs[i-5:i])
                    if closes[i] > recent_high * 0.95:
                        strength = min(100, (closes[i] / recent_high - 1) * 100)
                        pattern = Pattern(
                            type=PatternType.BEARISH,
                            strength=strength,
                            confidence=min(1.0, strength / 100),
                            start_idx=max(0, i-5),
                            end_idx=i,
                            description="GEX Resistance Level",
                            signals={
                                'resistance_level': float(recent_high),
                                'current_price': float(closes[i])
                            }
                        )
                        patterns.append(pattern)
        except Exception as e:
            logger.error(f"Error detecting GEX resistance: {e}")
        
        return patterns
    
    def _detect_gex_support(self, data: pd.DataFrame) -> List[Pattern]:
        """Detect GEX support patterns"""
        patterns = []
        
        try:
            closes = data['close'].values
            lows = data['low'].values
            
            for i in range(self.min_pattern_length, len(closes)):
                # Look for support formation
                if i >= 5:
                    recent_low = np.min(lows[i-5:i])
                    if closes[i] < recent_low * 1.05:
                        strength = min(100, (1 - closes[i] / recent_low) * 100)
                        pattern = Pattern(
                            type=PatternType.BULLISH,
                            strength=strength,
                            confidence=min(1.0, strength / 100),
                            start_idx=max(0, i-5),
                            end_idx=i,
                            description="GEX Support Level",
                            signals={
                                'support_level': float(recent_low),
                                'current_price': float(closes[i])
                            }
                        )
                        patterns.append(pattern)
        except Exception as e:
            logger.error(f"Error detecting GEX support: {e}")
        
        return patterns
    
    def _detect_volatility_patterns(self, data: pd.DataFrame) -> List[Pattern]:
        """Detect volatility patterns"""
        patterns = []
        
        try:
            closes = data['close'].values
            if len(closes) < 10:
                return patterns
            
            # Calculate rolling volatility
            returns = np.diff(closes) / closes[:-1]
            volatility = np.std(returns[-10:])
            
            if volatility > np.std(returns) * 1.5:
                pattern = Pattern(
                    type=PatternType.NEUTRAL,
                    strength=min(100, volatility * 100),
                    confidence=0.7,
                    start_idx=max(0, len(closes) - 10),
                    end_idx=len(closes) - 1,
                    description="High Volatility Period",
                    signals={'volatility': float(volatility)}
                )
                patterns.append(pattern)
        except Exception as e:
            logger.error(f"Error detecting volatility patterns: {e}")
        
        return patterns
    
    def _detect_trend_patterns(self, data: pd.DataFrame) -> List[Pattern]:
        """Detect trend patterns"""
        patterns = []
        
        try:
            closes = data['close'].values
            if len(closes) < 5:
                return patterns
            
            # Detect uptrend
            if closes[-1] > closes[-5]:
                strength = ((closes[-1] / closes[-5] - 1) * 100)
                pattern = Pattern(
                    type=PatternType.BULLISH,
                    strength=min(100, strength),
                    confidence=0.6,
                    start_idx=len(closes) - 5,
                    end_idx=len(closes) - 1,
                    description="Uptrend",
                    signals={'trend': 'up', 'change_percent': float(strength)}
                )
                patterns.append(pattern)
            # Detect downtrend
            elif closes[-1] < closes[-5]:
                strength = ((closes[-5] / closes[-1] - 1) * 100)
                pattern = Pattern(
                    type=PatternType.BEARISH,
                    strength=min(100, strength),
                    confidence=0.6,
                    start_idx=len(closes) - 5,
                    end_idx=len(closes) - 1,
                    description="Downtrend",
                    signals={'trend': 'down', 'change_percent': float(strength)}
                )
                patterns.append(pattern)
        except Exception as e:
            logger.error(f"Error detecting trend patterns: {e}")
        
        return patterns
    
    def classify_pattern(self, pattern: Pattern) -> Dict:
        """
        Classify and provide analysis for a pattern
        
        Args:
            pattern: Pattern to classify
            
        Returns:
            Classification dictionary
        """
        return {
            'type': pattern.type.value,
            'strength': pattern.strength,
            'confidence': pattern.confidence,
            'description': pattern.description,
            'signals': pattern.signals,
            'recommendation': self._generate_recommendation(pattern)
        }
    
    def _generate_recommendation(self, pattern: Pattern) -> str:
        """Generate trading recommendation based on pattern"""
        if pattern.type == PatternType.BULLISH:
            if pattern.confidence > 0.8:
                return "STRONG BUY"
            else:
                return "BUY"
        elif pattern.type == PatternType.BEARISH:
            if pattern.confidence > 0.8:
                return "STRONG SELL"
            else:
                return "SELL"
        else:
            return "NEUTRAL"
