import logging
import asyncio
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.db import fetch_unprocessed_news, fetch_unprocessed_nse, upsert_news_insight, upsert_raw_news, upsert_nse_filings
from src.agent import start_agent
from src.helpers import pdf_reader, webpage_reader, parse_insight
from src.config import INSIGHT_REFRESH_TIME

logger = logging.getLogger(__name__)


def process_news():
    """
    Fetches the unprocessed news, parses the url/pdf and then compresses. 
    Finally get the news insight from the agent.
    """
    raw_news= fetch_unprocessed_news()
    for news in raw_news:
        if (news.get('category') and news.get('ticker_tags')) or (news.get('category') == 'macro' or news.get('category') == 'sector' and not news.get('ticker_tags')):
            if len(news.get('headline').strip()+news.get('summary').strip()) <= 60:
                parsed_body = webpage_reader(news["url"])
                if parsed_body and isinstance(parsed_body, str) and len(parsed_body) >= 800:
                    parsed_body = parsed_body[40:min(800, len(parsed_body))]
                news["parsed_text"] = parsed_body
        insight = asyncio.run(start_agent(news))
        parsed = parse_insight(insight)
        parsed["raw_news_id"] = news["id"]
        parsed['tickers'] = news.get('ticker_tags')
        parsed['raw_response'] = insight
        count = upsert_news_insight(parsed, "rss")
        logger.info(
            "Inserted %d rows in the news_insight table successfully", count)
        count = upsert_raw_news(parsed)
        logger.info("Updated %d rows in raw_news", count)
    nse_filings = fetch_unprocessed_nse()
    for nse in nse_filings:
        parsed_body = pdf_reader(nse["pdf_url"])
        if parsed_body and isinstance(parsed_body, str) and len(parsed_body) >= 800:
            parsed_body = parsed_body[40:min(800, len(parsed_body))]
        nse["parsed_text"] = parsed_body
        insight = asyncio.run(start_agent(nse))
        parsed = parse_insight(insight)
        parsed["nse_filing_id"] = nse["filing_id"]
        parsed['tickers'] = [nse.get('symbol')]
        parsed['raw_response'] = insight
        count = upsert_news_insight(parsed, "nse")
        logger.info(
            "Inserted %d rows in the news_insight table successfully", count)
        count = upsert_nse_filings(parsed)
        logger.info("Updated %d rows in nse_filing", count)


def start():
    """
    Schedules the get insight function to start the agent.
    """
    scheduler = BlockingScheduler(timezone='Asia/Kolkata')
    scheduler.add_job(
        process_news,
        trigger=IntervalTrigger(minutes=INSIGHT_REFRESH_TIME),
        id="get_insights",
        name="Get insights",
        misfire_grace_time=20,
        replace_existing=True,
        next_run_time=datetime.now(),
    )
    logger.info("Added the get insight job re-runs in every %d mins",
                INSIGHT_REFRESH_TIME)
    logger.info("Starting the scheduler now")
    scheduler.start()
