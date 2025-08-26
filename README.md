# Arb Backend - FastAPI Sports Betting Scraper

A FastAPI backend application that scrapes sports betting data from multiple sources and provides real-time updates via WebSocket.

## Features

- **FastAPI** backend with WebSocket support
- **Playwright** web scraping for sports betting data
- **Real-time data streaming** via WebSocket
- **Multiple data sources**: golbet724 and orbitxch
- **REST API endpoints** for data retrieval

## API Endpoints

- `GET /summary` - Get current scraped data summary
- `WebSocket /ws` - Real-time data streaming

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   playwright install-deps chromium
   ```

3. **Run the server:**
   ```bash
   python server.py
   ```

4. **Access the API:**
   - API: http://localhost:8000/summary
   - WebSocket: ws://localhost:8000/ws

## Deployment on Render

### Option 1: Docker Deployment (Recommended)

1. **Push your code to GitHub** (if not already done)

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Sign up/Login with your GitHub account
   - Click "New +" → "Web Service"

3. **Configure the service:**
   - **Name**: `arb-backend` (or your preferred name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Build Command**: `docker build -t arb-backend .`
   - **Start Command**: `docker run -p $PORT:8000 arb-backend`

4. **Environment Variables:**
   - `PORT`: `8000`
   - `PYTHON_VERSION`: `3.11.0`

5. **Health Check Path**: `/summary`

6. **Click "Create Web Service"**

### Option 2: Direct Python Deployment

1. **Connect to Render** as above

2. **Configure the service:**
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium`
   - **Start Command**: `gunicorn -c gunicorn_config.py server:app`

3. **Environment Variables:**
   - `PORT`: `8000`
   - `PYTHON_VERSION`: `3.11.0`

## Important Notes for Render Deployment

### Playwright Setup
- The Dockerfile automatically installs Playwright and its dependencies
- For direct Python deployment, the build command includes Playwright installation

### Port Configuration
- Render automatically sets the `PORT` environment variable
- The application binds to `0.0.0.0:8000` for external access

### Health Checks
- Render will use `/summary` endpoint for health monitoring
- Ensure this endpoint responds quickly and reliably

### Resource Requirements
- **Starter Plan**: Suitable for development/testing
- **Standard Plan**: Recommended for production with moderate traffic
- **Pro Plan**: For high-traffic production applications

## Monitoring and Logs

- **Render Dashboard**: Monitor deployment status and logs
- **Application Logs**: Available in Render's log viewer
- **Health Checks**: Automatic monitoring via `/summary` endpoint

## Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check Playwright installation in build logs
   - Verify Python version compatibility

2. **Runtime Errors:**
   - Check application logs in Render dashboard
   - Verify environment variables are set correctly

3. **Health Check Failures:**
   - Ensure `/summary` endpoint is working
   - Check if scrapers are running properly

### Performance Optimization

- **Worker Processes**: Adjust `workers` in `gunicorn_config.py`
- **Memory Usage**: Monitor resource usage in Render dashboard
- **Database Connections**: Optimize if adding database later

## Security Considerations

- **CORS**: Currently allows all origins (`*`) - restrict in production
- **Authentication**: Add proper authentication for production use
- **Rate Limiting**: Implement rate limiting for API endpoints
- **Environment Variables**: Use Render's secure environment variable storage

## Support

For deployment issues:
1. Check Render's [documentation](https://render.com/docs)
2. Review build and runtime logs in Render dashboard
3. Verify all required files are committed to your repository
