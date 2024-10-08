# ida-hackathon-2024

CVUT FEL IDA Hackathon based on Gnosis projects

## Setup

1. Install virtualenv

```
python -m pip install virtualenv
```

2. Create a new venv

```
python -m venv venv
```

3. Activate it

```
source venv/bin/activate
```

4. Install dependencies

```
python -m pip install -r requirements.txt
```

5. Fill up keys

```
cp .env.example .env
```

And fill in the API keys:

- SERPER_API_KEY: can be obtained for free on https://serper.dev (Required for google search function)
- FIRECRAWL_API_KEY: can be obtained for free on (Required for web scraping function)
- OPENAI_API_KEY: I can send you one (Required for LLM calls)
- BET_FROM_PRIVATE_KEY: Create wallet on Gnosis Chain, for example with [MetaMask](https://metamask.io/) and I can send you some xDai (Required for creating a market)

## Run

```
streamlit run create_markets.py
```

## Task

Play with the google search query -- what queries will give interesting results to create markets from?

Play with the LLM prompt -- how can it be modified to return more interesting questions?

Optionally play with `get_url_content` to retrieve content from custom URL that can be used to create questions.

Optionall 2 implement anything that you find useful to create prediction market questions.
