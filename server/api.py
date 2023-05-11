import langchain
from langchain.agents import AgentType, initialize_agent
from langchain import PromptTemplate
from langchain.agents.tools import Tool
from steamship import check_environment, RuntimeEnvironments, Steamship
from steamship.invocable import post, PackageService
from steamship_langchain.cache import SteamshipCache
from steamship_langchain.llms import OpenAIChat
from steamship_langchain.tools import SteamshipSERP
from termcolor import colored


class BiasCompass(PackageService):

  @post("/evaluate_article")
  def evaluate_article(self, article_link: str):
    langchain.llm_cache = SteamshipCache(client=self.client)
    
    template = """
    Use the search tool to find three separate news articles that have similar titles to this news article: {link}

    Respond with the links to these three articles
    """
    initial_prompt = PromptTemplate(
        input_variables=["link"],
        template=template
    )

    llm = OpenAIChat(client=self.client,
                     temperature=0.0,
                     cache=True,
                     model_name="gpt-3.5-turbo")

    serp_tool = SteamshipSERP(client=self.client, cache=True)
    tools = [
      Tool(name="Search Tool",
           description="useful for searching for news articles",
           func=serp_tool.search)
    ]

    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    
    return agent(initial_prompt.format(link=article_link)
)

