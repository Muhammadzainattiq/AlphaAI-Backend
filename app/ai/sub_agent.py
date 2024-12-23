from langgraph.graph import START, StateGraph, END
import os
from app.ai.tools import (SubState, check_single_or_multiple, tavily_search, web_loader, combine_news, continue_to_url_loads)
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# # Access the environment variable
# tavily_api_key = os.getenv("TAVILY_API_KEY")
# os.environ['TAVILY_API_KEY'] = "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"

#Nodes


#compiled the agent: In the actual application it should only compiled once may be in the main.py
def compile_sub_agent() :
    sub_builder = StateGraph(SubState)
    sub_builder.add_node("check_single_or_multiple", check_single_or_multiple)
    sub_builder.add_node("news_search", tavily_search)
    sub_builder.add_node("web_loader", web_loader)
    sub_builder.add_node("combine_news", combine_news)

    #Edges
    sub_builder.add_edge(START, "check_single_or_multiple")
    sub_builder.add_edge("check_single_or_multiple", "news_search")
    sub_builder.add_conditional_edges("news_search", continue_to_url_loads, ["web_loader"])
    sub_builder.add_edge("web_loader", "combine_news")
    sub_builder.add_edge("combine_news", END)
    compiled_sub_agent = sub_builder.compile()
    return compiled_sub_agent


#Here is the function to call the sub_agent i.e the fetch news agent


