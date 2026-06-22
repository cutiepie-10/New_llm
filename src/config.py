import os
from dotenv import load_dotenv

load_dotenv()

USER_AGENT = os.environ['USER_AGENT']
LLAMA_API_KEY = os.environ['LLAMA_API_KEY']
FIRECRAWL_API_KEY = os.environ['FIRECRAWL_API_KEY']

MODEL = "openai/gpt-oss-120b"
MAX_TOKENS = 512
GROQ_API_KEY = os.environ['GROQ_API_KEY']

INSIGHT_REFRESH_TIME = int(os.environ['INSIGHT_REFRESH_TIME'])

DATABASE_URL = os.environ['DATABASE_URL']
