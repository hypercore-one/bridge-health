# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready Flask-based web application that monitors Zenon Network orchestrator nodes in real-time. It provides a modern, responsive status dashboard with real-time updates, comprehensive APIs, and enterprise-grade security features.

## Essential Commands

### Development
```bash
# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration template
cp .env.example .env
# Edit .env with your orchestrator IPs and configuration

# Run development server
python orchestrator_status.py

# Run both web app and status updater (development)
python run_all.py

# Manual orchestrator check
python check_orchestrators.py

# Health monitoring
python health_monitor.py
```

### Production Deployment
```bash
# Secure deployment (recommended)
chmod +x deploy-secure.sh
./deploy-secure.sh

# Basic deployment
chmod +x deploy.sh
./deploy.sh

# Check service status
sudo systemctl status orchestrator-status.service status-updater.service

# View logs
sudo journalctl -u orchestrator-status.service -f
sudo journalctl -u status-updater.service -f
```

### Testing and Development
```bash
# Test API endpoints
curl "http://localhost:5001/health"
curl -H "X-API-Key: your-api-key" "http://localhost:5001/api/status"

# Monitor performance
python check_orchestrators.py  # Shows query time improvements

# Run health checks
python health_monitor.py
```

## Architecture Overview

### Core Components

1. **Flask Web Server** (`orchestrator_status.py`): 
   - Serves modern Zenon-themed status dashboard at port 5001
   - Provides RESTful APIs with authentication
   - Real-time AJAX updates every 30 seconds
   - Security middleware (CORS, rate limiting, headers)

2. **Status Updater** (`status_updater.py`): 
   - Background service with concurrent orchestrator queries
   - Updates every 60 seconds with 13-20x performance improvement
   - Structured logging and error handling

3. **Orchestrator Client** (`orchestrator_client.py`): 
   - Shared module with ThreadPoolExecutor for concurrent requests
   - Connection pooling and retry logic
   - Standardized error handling and response format

4. **Configuration Management** (`config.py`):
   - Environment variable validation and type checking
   - Security settings and SSL configuration
   - Centralized application configuration

5. **Health Monitor** (`health_monitor.py`):
   - Service health monitoring and alerting
   - Disk space, log file, and performance monitoring
   - Email alert capabilities

### Performance Improvements
- **Before**: Sequential queries took ~40 seconds for 20 orchestrators
- **After**: Concurrent queries take ~2-3 seconds (13-20x faster)

### Security Features
- API key authentication for all API endpoints
- Rate limiting (configurable, default 60 req/min)
- CORS policy configuration
- Security headers (XSS, CSRF, clickjacking protection)
- SSL/TLS support with certificate management
- Dedicated system user with minimal permissions

### Modern UI Features
- Zenon-themed design with proper branding
- Real-time updates without page refresh
- Responsive design for mobile devices
- Loading animations and status indicators
- Interactive elements with hover effects
- Auto-refresh with connection status

## API Endpoints

### Public Endpoints
- `GET /` - Main status dashboard
- `GET /health` - Health check endpoint

### Authenticated Endpoints (require API key)
- `GET /api/status` - Complete orchestrator status data
- `GET /api/status/summary` - Summary without individual orchestrator details

### Authentication
Pass API key via header: `X-API-Key: your-api-key`  
Or query parameter: `?api_key=your-api-key`

## Configuration

### Environment Variables (.env file)
```bash
# Flask Application
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=false

# Security
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here
ALLOWED_ORIGINS=*
RATE_LIMIT_PER_MINUTE=60

# SSL/TLS
SSL_ENABLED=false
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem

# Orchestrator IPs
ORCHESTRATOR_IP_1=xxx.xxx.xxx.xxx
ORCHESTRATOR_IP_2=xxx.xxx.xxx.xxx
# ... up to ORCHESTRATOR_IP_20

# Performance
MAX_CONCURRENT_REQUESTS=10
ORCHESTRATOR_TIMEOUT=5
UPDATE_INTERVAL=60

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs
```

### State Mapping
- 0: LiveState (online) ✅
- 1: KeyGenState (online) ✅
- 2: HaltedState (offline) ❌
- 3: EmergencyState (offline) ❌
- 4: ReSignState (offline) ❌

Bridge status: "Online" when ≥16 orchestrators are online (states 0 or 1)

## File Structure
```
├── orchestrator_status.py      # Main Flask application
├── status_updater.py          # Background status updater
├── orchestrator_client.py     # Shared client with concurrency
├── config.py                  # Configuration management
├── logging_config.py          # Centralized logging setup
├── health_monitor.py          # Health monitoring and alerts
├── check_orchestrators.py     # CLI tool for manual checks
├── run_all.py                 # Development helper script
├── deploy-secure.sh           # Enhanced deployment script
├── templates/status.html      # Modern Zenon-themed UI
├── requirements.txt           # Python dependencies
├── .env.example              # Configuration template
├── SECURITY.md               # Security documentation
└── logs/                     # Application logs
```

## Monitoring and Maintenance

### Health Monitoring
```bash
# Manual health check
python health_monitor.py

# Set up automated monitoring (crontab)
*/5 * * * * /opt/orchestrator-status-page/venv/bin/python /opt/orchestrator-status-page/health_monitor.py
```

### Log Files
- `logs/orchestrator_status.log` - Main application logs
- `logs/status_updater.log` - Background service logs
- `logs/check_orchestrators.log` - Manual check logs
- `logs/health_monitor.log` - Health monitoring logs

### Performance Monitoring
- Query time displayed in UI and logs
- Health check endpoint for external monitoring
- Resource usage tracking in health monitor

## Security Considerations

### Production Deployment
1. Use `deploy-secure.sh` for enhanced security
2. Set strong SECRET_KEY and API_KEY
3. Configure SSL/TLS certificates
4. Set up firewall rules
5. Configure log rotation
6. Monitor for security events

### See SECURITY.md for comprehensive security guide

## Development Tips

1. **Configuration Changes**: Always update both `.env` and `.env.example`
2. **API Changes**: Update API version when making breaking changes
3. **UI Updates**: Test responsiveness on mobile devices
4. **Performance**: Monitor query times after orchestrator changes
5. **Security**: Never commit secrets or API keys to repository
6. **Logging**: Use structured logging with appropriate levels
7. **Testing**: Verify concurrent orchestrator queries work correctly