#!/usr/bin/env python3
"""Main entry point for the Zenon Orchestrator Status Page application"""

import os
import sys
import signal

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import create_app, get_logger
from config.settings import Config


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("Shutting down gracefully...")
    sys.exit(0)


def main():
    """Main function to start the application."""
    # Validate configuration
    if not Config.validate():
        print("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    orchestrator_ips = Config.get_orchestrator_ips()
    if not orchestrator_ips:
        print("No valid orchestrator IPs found. Exiting.")
        sys.exit(1)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        logger = get_logger()
        logger.info(f"Starting orchestrator status web service")
        logger.info(f"Configuration: {Config.get_config_dict()}")
        logger.info(f"Monitoring {len(orchestrator_ips)} orchestrators")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the Flask app
    ssl_context = None
    if Config.SSL_ENABLED:
        ssl_context = (Config.SSL_CERT_PATH, Config.SSL_KEY_PATH)
        with app.app_context():
            logger = get_logger()
            logger.info("SSL enabled")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
        ssl_context=ssl_context
    )


if __name__ == '__main__':
    main()