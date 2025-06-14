# Deployment Guide

## Quick Setup

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd orchestrator-status-page
```

2. **Set up virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your orchestrator IPs and generate API keys
python scripts/generate_api_key.py
```

4. **Run the application**:
```bash
python run.py
```

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 "app.main:create_app()"
```

### Using Docker (Optional)
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app.main:create_app()"]
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `ORCHESTRATOR_IP_1` through `ORCHESTRATOR_IP_20`: Your orchestrator IP addresses
- `API_KEYS`: Comma-separated list of API keys
- `SECRET_KEY`: Flask secret key for security
- `FLASK_PORT`: Port to run the application (default: 5001)

## Security Notes

- Never commit `.env` files to version control
- Generate new API keys for each deployment
- Use HTTPS in production
- Configure proper firewall rules