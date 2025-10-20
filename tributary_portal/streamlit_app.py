"""Streamlit app for diritto tributario study helper."""
from __future__ import annotations

import datetime as dt
import json
import random
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

RESOURCE_BASE_PATH = Path(__file__).resolve().parent.parent / "risorse"
PROGRAM_BASE_PATH = RESOURCE_BASE_PATH / "programma_base.json"
QUIZ_DATA_PATH = RESOURCE_BASE_PATH / "quiz_tributario.json"


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


def load_quiz_questions() -> List[Dict[str, str]]:
    """Load quiz questions from the bundled JSON dataset."""
    if not QUIZ_DATA_PATH.exists():
        return []

    try:
        with QUIZ_DATA_PATH.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []

    questions: List[Dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        required_keys = {"id", "question", "options", "correct_answer", "explanation"}
        if not required_keys.issubset(item):
            continue
        options = item.get("options", [])
        if not isinstance(options, list) or not all(isinstance(opt, str) for opt in options):
            continue
        question_entry = {
            "id": str(item["id"]),
            "question": str(item["question"]),
            "correct_answer": str(item["correct_answer"]),
            "explanation": str(item["explanation"]),
            "topic": str(item.get("topic", "Generale")),
            "options": options,
        }
        questions.append(question_entry)

    return questions


def render_quiz_tab() -> None:
    """Render the interactive quiz experience."""
    st.subheader("Quiz di diritto tributario")

    all_questions = load_quiz_questions()
    if not all_questions:
        st.info(
            "Nessun quiz disponibile al momento. Aggiungi domande al file "
            "`risorse/quiz_tributario.json` per iniziare."
        )
        return

    topics = sorted({question.get("topic", "Generale") for question in all_questions})

    quiz_state = st.session_state.setdefault(
        "quiz_state",
        {
            "responses": {},
            "mistakes": [],
            "order": [],
            "order_key": "",
            "seed": random.randint(0, 1_000_000),
        },
    )

    st.markdown(
        "Scegli l'argomento o concentrati sulle domande in cui hai commesso errori per un ripasso mirato."
    )

    filter_topic = st.selectbox(
        "Filtra per argomento",
        options=["Tutti gli argomenti"] + topics,
        key="quiz_topic_filter",
    )

    mode_options = ["Quiz completo", "Ripasso mirato (errori)"]
    review_mode = st.selectbox(
        "Modalità di esercizio",
        options=mode_options,
        key="quiz_mode",
    )

    filtered_questions = all_questions
    mistakes: List[str] = quiz_state.setdefault("mistakes", [])

    if review_mode == "Ripasso mirato (errori)":
        if not mistakes:
            st.info(
                "Non ci sono errori da ripassare: completa prima il quiz o rispondi "
                "ad alcune domande."
            )
            filtered_questions = []
        else:
            filtered_questions = [
                question for question in all_questions if question["id"] in mistakes
            ]

    if filter_topic != "Tutti gli argomenti":
        filtered_questions = [
            question for question in filtered_questions if question.get("topic") == filter_topic
        ]

    if not filtered_questions:
        st.warning("Nessuna domanda corrisponde ai filtri selezionati.")
        if st.button("Reimposta filtri quiz"):
            st.session_state.pop("quiz_topic_filter", None)
            st.session_state.pop("quiz_mode", None)
            st.experimental_rerun()
        return

    filter_key = (
        f"{review_mode}|{filter_topic}|"
        f"{','.join(sorted(question['id'] for question in filtered_questions))}"
    )

    if quiz_state.get("order_key") != filter_key:
        question_ids = [question["id"] for question in filtered_questions]
        random.Random(f"{quiz_state['seed']}|{filter_key}").shuffle(question_ids)
        quiz_state["order"] = question_ids
        quiz_state["order_key"] = filter_key

    question_lookup = {question["id"]: question for question in filtered_questions}

    st.divider()

    placeholder_option = "Seleziona una risposta"
    responses: Dict[str, str] = quiz_state.setdefault("responses", {})
    correct_answers = 0
    answered_questions = 0
    incorrect_details = []

    for question_id in quiz_state.get("order", []):
        question = question_lookup.get(question_id)
        if question is None:
            continue

        st.markdown(f"### {question['question']}")
        st.caption(f"Argomento: {question.get('topic', 'Generale')}")

        widget_key = f"quiz_answer_{question_id}"
        display_options = [placeholder_option] + question["options"]
        if widget_key not in st.session_state:
            st.session_state[widget_key] = placeholder_option

        choice = st.radio(
            "Seleziona la risposta corretta",
            options=display_options,
            key=widget_key,
            label_visibility="collapsed",
        )

        if choice == placeholder_option:
            responses.pop(question_id, None)
            st.info("Scegli un'opzione per visualizzare il feedback.")
            st.divider()
            continue

        responses[question_id] = choice
        answered_questions += 1

        if choice == question["correct_answer"]:
            correct_answers += 1
            if question_id in mistakes:
                mistakes = [item for item in mistakes if item != question_id]
                quiz_state["mistakes"] = mistakes
            st.success("Risposta corretta! ✅")
        else:
            if question_id not in mistakes:
                mistakes.append(question_id)
                quiz_state["mistakes"] = mistakes
            incorrect_details.append((question, choice))
            st.error(
                "Risposta errata. Rivedi la spiegazione e prova di nuovo."
            )

        st.info(f"Spiegazione: {question['explanation']}")
        st.divider()

    total_questions = len(all_questions)
    st.subheader("Riepilogo del quiz")
    st.write(
        f"Domande mostrate: **{len(filtered_questions)}** · Risposte date: **{answered_questions}**"
    )
    st.metric(label="Punteggio parziale", value=f"{correct_answers}/{len(filtered_questions)}")

    if incorrect_details:
        st.warning("Domande da ripassare")
        for question, user_choice in incorrect_details:
            st.markdown(
                f"- **{question['question']}** — hai risposto: `{user_choice}` · "
                f"corretta: `{question['correct_answer']}`"
            )

    overall_correct = sum(
        1
        for question in all_questions
        if responses.get(question["id"]) == question["correct_answer"]
    )
    overall_answered = len(responses)
    st.caption(
        f"Punteggio complessivo: {overall_correct}/{total_questions} · Domande completate: "
        f"{overall_answered}/{total_questions}"
    )

    if responses:
        summary_rows = []
        for question in all_questions:
            user_choice = responses.get(question["id"])
            if not user_choice:
                continue
            summary_rows.append(
                {
                    "Argomento": question.get("topic", "Generale"),
                    "Domanda": question["question"],
                    "Risposta data": user_choice,
                    "Risposta corretta": question["correct_answer"],
                    "Esito": "Corretto" if user_choice == question["correct_answer"] else "Errato",
                }
            )

        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            st.dataframe(summary_df, hide_index=True, use_container_width=True)

    if mistakes:
        st.info(
            "Hai ancora domande da ripassare. Seleziona la modalità "
            "'Ripasso mirato (errori)' per concentrarti su di esse."
        )

    col_reset, col_review = st.columns(2)
    with col_reset:
        if st.button("Azzera risposte e punteggio"):
            for question in all_questions:
                st.session_state.pop(f"quiz_answer_{question['id']}", None)
            st.session_state.pop("quiz_state", None)
            st.experimental_rerun()

    with col_review:
        if st.button("Ripasso mirato"):
            st.session_state["quiz_mode"] = "Ripasso mirato (errori)"
            st.experimental_rerun()

    st.caption(
        "Totale domande nel database: "
        f"{total_questions}. Aggiorna il file JSON per aggiungere nuovi quiz."
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

    tab_labels = list(CATEGORY_PROMPTS.keys()) + ["Piano di studio", "Quiz"]
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
            elif label == "Piano di studio":
                render_study_plan_tab()
            else:
                render_quiz_tab()


if __name__ == "__main__":
    main()
