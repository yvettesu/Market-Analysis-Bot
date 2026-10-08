# Market-Analysis-Bot

Market Hotspot Intelligence System for crypto perpetuals and stock-linked trading products. The system keeps instruments distinct by venue and product type, detects quantitative market anomalies, attributes relevant news events, validates tradeability, and produces a BI-ready hotspot ranking.

## MVP Scope

- Manual market snapshots and supported historical backfills.
- MySQL-backed instrument metadata, market snapshots, OI metrics, news events, and hotspot rankings.
- Product-aware routing for crypto perpetuals, stock perpetuals, rTokens, CFDs, and stock references.
- Quantitative scoring, event attribution, tradeability risk checks, and JSON/Markdown/BI exports.
- No scheduler, automatic campaign delivery, Lark alerts, API credentials, or application implementation in this initial commit.

## Architecture

```mermaid
flowchart TD
    A[Product Discovery] --> B[Instrument Registry]
    C[Binance / OKX / Bybit / Bitget APIs] --> D[Market Ingestion]
    E[News Sources / Official Announcements] --> F[Event Attribution]
    B --> D
    D --> G[(MySQL Market Snapshots)]
    G --> H[Metric Engine]
    F --> I[Event Engine]
    H --> J[Quant Score]
    I --> K[Event Score]
    D --> L[Tradeability Gate]
    J --> M[Hotspot Ranking]
    K --> M
    L --> M
    M --> N[BI Results Table and Latest View]
    N --> O[JSON and Markdown Review Export]
```

## Core Principles

- An identical underlying asset does not make products interchangeable. Price, OI, order book, and tradeability data stay bound to their exact venue and instrument ID.
- Market priority and tradeability are separate. A P0 hotspot can require review or be prohibited from trade-directed delivery.
- Missing, stale, unsupported, and insufficient-history metrics are explicit states. The system never fabricates an OI change or redistributes unavailable metric weights.
