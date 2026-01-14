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
    Main analysis endpoint - NEW FORMAT
    Accepts: current_price, expiration_date, options (with ticker, tipo, strike, gamma, OI)
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_price = data.get('current_price')
        expiration_date = data.get('expiration_date')
        options = data.get('options', [])
        
        if not current_price or not expiration_date or not options:
            return jsonify({'error': 'Missing required fields: current_price, expiration_date, options'}), 400
        
        try:
            current_price = float(current_price)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid current_price value'}), 400
        
        if not options or not isinstance(options, list):
            return jsonify({'error': 'Options must be a non-empty list'}), 400
        
        # Initialize analyzers
        gex_calc = GexCalculator()
        pattern_detector = PatternDetector()
        strategy_engine = StrategyEngine()
        
        # Process options data
        calls = [opt for opt in options if opt.get('tipo', '').upper() in ['CALL', 'C']]
        puts = [opt for opt in options if opt.get('tipo', '').upper() in ['PUT', 'P']]
        
        # Calculate GEX analysis
        strikes_analysis = []
        total_gex = 0
        
        for option in options:
            try:
                strike = float(option.get('strike', 0))
                gamma = float(option.get('gamma', 0))
                oi = float(option.get('oi', 0))
                tipo = option.get('tipo', '').upper()
                
                # Calculate GEX for this option
                # GEX = Gamma * Open Interest * Strike
                gex_value = gamma * oi * strike
                
                # Adjust sign: CALL = positive, PUT = negative
                if tipo in ['PUT', 'P']:
                    gex_value = -gex_value
                
                strikes_analysis.append({
                    'ticker': option.get('ticker', 'N/A'),
                    'type': tipo,
                    'strike': strike,
                    'gamma': gamma,
                    'oi': oi,
                    'gex': gex_value
                })
                
                total_gex += gex_value
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid option data: {option}, error: {e}")
                continue
        
        if not strikes_analysis:
            return jsonify({'error': 'No valid options data found'}), 400
        
        # Determine regime based on GEX
        if total_gex > 0:
            regime = 'Positive Gamma'
        elif total_gex < 0:
            regime = 'Negative Gamma'
        else:
            regime = 'Neutral'
        
        # Detect patterns
        patterns = _detect_patterns(strikes_analysis, current_price)
        
        # Generate strategies
        strategies = _generate_strategies(
            strikes_analysis, 
            current_price, 
            total_gex, 
            regime,
            patterns
        )
        
        # Sort strikes
        strikes_analysis.sort(key=lambda x: x['strike'])
        
        # Prepare response
        response = {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'current_price': current_price,
            'expiration_date': expiration_date,
            'total_gex': total_gex,
            'regime': regime,
            'strikes': strikes_analysis,
            'patterns': patterns,
            'strategies': strategies,
            'summary': {
                'total_options': len(strikes_analysis),
                'calls': len(calls),
                'puts': len(puts),
                'call_gex': sum(s['gex'] for s in strikes_analysis if s['type'] in ['CALL', 'C']),
                'put_gex': sum(s['gex'] for s in strikes_analysis if s['type'] in ['PUT', 'P'])
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


def _detect_patterns(strikes, current_price):
    """
    Detect gamma patterns: walls, flips, pins
    """
    patterns = {
        'walls': [],
        'flips': [],
        'pins': []
    }
    
    try:
        # Sort by strike
        sorted_strikes = sorted(strikes, key=lambda x: x['strike'])
        
        # Detect walls (high concentration of gamma)
        gex_values = [s['gex'] for s in sorted_strikes]
        if gex_values:
            mean_gex = np.mean(gex_values)
            std_gex = np.std(gex_values)
            
            for strike in sorted_strikes:
                wall_strength = abs(strike['gex']) / (mean_gex + std_gex) if (mean_gex + std_gex) != 0 else 0
                if wall_strength > 2.5:  # Threshold for wall detection
                    patterns['walls'].append({
                        'strike': strike['strike'],
                        'type': strike['type'],
                        'strength': wall_strength,
                        'gex': strike['gex']
                    })
        
        # Detect flips (sign inversion between calls and puts)
        calls_gex = sum(s['gex'] for s in sorted_strikes if s['type'] in ['CALL', 'C'])
        puts_gex = sum(s['gex'] for s in sorted_strikes if s['type'] in ['PUT', 'P'])
        
        if calls_gex > 0 and puts_gex < 0:
            patterns['flips'].append({
                'type': 'Bearish Flip',
                'strength': abs(calls_gex + puts_gex) / (abs(calls_gex) + abs(puts_gex)) if (abs(calls_gex) + abs(puts_gex)) > 0 else 0,
                'call_gex': calls_gex,
                'put_gex': puts_gex
            })
        elif calls_gex < 0 and puts_gex > 0:
            patterns['flips'].append({
                'type': 'Bullish Flip',
                'strength': abs(calls_gex + puts_gex) / (abs(calls_gex) + abs(puts_gex)) if (abs(calls_gex) + abs(puts_gex)) > 0 else 0,
                'call_gex': calls_gex,
                'put_gex': puts_gex
            })
        
        # Detect pins (high OI concentration at single strike)
        max_oi_strike = max(strikes, key=lambda x: x['oi']) if strikes else None
        if max_oi_strike:
            total_oi = sum(s['oi'] for s in strikes)
            oi_ratio = max_oi_strike['oi'] / total_oi if total_oi > 0 else 0
            
            if oi_ratio > 0.2:  # 20% of total OI at single strike
                patterns['pins'].append({
                    'strike': max_oi_strike['strike'],
                    'oi': max_oi_strike['oi'],
                    'oi_ratio': oi_ratio,
                    'strength': oi_ratio
                })
    
    except Exception as e:
        logger.error(f"Pattern detection error: {e}")
    
    return patterns


def _generate_strategies(strikes, current_price, total_gex, regime, patterns):
    """
    Generate trading strategies based on analysis
    """
    strategies = []
    
    try:
        # Positive gamma strategy
        if total_gex > 0:
            strategies.append({
                'strategy_name': 'Positive Gamma Trade',
                'direction': 'LONG',
                'description': 'Price moving in favor - favorable for option sellers near market price',
                'confidence': min(0.95, abs(total_gex) / (abs(total_gex) + 1)),
                'entry_price': current_price,
                'target_price': current_price * 1.02,
                'stop_loss': current_price * 0.98
            })
        
        # Negative gamma strategy
        elif total_gex < 0:
            strategies.append({
                'strategy_name': 'Negative Gamma Trade',
                'direction': 'SHORT',
                'description': 'Price moving against positions - unfavorable for ATM option sellers',
                'confidence': min(0.95, abs(total_gex) / (abs(total_gex) + 1)),
                'entry_price': current_price,
                'target_price': current_price * 0.98,
                'stop_loss': current_price * 1.02
            })
        
        # Gamma wall strategy
        if patterns.get('walls'):
            for wall in patterns['walls']:
                direction = 'LONG' if wall['gex'] > 0 else 'SHORT'
                strategies.append({
                    'strategy_name': f'Gamma Wall at {wall["strike"]:.2f}',
                    'direction': direction,
                    'description': f'Strong gamma wall - expect support/resistance',
                    'confidence': min(wall['strength'] / 5, 1.0),
                    'entry_price': current_price,
                    'target_price': wall['strike'],
                    'stop_loss': current_price * (0.97 if direction == 'SHORT' else 1.03)
                })
        
        # Pin risk strategy
        if patterns.get('pins'):
            for pin in patterns['pins']:
                strategies.append({
                    'strategy_name': f'Pin Risk Alert at {pin["strike"]:.2f}',
                    'direction': 'NEUTRAL',
                    'description': f'High OI concentration - pin risk detected',
                    'confidence': min(pin['oi_ratio'], 1.0),
                    'entry_price': None,
                    'target_price': pin['strike'],
                    'stop_loss': None
                })
    
    except Exception as e:
        logger.error(f"Strategy generation error: {e}")
    
    return strategies


@api_blueprint.route('/examples', methods=['GET'])
def examples():
    """
    Get example data for testing
    Returns sample options data with predefined scenarios
    """
    try:
        examples_list = [
            {
                'scenario': 'Positive Gamma (Support)',
                'current_price': 100.0,
                'expiration_date': '2024-02-16',
                'description': 'Strong call gamma at support level',
                'options': [
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 98.0, 'gamma': 0.15, 'oi': 5000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 99.0, 'gamma': 0.25, 'oi': 8000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 100.0, 'gamma': 0.28, 'oi': 12000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 101.0, 'gamma': 0.18, 'oi': 6000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 98.0, 'gamma': 0.08, 'oi': 2000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 99.0, 'gamma': 0.12, 'oi': 3500},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 100.0, 'gamma': 0.15, 'oi': 4000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 101.0, 'gamma': 0.08, 'oi': 2000},
                ]
            },
            {
                'scenario': 'Negative Gamma (Breakdown)',
                'current_price': 100.0,
                'expiration_date': '2024-02-16',
                'description': 'Strong put gamma at resistance level',
                'options': [
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 98.0, 'gamma': 0.08, 'oi': 2000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 99.0, 'gamma': 0.12, 'oi': 3500},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 100.0, 'gamma': 0.15, 'oi': 4000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 101.0, 'gamma': 0.08, 'oi': 2000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 98.0, 'gamma': 0.15, 'oi': 5000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 99.0, 'gamma': 0.25, 'oi': 8000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 100.0, 'gamma': 0.28, 'oi': 12000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 101.0, 'gamma': 0.18, 'oi': 6000},
                ]
            },
            {
                'scenario': 'Gamma Wall',
                'current_price': 100.0,
                'expiration_date': '2024-02-16',
                'description': 'Concentrated gamma at single strike',
                'options': [
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 98.0, 'gamma': 0.05, 'oi': 1000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 99.0, 'gamma': 0.10, 'oi': 2500},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 100.0, 'gamma': 0.45, 'oi': 25000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 101.0, 'gamma': 0.10, 'oi': 2500},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 98.0, 'gamma': 0.05, 'oi': 1000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 99.0, 'gamma': 0.10, 'oi': 2500},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 100.0, 'gamma': 0.45, 'oi': 25000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 101.0, 'gamma': 0.10, 'oi': 2500},
                ]
            },
            {
                'scenario': 'Pin Risk',
                'current_price': 100.0,
                'expiration_date': '2024-02-16',
                'description': 'Extreme OI concentration at ATM',
                'options': [
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 98.0, 'gamma': 0.05, 'oi': 500},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 99.0, 'gamma': 0.08, 'oi': 1000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 100.0, 'gamma': 0.12, 'oi': 50000},
                    {'ticker': 'SPY', 'tipo': 'CALL', 'strike': 101.0, 'gamma': 0.08, 'oi': 1000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 98.0, 'gamma': 0.05, 'oi': 500},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 99.0, 'gamma': 0.08, 'oi': 1000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 100.0, 'gamma': 0.12, 'oi': 50000},
                    {'ticker': 'SPY', 'tipo': 'PUT', 'strike': 101.0, 'gamma': 0.08, 'oi': 1000},
                ]
            }
        ]
        
        return jsonify(examples_list), 200
        
    except Exception as e:
        logger.error(f"Error in examples endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@api_blueprint.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    }), 200

