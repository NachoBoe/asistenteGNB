
from dotenv import load_dotenv
from pyprojroot import here
import os
from uuid import uuid4
from langsmith import Client

from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent

from langchain_openai import AzureOpenAIEmbeddings
import prompts as p

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

import unicodedata
import dill 


from azure.search.documents.models import VectorFilterMode
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# INICIAR LANGSMITH Y API KEYS

## envs
dotenv_path = here() / ".env"
load_dotenv(dotenv_path=dotenv_path)


## langsmith
client = Client()
unique_id = uuid4().hex[0:8]
os.environ["LANGCHAIN_PROJECT"] = f"API - {unique_id}"


# LEVANTAR DATOS

## arbol urls
with open('tree_podado.dill', 'rb') as archivo:
    tree_podado = dill.load(archivo)

## contenido urls
with open('contenido_urls.dill', 'rb') as archivo:
    contenido_urls = dill.load(archivo)


# DEFINIR TOOLS

class url_path_list(BaseModel):
    url_path_list: list = Field(description="List of url paths to retrieve content from. Must start with '/' and not include the domain.")



## TOOL 1
@tool("retrieve_url_content", args_schema=url_path_list)
def retrieve_url_content(url_path_list:list):
    """ Returns the content of the listed urls. """
    print(url_path_list)
    url_path_list = ["https://www.gnbsudameris.com.co" + url for url in url_path_list]
    print(url_path_list)
    content = ""
    for cont in contenido_urls:
        print(cont["url"])
        if cont["url"] in url_path_list:
            print(content)
            content += str(cont) + '\n\n'
    return content





# DEFINIR AGENTE
tools = [retrieve_url_content]

openai = ChatOpenAI(model="gpt-3.5-turbo",temperature=0.0,streaming=True)



agent = create_openai_tools_agent(openai, tools, p.chat_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

