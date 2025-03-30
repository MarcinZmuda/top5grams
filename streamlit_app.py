import os
import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from collections import Counter
from nltk import ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Pobierz klucz API z secrets.toml
SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

# Pobierz top 5 wyników Google z SERPAPI
def get_google_results(query):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "gl": "pl",
        "hl": "pl",
        "api_key": SERP_API_KEY,
        "num": 5
    }
    res = requests.get(url, params=params)
    results = res.json()
    return [r["link"] for r in results.get("organic_results", [])][:5]

# Wyciągnij tekst
