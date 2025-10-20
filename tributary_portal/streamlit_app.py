"""Streamlit app for diritto tributario study helper."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import streamlit as st
from duckduckgo_search import DDGS


@dataclass
class SearchResult:
    title: str
    href: str
    body: str


CATEGORY_PROMPTS = {
    "Articolo di riferimento": "articolo di legge di riferimento diritto tributario",
    "Spiegazione dell'argomento": "spiegazione diritto tributario",
    "Esempio pratico": "esempio pratico applicazione diritto tributario",
}


def run_search(query: str, context: str, max_results: int = 5) -> List[SearchResult]:
    """Esegue una ricerca tematica usando DuckDuckGo."""
    keywords = f"{query} {context}".strip()
    results: List[SearchResult] = []
    with DDGS() as search:
        for item in search.text(keywords, region="it-it", safesearch="moderate", max_results=max_results):
            results.append(
                SearchResult(
                    title=item.get("title", "Risultato senza titolo"),
                    href=item.get("href", ""),
                    body=item.get("body", "Sintesi non disponibile."),
                )
            )
    return results


def render_results(results: List[SearchResult]) -> None:
    if not results:
        st.info("Nessun risultato trovato. Prova a riformulare la richiesta.")
        return

    for result in results:
        st.subheader(result.title)
        if result.href:
            st.markdown(f"[Apri la fonte originale]({result.href})")
        st.write(result.body)
        st.divider()


def main() -> None:
    st.set_page_config(
        page_title="Diritto Tributario Helper",
        page_icon="⚖️",
        layout="wide",
    )

    st.title("Portale di supporto allo studio del diritto tributario")
    st.write(
        "Inserisci l'argomento di diritto tributario che vuoi studiare. "
        "Il portale cercherà per te l'articolo di riferimento, una spiegazione "
        "dettagliata e un esempio pratico."
    )

    query = st.text_input("Argomento di interesse", placeholder="Es. accertamento fiscale")
    max_results = st.slider("Numero di risultati per categoria", min_value=1, max_value=10, value=3)

    if query:
        tabs = st.tabs(list(CATEGORY_PROMPTS.keys()))
        for tab, (label, context) in zip(tabs, CATEGORY_PROMPTS.items()):
            with tab:
                st.caption(f"Ricerca in corso: **{query}** → {label.lower()}")
                results = run_search(query, context, max_results=max_results)
                render_results(results)
    else:
        st.info("Digita un argomento per iniziare la ricerca.")


if __name__ == "__main__":
    main()
