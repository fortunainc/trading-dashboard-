# Quick Start Guide - Trading Dashboard

## 🚀 5-Minute Setup

### Step 1: Get Your Tradier API Key (Required)

1. Go to: https://developer.tradier.com
2. Sign up (free tier available)
3. Create an application
4. Copy your API key

**Why needed?** Primary source for real-time trading data (quotes, options, live prices)

### Step 2: Configure Environment

```bash
cd trading-dashboard/backend
cp .env.example .env
nano .env  # Edit these lines:
```

**Minimum配置:**
```bash
TRADIER_API_KEY=your_actual_key_here
```

### Step 3: Start Everything

```bash
cd trading-dashboard  # Back to root
docker-compose up -d
```

### Step 4: Open Browser

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Step 5: Test It

```bash
# Test backend
curl http://localhost:8000/health

# Test data fetching
curl http://localhost:8000/api/price/NVDA
```

## 🐛 Common Issues

**"Connection refused"**: Run `docker-compose up -d`

**"API Key invalid"**: Check .env file for typos

**"Module not found"**: Run `docker-compose down && docker-compose up --build`

## 📦 Stopping Services

```bash
docker-compose down
```

## 🔍 Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

## 📱 Additional API Keys (Optional)

While Tradier is required, these add features:

- **Alpha Vantage** (https://www.alphavantage.co): Fallback historical data
- **Finnhub** (https://finnhub.io): News and catalysts

Add to `.env`:
```bash
ALPHA_VANTAGE_API_KEY=your_key
FINNHUB_API_KEY=your_key
```

## 🎯 What's Working?

✅ Multi-source data aggregation (Tradier → Yahoo → AlphaVantage)
✅ Real-time price data with 4 price types separated
✅ ICT, STRAT, FVG engines (deterministic, rule-based)
✅ 11 hard filters for setup quality
✅ Redis caching with intelligent TTL
✅ Circuit breaker failure handling
✅ Beautiful dark-mode dashboard

## 🚧 What's Next?

1. Replace mock data with real API integration
2. Implement Night-Before Prep mode
3. Implement Live Execution mode
4. Add more UI components
5. Deploy to cloud (see DEPLOYMENT.md)

## 📚 Full Documentation

- **README.md**: Complete project overview
- **DEPLOYMENT.md**: Detailed deployment guide
- **DIRECTORY_STRUCTURE.md**: Code structure
- **IMPLEMENTATION_PROGRESS.md**: Development status

## 💡 Tips

- Use `docker-compose restart backend` to restart just the backend
- Use `docker-compose logs -f backend --tail 100` for recent backend logs
- Check `/health` endpoint often to verify system status
- The system works without optional API keys (falls back to free sources)

## ⚡ Performance

- **Development**: Runs on any machine with 2GB RAM and Docker
- **Production**: Needs 4GB RAM minimum
- **API Calls**: Tradier free tier = limited, Paid = unlimited

## 🎨 Features

### Price Data
- ✅ Official Close (previous day)
- ✅ After Hours (3 minute TTL)
- ✅ Pre-market (3 minute TTL)
- ✅ Live (1 minute TTL)

### Analysis
- ✅ ICT Structure & Trend
- ✅ STRAT Candle Classification
- ✅ FVG Fair Value Gaps
- ✅ Explainable Scoring (0-100)

### Quality
- ✅ 11 Hard Filters
- ✅ Data Validation
- ✅ Circuit Breakers
- ✅ Graceful Degradation

---

**Need help?** Check `docker-compose logs -f` or review `DEPLOYMENT.md`