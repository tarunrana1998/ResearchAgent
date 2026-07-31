from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

import config
from tools import scrape_url, web_search


def get_llm(model_name: str = None):
    model = model_name or config.LLM_MODEL
    return ChatGoogleGenerativeAI(model=model, temperature=config.LLM_TEMPERATURE)


#1st agent 
def build_search_agent(model_name: str = None):
    return create_agent(
        model = get_llm(model_name),
        tools= [web_search]
    )

#2nd agent 

def build_reader_agent(model_name: str = None):
    return create_agent(
        model = get_llm(model_name),
        tools = [scrape_url]
    )


#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

def build_writer_chain(model_name: str = None):
    return writer_prompt | get_llm(model_name) | StrOutputParser()

#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

def build_critic_chain(model_name: str = None):
    return critic_prompt | get_llm(model_name) | StrOutputParser()