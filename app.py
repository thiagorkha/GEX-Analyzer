"""
GEX Analyzer - Flask Application Entry Point
Main application for GEX technical analysis and trading strategy evaluation.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
from backend import config
from backend.api.routes import api_blueprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='frontend', static_folder='frontend')
CORS(app)

# Load configuration
app.config.from_object(config.Config)

# Register blueprints
app.register_blueprint(api_blueprint)

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    debug_mode = app.config.get('DEBUG', True)
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
