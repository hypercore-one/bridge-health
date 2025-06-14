"""
Configuration management for the orchestrator status application.
"""
import os
import ipaddress
from typing import List, Dict, Any
from dotenv import load_dotenv
from config.logging import setup_logging, get_logger

# Load environment variables
load_dotenv()

# Set up logging
logger = get_logger(__name__)


class Config:
    """Application configuration."""
    
    # Flask settings
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5001'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # Security settings
    API_KEY = os.getenv('API_KEY')  # Legacy single API key for backward compatibility
    
    # Multiple API keys - comma-separated list
    API_KEYS = []
    if os.getenv('API_KEYS'):
        API_KEYS = [key.strip() for key in os.getenv('API_KEYS').split(',') if key.strip()]
    elif API_KEY:  # Fall back to single API_KEY if API_KEYS not set
        API_KEYS = [API_KEY]
    
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # SSL/TLS settings
    SSL_ENABLED = os.getenv('SSL_ENABLED', 'False').lower() == 'true'
    SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')
    SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')
    
    # Redis settings
    REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'False').lower() == 'true'
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    
    # Orchestrator settings
    ORCHESTRATOR_PORT = int(os.getenv('ORCHESTRATOR_PORT', '55000'))
    ORCHESTRATOR_TIMEOUT = int(os.getenv('ORCHESTRATOR_TIMEOUT', '5'))
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
    
    # Update settings
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '60'))
    MIN_ONLINE_FOR_BRIDGE = int(os.getenv('MIN_ONLINE_FOR_BRIDGE', '16'))
    
    # File paths
    STATUS_FILE = os.getenv('STATUS_FILE', 'orchestrator_status.json')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', str(10 * 1024 * 1024)))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    @classmethod
    def get_orchestrator_ips(cls) -> List[str]:
        """Get and validate orchestrator IPs from environment variables."""
        ips = []
        max_orchestrators = int(os.getenv('MAX_ORCHESTRATORS', '20'))
        
        for i in range(1, max_orchestrators + 1):
            ip = os.getenv(f'ORCHESTRATOR_IP_{i}')
            if ip:
                ips.append(ip)
        
        # Validate IPs
        valid_ips = []
        for ip in ips:
            try:
                ipaddress.ip_address(ip)
                valid_ips.append(ip)
            except ValueError:
                logger.warning(f"Invalid IP address in configuration: {ip}")
        
        return valid_ips
    
    @classmethod
    def validate(cls) -> bool:
        """Validate the configuration."""
        valid = True
        
        # Check for required settings
        ips = cls.get_orchestrator_ips()
        if not ips:
            logger.error("No valid orchestrator IPs found in configuration")
            valid = False
        
        # Validate numeric ranges
        if cls.ORCHESTRATOR_TIMEOUT <= 0:
            logger.error("ORCHESTRATOR_TIMEOUT must be positive")
            valid = False
        
        if cls.UPDATE_INTERVAL <= 0:
            logger.error("UPDATE_INTERVAL must be positive")
            valid = False
        
        if cls.MIN_ONLINE_FOR_BRIDGE < 0:
            logger.error("MIN_ONLINE_FOR_BRIDGE must be non-negative")
            valid = False
        
        if cls.MAX_CONCURRENT_REQUESTS <= 0:
            logger.error("MAX_CONCURRENT_REQUESTS must be positive")
            valid = False
        
        # Security validations
        if not cls.FLASK_DEBUG and cls.SECRET_KEY == 'dev-key-change-in-production':
            logger.warning("Using default SECRET_KEY in production mode. Please set a secure SECRET_KEY.")
        
        if cls.SSL_ENABLED:
            if not cls.SSL_CERT_PATH or not cls.SSL_KEY_PATH:
                logger.error("SSL_CERT_PATH and SSL_KEY_PATH are required when SSL_ENABLED=true")
                valid = False
            elif not (os.path.exists(cls.SSL_CERT_PATH) and os.path.exists(cls.SSL_KEY_PATH)):
                logger.error("SSL certificate or key file not found")
                valid = False
        
        if cls.RATE_LIMIT_PER_MINUTE <= 0:
            logger.error("RATE_LIMIT_PER_MINUTE must be positive")
            valid = False
        
        return valid
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as a dictionary."""
        return {
            'flask_host': cls.FLASK_HOST,
            'flask_port': cls.FLASK_PORT,
            'flask_debug': cls.FLASK_DEBUG,
            'ssl_enabled': cls.SSL_ENABLED,
            'orchestrator_port': cls.ORCHESTRATOR_PORT,
            'orchestrator_timeout': cls.ORCHESTRATOR_TIMEOUT,
            'max_concurrent_requests': cls.MAX_CONCURRENT_REQUESTS,
            'update_interval': cls.UPDATE_INTERVAL,
            'min_online_for_bridge': cls.MIN_ONLINE_FOR_BRIDGE,
            'status_file': cls.STATUS_FILE,
            'log_level': cls.LOG_LEVEL,
            'log_dir': cls.LOG_DIR,
            'rate_limit_per_minute': cls.RATE_LIMIT_PER_MINUTE,
            'redis_enabled': cls.REDIS_ENABLED,
            'orchestrator_count': len(cls.get_orchestrator_ips())
        }