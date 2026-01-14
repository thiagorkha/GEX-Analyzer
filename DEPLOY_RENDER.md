# GEX Analyzer - Deployment Guide (Render)

## Overview

This guide covers deploying GEX Analyzer to Render.com, a modern cloud platform.

## Prerequisites

1. **GitHub Account**: Render deploys from GitHub repositories
2. **Render Account**: Sign up at https://render.com
3. **Code Pushed to GitHub**: Repository must be on GitHub

## Step 1: Prepare Repository

### 1.1 Create GitHub Repository
```bash
git init
git add .
git commit -m "Initial commit: GEX Analyzer"
git remote add origin https://github.com/USERNAME/gex-analyzer.git
git push -u origin main
```

### 1.2 Verify Files
Ensure these files exist:
- `requirements.txt` ✓
- `Procfile` ✓
- `runtime.txt` ✓
- `app.py` ✓

## Step 2: Prepare Application

### 2.1 Update app.py for Production
```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 2.2 Update Procfile
```
web: pip install --upgrade setuptools wheel && gunicorn app:app
```

### 2.3 Update requirements.txt
Ensure these are included with setuptools first:
```
setuptools>=65.5.0
wheel>=0.38.0
pip>=23.0.0
Flask==3.0.0
Flask-CORS==4.0.0
gunicorn==21.2.0
pandas==2.0.3
numpy==1.24.3
python-dateutil==2.8.2
Werkzeug==3.0.0
Jinja2==3.1.2
requests==2.31.0
python-dotenv==1.0.0
scipy==1.11.0
pytest==7.4.0
pytest-cov==4.1.0
```

### 2.4 Create .env File (Local Reference)
```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here
```

## Step 3: Deploy to Render

### 3.1 Connect to Render
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Select "Deploy an existing repository"
4. Connect your GitHub account
5. Select the gex-analyzer repository

### 3.2 Configure Web Service

**Name**: `gex-analyzer`

**Environment**: `Python 3`

**Build Command**:
```
pip install -r requirements.txt
```

**Start Command**:
```
gunicorn app:app
```

**Environment Variables**:
```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=[generate-random-string]
```

### 3.3 Instance Settings
- **Instance Type**: `Standard` (free tier available)
- **Auto-Deploy**: Enable (redeploy on GitHub push)

### 3.4 Click Deploy

## Step 4: Post-Deployment

### 4.1 Verify Deployment
```bash
# Check service status
curl https://gex-analyzer.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 4.2 Test Endpoints
```bash
# Test analysis endpoint
curl -X POST https://gex-analyzer.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"ohlc_data": [{"open": 100, "high": 105, "low": 98, "close": 102, "volume": 1000}]}'
```

### 4.3 Access Application
Open browser: `https://gex-analyzer.onrender.com`

## Environment Variables

### Required
- `FLASK_ENV`: `production`
- `DEBUG`: `False`
- `SECRET_KEY`: Random string (use Python: `import secrets; secrets.token_hex(16)`)

### Optional
- `LOG_LEVEL`: `INFO` or `DEBUG`
- `MAX_CONTENT_LENGTH`: File upload limit

## Monitoring

### 4.1 View Logs
In Render dashboard:
1. Select your service
2. Click "Logs" tab
3. Monitor in real-time

### 4.2 Set Alerts
1. Go to Settings
2. Enable notifications for deployment failures
3. Configure email alerts

## Scaling

### Auto-Scaling
1. Click service settings
2. Enable "Auto Scaling"
3. Set min/max instances (requires paid plan)

### Manual Scaling
1. Change instance type
2. Adjust number of instances
3. Applies on next deploy

## Troubleshooting

### Issue: Build Failed - setuptools.build_meta Error

This error: `pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import 'setuptools.build_meta'`

**Root Cause**: Missing setuptools during dependency installation

**Solution**:
1. Add setuptools to requirements.txt (first line):
```
setuptools>=65.5.0
wheel>=0.38.0
pip>=23.0.0
```

2. Update Procfile to ensure upgrade:
```
web: pip install --upgrade setuptools wheel && gunicorn app:app
```

3. Clear Render cache and redeploy:
   - In Render dashboard, select your service
   - Click "Settings" → "Environment"
   - Trigger manual redeploy

### Issue: Build Failed
**Check**: 
- All dependencies in requirements.txt
- Python version compatibility
- No syntax errors

**Fix**:
```bash
# Verify locally
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Issue: 502 Bad Gateway
**Check**:
- Application crashes (check logs)
- Wrong start command
- Port mismatch

**Fix**:
- Verify `gunicorn app:app` command
- Check for startup errors in logs
- Restart service

### Issue: Timeout Errors
**Check**:
- Long-running calculations
- Database queries

**Fix**:
- Add Render.com timeout to 30s
- Optimize algorithms
- Add caching

### Issue: Memory Issues
**Check**:
- Large data processing
- Memory leaks

**Fix**:
- Upgrade to larger instance
- Optimize code
- Use streaming for large files

## Performance Optimization

### 1. Database Optimization
- Add indexes for frequent queries
- Cache expensive calculations
- Use pagination for large datasets

### 2. Code Optimization
```python
# Example: Cache calculations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param):
    return result
```

### 3. CDN Setup
For static files:
1. Store assets in Render static directory
2. Or use external CDN like Cloudflare

### 4. API Response Compression
```python
from flask_compress import Compress

app = Flask(__name__)
Compress(app)
```

## Backup & Recovery

### 1. Backup Code
- GitHub is your backup (use Git)
- Create releases for versions

### 2. Backup Data
If using database:
```bash
# Export data
pg_dump DATABASE_URL > backup.sql

# Restore data
psql DATABASE_URL < backup.sql
```

## Security

### 1. SSL/HTTPS
- Render provides free SSL
- Force HTTPS:
```python
from flask_talisman import Talisman
Talisman(app)
```

### 2. CORS Configuration
```python
from flask_cors import CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 3. Environment Secrets
- Never commit `.env` files
- Use Render environment variables
- Rotate secrets regularly

## Custom Domain

### Add Custom Domain
1. In Render dashboard, go to Settings
2. Click "Custom Domains"
3. Add your domain (e.g., `gex-analyzer.com`)
4. Update DNS records:
   - Add CNAME to `gex-analyzer.onrender.com`

### SSL Certificate
- Automatic with Let's Encrypt
- Renews automatically

## Continuous Deployment

### GitHub Integration
1. Push to main branch
2. Render automatically deploys
3. Check "Auto Deploy" in settings

### Deployment Status
- Green: Active
- Yellow: Deploying
- Red: Failed

## Cost Estimation

### Render Pricing (as of 2024)
- **Free Tier**: 0.5GB RAM, limited hours
- **Starter**: $7/month, 0.5GB RAM
- **Standard**: $15/month, 2GB RAM
- **Professional**: Custom pricing

### Cost Reduction
- Use free tier for development
- Monitor and optimize resource usage
- Schedule deployments during off-peak

## Disaster Recovery

### 1. Redeploy Latest
```bash
# In Render dashboard
- Service → Manual Deploy → Latest Commit
```

### 2. Rollback
```bash
git revert [commit-hash]
git push  # Trigger redeploy
```

### 3. Database Recovery
```bash
# Restore from backup
psql < backup.sql
```

## Maintenance

### Regular Tasks
- Monitor logs weekly
- Review performance metrics
- Update dependencies monthly
- Test deployments in staging

### Staging Environment
Create separate staging:
1. Create new service on Render
2. Deploy from develop branch
3. Test before promoting to production

## Support

### Render Support
- https://support.render.com
- Status page: https://status.render.com

### Community
- GitHub Issues
- Stack Overflow tag: render

## Additional Resources

- Render Docs: https://render.com/docs
- Flask Deployment: https://flask.palletsprojects.com/deployment/
- Gunicorn Docs: https://gunicorn.org/

