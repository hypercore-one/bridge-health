"""Web UI routes for the orchestrator status application"""

from datetime import datetime
from flask import Blueprint, render_template, jsonify

from app.services.status_service import StatusService

# Create web blueprint
web_bp = Blueprint('web', __name__)

# Initialize status service
status_service = StatusService()


@web_bp.route('/')
def status_page():
    """Render the status page."""
    data = status_service.get_status()
    if not data:
        data = {
            'timestamp': None,
            'bridge_status': 'unknown',
            'online_count': 0,
            'total_count': 0,
            'orchestrators': [],
            'error': 'Status file not found. Please wait for the updater to run.'
        }
    return render_template('status.html', data=data)


@web_bp.route('/health')
def health_check():
    """Health check endpoint."""
    data = status_service.get_status()
    is_healthy = data is not None
    
    return jsonify({
        'status': 'healthy' if is_healthy else 'unhealthy',
        'has_data': is_healthy,
        'timestamp': datetime.now().isoformat()
    }), 200 if is_healthy else 503