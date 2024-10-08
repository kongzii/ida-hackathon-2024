import os

import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from firecrawl.firecrawl import FirecrawlApp
from prediction_market_agent_tooling.markets.omen.data_models import (
    OMEN_BINARY_MARKET_OUTCOMES,
)
from prediction_market_agent_tooling.tools.utils import utcnow
from datetime import timedelta
from prediction_market_agent_tooling.markets.omen.omen import (
    OmenMarket,
    omen_create_market_tx,
    APIKeys,
    xDai,
)

load_dotenv()


def query_google_seach(q: str) -> list[str]:
    url = "https://google.serper.dev/search"
    response = requests.post(
        url,
        headers={
            "X-API-KEY": os.environ["SERPER_API_KEY"],
            "Content-Type": "application/json",
        },
        json={"q": q},
    )
    response.raise_for_status()
    parsed = response.json()
    return [x["snippet"] for x in parsed["organic"]]


def llm(results: list[str]) -> str:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=1,
    )
    template = f"""Today is {utcnow()}.
    Given the following results from Google, create a prediction market question in Yes/No format, resolvable in 2 days, mention dates in UTC format.
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


st.write("Input a google query")
query = st.text_input(label="Google Search input", value=None)
st.write("Or directly a webiste link")
website_url = st.text_input(label="Website URL", value=None)

if not query and not website_url:
    st.warning("Please provide google query or website url.")
    st.stop()

with st.spinner():
    results = (
        query_google_seach(query)
        if not website_url
        else [scrap_url_content(website_url)]
    )

st.markdown("### Found results:")
st.markdown("\n".join(f"- {r}" for r in results).replace("$", "\\$"))

with st.spinner():
    question = llm(results)

st.markdown("### Generated question:")
st.write(question)

# In the prompt we ask for markets resolvable in 2 days, but close the market in 7 days just to be sure.
closing_time = utcnow() + timedelta(days=7)

if st.button("Create this market?"):
    market = OmenMarket.from_created_market(
        omen_create_market_tx(
            APIKeys(),  # Will load `BET_FROM_PRIVATE_KEY` from .env file.
            initial_funds=xDai(0.01),  # Create only with a small liquidity.
            question=question,
            closing_time=closing_time,
            category="ida-hackathon-2024",  # Don't change, so we can identify these markets.
            language="en",
            outcomes=OMEN_BINARY_MARKET_OUTCOMES,  # We can work only with [Yes, No] markets.
            auto_deposit=True,  # Auto-convert xDai into wxDai (required).
        )
    )
    st.write(f"Market created at {market.url}.")
