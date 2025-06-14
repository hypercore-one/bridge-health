# Security Guidelines

## Environment Configuration

### ⚠️ NEVER commit these files to Git:
- `.env` - Contains sensitive configuration
- `data/` - Contains live orchestrator data  
- `logs/` - May contain sensitive information

### ✅ Safe to commit:
- `.env.example` - Template with no real values
- All application code
- Documentation files

## API Key Management

1. **Generate secure API keys**:
```bash
python scripts/generate_api_key.py
```

2. **Add keys to .env file**:
```bash
API_KEYS=key1,key2,key3
```

3. **Rotate keys regularly** in production environments

## Production Security Checklist

- [ ] Use HTTPS/TLS encryption
- [ ] Configure proper firewall rules
- [ ] Set up rate limiting (configured by default)
- [ ] Monitor logs for unauthorized access attempts
- [ ] Use environment variables for all secrets
- [ ] Enable CORS only for trusted domains
- [ ] Keep dependencies updated

## Access Control

The application provides two levels of access:

1. **Web UI**: No authentication required (browser access)
2. **API Endpoints**: Require valid API key for external access

External API requests without valid API keys will receive `401 Unauthorized` responses.

## Monitoring

Check logs for unauthorized access attempts:
```bash
tail -f logs/orchestrator_status.log | grep "Unauthorized"
```

## Reporting Security Issues

If you discover a security vulnerability, please report it privately rather than using public issue trackers.