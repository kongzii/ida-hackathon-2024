import json
import os

import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from firecrawl.firecrawl import FirecrawlApp

load_dotenv()


def query_google_seach(q: str) -> list[str]:
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": q})
    headers = {
        "X-API-KEY": os.environ["SERPER_API_KEY"],
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    parsed = response.json()
    return [x["snippet"] for x in parsed["organic"]]


def llm(results: list[str]) -> str:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=1,
    )
    template = """Given the following results from Google, create a prediction market question in Yes/No format, resolvable in 2 days, mention dates in UTC format.
    Only output the question itself, nothing else.

    Results: {results}
    """
    prompt = ChatPromptTemplate.from_template(template=template)
    messages = prompt.format_messages(results=results)
    completion = str(llm.invoke(messages, max_tokens=512).content)
    return completion


def scrap_url_content(url: str) -> str:
    app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
    scraped = app.scrape_url(url, params={"formats": ["markdown"]})
    return scraped["markdown"]


query = st.text_input(
    label="Google Search input", value="What is the current Ethereum price?"
)

with st.spinner():
    results = query_google_seach(query)

st.markdown("### Found results:")
st.markdown("\n".join(f"- {r}" for r in results).replace("$", "\\$"))

with st.spinner():
    question = llm(results)

st.markdown("### Generated question:")
st.write(question)
