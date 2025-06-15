# Bridge Health Monitoring Service

A production-ready Flask web application that monitors Zenon Network orchestrator nodes in real-time, providing a modern web dashboard and comprehensive JSON API endpoints with API key authentication. This service monitors the health of the Zenon bridge infrastructure by tracking orchestrator node status.

## Features

- **⚡ High Performance**: 23x faster status updates using concurrent HTTP requests (40s → 1.7s)
- **🎨 Modern UI**: Zenon-themed responsive web interface with real-time updates
- **🔒 API Security**: Protected API endpoints with multiple API key support
- **📊 Comprehensive Monitoring**: Tracks all 20 orchestrator nodes with static pillar mapping
- **🌐 Bridge Status Monitoring**: Automatic bridge health detection (online when ≥16 orchestrators active)
- **📈 Network Statistics**: Real-time wrap/unwrap counts for BNB Chain, Ethereum, and Supernova
- **🔄 Auto-refresh**: Background status updates every 60 seconds with web UI auto-refresh
- **📝 Structured Logging**: Rotating file logs with configurable levels
- **🏗️ Production Ready**: Environment-based configuration with validation

## Quick Start

1. **Clone and Setup**:
```bash
git clone https://github.com/hypercore-one/bridge-health.git
cd bridge-health
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**:
```bash
cp .env.example .env
nano .env  # Add your API keys and update settings
```

3. **Configure Orchestrator Mapping**:
```bash
cp config/orchestrator_mapping.py.example config/orchestrator_mapping.py
nano config/orchestrator_mapping.py  # Add actual orchestrator IPs and names
```

4. **Create Required Directories**:
```bash
mkdir -p data logs
```

5. **Generate API Keys**:
```bash
python scripts/generate_api_key.py
# Add generated keys to .env file API_KEYS setting
```

6. **Run Development Server**:
```bash
python run.py
```

7. **Access**:
- Web UI: http://localhost:5001
- API: http://localhost:5001/api/status (requires API key for external access)

## Configuration

The application uses environment variables for configuration. Key settings in `.env`:

### Required Settings
```bash
# Orchestrator IP addresses (up to 20)
ORCHESTRATOR_IP_1=192.168.1.100
ORCHESTRATOR_IP_2=192.168.1.101
# ... add up to ORCHESTRATOR_IP_20

# API Keys (comma-separated list)
API_KEYS=zn_admin_abc123,zn_readonly_def456,zn_monitor_ghi789

# Security
SECRET_KEY=your-secret-key-here
```

### Optional Settings
```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
ORCHESTRATOR_TIMEOUT=5
MAX_CONCURRENT_REQUESTS=10
UPDATE_INTERVAL=60
MIN_ONLINE_FOR_BRIDGE=16
LOG_LEVEL=INFO
```

## API Authentication

### Generating API Keys

Use the included script to generate secure API keys:
```bash
python scripts/generate_api_key.py
```

This generates 5 different API keys with descriptive prefixes:
- `zn_admin_*` - For administrative access
- `zn_readonly_*` - For read-only access  
- `zn_monitor_*` - For monitoring systems
- `zn_dashboard_*` - For dashboard applications
- `zn_external_*` - For external integrations

### Managing API Keys

1. **Adding Keys**: Edit `.env` file and add new keys to the `API_KEYS` list
2. **Removing Keys**: Edit `.env` file and remove keys from the `API_KEYS` list  
3. **Restart**: Restart the application to apply changes

Example:
```bash
# Multiple API keys (recommended)
API_KEYS=zn_admin_abc123,zn_readonly_def456,zn_monitor_ghi789

# Legacy single API key (for backward compatibility)
API_KEY=your_single_api_key_here
```

### Using API Keys

**Header Method (Recommended)**:
```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:5001/api/status
```

**Query Parameter Method**:
```bash
curl "http://localhost:5001/api/status?api_key=your_api_key_here"
```

## API Endpoints

### Public Endpoints (No Authentication Required)

#### `GET /`
Web dashboard showing orchestrator status with modern Zenon-themed UI.

#### `GET /health`
Health check endpoint:
```json
{
  "status": "healthy",
  "has_data": true,
  "timestamp": "2025-06-14T12:00:00"
}
```

### API Endpoints (Authentication Required)

> **Note**: The web UI can access `/api/status` without authentication, but external requests require an API key.

#### `GET /api/status`
Returns complete orchestrator status data:
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-06-14T16:05:30.616745",
    "bridge_status": "online",
    "online_count": 18,
    "total_count": 20,
    "query_time_seconds": 1.79,
    "orchestrators": [
      {
        "ip": "192.168.1.100",
        "pillar_name": "Anvil",
        "pillar_url": "anvil",
        "producer_address": "z1qzkd8urw7c4wg6x0cvd2nrzr4ke9d4zh0tvd8s",
        "status": "online",
        "state": "0 (LiveState)",
        "state_num": 0,
        "network_stats": {
          "bnb": {"wraps": 0, "unwraps": 0},
          "eth": {"wraps": 0, "unwraps": 0},
          "supernova": {"wraps": 0, "unwraps": 0}
        },
        "error": null,
        "last_checked": "2025-06-14T16:05:29.229334",
        "api_pillar_name": "Anvil",
        "name_mismatch": false
      }
    ]
  },
  "api_version": "1.0"
}
```

#### `GET /api/status/summary`
Returns summary statistics without individual orchestrator details:
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-06-14T16:05:30.616745",
    "bridge_status": "online",
    "online_count": 18,
    "total_count": 20,
    "query_time_seconds": 1.79
  },
  "api_version": "1.0"
}
```

#### `GET /api/pillars`
Returns comprehensive pillar data combining static information with current status:
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-06-14T16:05:30.616745",
    "total_pillars": 20,
    "online_count": 18,
    "offline_count": 2,
    "unknown_count": 0,
    "pillars": [
      {
        "ip": "192.168.1.100",
        "pillar_name": "Anvil",
        "pillar_url": "anvil",
        "pubkey": "Cdq18YwdIT21VcOOl3uczUl/W+RGCqi9CgFIf4CLr8g=",
        "zenonhub_url": "https://zenonhub.io/pillar/anvil",
        "status": "online",
        "producer_address": "z1qzkd8urw7c4wg6x0cvd2nrzr4ke9d4zh0tvd8s",
        "producer_explorer_url": "https://zenonhub.io/explorer/account/z1qzkd8urw7c4wg6x0cvd2nrzr4ke9d4zh0tvd8s",
        "state": "0 (LiveState)",
        "state_num": 0,
        "network_stats": {
          "bnb": {"wraps": 0, "unwraps": 0},
          "eth": {"wraps": 0, "unwraps": 0},
          "supernova": {"wraps": 0, "unwraps": 0}
        },
        "error": null,
        "last_checked": "2025-06-14T16:05:29.229334",
        "api_pillar_name": "Anvil",
        "name_mismatch": false
      }
    ]
  },
  "api_version": "1.0"
}
```

#### `GET /api/auth/info`
Returns API authentication information:
```json
{
  "success": true,
  "data": {
    "authenticated": true,
    "key_index": 1,
    "total_keys_configured": 3,
    "key_prefix": "zn_admin_...",
    "access_time": "2025-06-14T15:56:06.123456"
  },
  "api_version": "1.0"
}
```

## Orchestrator States

- **0 (LiveState)**: Online and operational
- **1 (KeyGenState)**: Online, generating keys  
- **2 (HaltedState)**: Offline, halted
- **3 (EmergencyState)**: Offline, emergency mode
- **4 (ReSignState)**: Offline, re-signing

## Static Pillar Mapping

The application includes static pillar name mapping for all 20 orchestrators, ensuring consistent display even when API endpoints are unreachable. Orchestrator mappings are configured in `config/orchestrator_mapping.py` (not committed to git for security).

## Performance

- **Query Time**: ~1.7 seconds for all 20 orchestrators (23x improvement from 40s)
- **Concurrent Requests**: Up to 10 simultaneous HTTP requests
- **Auto-refresh**: Web UI updates every 30 seconds
- **Background Updates**: Status cache refreshed every 60 seconds

## Security Features

- **API Key Authentication**: Multiple API keys with external access control
- **Web UI Exception**: Browser requests bypass API key requirement
- **Rate Limiting**: 60 requests per minute per IP
- **Security Headers**: CORS, CSRF, XSS protection
- **Audit Logging**: All authentication attempts are logged

### Security Best Practices

1. **Use Strong Keys**: Always use the generator script for secure keys
2. **Rotate Keys**: Regularly rotate API keys, especially for production
3. **Limit Access**: Give each user/application their own unique key
4. **Monitor Usage**: Check logs for unauthorized access attempts
5. **Environment Variables**: Never commit API keys to version control

## Logging

Logs are written to the `logs/` directory with automatic rotation:
- **orchestrator_status.log**: Web server and API logs
- **check_orchestrators.log**: Manual check logs

Example log entries:
```
2025-06-14 16:05:30 - orchestrator_status - INFO - Orchestrator status update complete. Queried 20 orchestrators in 1.79s
2025-06-14 16:56:26 - orchestrator_status - WARNING - Unauthorized API access attempt from 127.0.0.1 with key: None
```

## Production Deployment

### Complete Setup Guide (Using Gunicorn at /opt/bridge-health)

1. **Clone to Production Location**:
```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/hypercore-one/bridge-health.git
sudo chown -R $USER:$USER /opt/bridge-health
cd /opt/bridge-health
```

2. **Set Up Python Environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

3. **Configure Application**:
```bash
# Create directories
mkdir -p data logs

# Set up environment
cp .env.example .env
nano .env  # Add your configuration

# Set up orchestrator mapping
cp config/orchestrator_mapping.py.example config/orchestrator_mapping.py
nano config/orchestrator_mapping.py  # Add actual orchestrator details

# Set permissions
chmod 600 .env
chmod 600 config/orchestrator_mapping.py
```

4. **Test with Gunicorn**:
```bash
gunicorn -c gunicorn_config.py "app.main:create_app()"
```

5. **Create Systemd Service**:
```bash
sudo nano /etc/systemd/system/bridge-health.service
```

Add:
```ini
[Unit]
Description=Bridge Health Monitoring Service with Gunicorn
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=/opt/bridge-health
Environment="PATH=/opt/bridge-health/venv/bin"
ExecStart=/opt/bridge-health/venv/bin/gunicorn -c /opt/bridge-health/gunicorn_config.py "app.main:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

6. **Enable and Start Service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bridge-health
sudo systemctl start bridge-health
sudo systemctl status bridge-health
```

7. **Configure Nginx** (Optional but recommended):
```bash
sudo nano /etc/nginx/sites-available/bridge-health
```

Add:
```nginx
upstream bridge_health {
    server 127.0.0.1:5001 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 4G;
    keepalive_timeout 5;

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://bridge_health;
    }

    location /static/ {
        alias /opt/bridge-health/app/static/;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/bridge-health /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

8. **Set Up SSL** (Recommended):
```bash
sudo certbot --nginx -d your-domain.com
```

9. **Configure Log Rotation**:
```bash
sudo nano /etc/logrotate.d/bridge-health
```

Add:
```
/opt/bridge-health/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 $USER $USER
    sharedscripts
    postrotate
        systemctl reload bridge-health
    endscript
}
```

### Monitoring Commands

```bash
# Service status
sudo systemctl status bridge-health

# View logs
sudo journalctl -u bridge-health -f
tail -f /opt/bridge-health/logs/orchestrator_status.log
tail -f /opt/bridge-health/logs/gunicorn_error.log

# Test application connectivity
curl http://127.0.0.1:5001/health

# Restart service
sudo systemctl restart bridge-health

# Reload workers (zero downtime)
sudo systemctl reload bridge-health
```

## Development

### Code Structure
```
├── app/                        # Main application package
│   ├── __init__.py
│   ├── main.py                 # Flask app factory
│   ├── models/                 # Data models (future use)
│   ├── services/               # Business logic
│   │   ├── orchestrator_client.py  # Core client with pillar mapping  
│   │   └── status_service.py   # Status management service
│   ├── api/                    # API routes
│   │   └── routes.py           # API endpoints
│   ├── web/                    # Web UI routes
│   │   └── routes.py           # Web interface
│   └── templates/              # Jinja2 templates
│       └── status.html         # Modern web UI template
├── config/                     # Configuration
│   ├── settings.py            # Application configuration
│   └── logging.py             # Logging setup
├── scripts/                    # Utility scripts
│   └── generate_api_key.py    # API key generation utility
├── data/                       # Data files (not in git)
│   └── orchestrator_status.json  # Status cache
├── logs/                       # Log files
├── run.py                      # Application entry point
├── .env                       # Environment configuration
└── requirements.txt           # Python dependencies
```

### Testing Authentication
```bash
# Test API key authentication
curl -H "X-API-Key: your_key" http://localhost:5001/api/auth/info

# Test external API access (should require API key)
curl http://localhost:5001/api/status

# Test browser-like access (should work without API key)
curl -H "User-Agent: Mozilla/5.0" -H "Referer: http://localhost:5001/" http://localhost:5001/api/status
```

## Troubleshooting

### API Authentication Issues
- **401 Unauthorized**: Check that your API key is in the `API_KEYS` list in `.env`
- **No authentication required**: Ensure `API_KEYS` is set in `.env` file
- **Key not working**: Restart the application after changing `.env`

### Performance Issues
- **Slow updates**: Adjust `MAX_CONCURRENT_REQUESTS` for more parallel queries
- **Timeouts**: Increase `ORCHESTRATOR_TIMEOUT` value
- **Memory usage**: Reduce `MAX_CONCURRENT_REQUESTS` if experiencing memory issues

### Network Issues
- **No orchestrators found**: Check that IP addresses are correctly set in `.env`
- **Connection errors**: Verify orchestrators are running on port 55000
- **Firewall**: Ensure outbound connections to orchestrator IPs are allowed

### Service Issues
- **Port conflicts**: Change `FLASK_PORT` if port 5001 is in use
- **Permission errors**: Ensure proper file permissions for logs directory
- **Configuration errors**: Run `python -c "from config import Config; print(Config.validate())"`
- **Rate limiter warnings**: The in-memory warnings are normal for production - can be ignored or configure Redis for distributed storage

### Production Deployment Issues
- **"Failed to find attribute 'create_app'"**: Use `"app.main:create_app()"` instead of `"app:create_app()"`
- **Can't connect to 127.0.0.1:5001**: Check if Gunicorn is actually running and binding to the correct port
- **Remote access not working**: Change `bind = "127.0.0.1:5001"` to `bind = "0.0.0.0:5001"` in `gunicorn_config.py`
- **Status not updating in Gunicorn**: The background updater now only runs in one worker to avoid conflicts. Check logs for "Background updater started in worker" message
- **Frontend not auto-refreshing**: The API authentication now allows browser requests from the same host. Restart Gunicorn after pulling latest changes
- **Unauthorized API access warnings**: These occur when API authentication is checking requests - normal for external API calls
- **Multiple Flask app creation messages**: Normal in multi-worker Gunicorn setup - each worker creates its own app instance
- **Firewall blocking access**: Ensure port 5001 is open in your firewall (e.g., `ufw allow 5001`)

## Monitoring Access

The application logs all authentication attempts. Monitor for unauthorized access:

```bash
tail -f logs/orchestrator_status.log | grep "Unauthorized"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[License information here]