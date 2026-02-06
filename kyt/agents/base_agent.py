from langchain_openai import AzureChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
import os


def get_llm():
    """Initialize and return the Azure OpenAI LLM instance."""
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-15-preview",
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0.1
    )


def create_base_agent(llm, tools, system_prompt: str):
    """Create a base agent with the given tools and system prompt."""
    # Use LangGraph's create_react_agent for modern agent creation
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
