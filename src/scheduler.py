import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.db import fetch_unprocessed_news, fetch_unprocessed_nse, upsert_news_insight
from src.agent import start_agent
from src.helpers import pdf_reader,webpage_reader
from src.config import INSIGHT_REFRESH_TIME


logger = logging.getLogger(__name__)

def get_insights():
    raw_news = fetch_unprocessed_news()
    for news in raw_news:
        news["parsed_text"] = webpage_reader(news["url"])
        insight = start_agent(news)
        insight["raw_news_id"] = news["id"]
        upsert_news_insight(insight, type="rss")
    nse_filings = fetch_unprocessed_nse()
    for nse in nse_filings:
        nse["parsed_text"] = pdf_reader(nse["pdf_url"])
        insight = start_agent(nse)
        insight["nse_filing_id"] = nse["filing_id"]
        upsert_news_insight(insight, type="nse")


def start():
    scheduler = BlockingScheduler(timezone='Asia/Kolkata')
    scheduler.add_job(
        get_insights,
        trigger= IntervalTrigger(minutes=INSIGHT_REFRESH_TIME),
        id="get_insights",
        name="Gets the news insights from parsed body and description",
        misfire_grace_time= 20,
        replace_existing=True,
    )
    logger.info("Added the get insight job re-runs in every %d mins",INSIGHT_REFRESH_TIME)
    logger.info("Starting the scheduler now")
    scheduler.start()