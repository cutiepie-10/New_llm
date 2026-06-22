import os
import logging
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec
from llama_index.tools.wikipedia import WikipediaToolSpec
from llama_index.llms.groq import Groq
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.prompts import RichPromptTemplate
from workflows.retry_policy import (
    retry_policy,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


from src.config import MODEL, MAX_TOKENS, GROQ_API_KEY


logger = logging.getLogger(__name__)


async def start_agent(feed: dict) -> str:
    """
    Starts the agent. Returns the response given by the agent.
    """
    llm = Groq(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=0.3,
        api_key=GROQ_API_KEY
    )
    policy = retry_policy(
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        wait=wait_exponential(multiplier=1, exp_base=2, max=30),
        stop=stop_after_attempt(2),
    )

    tools = []
    for tool in WikipediaToolSpec().to_tool_list():
        tools.append(tool)
    for tool in DuckDuckGoSearchToolSpec().to_tool_list():
        tools.append(tool)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    system_prompt_path = os.path.join(current_dir, "system_prompt.txt")
    with open(system_prompt_path, "r", encoding='utf-8') as file:
        system_prompt = file.read()
    agent = ReActAgent(
        tools=tools,
        llm=llm,
        verbose=True,
        system_prompt=system_prompt,
        retry_policy=policy,
    )
    template_str = """
    Providing the input information for the filing or the news
    ---------
        headline: {{headline}}
        summary: {{summary}}
        parsed_text:{{parsed_text}}
    ---------
    Now based on the input above tell the sentiment, urgency score, is market moving, catalyst type and catalyst summary.
    """

    template = RichPromptTemplate(template_str)
    prompt = template.format(
        headline=feed.get('headline') or feed.get("subject"),
        summary=feed.get("summary"), parsed_text=feed.get("parsed_text"), ticker_tags=feed.get(
            "ticker_tags")
        or feed.get("symbol"), category=feed.get("category") or feed.get("filing_type")
    )
    response = await agent.run(
        prompt, max_iterations=5, early_stopping_method="generate"
    )
    res = response.response
    logger.info("Final answer has %d tokens and final answer is %s", len(res.blocks[0].text),res.blocks[0].text)
    return res.blocks[0].text
