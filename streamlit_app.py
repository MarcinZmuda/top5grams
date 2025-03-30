import os
import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from collections import Counter
from nltk import ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")

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

def extract_text(url):
    try:
        page = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(page.text, "html.parser")
        for s in soup(["script", "style", "header", "footer", "nav"]): s.extract()
        return soup.get_text(separator=" ", strip=True)
    except:
        return ""

def generate_ngrams(text, n):
    tokens = [t.lower() for t in text.split() if t.isalpha()]
    return [" ".join(gram) for gram in ngrams(tokens, n)]

st.title("🔎 Top5Grams – analiza n-gramów z top 5 wyników Google")

query = st.text_input("Wpisz słowo kluczowe", placeholder="np. audyt SEO")
if st.button("Analizuj") and query:
    with st.spinner("Pobieram dane..."):
        urls = get_google_results(query)
        all_text = " ".join([extract_text(url) for url in urls])
        ngram_data = []

        for n in [1, 2, 3]:
            ngram_list = generate_ngrams(all_text, n)
            freq = Counter(ngram_list)
            for k, v in freq.items():
                ngram_data.append({"n-gram": k, "typ": f"{n}-gram", "liczba wystąpień": v})

        df = pd.DataFrame(ngram_data).sort_values("liczba wystąpień", ascending=False)

    st.success("Gotowe! ✅")
    st.subheader("📊 Najczęstsze n-gramy")
    st.dataframe(df.head(50), use_container_width=True)

    st.download_button("📥 Pobierz CSV", df.to_csv(index=False), "ngrams.csv", "text/csv")

    st.subheader("☁️ Word Cloud")
    wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(df["n-gram"]))
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
