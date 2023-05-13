import langchain
from langchain.agents import AgentType, initialize_agent
from langchain import PromptTemplate
from langchain.agents.tools import Tool
from langchain.llms import OpenAIChat
from langchain.utilities import GoogleSerperAPIWrapper
from termcolor import colored
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

article_link = ""

template = """
Use the search tool to find three separate news articles that have similar titles to this news article: {link}
These three news articles must be written within the same relative time frame as the original article.
Respond with only the links to these three articles.
"""
initial_prompt = PromptTemplate(
    input_variables=["link"],
    template=template
)

llm = OpenAIChat(model_name='gpt-3.5-turbo', temperature=0.0)

serp_tool = GoogleSerperAPIWrapper(type="news", tbs="qdr:m")
tools = [
    Tool(name="Search Tool",
        description="useful for searching for news articles",
        func=serp_tool.run)
]

agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

print(agent(initial_prompt.format(link=article_link)))

