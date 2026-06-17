import logging
from io import BytesIO
import json
import re

import requests

from llama_parse import LlamaParse
from firecrawl import Firecrawl
from src.config import USER_AGENT, LLAMA_API_KEY, FIRECRAWL_API_KEY, COMPRESSOR

logger = logging.getLogger(__name__)


def pdf_reader(url: str) -> str:
    """To read the pdf from nse filing. It uses the Llama parse.
        Output :
        str-> The joined document string from the Llama Parse.
    """
    headers = {
        'User-Agent': USER_AGENT,
    }
    res = requests.get(url=url, timeout=12, headers=headers)
    pdf_buffer = BytesIO(res.content)
    parser = LlamaParse(api_key=LLAMA_API_KEY,
                        results="markdown",
                        verbose=True,
                        )
    documents = parser.load_data(pdf_buffer)
    return '\n \n'.join([doc.text for doc in documents])


def webpage_reader(url: str) -> str:
    """To read the news webpage from raw_news using Firecrawl."""
    firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY)
    scraped = firecrawl.scrape(
        url, formats=["markdown"], only_main_content=True)
    return scraped.markdown


def parse_insight(insight: str) -> dict:
    """
    Parses the json string to python dictionary given by the agent reponse
    """
    lower_text = insight.lower()
    json_match = re.search(r'\{.*\}', lower_text, re.DOTALL)
    if not json_match:
        raise ValueError('No json found in the returned response')
    raw_json_str = json_match.group(0)
    parsed_dict = json.loads(raw_json_str.strip())
    logger.info("Parsed json to python dictionary object: \n%s", parsed_dict)
    return parsed_dict


def compress_article(article: str) -> str:
    """
    Compresses the pdf or the webpage content
    """
    if len(article) > 500:
        chunks = [' '.join(article[i:i+400])
                  for i in range(0, len(article), 400)]
        compressed_chunks = []
        for chunk in chunks:
            if not chunk.strip():
                continue
            compressed = COMPRESSOR.compress_prompt_llmlingua2(
                chunk,
                rate=0.4,
                target_token=120,
            )
            compressed_chunks.append(compressed['compressed_prompt'].strip())
        article = "".join(compressed_chunks)
        logger.info("Compressed article to %d tokens", len(article))
    return article
