# Deploying ACUR Embedding Service to Render

This guide will help you deploy the embedding service to Render.com.

## Prerequisites

1. A [Render.com](https://render.com) account (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Options

### Option 1: Deploy via Render Blueprint (Recommended)

This method uses the `render.yaml` file for automated setup.

1. **Push your code to GitHub/GitLab**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create New Blueprint on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your Git repository
   - Render will automatically detect `render.yaml` and configure everything

3. **Review and Deploy**
   - Review the detected configuration
   - Click "Apply" to start deployment
   - Wait 5-10 minutes for initial deployment (model download takes time)

### Option 2: Manual Web Service Setup

1. **Push your code to GitHub/GitLab**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your Git repository
   - Select this repository

3. **Configure the Service**
   Fill in the following settings:

   | Setting | Value |
   |---------|-------|
   | **Name** | `acur-embedding-service` (or your choice) |
   | **Region** | Choose closest to your users |
   | **Branch** | `main` (or your default branch) |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn embedding_service:app --host 0.0.0.0 --port $PORT` |
   | **Instance Type** | `Free` or `Starter` ($7/month recommended) |

4. **Add Environment Variables** (Optional)
   - Click "Advanced" → "Add Environment Variable"
   - Add if needed:
     ```
     EMBEDDING_SERVICE_HOST=0.0.0.0
     ```

5. **Set Health Check**
   - Health Check Path: `/health`

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes for first deploy)

## After Deployment

### 1. Get Your Service URL

After deployment, Render will give you a URL like:
```
https://acur-embedding-service.onrender.com
```

### 2. Test the Deployment

Test your endpoints:

```bash
# Health check
curl https://your-service.onrender.com/health

# Test embedding
curl -X POST https://your-service.onrender.com/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "Can I submit unfinished work?"}'
```

### 3. Update WordPress Plugin

Update your WordPress plugin configuration with the new URL:

```php
// In wp-config.php
define('ACUR_EMBEDDING_SERVICE_URL', 'https://your-service.onrender.com');
```

## Important Notes

### Free Tier Limitations

Render's free tier has these limitations:
- **Sleeps after 15 minutes of inactivity** (first request after sleep takes ~30 seconds)
- **750 hours/month** of runtime
- **512MB RAM** (may be tight for this service)

**Recommendations:**
- Use **Starter plan ($7/month)** for production:
  - No sleep
  - 512MB RAM (or upgrade to 2GB for $15/month)
  - Better performance
- Or use **cron-job.org** to ping `/health` every 14 minutes to prevent sleep

### Memory Considerations

The embedding model requires ~500MB RAM:
- **Free tier:** May work but can be unstable
- **Starter (512MB):** Minimum recommended
- **Starter Plus (2GB):** Recommended for production

If you experience memory issues, upgrade your instance type.

### Cold Start Time

First request after deployment or sleep takes longer:
- Model download: ~30-60 seconds
- Model loading: ~2-5 seconds
- Subsequent requests: ~30-50ms

### CORS Configuration

The service currently allows all origins (`allow_origins=["*"]`). For production, update embedding_service.py:150 to restrict to your domain:

```python
allow_origins=["https://yourdomain.com"],
```

## Monitoring

### View Logs
- Go to Render Dashboard → Your Service → "Logs" tab
- Filter by severity or search for specific events

### Health Checks
Render automatically monitors `/health` endpoint:
- If health check fails, service auto-restarts
- View status in "Events" tab

### Metrics
In the Dashboard you can see:
- CPU usage
- Memory usage
- Request volume
- Response times

## Troubleshooting

### Deployment Fails

**Check build logs:**
```
ERROR: Failed to build requirements
```
→ Check that all dependencies in `requirements.txt` are valid

### Out of Memory
```
ERROR: Process killed (OOM)
```
→ Upgrade to instance with more RAM (2GB recommended)

### Service Not Responding
- Check logs for errors
- Verify start command is correct
- Check health check endpoint is working

### Slow First Request
- This is normal on free tier (sleep/wake cycle)
- Upgrade to paid tier to eliminate sleep
- Or set up a keep-alive ping

## Updating the Service

Render auto-deploys when you push to your connected branch:

```bash
# Make changes
git add .
git commit -m "Update service"
git push origin main
# Render automatically deploys the changes
```

To disable auto-deploy:
- Service Settings → "Auto-Deploy" → Turn off

## Cost Estimation

| Plan | Price | RAM | Sleep | Use Case |
|------|-------|-----|-------|----------|
| Free | $0 | 512MB | Yes (15min) | Testing only |
| Starter | $7/mo | 512MB | No | Small production |
| Starter Plus | $15/mo | 2GB | No | Production (recommended) |

## Alternative: Use Hugging Face Inference API

If you prefer not to manage infrastructure, consider using Hugging Face Inference API instead:
- See `HUGGINGFACE_SETUP.md` for details
- No deployment needed
- Pay per use
- Free tier available

## Support

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [Python on Render Guide](https://render.com/docs/deploy-fastapi)
