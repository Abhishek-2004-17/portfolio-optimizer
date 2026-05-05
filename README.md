# Portfolio Optimizer

A full-stack portfolio optimization platform that helps you build, analyze, and optimize investment portfolios using modern portfolio theory. Fetches real market data via Yahoo Finance and computes efficient frontier allocations, risk metrics, and portfolio comparisons.

**Stack:** FastAPI + PostgreSQL (backend) · React + TypeScript + Tailwind (frontend)

---

## Features

- **Portfolio Builder** — Add tickers, set target weights, and create portfolios
- **Efficient Frontier** — Mean-variance optimization via PyPortfolioOpt (max Sharpe, min volatility)
- **Risk Analytics** — VaR, CVaR, max drawdown, annualized volatility, Sharpe/Sortino ratios
- **Correlation Matrix** — Visualize asset return correlations
- **Portfolio Comparison** — Side-by-side comparison of multiple portfolios
- **Smart Suggestions** — AI-generated ticker recommendations based on existing holdings

---

## Architecture

```
portfolio-optimizer/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/v1/endpoints/ # REST endpoints (portfolios, data, optimization, risk, suggestions)
│   │   ├── core/             # Config & exceptions
│   │   ├── db/               # SQLAlchemy session, init
│   │   ├── models/           # ORM models
│   │   ├── repositories/     # Data access layer
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic
│   │   └── tests/            # pytest test suite
│   ├── alembic/              # Database migrations
│   ├── pyproject.toml        # Python dependencies (uv)
│   └── requirements.txt      # Fallback for pip
├── frontend/                 # React + TypeScript app
│   ├── src/
│   │   ├── api/              # Axios API clients
│   │   ├── components/       # Charts, layout, UI components
│   │   ├── pages/            # Route pages (Builder, Dashboard, Risk, Compare)
│   │   ├── store/            # Zustand global state
│   │   └── types/            # TypeScript type definitions
│   └── package.json
└── README.md
```

---

## Prerequisites

- **Python 3.12+** (up to 3.13)
- **Node.js 20+** and npm
- **PostgreSQL 14+** (local install or Docker)
- **Docker** (optional, for containerized database)
- **[uv](https://docs.astral.sh/uv/)** (recommended) or pip

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Abhishek-2004-17/portfolio-optimizer.git
cd portfolio-optimizer
```

### 2. Database

You can set up PostgreSQL either with Docker or a local install.

#### Option A: Docker (recommended)

```bash
docker run -d \
  --name portfolio-db \
  -e POSTGRES_USER=portfolio \
  -e POSTGRES_PASSWORD=portfolio \
  -e POSTGRES_DB=portfolio_db \
  -p 5432:5432 \
  postgres:16
```

This creates a PostgreSQL 16 container with:
- **User:** `portfolio`
- **Password:** `portfolio`
- **Database:** `portfolio_db`
- **Port:** `5432`

To stop/restart the container later:

```bash
docker stop portfolio-db
docker start portfolio-db
```

To remove the container entirely:

```bash
docker rm -f portfolio-db
```

#### Option B: Local PostgreSQL

```bash
psql -U postgres
```

```sql
CREATE USER portfolio WITH PASSWORD 'portfolio';
CREATE DATABASE portfolio_db OWNER portfolio;
```

### 3. Backend

```bash
cd backend

# Option A: Using uv (recommended)
uv sync

# Option B: Using pip with virtualenv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
DATABASE_URL=postgresql+psycopg2://portfolio:portfolio@localhost:5432/portfolio_db
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
RISK_FREE_RATE=0.04
```

### 4. Create database tables

Alembic handles all table creation. The initial migration creates the full schema:

```bash
cd backend
alembic upgrade head
```

This creates the following tables and columns:

**`portfolios`** — Stores user portfolios
| Column           | Type                     | Description              |
| ---------------- | ------------------------ | ------------------------ |
| `id`             | `INTEGER` (PK)           | Auto-increment ID        |
| `name`           | `VARCHAR(100)`           | Portfolio name           |
| `description`    | `TEXT`                   | Optional description     |
| `base_currency`  | `CHAR(3)`                | Currency code (e.g. USD) |
| `initial_capital`| `NUMERIC(18,2)`          | Starting capital amount  |
| `created_at`     | `TIMESTAMPTZ`            | Creation timestamp       |
| `updated_at`     | `TIMESTAMPTZ`            | Last update timestamp    |

**`portfolio_assets`** — Holdings within a portfolio (FK → `portfolios.id`)
| Column           | Type                     | Description              |
| ---------------- | ------------------------ | ------------------------ |
| `id`             | `INTEGER` (PK)           | Auto-increment ID        |
| `portfolio_id`   | `INTEGER` (FK)           | Parent portfolio         |
| `ticker`         | `VARCHAR(20)`            | Stock ticker symbol      |
| `weight`         | `NUMERIC(8,6)`           | Portfolio weight (0–1)   |
| `shares`         | `NUMERIC(18,6)`          | Number of shares held    |
| `purchase_price` | `NUMERIC(18,4)`          | Price at purchase        |
| `added_at`       | `TIMESTAMPTZ`            | When asset was added     |

**`price_history`** — Cached OHLCV price data from Yahoo Finance
| Column           | Type                     | Description              |
| ---------------- | ------------------------ | ------------------------ |
| `id`             | `BIGINT` (PK)            | Auto-increment ID        |
| `ticker`         | `VARCHAR(20)`            | Stock ticker symbol      |
| `date`           | `DATE`                   | Trading date             |
| `open`           | `NUMERIC(18,6)`          | Opening price            |
| `high`           | `NUMERIC(18,6)`          | Highest price            |
| `low`            | `NUMERIC(18,6)`          | Lowest price             |
| `close`          | `NUMERIC(18,6)`          | Closing price            |
| `adj_close`      | `NUMERIC(18,6)`          | Adjusted close price     |
| `volume`         | `BIGINT`                 | Trading volume           |

**`optimization_results`** — Optimization run outputs (FK → `portfolios.id`)
| Column             | Type                     | Description                  |
| ------------------ | ------------------------ | ---------------------------- |
| `id`               | `INTEGER` (PK)           | Auto-increment ID            |
| `portfolio_id`     | `INTEGER` (FK)           | Parent portfolio             |
| `method`           | `VARCHAR(32)`            | Optimization method used     |
| `weights`          | `JSONB`                  | Optimized weight allocation  |
| `expected_return`  | `DOUBLE`                 | Expected annualized return   |
| `volatility`       | `DOUBLE`                 | Annualized volatility        |
| `sharpe_ratio`     | `DOUBLE`                 | Sharpe ratio of result       |
| `parameters`       | `JSONB`                  | Input parameters used        |
| `created_at`       | `TIMESTAMPTZ`            | When optimization ran        |

**`risk_metrics`** — Risk analysis results (FK → `portfolios.id`)
| Column               | Type                     | Description                       |
| -------------------- | ------------------------ | --------------------------------- |
| `id`                 | `INTEGER` (PK)           | Auto-increment ID                 |
| `portfolio_id`       | `INTEGER` (FK)           | Parent portfolio                  |
| `computed_at`        | `TIMESTAMPTZ`            | When metrics were computed        |
| `var_historical_95`  | `DOUBLE`                 | Historical VaR at 95% confidence  |
| `var_historical_99`  | `DOUBLE`                 | Historical VaR at 99% confidence  |
| `var_parametric_95`  | `DOUBLE`                 | Parametric VaR at 95%             |
| `var_parametric_99`  | `DOUBLE`                 | Parametric VaR at 99%             |
| `var_montecarlo_95`  | `DOUBLE`                 | Monte Carlo VaR at 95%            |
| `var_montecarlo_99`  | `DOUBLE`                 | Monte Carlo VaR at 99%            |
| `cvar_historical_95` | `DOUBLE`                 | Historical CVaR at 95%            |
| `cvar_historical_99` | `DOUBLE`                 | Historical CVaR at 99%            |
| `cvar_parametric_95` | `DOUBLE`                 | Parametric CVaR at 95%            |
| `cvar_parametric_99` | `DOUBLE`                 | Parametric CVaR at 99%            |
| `cvar_montecarlo_95` | `DOUBLE`                 | Monte Carlo CVaR at 95%           |
| `cvar_montecarlo_99` | `DOUBLE`                 | Monte Carlo CVaR at 99%           |
| `max_drawdown`       | `DOUBLE`                 | Maximum drawdown                  |
| `sharpe_ratio`       | `DOUBLE`                 | Portfolio Sharpe ratio            |
| `sortino_ratio`      | `DOUBLE`                 | Portfolio Sortino ratio           |
| `beta`               | `DOUBLE`                 | Portfolio beta vs market          |
| `annualised_return`  | `DOUBLE`                 | Annualized return                 |
| `annualised_volatility` | `DOUBLE`              | Annualized volatility             |
| `correlation_matrix` | `JSONB`                  | Asset correlation matrix          |

To drop all tables and start fresh:

```bash
alembic downgrade base
alembic upgrade head
```

### 5. Start the backend server

```bash
# With uv
uv run uvicorn app.main:app --reload --port 8001

# With pip (venv must be active)
uvicorn app.main:app --reload --port 8001
```

The API will be available at `http://localhost:8001`. Interactive docs at `http://localhost:8001/docs`.

### 6. Frontend

```bash
cd frontend

npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend automatically via Vite.

---

## Running Tests

```bash
cd backend

# With uv
uv run pytest

# With pip
pytest
```

---

## API Endpoints

| Method | Path                        | Description                      |
| ------ | --------------------------- | -------------------------------- |
| GET    | `/health`                   | Health check                     |
| GET    | `/api/portfolios`           | List all portfolios              |
| POST   | `/api/portfolios`           | Create a portfolio               |
| GET    | `/api/portfolios/{id}`      | Get portfolio by ID              |
| DELETE | `/api/portfolios/{id}`      | Delete a portfolio               |
| GET    | `/api/data/{ticker}`        | Fetch price data for a ticker    |
| POST   | `/api/optimization/optimize`| Run portfolio optimization       |
| POST   | `/api/risk/analyze`         | Compute risk metrics             |
| GET    | `/api/suggestions/{ticker}` | Get related ticker suggestions   |

Full interactive documentation is available at `/docs` when the backend is running.

---

## Environment Variables

| Variable               | Default                                                    | Description                    |
| ---------------------- | ---------------------------------------------------------- | ------------------------------ |
| `DATABASE_URL`         | `postgresql+psycopg2://portfolio:portfolio@localhost:5432/portfolio_db` | PostgreSQL connection string |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:5173"]`                                | Allowed CORS origins           |
| `RISK_FREE_RATE`       | `0.04`                                                     | Risk-free rate for Sharpe ratio|
| `DEFAULT_TRADING_DAYS` | `252`                                                      | Trading days per year          |

---

## License

MIT
