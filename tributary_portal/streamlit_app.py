"""Streamlit app for diritto tributario study helper."""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import uuid

import streamlit as st
import pandas as pd
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

PROGRAM_BASE_PATH = Path(__file__).resolve().parent.parent / "risorse" / "programma_base.json"


def load_base_topics() -> List[str]:
    """Load the default study topics from a JSON resource."""
    if PROGRAM_BASE_PATH.exists():
        try:
            with PROGRAM_BASE_PATH.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list) and all(isinstance(item, str) for item in data):
                return data
        except (json.JSONDecodeError, OSError):
            pass

    return [
        "Fonti del diritto tributario",
        "Soggetti passivi e capacità contributiva",
        "Imposta sul reddito delle persone fisiche",
        "Imposta sul valore aggiunto",
        "Accertamento e riscossione",
        "Contenzioso tributario",
        "Sanzioni e interessi",
        "Tributi locali",
    ]


def distribute_topics(
    start_date: dt.date, exam_date: dt.date, hours_available: float, topics: List[str]
) -> pd.DataFrame:
    """Create a study schedule distributing topics across the available days."""
    if exam_date <= start_date:
        raise ValueError("La data dell'esame deve essere successiva ad oggi.")

    days_available = (exam_date - start_date).days + 1
    if days_available <= 0 or not topics:
        return pd.DataFrame(columns=["Data", "Argomento", "Ore pianificate"])

    day_sequence = [start_date + dt.timedelta(days=offset) for offset in range(days_available)]
    day_topics: Dict[dt.date, List[str]] = {day: [] for day in day_sequence}
    for index, topic in enumerate(topics):
        day = day_sequence[index % len(day_sequence)]
        day_topics[day].append(topic)

    plan_rows = []
    for day in day_sequence:
        topics_for_day = day_topics[day]
        if not topics_for_day:
            continue
        hours_per_topic = round(hours_available / max(len(topics_for_day), 1), 2)
        for topic in topics_for_day:
            plan_rows.append(
                {
                    "Data": day,
                    "Argomento": topic,
                    "Ore pianificate": hours_per_topic,
                }
            )

    return pd.DataFrame(plan_rows)


def plan_to_ics(plan: pd.DataFrame) -> str:
    """Convert a plan dataframe into a minimal ICS calendar string."""
    dtstamp = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    events = []
    for _, row in plan.iterrows():
        date_value = row["Data"]
        if isinstance(date_value, dt.datetime):
            date_value = date_value.date()
        if not isinstance(date_value, dt.date):
            continue
        date_str = date_value.strftime("%Y%m%d")
        summary = f"Studio: {row['Argomento']}"
        description = f"Ore pianificate: {row['Ore pianificate']}"
        uid = uuid.uuid4().hex
        events.append(
            "\n".join(
                [
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{dtstamp}",
                    f"DTSTART;VALUE=DATE:{date_str}",
                    f"SUMMARY:{summary}",
                    f"DESCRIPTION:{description}",
                    "END:VEVENT",
                ]
            )
        )

    calendar_body = "\n".join(events)
    return "\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//DirittoTributarioHelper//StudyPlan//IT",
            calendar_body,
            "END:VCALENDAR",
        ]
    )


def render_study_plan_tab() -> None:
    """Render the study plan creation interface."""
    st.subheader("Piano di studio personalizzato")

    topics = load_base_topics()
    today = dt.date.today()
    default_exam = today + dt.timedelta(days=30)

    plan_state = st.session_state.setdefault("study_plan", {})

    exam_date = st.date_input(
        "Data dell'esame",
        value=plan_state.get("exam_date", default_exam),
        min_value=today,
    )
    hours_available = st.number_input(
        "Ore disponibili giornaliere",
        min_value=1.0,
        max_value=12.0,
        value=float(plan_state.get("hours_available", 2.0)),
        step=0.5,
    )
    selected_topics = st.multiselect(
        "Argomenti da coprire",
        options=topics,
        default=plan_state.get("topics", topics),
    )

    if not selected_topics:
        st.info("Seleziona almeno un argomento per generare il piano di studio.")
        return

    try:
        plan_df = distribute_topics(today, exam_date, hours_available, selected_topics)
    except ValueError as exc:
        st.error(str(exc))
        return

    if plan_df.empty:
        st.warning("Impossibile generare il piano con i parametri selezionati.")
        return

    plan_state.update(
        {
            "exam_date": exam_date,
            "hours_available": hours_available,
            "topics": selected_topics,
            "plan_df": plan_df,
        }
    )

    st.success("Piano di studio generato!")
    st.dataframe(plan_df, use_container_width=True)

    csv_data = plan_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Scarica piano in CSV",
        data=csv_data,
        file_name="piano_di_studio.csv",
        mime="text/csv",
    )

    ics_data = plan_to_ics(plan_df)
    st.download_button(
        label="Scarica calendario (ICS)",
        data=ics_data,
        file_name="piano_di_studio.ics",
        mime="text/calendar",
    )


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

    tab_labels = list(CATEGORY_PROMPTS.keys()) + ["Piano di studio"]
    tabs = st.tabs(tab_labels)

    for tab, label in zip(tabs, tab_labels):
        with tab:
            if label in CATEGORY_PROMPTS:
                if query:
                    st.caption(f"Ricerca in corso: **{query}** → {label.lower()}")
                    results = run_search(query, CATEGORY_PROMPTS[label], max_results=max_results)
                    render_results(results)
                else:
                    st.info("Digita un argomento per iniziare la ricerca.")
            else:
                render_study_plan_tab()


if __name__ == "__main__":
    main()
