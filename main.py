import langchain
import requests
import functools
import validators
import os

from threading import Thread
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.output_parsers import RegexParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from bs4 import BeautifulSoup
from dotenv import load_dotenv

prompt_template = """Use the following excerpt from a news article titled "{question}" to determine whether any signals of political bias, political narratives, misinformation, or opinion-based journalism practices exist within the news article.

If you detect any signals of political bias, signals of a political narrative being pushed, signals of misinformation, or signals opinion-based journalism practices, concisely explain what the signals are. This explination should be between 25 and 100 words long. If you can't find any signals, reply with "None found.", don't try to make up signals.

In addition to giving an explanation of the signals, also return a score of how confident you are that political bias, political narratives, misinformation, or opinion-based journalism exists in the excerpt. This should be in the following format:

Signals: [explination of signals here]
Score: [confidence score between 0 and 100](Only return a number for the score, no other text is allowed.)

Begin!

excerpt:
---------
{context}
---------
Signals:"""

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello. Welcome to Bias Compass, a tool for detecting bias in news articles.\n\nTo begin, simply send the link of an article that you suspect might contain bias.')

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

def handle_response(text: str) -> str:
    if not validators.url(text):
        return "The provided URL is not valid, please try again."

    response = requests.get(text)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('title')
    if title is not None:
        title = soup.find('title').get_text().split('|')[0]
    else:
        llm = OpenAI(model_name='gpt-3.5-turbo', temperature=0.0)
        title = llm(f"Make an educated guess on what the title of a news article would be with the following URL: {text}")

    # serp_tool = GoogleSerperAPIWrapper(tbs="qdr:m")
    # similar_articles_serp = serp_tool.results(f"{title} news articles")
    # similar_articles_final = []
    # for article_meta in similar_articles_serp["organic"]:
    #     link = article_meta["link"]
    #     if not link.startswith('https://www.youtube.com') and not link.startswith('https://youtube.com'):
    #         similar_articles_final.append(link)
    #         if len(similar_articles_final) == SIMILAR_COUNT:
    #             break
    # print(similar_articles_final)

    total_articles = [text]
    # total_articles.extend(similar_articles_final)
    loader = UnstructuredURLLoader(urls=total_articles)
    try:
        articles_data = timeout(timeout=15)(loader.load)()
    except:
        return "The news source of the provided doesn't allow bots to read articles on their website. Please try again with a different article."

    medium_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap  = 75,
        length_function = len
    )

    # article_documents = []
    # for article_content in articles_data[1:]:
    #     article_documents.extend(medium_text_splitter.create_documents([article_content.page_content]))

    primary_texts = medium_text_splitter.split_text([articles_data[0].page_content])

    # embeddings = OpenAIEmbeddings()
    # article_db = FAISS.from_documents(article_documents, embeddings)
    # article_retriever = article_db.as_retriever()

    primary_embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(primary_texts, primary_embeddings, metadatas=[{"source": str(i)} for i in range(len(primary_texts))])
    docs = docsearch.similarity_search(title)

    output_parser = RegexParser(
        regex=r"(.*?)\nScore: (.*)",
        output_keys=["answer", "score"],
    )

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
        output_parser=output_parser,
    )

    chain = load_qa_with_sources_chain(ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.0), chain_type="map_rerank", metadata_keys=['source'], return_intermediate_steps=False, prompt=PROMPT)
    result = chain({"input_documents": docs, "question": title}, return_only_outputs=False)

    if result["output_text"].replace(" ", "") == 'Nonefound.':
        return "No signals of bias found."

    for doc in result['input_documents']:
        if doc.metadata['source'] == result['source']:
            # Document containing bias: doc.page_content
            return result["output_text"]
    
    return "An issue occured when evaluating your article, please try again."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if '@BiasCompassBot' in text:
            new_text: str = text.replace('@BiasCompassBot', '').strip()
            response: str = handle_response(new_text)
        else:
            return 
    else:
        response: str = handle_response(text)

    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    load_dotenv()
    app = Application.builder().token(os.environ.get("TELEGRAM_TOKEN")).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=5)
