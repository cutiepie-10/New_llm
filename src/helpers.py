import requests
from io import BytesIO
from llama_parse import LlamaParse
from firecrawl import Firecrawl
from src.config import USER_AGENT, LLAMA_API_KEY, FIRECRAWL_API_KEY

from llama_index.core.tools import FunctionTool


def pdf_reader(url: str) -> str:
    """To read the pdf from nse filing. It uses the Llama parse.
        Input args:
         "url": str 
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
                        verbose=True)
    documents = parser.load_data(pdf_buffer)
    return '\n \n'.join([doc.text for doc in documents])


def webpage_reader(url: str) -> str:
    """To read the news webpage from raw_news using Firecrawl."""
    firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY)
    scraped = firecrawl.scrape(url, formats=["markdown"])
    return scraped.markdown
