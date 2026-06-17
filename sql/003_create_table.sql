CREATE EXTENSION IF NOT EXISTS pgcrypto; -- loads gen_random_uuid()


CREATE TABLE IF NOT EXISTS news_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_news_id UUID REFERENCES raw_news(id),
    nse_filing_id TEXT REFERENCES nse_filings(filing_id),
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    tickers TEXT[],
    sentiment TEXT, -- bearish|bullish|neutral
    urgency_score INT, -- 1 - 5
    catalyst_type TEXT, --earning | regulatory | corporate | macro | other
    catalyst_summary TEXT, -- 1- sentence, what happened and why it matters
    is_market_moving BOOLEAN,
    raw_response TEXT --full llm output for debugging 
);