"""Flask application factory and main application setup"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from config.logging import setup_logging


def create_app():
    """Create and configure the Flask application using the app factory pattern."""
    
    # Initialize Flask app
    app = Flask(__name__, template_folder='templates')
    app.secret_key = Config.SECRET_KEY
    
    # Set up logging
    logger = setup_logging(
        'orchestrator_status',
        log_level=Config.LOG_LEVEL,
        log_dir=Config.LOG_DIR,
        max_bytes=Config.LOG_MAX_BYTES,
        backup_count=Config.LOG_BACKUP_COUNT
    )
    
    # Store logger in app context for access by other modules
    app.logger_instance = logger
    
    # Configure CORS
    CORS(app, origins=Config.ALLOWED_ORIGINS)
    
    # Configure rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{Config.RATE_LIMIT_PER_MINUTE} per minute"]
    )
    limiter.init_app(app)
    
    # Security headers middleware
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    # Register blueprints
    from app.web.routes import web_bp
    from app.api.routes import api_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    logger.info("Flask application created successfully")
    return app


def get_logger():
    """Get the application logger instance."""
    from flask import current_app
    if hasattr(current_app, 'logger_instance'):
        return current_app.logger_instance
    else:
        # Fallback if called outside app context
        return setup_logging('orchestrator_status')