# Options Trading Dashboard

A production-grade options trading dashboard with two mandatory modes: Night-Before Prep and Live Execution.

## Project Status

### ✅ Completed

**Phase 1: Project Setup & Infrastructure**
- Complete project structure with backend (FastAPI) and frontend (Next.js)
- Docker configurations for both services
- Data models with explicit price type separation (official_close, after_hours, premarket, live)
- Configuration system with environment variables

**Phase 2: Data Pipeline Foundation**
- **Data Source Clients:**
  - Tradier API client - Real-time options data and live prices
  - Yahoo Finance client - Official close data (yfinance)
  - Alpha Vantage client - Fallback historical data
  - Finnhub client - Catalyst data (news, events, earnings)
  
- **Data Normalization Layer** (`data_normalizer.py`):
  - Unifies data from multiple sources into consistent format
  - Source priority system with automatic fallback
  - Handles all 4 price types explicitly (never collapses them)
  - Returns validation results with source tracking
  
- **Data Validation** (`data_validator.py`):
  - Price data validation (range, freshness, consistency)
  - OHLCV validation (minimum candles, data quality)
  - Live price validation (bid/ask spread, OHLC consistency)
  - Time series consistency checks
  - Configurable strict mode
  
- **Redis Cache Manager** (`cache_manager.py`):
  - Intelligent caching with differentiated TTLs:
    - Live quotes: 1 minute
    - After-hours/premarket: 3 minutes
    - Official close: 1 hour
    - Intraday OHLCV: 1 minute
    - Daily OHLCV: 30 minutes
    - Analysis results: 5 minutes
  - Cache invalidation by symbol
  - Cache statistics monitoring
  
- **Data Service Layer** (`data_service.py`):
  - Integrated service combining all data sources
  - Automatic caching with TTL management
  - Data validation before caching
  - Circuit breaker pattern with failure handling
  - Graceful degradation with fallback chains
  - Batch operations support
  
**Phase 3: Core Analysis Engines**
- **ICT Engine** (`ict_engine.py`):
  - Trend detection using HH/HL rules
  - BOS/CHoCH detection
  - Displacement detection (15m: 1.5%, 1h: 2.0%)
  - Liquidity sweep detection
  - All thresholds explicitly defined
  
- **STRAT Engine** (`strat_engine.py`):
  - Candle classification (Type 1, 2U, 2D, Type 3)
  - Continuation body threshold: 60%
  - Rejection wick threshold: 40%
  - Balance body threshold: 30%
  
- **FVG Engine** (`fvg_engine.py`):
  - Fair value gap detection
  - Freshness tracking (Fresh < 1 day, Ageing 1-3 days, Stale > 3 days)
  - Test status updating
  
- **Scoring Engine** (`scoring_engine.py`):
  - Explainable 0-100 scores with component breakdowns
  - Scalp weights: ICT 30%, STRAT 30%, FVG 20%, Confluence 20%
  - Swing weights: All components 25%
  - Detailed score composition available

**Phase 4: Hard Filters**
- All 11 hard filters implemented:
  1. Liquidity filter - Grade A/B requirement
  2. Spread filter - Max 10% (scalp) / 5% (swing)
  3. ICT confidence filter - Min 60/100
  4. STRAT conflict filter - Reject conflicts
  5. STRAT freshness filter - Max 24 hours
  6. Structure freshness filter - Max 8 hours
  7. Market regime filter - Bad regimes, SPY -2%, VIX > 35
  8. Data completeness filter - All timeframes required
  9. Gap risk filter - Max 5% gap, earnings stand-down
  10. Volume filter - Min 50% average, min 500K shares
  11. IV filter - IV Rank 10-90
  12. Earnings filter - 7-day stand-down

**Phase 7: Backend API (Partial)**
- FastAPI application with CORS
- Health check endpoint with cache stats
- Price data endpoints (with mock data)
- Analysis endpoints (with mock data)
- Main router with sub-routers

**Phase 8: Frontend Dashboard (Partial)**
- Next.js 14 with TypeScript
- Tailwind CSS with dark mode
- State management with Zustand
- API client with Axios
- **PriceBaseline component** - Displays all 4 price types explicitly separated
- **SetupQualityBars component** - Shows scoring breakdown with progress bars
- Main dashboard page with mode toggle

## Architecture

### Non-Negotiable Requirements Implemented

✅ **Explicit Price Type Separation**: Four distinct price types (official_close, after_hours, premarket, live) are never collapsed or combined. Each has its own data structure in models and UI.

✅ **Deterministic Engines**: All three engines (ICT, STRAT, FVG) use purely rule-based, deterministic logic with explicitly defined thresholds. No AI or black-box components.

✅ **Explainable Scoring**: Scores show component breakdowns, enabling transparency in trading decisions.

✅ **Circuit Breaker Pattern**: Graceful degradation with failure thresholds (3 failures) and cooldown periods (300 seconds).

✅ **Type Safety**: TypeScript throughout frontend with comprehensive type definitions matching backend models.

## Tech Stack

### Backend
- **Python 3.11** - Latest Python version
- **FastAPI 0.104.1** - Modern, fast web framework
- **Pydantic** - Data validation and settings
- **Redis 5.0** - High-performance caching
- **httpx/aiohttp** - Async HTTP clients
- **yfinance** - Yahoo Finance data
- PostgreSQL (planned) - Persistent storage

### Frontend
- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript 5.0** - Type safety
- **Tailwind CSS 3.3** - Utility-first styling
- **Zustand 4** - Lightweight state management
- **Chart.js 4** - Data visualization
- **Axios** - HTTP client

## Installation

### Backend

```bash
cd trading-dashboard/backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### Frontend

```bash
cd trading-dashboard/frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API URLs
```

## Configuration

### Environment Variables

Required environment variables (see `.env.example`):

```bash
# API Keys
TRADIER_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trading_dashboard

# Redis
REDIS_URL=redis://localhost:6379/0

# Analysis
WATCHLIST=NVDA,META,TSLA,AAPL,GOOGL,AMZN,MSFT
```

## Running

### Backend (Development)

```bash
cd trading-dashboard/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Development)

```bash
cd trading-dashboard/frontend
npm run dev
```

### Using Docker

```bash
# Build backend
docker build -f Dockerfile.backend -t trading-dashboard-backend .

# Build frontend
docker build -f Dockerfile.frontend -t trading-dashboard-frontend .

# Run with docker-compose (create file first)
docker-compose up
```

## API Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check with cache stats

### Price Data
- `GET /api/price/{symbol}` - Get price data for a symbol
- `GET /api/price/batch` - Batch price data for multiple symbols

### Analysis
- `POST /api/analysis/prep` - Run night-before prep analysis
- `POST /api/analysis/live` - Run live execution analysis

## Data Flow

```
User Request → API Route → Data Service
                              ↓
                    Check Cache → Cache Hit → Return
                              ↓
                      Cache Miss → Normalizer
                              ↓
                    Try Sources (Tradier → Yahoo → AlphaVantage)
                              ↓
                    Validator → Success → Cache → Return
                              ↓
                    Validation Fail → Return errors
```

## Key Features

### 1. Multi-Source Data Aggregation
- Primary: Tradier (real-time)
- Secondary: Yahoo Finance (official close)
- Fallback: Alpha Vantage (historical)
- Catalysts: Finnhub (news, events)

### 2. Intelligent Caching
- Different TTLs based on data type
- Automatic invalidation
- Cache statistics monitoring
- Option to cache only validated data

### 3. Data Validation
- Price range checks
- Freshness validation
- OHLCV consistency
- Time series validation
- Configurable strict mode

### 4. Failure Handling
- Circuit breaker pattern
- Automatic fallback chains
- Graceful degradation
- Service status monitoring

### 5. Deterministic Engines
- ICT: Structure, trend, displacement
- STRAT: Candle classification
- FVG: Gap detection with freshness
- Scoring: Explainable, weighted components

## Next Steps

### Immediate Priorities

1. **Replace Mock Data**: Integrate real data fetching in API routes using the Data Service layer

2. **"Do Not Trade" Framework**: Implement stand-down conditions and warnings

3. **Mode Implementation**: Complete Night-Before Prep and Live Execution modes

4. **Additional UI Components**: 
   - Header with lockout timer
   - Do Not Trade warnings
   - Active Setups Table
   - Contract Suggestions
   - Market Regime Indicator
   - Session Clock

5. **Contract Selection**: Implement scalp and swing contract selectors

6. **Database Integration**: Set up PostgreSQL for journal and persistence

## Testing

```bash
# Backend tests
cd trading-dashboard/backend
pytest

# Frontend tests
cd trading-dashboard/frontend
npm test
```

## Contributing

This is a production trading system. Changes should:
- Maintain price type separation
- Keep engines deterministic
- Preserve explainable scoring
- Test failure scenarios
- Document any new filters or thresholds

## License

Internal use only.