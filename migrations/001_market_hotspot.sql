CREATE TABLE IF NOT EXISTS market_instruments (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  watch_symbol VARCHAR(32) NOT NULL,
  underlying_asset VARCHAR(32) NOT NULL,
  venue VARCHAR(32) NOT NULL,
  target_venue VARCHAR(32) NOT NULL,
  product_type VARCHAR(32) NOT NULL,
  instrument_id VARCHAR(128) NOT NULL,
  quote_currency VARCHAR(16) NULL,
  quantity_unit VARCHAR(32) NULL,
  contract_multiplier DECIMAL(30,12) NULL,
  trading_status VARCHAR(32) NOT NULL,
  capabilities JSON NOT NULL,
  discovered_at DATETIME(3) NOT NULL,
  UNIQUE KEY uq_market_instrument (venue, product_type, instrument_id),
  KEY ix_market_watch_symbol (watch_symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS market_price_snapshot (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  instrument_id BIGINT UNSIGNED NOT NULL,
  source_ts DATETIME(3) NOT NULL,
  collected_at DATETIME(3) NOT NULL,
  available_at DATETIME(3) NOT NULL,
  last_price DECIMAL(30,12) NULL,
  price_change_24h DECIMAL(18,8) NULL,
  volume_24h DECIMAL(30,8) NULL,
  funding_rate DECIMAL(18,12) NULL,
  quality_status VARCHAR(32) NOT NULL,
  UNIQUE KEY uq_price_snapshot (instrument_id, source_ts),
  CONSTRAINT fk_price_instrument FOREIGN KEY (instrument_id) REFERENCES market_instruments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS market_oi_snapshot (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  instrument_id BIGINT UNSIGNED NOT NULL,
  source_ts DATETIME(3) NOT NULL,
  collected_at DATETIME(3) NOT NULL,
  oi_contracts DECIMAL(30,8) NULL,
  oi_usd DECIMAL(30,8) NULL,
  oi_unit VARCHAR(32) NOT NULL,
  quality_status VARCHAR(32) NOT NULL,
  UNIQUE KEY uq_oi_snapshot (instrument_id, source_ts, oi_unit),
  CONSTRAINT fk_oi_instrument FOREIGN KEY (instrument_id) REFERENCES market_instruments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS market_oi_metrics (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  instrument_id BIGINT UNSIGNED NOT NULL,
  as_of_ts DATETIME(3) NOT NULL,
  oi_change_1h DECIMAL(18,8) NULL,
  oi_change_4h DECIMAL(18,8) NULL,
  oi_change_24h DECIMAL(18,8) NULL,
  quality_status VARCHAR(32) NOT NULL,
  UNIQUE KEY uq_oi_metrics (instrument_id, as_of_ts),
  CONSTRAINT fk_metric_instrument FOREIGN KEY (instrument_id) REFERENCES market_instruments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS market_hotspot_runs (
  run_id CHAR(36) PRIMARY KEY,
  as_of_ts DATETIME(3) NOT NULL,
  ranking_mode VARCHAR(32) NOT NULL,
  config_version VARCHAR(32) NOT NULL,
  created_at DATETIME(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS market_hotspot_results (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  run_id CHAR(36) NOT NULL,
  instrument_id BIGINT UNSIGNED NOT NULL,
  quant_score DECIMAL(8,4) NULL,
  event_score DECIMAL(8,4) NULL,
  hotspot_score DECIMAL(8,4) NULL,
  scoring_profile VARCHAR(32) NOT NULL,
  score_quality VARCHAR(32) NOT NULL,
  hotspot_priority VARCHAR(16) NOT NULL,
  risk_status VARCHAR(16) NOT NULL,
  delivery_status VARCHAR(32) NOT NULL,
  reason_codes JSON NOT NULL,
  created_at DATETIME(3) NOT NULL,
  UNIQUE KEY uq_hotspot_result (run_id, instrument_id),
  CONSTRAINT fk_result_run FOREIGN KEY (run_id) REFERENCES market_hotspot_runs(run_id),
  CONSTRAINT fk_result_instrument FOREIGN KEY (instrument_id) REFERENCES market_instruments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE OR REPLACE VIEW vw_market_hotspot_latest AS
SELECT r.*
FROM market_hotspot_results r
JOIN (
  SELECT instrument_id, MAX(created_at) AS created_at
  FROM market_hotspot_results
  GROUP BY instrument_id
) latest ON latest.instrument_id = r.instrument_id AND latest.created_at = r.created_at;
