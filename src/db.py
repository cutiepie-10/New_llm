import logging
import psycopg2
import psycopg2.extras
from src.config import DATABASE_URL

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(
        dsn=DATABASE_URL
    )


def fetch_unprocessed_news() -> list[dict]:
    """
    Fetches the unprocessed news rows from the raw_news table.
    """
    sql = """
    SELECT id, url,source_id, headline, summary, ingested_at,
    ticker_tags, category, is_processed 
    FROM raw_news
    WHERE is_processed= FALSE
    ORDER BY ingested_at ASC,
    published_at ASC
    LIMIT 3;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curr:
            curr.execute(sql)
            res = curr.fetchall()
    unprocessed = [dict(r) for r in res]
    logger.info("Loaded %d unprocessed news", len(unprocessed))
    return unprocessed


def fetch_unprocessed_nse() -> list[dict]:
    """
    Fetched the unprocessed nse filings from nse_filings table
    """
    sql = """
    SELECT filing_id, pdf_url,symbol,subject, description, exchange, ingested_at,
    filing_type, is_processed, filing_date
    FROM nse_filings
    WHERE is_processed= FALSE
    ORDER BY ingested_at ASC,
    filing_date ASC
    LIMIT 2;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curr:
            curr.execute(sql)
            res = curr.fetchall()
    unprocessed = [dict(r) for r in res]
    logger.info("Loaded %d unprocessed nse_filing", len(unprocessed))
    return unprocessed


def upsert_news_insight(insight: dict, insight_type: str) -> int:
    """
     Inserts data into news_insight 
    """
    with get_connection() as conn:
        with conn.cursor() as curr:
            if insight_type == 'rss':
                curr.execute(
                    """
                    INSERT INTO news_insights(
                    raw_news_id, tickers, sentiment,
                    urgency_score, catalyst_type,
                    catalyst_summary, is_market_moving, raw_response
                    ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        insight.get("raw_news_id"),
                        insight.get("ticker_tags"),
                        insight.get("sentiment"),
                        insight.get("urgency_score"),
                        insight.get("catalyst_type"),
                        insight.get("catalyst_summary"),
                        insight.get("is_market_moving"),
                        insight.get("raw_response")
                    ))
            if insight_type == "nse":
                curr.execute(
                    """
                    INSERT INTO news_insights (
                    nse_filing_id,tickers, sentiment,
                    urgency_score, catalyst_type,
                    catalyst_summary, is_market_moving, raw_response
                    ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        insight.get("nse_filing_id"),
                        insight.get("ticker_tags"),
                        insight.get("sentiment"),
                        insight.get("urgency_score"),
                        insight.get("catalyst_type"),
                        insight.get("catalyst_summary"),
                        insight.get("is_market_moving"),
                        insight.get("raw_response")
                    ))
            return curr.rowcount


def upsert_raw_news(insight: dict) -> int:
    """
    Updates the raw news table.
    """
    with get_connection() as conn:
        with conn.cursor() as curr:
            curr.execute("""
                    UPDATE  raw_news
                    SET is_processed =%s ,
                        body = %s,
                        ticker_tags= %s
                    WHERE id= %s ;
                    """, (True, insight['body'], insight['ticker_tags'], insight["raw_news_id"],))
            return curr.rowcount


def upsert_nse_filings(insight: dict) -> int:
    """
    Updates the nse filing table.
    """
    with get_connection() as conn:
        with conn.cursor() as curr:
            curr.execute("""
                UPDATE  nse_filings
                SET is_processed =%s
                WHERE filing_id= %s;
                """, (True, insight["nse_filing_id"]))
            return curr.rowcount
