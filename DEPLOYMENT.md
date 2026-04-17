# Deployment Guide

## Prerequisites

Before deploying, ensure you have:

1. **API Keys** (at minimum):
   - ⚠️ **TRADIER_API_KEY** - Required for real-time data (get from https://developer.tradier.com)
   - Optional: ALPHA_VANTAGE_API_KEY (fallback data)
   - Optional: FINNHUB_API_KEY (news/catalysts)

2. **Infrastructure**:
   - Docker and Docker Compose installed
   - For production: GitHub account OR cloud hosting (AWS/GCP/Azure)

3. **Minimum Resources**:
   - 2GB RAM for development
   - 4GB RAM for production
   - 20GB disk space

---

## Quick Start - Local Development

### Step 1: Clone and Setup

```bash
# Clone the repository (once you push to GitHub)
git clone <your-github-repo-url>
cd trading-dashboard

# OR if you're working locally
cd /workspace/trading-dashboard
```

### Step 2: Configure Environment Variables

```bash
# Copy the environment template
cd backend
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Required in `.env`**:
```bash
# Minimum required for basic functionality
TRADIER_API_KEY=your_tradier_api_key_here

# Database (docker-compose provides this)
DATABASE_URL=postgresql://trading_user:trading_password@postgres:5432/trading_dashboard

# Redis (docker-compose provides this)
REDIS_URL=redis://redis:6379/0

# Watchlist
WATCHLIST=NVDA,META,TSLA,AAPL,GOOGL,AMZN,MSFT
```

### Step 3: Start with Docker Compose

```bash
# From the root directory
cd trading-dashboard

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Verify services
docker-compose ps
```

### Step 4: Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 5: Stop Services

```bash
docker-compose down

# To remove volumes (WARNING: deletes database)
docker-compose down -v
```

---

## Deployment Options

### Option 1: GitHub + Local Development (Recommended First Step)

This is the easiest way to get started and test the application.

#### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `trading-dashboard`)
3. Do NOT initialize with README (we already have one)
4. Copy the repository URL

#### Step 2: Push to GitHub

```bash
cd /workspace/trading-dashboard

# Set your GitHub credentials
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Add remote origin (replace with your repo URL)
git remote add origin https://github.com/your-username/trading-dashboard.git

# Push to GitHub
git push -u origin main
```

#### Step 3: Clone and Run on Any Machine

```bash
# On any machine with Docker
git clone https://github.com/your-username/trading-dashboard.git
cd trading-dashboard
cd backend
cp .env.example .env
# Edit .env with your API keys
cd ..
docker-compose up -d
```

**Advantages:**
- ✅ Easy setup
- ✅ Version control
- ✅ Can run on any machine with Docker
- ✅ Good for development and testing

**Limitations:**
- ❌ Not accessible from outside network
- ❌ Requires manual startup
- ❌ Not suitable for production trading

---

### Option 2: Cloud Deployment (Production-Ready)

For production deployment, you have several options:

#### Option 2A: Render.com (Easiest)

1. **Create Render Account**: https://render.com
2. **Connect GitHub Repository**
3. **Create Services**:

**Backend Service:**
- Type: Web Service
- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment Variables: Add your API keys

**Frontend Service:**
- Type: Web Service
- Runtime: Node
- Build Command: `npm run build`
- Start Command: `npm start`
- Environment Variables: `NEXT_PUBLIC_API_URL=<your-backend-url>`

**PostgreSQL Service:**
- Type: PostgreSQL
- Update DATABASE_URL in backend env vars

**Redis Service:**
- Type: Redis
- Update REDIS_URL in backend env vars

#### Option 2B: AWS (Most Scalable)

1. **ECS Fargate** for containers
2. **RDS** for PostgreSQL
3. **ElastiCache** for Redis
4. **ALB** for load balancing
5. **Route53** for DNS

Use the provided `Dockerfile.backend` and `Dockerfile.frontend`.

#### Option 2C: Railway (Simple Cloud)

1. **Create Railway Account**: https://railway.app
2. **Connect GitHub Repository**
3. **Add PostgreSQL and Redis services**
4. **Deploy backend and frontend as services**
5. **Add environment variables**

Railway will automatically detect and deploy.

#### Option 2D: VPS with Docker Compose

Set up a VPS on DigitalOcean, Linode, or AWS EC2:

```bash
# On VPS
git clone https://github.com/your-username/trading-dashboard.git
cd trading-dashboard
cp backend/.env.example backend/.env
nano backend/.env  # Add your API keys and production URLs
docker-compose up -d
```

Use Nginx as reverse proxy and Let's Encrypt for HTTPS.

---

## Getting Your Tradier API Key

### Why Tradier API Key is Critical

The Tradier API is the PRIMARY data source for:
- ✅ Real-time stock quotes
- ✅ Options chains
- ✅ Live prices
- ✅ Historical data

Without it, the system will fall back to Yahoo Finance (delayed) and Alpha Vantage (rate-limited).

### How to Get Your Free Tradier Key

1. **Sign Up**: https://developer.tradier.com
2. **Choose Plan**:
   - Free tier: Limited monthly calls (good for testing)
   - Paid tier: Unlimited calls (required for live trading)
3. **Create Application**:
   - Go to Console → Applications
   - Click "Create New Application"
   - Name: "Trading Dashboard"
   - Description: "Options trading analysis"
   - Callback URL: Leave blank
4. **Get API Key**:
   - Your API key will be displayed
   - Copy it immediately

### Add to Environment

```bash
# In backend/.env
TRADIER_API_KEY=your_actual_tradier_api_key_here
```

### Testing Your Key

```bash
# Test Tradier connection
curl "https://api.tradier.com/v1/markets/quotes?symbols=AAPL" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## Production Configuration Checklist

### Security

- [ ] Use strong passwords for PostgreSQL
- [ ] Use secrets management (AWS Secrets Manager, etc.)
- [ ] Enable HTTPS/TLS
- [ ] Set proper CORS origins (not "*")
- [ ] Use environment variables, never commit secrets
- [ ] Enable firewall rules
- [ ] Set up log monitoring

### Performance

- [ ] Configure Redis with proper memory settings
- [ ] Set up database connection pooling
- [ ] Configure caching TTLs appropriately
- [ ] Enable Gzip compression
- [ ] Use CDN for static assets
- [ ] Set up load balancing

### Reliability

- [ ] Configure health checks
- [ ] Set up auto-restart policies
- [ ] Enable database backups
- [ ] Set up log aggregation
- [ ] Configure alerting
- [ ] Implement circuit breakers (already done!)

### Monitoring

- [ ] Set up Prometheus/Grafana
- [ ] Configure error tracking (Sentry)
- [ ] Monitor API rate limits
- [ ] Track cache hit rates
- [ ] Monitor system resources

---

## Troubleshooting

### Common Issues

**Issue: "Connection refused" for database/redis**

```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs postgres
docker-compose logs redis
```

**Issue: API returns 401 Unauthorized**

- Verify TRADIER_API_KEY in .env
- check API key is valid (test with curl)
- Check for typos in environment variables

**Issue: "Module not found" errors**

```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Issue: Frontend can't connect to backend**

- Check NEXT_PUBLIC_API_URL in frontend
- Verify backend is running on port 8000
- Check CORS settings in main.py

**Issue: Data fetching fails**

- Check API keys are valid
- Check internet connectivity
- Verify data source is not rate-limited
- Check error logs: `docker-compose logs backend`

---

## Cost Estimates

### Development (Free)
- ✓ Local machine
- ✓ Docker Compose
- ✓ Free Tradier tier (limited calls)

### Production (Monthly Estimates)

**Render.com:**
- Backend: $7-25/month
- Frontend: $7/static month
- PostgreSQL: $7/month
- Redis: $15/month
- **Total: ~$36-54/month**

**Railway:**
- All services: ~$20-50/month (usage-based)
- **Total: ~$20-50/month**

**AWS:**
- ECS Fargate: $30-100/month
- RDS PostgreSQL: $15-50/month
- ElastiCache Redis: $15-50/month
- Data Transfer: $20-50/month
- **Total: ~$80-250/month**

**VPS (DigitalOcean/Linode):**
- VPS $20/month (4GB RAM)
- Includes PostgreSQL and Redis
- **Total: ~$20/month**

---

## Next Steps After Deployment

1. **Test the Application**:
   - Navigate to frontend URL
   - Check price data is loading
   - Verify API health endpoint
   - Test analysis endpoints

2. **Configure API Keys**:
   - Add Tradier API key (required)
   - Optionally add Alpha Vantage and Finnhub

3. **Test Data Fetching**:
   - Fetch price data for watchlist symbols
   - Verify caching is working
   - Check data validation

4. **Monitor Logs**:
   - Watch for errors
   - Check cache hit rates
   - Monitor API rate limits

5. **Set Up Monitoring**:
   - Configure alerts
   - Set up log aggregation
   - Enable health checks

---

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review API documentation: http://localhost:8000/docs
- Check health status: http://localhost:8000/health
- Review troubleshooting section above

---

**Remember**: The system is designed to work with or without all API keys. It will gracefully degrade to free sources (Yahoo Finance) if paid sources are not available, though with reduced functionality and data quality.