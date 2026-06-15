import json
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec
from llama_index.tools.wikipedia import WikipediaToolSpec
from llama_index.llms.groq import Groq
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.prompts import RichPromptTemplate
from src.config import MODEL, MAX_TOKENS, GROQ_API_KEY

async def start_agent(feed:dict)->dict:
    llm= Groq(
        model = MODEL,
        max_tokens = MAX_TOKENS,
        temperature= 0.1,
        api_key = GROQ_API_KEY
    )
    tools=[]
    tools.append(WikipediaToolSpec.to_tool_list())
    tools.append(DuckDuckGoSearchToolSpec.to_tool_list())
    agent = ReActAgent.from_tools(
        tools = tools,
        llm = llm,
        verbose = True
    )
    template_str= """
    Providing the input information for the filing or the news
    ---------
        headline: {{headline}}
        summary: {{summary}}
        parsed_text:{{parsed_text}}
        category:{{category}}
        ticker_tags:{{ticker_tags}}
    ---------
    Now based on the input above tell the sentiment, urgency score, is market moving, catalyst type and catalyst summary.
    """
    template = RichPromptTemplate(template_str)
    prompt = template.format_messages(headline= feed['headline'] or feed["subject"] , summary= feed["summary"], parsed_text= feed["parsed_text"], 
    ticker_tags=feed["ticker_tags"] or feed["symbol"], category= feed["category"] or feed["filing_type"])
    with open("system_prompt.txt","r",encoding= 'utf-8') as file:
        system_prompt= file.read()
    agent.update_prompts({"react_header":system_prompt})
    response= await agent.run(
        prompt, max_iterations=5, early_stopping_method= "generate"
    )
    res = json.loads(response)
    print(res)
    return res
