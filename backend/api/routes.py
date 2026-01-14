"""
API routes for GEX Analyzer
Flask blueprints for API endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import pandas as pd
import numpy as np

from backend.data.validator import DataValidator
from backend.gex.calculator import GexCalculator
from backend.gex.patterns import PatternDetector
from backend.gex.regime import RegimeAnalyzer
from backend.strategies.engine import StrategyEngine

logger = logging.getLogger(__name__)

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

@api_blueprint.route('/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint
    Accepts OHLC data and returns comprehensive analysis
    """
    try:
        data = request.get_json()
        
        if not data or 'ohlc_data' not in data:
            return jsonify({'error': 'No OHLC data provided'}), 400
        
        # Validate and process data
        ohlc_list = data.get('ohlc_data', [])
        if not ohlc_list:
            return jsonify({'error': 'Empty OHLC data'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlc_list)
        
        # Validate
        validator = DataValidator()
        is_valid, error_msg = validator.validate_ohlc_data(df)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        df = validator.clean_data(df)
        
        # Initialize analyzers
        gex_calc = GexCalculator()
        pattern_detector = PatternDetector()
        regime_analyzer = RegimeAnalyzer()
        strategy_engine = StrategyEngine()
        
        # Perform calculations
        # GEX Analysis
        strike_prices = data.get('strike_prices', [])
        gamma_values = data.get('gamma_values', [])
        open_interest = data.get('open_interest', [])
        
        gex_result = None
        if strike_prices and gamma_values and open_interest:
            current_price = float(df['close'].iloc[-1])
            gex_result = gex_calc.calculate_gex(
                current_price, strike_prices, gamma_values, open_interest
            )
        
        # Pattern Detection
        patterns = pattern_detector.detect_patterns(df)
        
        # Regime Analysis
        regimes = regime_analyzer.analyze_regime(df)
        
        # Strategy Signals
        gex_data = {
            'net_gex': gex_result.net_gex if gex_result else 0,
            'gex_long': gex_result.gex_long if gex_result else 0,
            'gex_short': gex_result.gex_short if gex_result else 0
        }
        signals = strategy_engine.generate_signals(df, gex_data, patterns, regimes)
        
        # Prepare response
        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'current_price': float(df['close'].iloc[-1]),
                'high_24h': float(df['high'].tail(24).max()),
                'low_24h': float(df['low'].tail(24).min()),
                'volume_24h': float(df['volume'].tail(24).sum())
            },
            'gex_analysis': {
                'gex_long': gex_result.gex_long if gex_result else 0,
                'gex_short': gex_result.gex_short if gex_result else 0,
                'net_gex': gex_result.net_gex if gex_result else 0,
                'interpretation': _interpret_gex(gex_result.net_gex) if gex_result else 'Neutral'
            },
            'patterns': [
                {
                    'type': p.type.value,
                    'strength': p.strength,
                    'confidence': p.confidence,
                    'description': p.description
                }
                for p in patterns[:5]
            ],
            'regimes': [
                {
                    'type': r.type.value,
                    'confidence': r.confidence,
                    'characteristics': r.characteristics
                }
                for r in regimes
            ],
            'signals': [
                {
                    'type': s.type.value,
                    'confidence': s.confidence,
                    'entry_price': s.entry_price,
                    'stop_loss': s.stop_loss,
                    'take_profit': s.take_profit,
                    'reason': s.reason
                }
                for s in signals[:5]
            ]
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/calculator', methods=['POST'])
def calculator():
    """Calculate GEX from options data"""
    try:
        data = request.get_json()
        
        spot_price = data.get('spot_price')
        strikes = data.get('strike_prices', [])
        gammas = data.get('gamma_values', [])
        oi = data.get('open_interest', [])
        
        if not spot_price or not strikes:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        calculator = GexCalculator()
        result = calculator.calculate_gex(spot_price, strikes, gammas, oi)
        
        return jsonify({
            'gex_long': result.gex_long,
            'gex_short': result.gex_short,
            'net_gex': result.net_gex,
            'analysis': calculator.analyze_gex_levels(result.gamma_exposure)
        })
    
    except Exception as e:
        logger.error(f"Error in calculator endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/patterns', methods=['POST'])
def patterns():
    """Detect patterns in market data"""
    try:
        data = request.get_json()
        ohlc_data = data.get('ohlc_data', [])
        
        if not ohlc_data:
            return jsonify({'error': 'No OHLC data provided'}), 400
        
        df = pd.DataFrame(ohlc_data)
        detector = PatternDetector()
        detected_patterns = detector.detect_patterns(df)
        
        return jsonify({
            'patterns': [
                {
                    'type': p.type.value,
                    'strength': p.strength,
                    'confidence': p.confidence,
                    'description': p.description,
                    'signals': p.signals
                }
                for p in detected_patterns
            ]
        })
    
    except Exception as e:
        logger.error(f"Error in patterns endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/regime', methods=['POST'])
def regime():
    """Analyze market regime"""
    try:
        data = request.get_json()
        ohlc_data = data.get('ohlc_data', [])
        
        if not ohlc_data:
            return jsonify({'error': 'No OHLC data provided'}), 400
        
        df = pd.DataFrame(ohlc_data)
        analyzer = RegimeAnalyzer()
        regimes = analyzer.analyze_regime(df)
        
        return jsonify({
            'regimes': [
                {
                    'type': r.type.value,
                    'confidence': r.confidence,
                    'characteristics': r.characteristics
                }
                for r in regimes
            ]
        })
    
    except Exception as e:
        logger.error(f"Error in regime endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/signals', methods=['POST'])
def signals():
    """Generate trading signals"""
    try:
        data = request.get_json()
        ohlc_data = data.get('ohlc_data', [])
        gex_data = data.get('gex_data', {})
        
        if not ohlc_data:
            return jsonify({'error': 'No OHLC data provided'}), 400
        
        df = pd.DataFrame(ohlc_data)
        engine = StrategyEngine()
        trade_signals = engine.generate_signals(df, gex_data)
        
        return jsonify({
            'signals': [
                {
                    'type': s.type.value,
                    'confidence': s.confidence,
                    'entry_price': s.entry_price,
                    'stop_loss': s.stop_loss,
                    'take_profit': s.take_profit,
                    'reason': s.reason
                }
                for s in trade_signals
            ]
        })
    
    except Exception as e:
        logger.error(f"Error in signals endpoint: {e}")
        return jsonify({'error': str(e)}), 500

def _interpret_gex(net_gex: float) -> str:
    """Interpret GEX value"""
    if net_gex > 0:
        return "Bullish (positive gamma)"
    elif net_gex < 0:
        return "Bearish (negative gamma)"
    else:
        return "Neutral"
