# Portfolio Optimization Platform - System Architecture

## Figure 1: High-Level System Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        FE[React Frontend<br/>TypeScript]
        UI[BuilderPage Component<br/>Charts & Forms]
    end

    subgraph "API Layer"
        API[FastAPI REST API<br/>Request/Response Validation]
        EP[Optimization Endpoints<br/>6 endpoints]
    end

    subgraph "Business Logic Layer"
        SVC[OptimizationService<br/>Core Algorithms]
    end

    subgraph "Data Access Layer"
        REPO[OptimizationResultRepository<br/>CRUD Operations]
    end

    subgraph "Database Layer"
        DB[(PostgreSQL Database)]
        PORT[Portfolio Table]
        OPT[Optimization Results Table]
        ASSET[Portfolio Assets Table]
    end

    subgraph "External Services"
        YF[yfinance<br/>Price Data]
        PF[PyPortfolioOpt<br/>Optimization Engine]
    end

    FE -->|HTTP JSON| API
    UI --> FE
    API --> EP
    EP --> SVC
    SVC -->|Fetch Prices| YF
    SVC -->|Run Optimization| PF
    EP -->|Save Results| REPO
    REPO --> DB
    DB --> PORT
    DB --> OPT
    DB --> ASSET

    style FE fill:#61dafb
    style API fill:#009688
    style SVC fill:#4caf50
    style DB fill:#3b82f6
    style YF fill:#f59e0b
    style PF fill:#ef4444
```

## Figure 2: Class Diagram - Core Domain Model

```mermaid
classDiagram
    %% Frontend Types
    class OptimizeRequest {
        +string[] tickers
        +string start_date
        +string end_date
        +float risk_free_rate
        +[float, float] weight_bounds
        +int? portfolio_id
        +float? total_portfolio_value
    }

    class OptimizeResponse {
        +string method
        +Dict~string, float~ weights
        +float expected_return
        +float volatility
        +float sharpe_ratio
        +Dict? discrete_allocation
        +float? leftover_cash
    }

    class FrontierResponse {
        +FrontierPoint[] points
        +FrontierPoint max_sharpe
        +FrontierPoint min_vol
        +AssetPoint[] asset_points
        +Dict? latest_prices
    }

    %% Backend Models
    class OptimizationResult {
        +int id
        +int portfolio_id
        +string method
        +JSONB weights
        +float expected_return
        +float volatility
        +float sharpe_ratio
        +JSONB parameters
        +datetime created_at
    }

    class Portfolio {
        +int id
        +string name
        +string description
        +string base_currency
        +float initial_capital
        +datetime created_at
        +datetime updated_at
    }

    class PortfolioAsset {
        +int id
        +int portfolio_id
        +string ticker
        +float weight
        +int? shares
    }

    class RiskMetric {
        +int id
        +int portfolio_id
        +string metric_type
        +float value
        +datetime calculated_at
    }

    %% Relationships
    Portfolio "1" --> "*" OptimizationResult : contains
    Portfolio "1" --> "*" PortfolioAsset : has
    Portfolio "1" --> "*" RiskMetric : measured by
    OptimizationResult --> OptimizeResponse : maps to
```

## Figure 3: Service Layer Architecture

```mermaid
classDiagram
    class OptimizationService {
        <<Service Layer>>
        +max_sharpe(tickers, dates, rate) dict
        +min_volatility(tickers, dates) dict
        +target_return(tickers, target) dict
        +target_risk(tickers, volatility) dict
        +efficient_frontier(tickers, dates) dict
        -_download_prices(tickers, dates) DataFrame
        -_compute_mu_sigma(prices) tuple
        -_make_ef(mu, sigma) EfficientFrontier
    }

    class OptimizationResultRepository {
        <<Repository Layer>>
        +save_result(db, portfolio_id) OptimizationResult
        +get_by_portfolio(db, id) list
        +get_history(db, id, limit) list
    }

    class EfficientFrontier {
        <<External Library>>
        +max_sharpe(risk_free_rate)
        +min_volatility()
        +efficient_return(target)
        +efficient_risk(target)
        +clean_weights()
        +portfolio_performance()
    }

    class DiscreteAllocation {
        <<External Library>>
        +lp_portfolio()
    }

    OptimizationService --> EfficientFrontier : uses
    OptimizationService --> DiscreteAllocation : uses
    OptimizationService --> OptimizationResultRepository : persists
```

## Figure 4: Sequence Diagram - Optimization Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as BuilderPage
    participant API as FastAPI Router
    participant SVC as OptimizationService
    participant YF as yfinance
    participant PF as PyPortfolioOpt
    participant DB as Database

    User->>UI: Enter tickers & parameters
    UI->>UI: Validate form (Zod)
    UI->>API: POST /efficient-frontier

    API->>API: Validate request (Pydantic)
    API->>SVC: efficient_frontier(tickers, dates)

    SVC->>YF: download(tickers, start, end)
    YF-->>SVC: Price DataFrame

    SVC->>SVC: Compute expected returns
    SVC->>SVC: Compute covariance matrix

    loop For each frontier point
        SVC->>PF: efficient_risk(target_volatility)
        PF-->>SVC: weights, performance
    end

    SVC-->>API: FrontierResponse
    API-->>UI: JSON Response
    UI->>UI: Render charts
    UI->>User: Display results

    opt User saves portfolio
        User->>UI: Click "Save Portfolio"
        UI->>API: POST /portfolios
        API->>DB: INSERT portfolio
        DB-->>API: portfolio_id
        API-->>UI: Success
    end
```

## Architectural Patterns Summary

| Layer | Responsibility | Technology |
|-------|---------------|------------|
| **Presentation** | UI rendering, form validation, data visualization | React, TypeScript, TanStack Query |
| **API Gateway** | HTTP routing, request/response validation, error handling | FastAPI, Pydantic |
| **Domain Logic** | Portfolio optimization, efficient frontier calculation | NumPy, Pandas, PyPortfolioOpt |
| **Data Access** | Database persistence, query abstraction | SQLAlchemy ORM |
| **External** | Market data, optimization algorithms | yfinance, PyPortfolioOpt |
| **Database** | Persistent storage, relational integrity | PostgreSQL |

## Key Design Decisions

1. **Layered Architecture**: Separation of concerns with clear boundaries between presentation, business logic, and data layers.

2. **Service Layer Pattern**: `OptimizationService` encapsulates all portfolio optimization algorithms, independent of API concerns.

3. **Repository Pattern**: `OptimizationResultRepository` abstracts database operations, enabling easy testing and potential data source changes.

4. **DTO Pattern**: Pydantic schemas separate API contracts from domain models, allowing independent evolution.

5. **Stateless API**: FastAPI endpoints are stateless; all required data is passed in requests.

6. **Client-Side Interpolation**: Risk tolerance slider performs local interpolation on frontier data, avoiding unnecessary API calls.
