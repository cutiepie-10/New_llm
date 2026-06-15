import os
from dotenv import load_dotenv

load_dot_env()

USER_AGENT = os.environ['USER_AGENT']
LLAMA_API_KEY = os.environ['LLAMA_API_KEY']
FIRECRAWL_API_KEY = os.environ['FIRECRAWL_API_KEY']

MODEL= "llama-3.3-70b-versatile"
MAX_TOKENS = 512
GROQ_API_KEY = os.environ['GORQ_API_KEY']

INSIGHT_REFRESH_TIME = os.environ['INSIGHT_REFRESH_TIME']
