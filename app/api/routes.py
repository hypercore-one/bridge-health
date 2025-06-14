"""API routes for the orchestrator status application"""

from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request, abort
from flask_limiter.util import get_remote_address

from config.settings import Config
from app.services.status_service import StatusService
from app.main import get_logger

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Initialize status service
status_service = StatusService()


def require_api_key(f):
    """Decorator to require API key authentication for external requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if this is an internal request (from the web UI)
        referer = request.headers.get('Referer', '')
        user_agent = request.headers.get('User-Agent', '')
        
        # If it's not from a browser (no referer), require API key
        is_browser_request = referer and ('localhost' in referer or '127.0.0.1' in referer) and 'Mozilla' in user_agent
        
        if not is_browser_request:
            # Require API key for external requests
            if Config.API_KEYS:
                api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
                if not api_key or api_key not in Config.API_KEYS:
                    logger = get_logger()
                    logger.warning(f"Unauthorized API access attempt from {get_remote_address()} with key: {api_key[:8] + '...' if api_key else 'None'}")
                    abort(401, description="Invalid or missing API key")
        
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/status')
@require_api_key
def api_status():
    """Return the current orchestrator status as JSON."""
    data = status_service.get_status()
    if not data:
        return jsonify({
            'error': 'Status data not available',
            'message': 'Please wait for the updater to run'
        }), 503
    
    # Add some metadata
    response_data = {
        'success': True,
        'data': data,
        'api_version': '1.0'
    }
    
    return jsonify(response_data)


@api_bp.route('/status/summary')
@require_api_key
def api_status_summary():
    """Return a summary of the orchestrator status."""
    data = status_service.get_summary()
    if not data:
        return jsonify({
            'error': 'Status data not available',
            'message': 'Please wait for the updater to run'
        }), 503
    
    # Return just the summary without individual orchestrator details
    summary = {
        'success': True,
        'data': data,
        'api_version': '1.0'
    }
    
    return jsonify(summary)


@api_bp.route('/pillars')
@require_api_key
def api_pillars():
    """Return comprehensive pillar data combining static info and current status."""
    data = status_service.get_pillars()
    if not data:
        return jsonify({
            'error': 'Status data not available',
            'message': 'Please wait for the updater to run'
        }), 503
    
    response_data = {
        'success': True,
        'data': data,
        'api_version': '1.0'
    }
    
    return jsonify(response_data)


@api_bp.route('/auth/info')
@require_api_key
def api_auth_info():
    """Return API authentication information."""
    api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
    
    # Find the index of the current API key (for identification)
    key_index = None
    if api_key and api_key in Config.API_KEYS:
        key_index = Config.API_KEYS.index(api_key) + 1
    
    return jsonify({
        'success': True,
        'data': {
            'authenticated': True,
            'key_index': key_index,
            'total_keys_configured': len(Config.API_KEYS),
            'key_prefix': api_key[:8] + '...' if api_key else None,
            'access_time': datetime.now().isoformat()
        },
        'api_version': '1.0'
    })


