"""
Trading strategy engine for GEX-based strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PositionType(Enum):
    """Position types"""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"

@dataclass
class TradeSignal:
    """Represents a trading signal"""
    type: PositionType
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    reason: str
    timestamp: str

class StrategyEngine:
    """
    Trading strategy engine
    Evaluates trading strategies based on GEX and technical analysis
    """
    
    def __init__(self):
        self.risk_reward_ratio = 2.0
        self.max_position_size = 0.1  # 10% of capital
        self.min_confidence = 0.6
    
    def generate_signals(
        self,
        data: pd.DataFrame,
        gex_data: Dict[str, Any],
        patterns: List[Any] = None,
        regimes: List[Any] = None
    ) -> List[TradeSignal]:
        """
        Generate trading signals from analysis
        
        Args:
            data: OHLC data
            gex_data: GEX analysis results
            patterns: Pattern analysis results
            regimes: Regime analysis results
            
        Returns:
            List of trading signals
        """
        signals = []
        
        if data.empty:
            return signals
        
        # Get current price and levels
        current_price = data['close'].iloc[-1]
        
        # Evaluate based on GEX
        gex_signals = self._evaluate_gex(gex_data, current_price)
        signals.extend(gex_signals)
        
        # Evaluate based on patterns
        if patterns:
            pattern_signals = self._evaluate_patterns(patterns, current_price)
            signals.extend(pattern_signals)
        
        # Evaluate based on regimes
        if regimes:
            regime_signals = self._evaluate_regimes(regimes, current_price)
            signals.extend(regime_signals)
        
        # Filter and rank signals
        signals = [s for s in signals if s.confidence >= self.min_confidence]
        signals = sorted(signals, key=lambda s: s.confidence, reverse=True)
        
        return signals
    
    def _evaluate_gex(
        self,
        gex_data: Dict[str, Any],
        current_price: float
    ) -> List[TradeSignal]:
        """Evaluate signals from GEX data"""
        signals = []
        
        try:
            net_gex = gex_data.get('net_gex', 0)
            gex_long = gex_data.get('gex_long', 0)
            gex_short = gex_data.get('gex_short', 0)
            
            # Strong positive GEX = bullish
            if net_gex > 0:
                confidence = min(1.0, gex_long / (gex_short + 1e-10))
                if confidence > 0.6:
                    stop_loss = current_price * 0.98
                    take_profit = current_price * (1 + 0.02 * self.risk_reward_ratio)
                    
                    signal = TradeSignal(
                        type=PositionType.LONG,
                        confidence=confidence,
                        entry_price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        reason="Positive GEX (bullish gamma)",
                        timestamp=datetime.utcnow().isoformat()
                    )
                    signals.append(signal)
            
            # Strong negative GEX = bearish
            elif net_gex < 0:
                confidence = min(1.0, gex_short / (gex_long + 1e-10))
                if confidence > 0.6:
                    stop_loss = current_price * 1.02
                    take_profit = current_price * (1 - 0.02 * self.risk_reward_ratio)
                    
                    signal = TradeSignal(
                        type=PositionType.SHORT,
                        confidence=confidence,
                        entry_price=current_price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        reason="Negative GEX (bearish gamma)",
                        timestamp=datetime.utcnow().isoformat()
                    )
                    signals.append(signal)
        except Exception as e:
            logger.error(f"Error evaluating GEX: {e}")
        
        return signals
    
    def _evaluate_patterns(
        self,
        patterns: List[Any],
        current_price: float
    ) -> List[TradeSignal]:
        """Evaluate signals from patterns"""
        signals = []
        
        try:
            for pattern in patterns[:3]:  # Use top 3 patterns
                pattern_type = getattr(pattern, 'type', None)
                confidence = getattr(pattern, 'confidence', 0)
                
                if pattern_type and confidence > 0.6:
                    if 'bullish' in str(pattern_type).lower():
                        stop_loss = current_price * 0.97
                        take_profit = current_price * (1 + 0.03 * self.risk_reward_ratio)
                        
                        signal = TradeSignal(
                            type=PositionType.LONG,
                            confidence=confidence,
                            entry_price=current_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            reason=f"Pattern: {getattr(pattern, 'description', 'Bullish')}",
                            timestamp=datetime.utcnow().isoformat()
                        )
                        signals.append(signal)
                    elif 'bearish' in str(pattern_type).lower():
                        stop_loss = current_price * 1.03
                        take_profit = current_price * (1 - 0.03 * self.risk_reward_ratio)
                        
                        signal = TradeSignal(
                            type=PositionType.SHORT,
                            confidence=confidence,
                            entry_price=current_price,
                            stop_loss=stop_loss,
                            take_profit=take_profit,
                            reason=f"Pattern: {getattr(pattern, 'description', 'Bearish')}",
                            timestamp=datetime.utcnow().isoformat()
                        )
                        signals.append(signal)
        except Exception as e:
            logger.error(f"Error evaluating patterns: {e}")
        
        return signals
    
    def _evaluate_regimes(
        self,
        regimes: List[Any],
        current_price: float
    ) -> List[TradeSignal]:
        """Evaluate signals from regimes"""
        signals = []
        
        try:
            if regimes:
                current_regime = regimes[-1]
                regime_type = getattr(current_regime, 'type', None)
                confidence = getattr(current_regime, 'confidence', 0.5)
                
                if regime_type:
                    regime_str = str(regime_type).lower()
                    if 'bull' in regime_str and confidence > 0.5:
                        signal = TradeSignal(
                            type=PositionType.LONG,
                            confidence=confidence * 0.8,
                            entry_price=current_price,
                            stop_loss=current_price * 0.96,
                            take_profit=current_price * 1.05,
                            reason="Bull market regime",
                            timestamp=datetime.utcnow().isoformat()
                        )
                        signals.append(signal)
                    elif 'bear' in regime_str and confidence > 0.5:
                        signal = TradeSignal(
                            type=PositionType.SHORT,
                            confidence=confidence * 0.8,
                            entry_price=current_price,
                            stop_loss=current_price * 1.04,
                            take_profit=current_price * 0.95,
                            reason="Bear market regime",
                            timestamp=datetime.utcnow().isoformat()
                        )
                        signals.append(signal)
        except Exception as e:
            logger.error(f"Error evaluating regimes: {e}")
        
        return signals
    
    def backtest_strategy(
        self,
        data: pd.DataFrame,
        signals: List[TradeSignal]
    ) -> Dict[str, Any]:
        """
        Backtest strategy performance
        
        Args:
            data: Historical OHLC data
            signals: Trading signals
            
        Returns:
            Backtest results
        """
        if data.empty or not signals:
            return {'error': 'No data or signals'}
        
        results = {
            'total_trades': len(signals),
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'avg_return': 0.0,
            'total_return': 0.0
        }
        
        try:
            closes = data['close'].values
            
            total_return = 0
            for signal in signals:
                if signal.entry_price <= 0:
                    continue
                
                # Simulate trade
                if signal.type == PositionType.LONG:
                    price_change = (signal.take_profit - signal.entry_price) / signal.entry_price
                else:
                    price_change = (signal.entry_price - signal.take_profit) / signal.entry_price
                
                if price_change > 0:
                    results['wins'] += 1
                else:
                    results['losses'] += 1
                
                total_return += price_change
            
            total_trades = results['wins'] + results['losses']
            if total_trades > 0:
                results['win_rate'] = results['wins'] / total_trades
                results['avg_return'] = total_return / total_trades
                results['total_return'] = total_return
        except Exception as e:
            logger.error(f"Error backtesting strategy: {e}")
        
        return results
