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

article_link = "https://www.npr.org/2023/05/13/1176037743/biden-howard-university-2024" # TODO: make configurable

template = """
You are an expert in detecting political bias.
Use the search tool to find three separate news articles that have similar titles to this news article: {link}
These three news articles will be called the perspective articles.
The perspective articles must be written within the same relative time frame as the original news article.
Perform a comparison of the content in the original article with the content in the perspective articles.
Respond with a rating as to how politically biased the original news article is, using the perspective articles for reference.
This rating should be from one to ten, one meaning that there's no political bias in the original article, and ten meaning that the original article is extremely politically biased.
"""
initial_prompt = PromptTemplate(
    input_variables=["link"],
    template=template
)

llm = OpenAIChat(model_name='gpt-3.5-turbo', temperature=0.0)

serp_tool = GoogleSerperAPIWrapper(type="news")

# TODO: Add Memory https://python.langchain.com/en/latest/modules/memory/how_to_guides.html

tools = [
    Tool(name="Search Tool",
        description="Useful for searching for news articles",
        func=serp_tool.run)
]

agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

print(agent(initial_prompt.format(link=article_link)))

