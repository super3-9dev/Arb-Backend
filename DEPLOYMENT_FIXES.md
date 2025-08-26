# Deployment Fixes for Render

## Issue Identified

The main problem is that Playwright browsers are not being installed correctly in the Docker container on Render. The error shows:

```
BrowserType.launch: Executable doesn't exist at /opt/render/.cache/ms-playwright/chromium_headless_shell-1181/chrome-linux/headless_shell
```

## Solutions

### Solution 1: Use the Updated Dockerfile (Recommended)

The updated `Dockerfile` includes:
- Additional system dependencies for Playwright
- Explicit browser path configuration
- Verification steps during build
- Startup script to check browser installation

### Solution 2: Use Alternative Dockerfile with Official Playwright Image

If Solution 1 doesn't work, use `Dockerfile.alternative` which:
- Uses Microsoft's official Playwright Python image
- Has all browsers pre-installed
- More reliable but larger image size

### Solution 3: Direct Python Deployment (Fallback)

If Docker continues to have issues:

1. **Update render.yaml:**
   ```yaml
   services:
     - type: web
       name: arb-backend
       env: python  # Change from docker to python
       plan: starter
       region: oregon
       healthCheckPath: /summary
       buildCommand: |
         pip install -r requirements.txt
         playwright install chromium
         playwright install-deps chromium
       startCommand: python server.py
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
         - key: PORT
           value: 8000
   ```

## Testing the Fix

### 1. Commit and Push Changes
```bash
git add .
git commit -m "Fix Playwright browser installation for Render deployment"
git push origin main
```

### 2. Monitor Build Logs
- Watch the build logs in Render dashboard
- Look for successful Playwright installation
- Check for browser verification steps

### 3. Verify Browser Installation
The startup script will show:
```
Checking Playwright browsers...
[list of browser files]
Starting application...
```

## Common Issues and Resolutions

### Issue: Browser Still Not Found
**Resolution:** Use `Dockerfile.alternative` with official Playwright image

### Issue: Build Times Out
**Resolution:** 
- Check Render plan limits
- Consider upgrading to Standard plan
- Optimize Docker layers

### Issue: Memory Issues
**Resolution:**
- Upgrade to Standard or Pro plan
- Reduce worker processes in application
- Monitor memory usage in logs

## Alternative Deployment Strategies

### 1. Render Blueprint
Use the `render.yaml` file for automatic deployment configuration.

### 2. Manual Configuration
If automatic deployment fails, manually configure:
- Environment: Docker
- Build Command: `docker build -t arb-backend .`
- Start Command: `docker run -p $PORT:8000 arb-backend`
- Health Check Path: `/summary`

### 3. Environment Variables
Ensure these are set:
- `PORT`: `8000`
- `PYTHON_VERSION`: `3.11.0`
- `PLAYWRIGHT_BROWSERS_PATH`: `/app/.cache/ms-playwright`

## Monitoring and Debugging

### 1. Check Application Logs
- Monitor startup sequence
- Look for browser initialization
- Check for scraper errors

### 2. Health Check Endpoint
- `/summary` should respond quickly
- Verify scrapers are running
- Check data collection status

### 3. Resource Usage
- Monitor CPU and memory usage
- Check for resource constraints
- Adjust plan if necessary

## Success Indicators

✅ **Build completes successfully**
✅ **Playwright browsers installed**
✅ **Application starts without browser errors**
✅ **Health checks pass**
✅ **Scrapers initialize properly**
✅ **API endpoints respond**

## Next Steps After Successful Deployment

1. **Test API endpoints:**
   - `GET /summary`
   - `WebSocket /ws`

2. **Monitor scraper performance:**
   - Check data collection
   - Monitor error rates
   - Verify real-time updates

3. **Scale if needed:**
   - Upgrade Render plan
   - Add more workers
   - Implement caching

## Support Resources

- [Render Documentation](https://render.com/docs)
- [Playwright Docker Guide](https://playwright.dev/python/docs/docker)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
