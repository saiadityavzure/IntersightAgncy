import os

from cnoe_agent_utils import LLMFactory
from config.config import LLM_PROVIDER

# def get_llm():
#   """
#     Get the LLM provider based on the configuration using cnoe-agent-utils LLMFactory.
#     """
#   factory = LLMFactory(
#     provider=LLM_PROVIDER,
#   )
#   return factory.get_llm()

from langchain_openai import ChatOpenAI

def get_llm():
  """
    Get the LLM provider based on the configuration using cnoe-agent-utils LLMFactory.
    """
  model = ChatOpenAI( model="meta/llama-3.1-8b-instruct", 
           base_url="http://10.20.1.116:8000/v1", 
           api_key="dummy-key", temperature=0.1)
 
  return model