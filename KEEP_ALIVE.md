# Keep Render Free Tier Service Alive

Render's free tier services sleep after 15 minutes of inactivity. This guide shows you how to keep your service awake continuously.

## Important Notes

⚠️ **Render's Free Tier Limits:**
- 750 hours/month total runtime across all free services
- 31 days × 24 hours = 744 hours/month
- You can run ONE service 24/7 on free tier
- Multiple services will exceed the limit

⚠️ **Alternative:** Consider upgrading to Starter plan ($7/month) for always-on service without workarounds.

## Methods to Keep Service Alive

### Method 1: Cron-job.org (Easiest, Recommended)

**Free external service that pings your endpoint every 14 minutes.**

1. **Deploy your service to Render first** and get the URL (e.g., `https://your-service.onrender.com`)

2. **Go to [cron-job.org](https://cron-job.org)** and create free account

3. **Create New Cronjob:**
   - **Title:** `Keep ACUR Embedding Alive`
   - **URL:** `https://your-service.onrender.com/health`
   - **Schedule:** Every 14 minutes
     - Pattern: `*/14 * * * *`
   - **Request Method:** GET
   - **Notifications:** Enable email alerts on failure (optional)

4. **Save and Activate**

**Pros:**
- No code needed
- Reliable external service
- Free tier available
- Email alerts on downtime

**Cons:**
- Depends on third-party service
- May violate Render ToS (see note below)

### Method 2: UptimeRobot (Popular Alternative)

1. **Create account at [uptimerobot.com](https://uptimerobot.com)** (free)

2. **Add New Monitor:**
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** `ACUR Embedding Service`
   - **URL:** `https://your-service.onrender.com/health`
   - **Monitoring Interval:** 5 minutes (free tier)

3. **Save Monitor**

**Pros:**
- More features (status page, multiple alert channels)
- 5-minute interval (better than cron-job)
- Free tier: 50 monitors

**Cons:**
- 5 minutes is minimum (Render sleeps at 15 min, so you have buffer)
- May violate Render ToS

### Method 3: GitHub Actions (Self-Hosted Cron)

Create a GitHub Actions workflow in your repository to ping your service.

**Create file:** `.github/workflows/keep-alive.yml`

```yaml
name: Keep Render Service Alive

on:
  schedule:
    # Run every 14 minutes
    - cron: '*/14 * * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping health endpoint
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" https://your-service.onrender.com/health)
          echo "Health check response: $response"
          if [ $response -ne 200 ]; then
            echo "Health check failed with status $response"
            exit 1
          fi
```

**Setup:**
1. Create `.github/workflows/` folder in your repo
2. Add the file above
3. Replace URL with your Render service URL
4. Commit and push
5. Go to repository → Actions tab → Enable workflows

**Pros:**
- No external dependency (except GitHub)
- Free on GitHub
- Version controlled

**Cons:**
- Requires GitHub repository
- GitHub Actions has usage limits (but generous for this)

### Method 4: Self-Ping (Not Recommended)

Add a background task in your service to ping itself.

**⚠️ Not recommended because:**
- Uses your service's resources
- Can't wake service if it's already asleep
- Doesn't work on Render's architecture

### Method 5: WordPress Cron (If Using WordPress Plugin)

Use WordPress's built-in cron to ping your service.

**Add to your WordPress plugin or theme's `functions.php`:**

```php
// Schedule keep-alive ping
if (!wp_next_scheduled('acur_keep_embedding_alive')) {
    wp_schedule_event(time(), 'acur_14min', 'acur_keep_embedding_alive');
}

// Add custom 14-minute interval
add_filter('cron_schedules', 'acur_add_14min_cron_interval');
function acur_add_14min_cron_interval($schedules) {
    $schedules['acur_14min'] = array(
        'interval' => 840, // 14 minutes in seconds
        'display'  => __('Every 14 Minutes')
    );
    return $schedules;
}

// The actual ping function
add_action('acur_keep_embedding_alive', 'acur_ping_embedding_service');
function acur_ping_embedding_service() {
    $service_url = defined('ACUR_EMBEDDING_SERVICE_URL')
        ? ACUR_EMBEDDING_SERVICE_URL
        : 'https://your-service.onrender.com';

    $response = wp_remote_get($service_url . '/health', array(
        'timeout' => 5,
        'sslverify' => true
    ));

    if (is_wp_error($response)) {
        error_log('ACUR Embedding keep-alive failed: ' . $response->get_error_message());
    } else {
        error_log('ACUR Embedding keep-alive ping successful');
    }
}

// Clean up on deactivation
register_deactivation_hook(__FILE__, 'acur_deactivate_keep_alive');
function acur_deactivate_keep_alive() {
    wp_clear_scheduled_hook('acur_keep_embedding_alive');
}
```

**Pros:**
- No external service needed
- Integrated with your WordPress site
- Automatic

**Cons:**
- Only works if your WordPress site has traffic
- WordPress cron requires site visits to trigger
- Less reliable than dedicated cron services

## Recommended Approach

**For most users, I recommend Method 1 (cron-job.org) because:**
1. Easy to set up (5 minutes)
2. No code changes needed
3. Reliable and free
4. Email alerts if service goes down

**Setup Steps:**

1. Deploy to Render first
2. Get your service URL: `https://your-service.onrender.com`
3. Create cron-job.org account
4. Add cronjob to ping `/health` every 14 minutes
5. Done!

## Monitoring Your Service

### Check if Keep-Alive is Working

1. **View Render Logs:**
   - Go to Render Dashboard → Your Service → Logs
   - You should see regular health check requests every 14 minutes
   - Look for: `GET /health` requests

2. **Check Response Times:**
   - First request after sleep: ~30 seconds
   - Subsequent requests: ~50-100ms
   - If all requests are fast, service is staying awake

3. **Monitor Uptime:**
   - UptimeRobot provides uptime percentage
   - Should be 99%+ if working correctly

## Troubleshooting

### Service Still Sleeping

**Check your cron interval:**
- Must be less than 15 minutes
- Recommended: 14 minutes or less

**Verify cron is actually running:**
- Check cron-job.org execution history
- Look for failed requests

**Check Render logs:**
- Ensure health checks are arriving
- Look for errors

### Exceeded Free Tier Hours

**You have 750 hours/month:**
- 750 ÷ 31 days = ~24.2 hours/day
- Running 24/7 uses ~744 hours/month ✅
- Running multiple services = exceeds limit ❌

**If exceeded:**
- Disable keep-alive for some services
- Upgrade to paid plan
- Use only during business hours

### Cron Job Failing

**Check the URL:**
```bash
curl -I https://your-service.onrender.com/health
```
Should return `200 OK`

**Check Render service status:**
- Ensure service is deployed and running
- Check for deployment errors

## Terms of Service Consideration

⚠️ **Important:** Check Render's Terms of Service regarding keep-alive tactics:

- Render designed free tier with sleep to reduce abuse
- Keeping service awake may violate ToS
- Render may throttle or suspend service

**Recommendation:**
- Use keep-alive for development/testing
- Upgrade to paid plan for production use
- Render Starter plan is only $7/month

## Cost Comparison

| Method | Cost | Reliability | Setup Time |
|--------|------|-------------|------------|
| Free tier + keep-alive | $0 | Medium | 10 min |
| Render Starter | $7/mo | High | 2 min |
| Render Starter Plus | $15/mo | Very High | 2 min |

**For production, the $7/month Starter plan is recommended:**
- No sleep workarounds needed
- Better performance
- More memory (important for ML models)
- Supports your development

## Alternative: Hugging Face Inference API

Instead of self-hosting, use Hugging Face's hosted API:
- No server management
- Free tier available
- Pay-as-you-go pricing
- See `HUGGINGFACE_SETUP.md` for setup

## Summary

**Quick Setup (5 minutes):**

1. Deploy to Render → Get URL
2. Go to [cron-job.org](https://cron-job.org)
3. Create cronjob:
   - URL: `https://your-service.onrender.com/health`
   - Schedule: `*/14 * * * *`
4. Activate
5. Done! ✅

Your service will now stay awake 24/7 on Render's free tier.
