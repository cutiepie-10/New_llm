import os
import pytest

from src.db import fetch_unprocessed_news, fetch_unprocessed_nse, upsert_news_insight


py_test_mark = pytest.mark.skipif(
    "DATABASE_URL" not in os.environ,
    reason="DATABASE_URL not in environment",
)

INSIGHT = {
    'raw_news_id':'05bf3f4f-e6f6-4573-8908-38f743a80592',
    'ticker_tags':[],
    'sentiment':'bearish',
    'urgency_score':2,
    'catalyst_type':'other',
    'catalyst_summary':'data',
    'is_market_moving':False,
    'raw_response':"",
    'nse_filing_id':'2e1e1e241411-1245124dsf-e332df2f23'
}
def test_fetch_unprocessed_news():
    """
    Tests the news fetch function
    """
    news = fetch_unprocessed_news()
    assert len(news) > 5
    for n in news:
        assert not n.get['category'] == ['other'] and not n.get['ticker_tags']


def test_fetch_unprocessed_nse():
    """
    Tests the nse fetch function
    """
    nse = fetch_unprocessed_nse()
    assert len(nse) > 5

def test_upsert_insight():
    """
    Tests whether the upsert insight function works
    """
    assert upsert_news_insight(INSIGHT,'rss')>1
    assert upsert_news_insight(INSIGHT,'nse')>1
