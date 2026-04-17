# Directory Structure

```
trading-dashboard/
│
├── backend/                          # FastAPI Python Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── config.py                 # Application configuration & settings
│   │   │
│   │   ├── api/                      # API Routes
│   │   │   ├── __init__.py
│   │   │   ├── routes.py             # Main API router
│   │   │   ├── price_routes.py       # Price data endpoints
│   │   │   └── analysis_routes.py    # Analysis endpoints
│   │   │
│   │   ├── models/                   # Data Models (Pydantic)
│   │   │   ├── __init__.py
│   │   │   ├── price_data.py         # ⭐ MASTER: 4 price types - NEVER COLLAPSE
│   │   │   ├── ohlcv.py              # OHLCV candle and series models
│   │   │   └── analysis.py           # Analysis result models
│   │   │
│   │   ├── engines/                  # Deterministic Analysis Engines
│   │   │   ├── __init__.py
│   │   │   ├── ict_engine.py         # ⭐ ICT: Structure, trend, displacement
│   │   │   ├── strat_engine.py       # ⭐ STRAT: Candle classification
│   │   │   ├── fvg_engine.py         # ⭐ FVG: Fair value gaps
│   │   │   └── scoring_engine.py     # ⭐ Explainable scoring (0-100)
│   │   │
│   │   ├── filters/                  # 11 Hard Filters
│   │   │   ├── __init__.py
│   │   │   ├── liquidity_filter.py
│   │   │   ├── spread_filter.py
│   │   │   ├── ict_confidence_filter.py
│   │   │   ├── strat_conflict_filter.py
│   │   │   ├── strat_freshness_filter.py
│   │   │   ├── structure_freshness_filter.py
│   │   │   ├── market_regime_filter.py
│   │   │   ├── data_completeness_filter.py
│   │   │   ├── gap_risk_filter.py
│   │   │   ├── volume_filter.py
│   │   │   ├── iv_filter.py
│   │   │   └── earnings_filter.py
│   │   │
│   │   ├── data_sources/             # Data Source Integration Layer
│   │   │   ├── __init__.py
│   │   │   ├── tradier_client.py     # Tradier API (real-time)
│   │   │   ├── yahoo_client.py       # Yahoo Finance (official close)
│   │   │   ├── alpha_vantage_client.py # Alpha Vantage (fallback)
│   │   │   ├── finnhub_client.py     # Finnhub (catalysts)
│   │   │   ├── data_normalizer.py    # ⭐ Unifies data from multiple sources
│   │   │   ├── data_validator.py     # ⭐ Validates data quality
│   │   │   ├── cache_manager.py      # ⭐ Redis caching layer
│   │   │   └── data_service.py       # ⭐ Integrated service layer
│   │   │
│   │   ├── utils/                    # Utilities
│   │   │   ├── __init__.py
│   │   │   └── date_utils.py
│   │   │
│   │   └── failure_handler.py        # ⭐ Circuit breaker pattern
│   │
│   ├── tests/                        # Backend Tests (not yet implemented)
│   │   ├── __init__.py
│   │   ├── test_engines.py
│   │   ├── test_filters.py
│   │   └── test_data_sources.py
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   └── Dockerfile.backend            # Backend Docker image
│
├── frontend/                         # Next.js Frontend
│   ├── app/
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # ⭐ Main dashboard page
│   │   └── globals.css               # Global styles
│   │
│   ├── src/
│   │   ├── components/               # React Components
│   │   │   ├── PriceBaseline.tsx     # ⭐ 4 price types separated
│   │   │   ├── SetupQualityBars.tsx  # ⭐ Scoring breakdown
│   │   │   └── [More components pending]
│   │   │
│   │   ├── lib/                      
│   │   │   └── api.ts                # ⭐ API client functions
│   │   │
│   │   ├── store/                    # State Management (Zustand)
│   │   │   └── tickerStore.ts        # ⭐ Ticker store
│   │   │
│   │   ├── types/                    # TypeScript Types
│   │   │   ├── ticker.types.ts       # Ticker data types
│   │   │   └── analysis.types.ts     # Analysis data types
│   │   │
│   │   ├── styles/                   # Styles
│   │   │   └── index.css             # Base styles
│   │   │
│   │   └── hooks/                    # Custom React Hooks
│   │       └── [Not yet implemented]
│   │
│   ├── public/                       # Static assets
│   │
│   ├── package.json                  # Node.js dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   ├── next.config.js                # Next.js configuration
│   └── Dockerfile.frontend           # Frontend Docker image (multi-stage)
│
├── infrastructure/                   # Infrastructure as Code
│   ├── kubernetes/                   # K8s manifests
│   │   ├── backend-deployment.yaml
│   │   └── frontend-deployment.yaml
│   │
│   └── monitoring/                   # Monitoring configuration
│       └── [Not yet implemented]
│
├── docs/                             # Documentation
│   └── [Not yet implemented]
│
├── docker-compose.yml                # Docker Compose configuration
├── README.md                         # ⭐ Main documentation
├── IMPLEMENTATION_PROGRESS.md        # ⭐ Implementation progress
├── DIRECTORY_STRUCTURE.md            # ⭐ This file
└── todo.md                           # ⭐ Task tracking

```

## Key Files Marked with ⭐

These are critical files that implement core requirements:

### Backend
- **`models/price_data.py`** - MASTER PRICE DATA MODEL with 4 explicit price types (NON-NEGOTIABLE requirement)
- **`engines/ict_engine.py`** - ICT structure detection with deterministic rules
- **`engines/strat_engine.py`** - STRAT candle classification
- **`engines/fvg_engine.py`** - Fair value gap detection
- **`engines/scoring_engine.py`** - Explainable scoring with component breakdowns
- **`data_sources/data_normalizer.py`** - Multi-source data normalization with fallback
- **`data_sources/data_validator.py`** - Comprehensive data validation
- **`data_sources/cache_manager.py`** - Redis caching with intelligent TTL management
- **`data_sources/data_service.py`** - Integrated data service layer
- **`failure_handler.py`** - Circuit breaker pattern for graceful degradation

### Frontend
- **`app/page.tsx`** - Main dashboard page
- **`components/PriceBaseline.tsx`** - Displays 4 price types explicitly separated
- **`components/SetupQualityBars.tsx`** - Shows scoring breakdown
- **`store/tickerStore.ts`** - Zustand state management
- **`lib/api.ts`** - API client functions

### Documentation
- **`README.md`** - Main project documentation
- **`IMPLEMENTATION_PROGRESS.md`** - Detailed progress tracking

## Data Flow Architecture

```
┌─────────────┐
│   Frontend  │ (Next.js + TypeScript)
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────────────────┐
│   API Routes            │ (FastAPI)
│  - price_routes.py      │
│  - analysis_routes.py   │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   Data Service          │ (data_service.py)
│  - Caching check        │
│  - Validation           │
│  - Failure handling     │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   Data Normalizer       │ (data_normalizer.py)
│  - Source priority      │
│  - Fallback chains      │
└──────┬──────────────────┘
       │
   ┌───┴──┬────────┬─────────┐
   │      │        │         │
┌──▼──┐ ┌▼───┐  ┌─▼────┐ ┌─▼─────┐
│Tradier│Yahoo│AlphaV│Finnhub│
│       │     │antage│       │
└──┬───┘ └────┘ └──────┘ └───────┘
   │
   ▼
┌──────────────────┐
│    External      │
│    APIs          │
└──────────────────┘
```

## Component Dependencies

### Backend Dependency Graph
```
main.py
  └── data_service.py
        ├── cache_manager.py
        ├── data_normalizer.py
        │     ├── tradier_client.py
        │     ├── yahoo_client.py
        │     ├── alpha_vantage_client.py
        │     └── finnhub_client.py
        ├── data_validator.py
        ├── failure_handler.py
        └── config.py

API Routes
  ├── data_service.py
  ├── engines/ (ict, strat, fvg, scoring)
  └── filters/ (11 hard filters)

Analysis Routes
  ├── engines/
  ├── filters/
  └── models/
```

### Frontend Dependency Graph
```
app/page.tsx
  ├── components/
  │   ├── PriceBaseline.tsx
  │   └── SetupQualityBars.tsx
  ├── store/tickerStore.ts
  ├── lib/api.ts
  └── types/
      ├── ticker.types.ts
      └── analysis.types.ts
```

## File Naming Conventions

- **Python files**: `snake_case.py` (e.g., `data_service.py`)
- **TypeScript files**: `PascalCase.ts` or `PascalCase.tsx` (e.g., `PriceBaseline.tsx`)
- **Components**: `PascalCase.tsx` (e.g., `SetupQualityBars.tsx`)
- **Hooks**: `useCamelCase.ts` (e.g., `useDataFetching.ts`)
- **Types**: `entity.types.ts` (e.g., `ticker.types.ts`)

## Environment Structure

### Development
```
Backend:  http://localhost:8000
Frontend: http://localhost:3000
Redis:    redis://localhost:6379
Database: postgresql://localhost:5432/trading_dashboard
```

### Production
```
Backend:  https://api.trading-dashboard.com
Frontend: https://dashboard.trading-dashboard.com
Redis:    Production Redis cluster
Database: Production PostgreSQL database
```

## Testing Structure (Planned)

```
tests/
├── unit/
│   ├── test_engines.py
│   ├── test_filters.py
│   └── test_data_sources.py
├── integration/
│   ├── test_api_integration.py
│   └── test_data_pipeline.py
└── e2e/
    └── test_trading_workflow.py
```

## Deployment Structure

```
docker-compose.yml (Development)
├── backend service
├── frontend service
├── redis service
└── postgres service

kubernetes/ (Production)
├── backend-deployment.yaml
├── frontend-deployment.yaml
├── redis-config.yaml
└── postgres-config.yaml
```

---

**Note**: This structure is designed for scalability and maintainability. Clear separation of concerns, modularity, and following best practices.