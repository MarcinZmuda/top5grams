import os
import requests
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
from collections import Counter
from nltk import ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from apify_client import ApifyClient

# === API keys ===
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

    # 🔍 DEBUG – sprawdź, czy klucz API się odczytał
    st.write("🛠️ API Key:", SERP_API_KEY)

    res = requests.get(url, params=params)
    results = res.json()
    st.write("📦 Odpowiedź SERP API:", results)
    return [r["link"] for r in results.get("organic_results", [])][:5]
# === Pobieranie treści przez Apify Web Scraper ===
def extract_text(url):
    try:
        run = apify_client.actor("apify/web-scraper").call(run_input={
            "startUrls": [{"url": url}],
            "pageFunction": """async function pageFunction(context) {
                return {
                    url: context.request.url,
                    text: document.body.innerText
                };
            }""",
            "proxyConfiguration": { "useApifyProxy": True }
        })
        items = apify_client.dataset(run["defaultDatasetId"]).list_items().get("items", [])
        return items[0]["text"] if items else ""
    except Exception as e:
        st.warning(f"Błąd pobierania z Apify dla {url}: {e}")
        return ""

# === Generowanie n-gramów ===
def generate_ngrams(text, n):
    tokens = [t.lower() for t in text.split() if t.isalpha()]
    return [" ".join(gram) for gram in ngrams(tokens, n)]

# === STREAMLIT INTERFEJS ===
st.title("🔎 Top5Grams – analiza n-gramów z top 5 wyników Google")

query = st.text_input("Wpisz słowo kluczowe", placeholder="np. audyt SEO")
if st.button("Analizuj") and query:
    with st.spinner("Pobieram dane..."):
        urls = get_google_results(query)
        st.write("🔗 Wyniki Google:", urls)

        all_text = ""
        for url in urls:
            st.write(f"📄 Pobieram z: {url}")
            tekst = extract_text(url)
            st.write(f"✅ Długość treści: {len(tekst)} znaków")
            all_text += tekst + " "

        ngram_data = []
        for n in [1, 2, 3]:
            ngram_list = generate_ngrams(all_text, n)
            freq = Counter(ngram_list)
            for k, v in freq.items():
                ngram_data.append({"n-gram": k, "typ": f"{n}-gram", "liczba wystąpień": v})

    if ngram_data:
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
    else:
        st.error("❌ Nie udało się pobrać treści z żadnej strony. Spróbuj inne słowo kluczowe.")
