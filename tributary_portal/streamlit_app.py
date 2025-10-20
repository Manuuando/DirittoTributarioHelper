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
import streamlit.components.v1 as components
import pandas as pd
from duckduckgo_search import DDGS
from fpdf import FPDF


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

    for index, result in enumerate(results):
        st.subheader(result.title)
        if result.href:
            st.markdown(f"[Apri la fonte originale]({result.href})")
        st.write(result.body)
        copy_payload = json.dumps(
            f"{result.title}\n{result.body}\nFonte: {result.href}" if result.href else f"{result.title}\n{result.body}"
        ).replace("'", "&#39;")
        components.html(
            f"""
            <button style='padding:0.35rem 0.7rem;border-radius:0.25rem;border:1px solid #bbb;'
                    onclick='navigator.clipboard.writeText({copy_payload});'>
                Copia questo risultato
            </button>
            """,
            height=38,
            key=f"copy_result_{index}",
        )
        st.divider()


def _notes_state() -> List[Dict[str, str]]:
    return st.session_state.setdefault("study_notes", [])


def _create_note_dataframe(notes: List[Dict[str, str]]) -> pd.DataFrame:
    if not notes:
        return pd.DataFrame(columns=["Titolo", "Categoria", "Ultimo aggiornamento"])

    df = pd.DataFrame(notes)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values(by=["Categoria", "timestamp"], ascending=[True, False])
    else:
        df = df.sort_values(by=["Categoria", "Ultimo aggiornamento"], ascending=[True, False])
    columns = [
        "id",
        "Titolo",
        "Categoria",
        "Contenuto",
        "Ultimo aggiornamento",
    ]
    if "timestamp" in df.columns:
        columns.append("timestamp")
    return df[columns]


def _notes_to_markdown(notes: List[Dict[str, str]]) -> str:
    lines = ["# Appunti di studio"]
    for note in notes:
        lines.append(f"\n## {note['Titolo']} ({note['Categoria']})")
        lines.append(note["Contenuto"])
    return "\n".join(lines)


def _notes_to_text(notes: List[Dict[str, str]]) -> str:
    lines = []
    for note in notes:
        lines.append(f"Titolo: {note['Titolo']}")
        lines.append(f"Categoria: {note['Categoria']}")
        lines.append(note["Contenuto"])
        lines.append("-" * 40)
        lines.append("")
    return "\n".join(lines)


def _notes_to_pdf(notes: List[Dict[str, str]]) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Appunti di studio", ln=True)
    for note in notes:
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"{note['Titolo']} ({note['Categoria']})")
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, note["Contenuto"])
    return pdf.output(dest="S").encode("latin-1")


def render_notes_tab() -> None:
    st.subheader("Appunti collegati alla ricerca")
    notes = _notes_state()

    with st.form("note_creator"):
        title = st.text_input(
            "Titolo dell'appunto",
            value=st.session_state.get("note_title", ""),
        )
        category_options = sorted({note["Categoria"] for note in notes if note.get("Categoria")})
        default_category = category_options[0] if category_options else ""
        category = st.text_input(
            "Categoria/Argomento",
            value=st.session_state.get("note_category", default_category),
            placeholder="Es. Accertamento fiscale",
        )
        query_context = st.session_state.get("last_query", "")
        content_placeholder = (
            f"Appunti su: {query_context}" if query_context else "Scrivi qui i tuoi appunti"
        )
        content = st.text_area(
            "Contenuto dell'appunto",
            height=200,
            value=st.session_state.get("note_content", ""),
            placeholder=content_placeholder,
        )

        st.session_state["note_title"] = title
        st.session_state["note_category"] = category
        st.session_state["note_content"] = content

        submit_col, reset_col = st.columns([3, 1])
        with submit_col:
            submitted = st.form_submit_button("Salva nota")
        with reset_col:
            reset = st.form_submit_button("Svuota campi")

        if reset:
            st.session_state["note_title"] = ""
            st.session_state["note_category"] = ""
            st.session_state["note_content"] = ""
            st.experimental_rerun()

        if submitted:
            if not title.strip() or not content.strip():
                st.warning("Titolo e contenuto sono obbligatori per salvare un appunto.")
            else:
                current_time = dt.datetime.now()
                note_entry = {
                    "id": uuid.uuid4().hex,
                    "Titolo": title.strip(),
                    "Categoria": category.strip() or "Generale",
                    "Contenuto": content.strip(),
                    "timestamp": current_time.isoformat(),
                    "Ultimo aggiornamento": current_time.strftime("%d/%m/%Y %H:%M"),
                }
                notes.append(note_entry)
                st.session_state["note_title"] = ""
                st.session_state["note_category"] = note_entry["Categoria"]
                st.session_state["note_content"] = ""
                st.success("Appunto salvato correttamente!")

    if not notes:
        st.info("Aggiungi il tuo primo appunto per iniziare a costruire un archivio di studio.")
        return

    df = _create_note_dataframe(notes)
    st.dataframe(
        df.drop(columns=[col for col in ["id", "Contenuto", "timestamp"] if col in df.columns]),
        hide_index=True,
        use_container_width=True,
    )

    note_lookup = {note["id"]: note for note in notes}
    selected_ids = st.multiselect(
        "Seleziona gli appunti su cui lavorare",
        options=[note["id"] for note in notes],
        format_func=lambda note_id: f"{note_lookup[note_id]['Titolo']} ({note_lookup[note_id]['Categoria']})",
    )

    selected_notes = [note_lookup[note_id] for note_id in selected_ids]

    if selected_notes:
        markdown_data = _notes_to_markdown(selected_notes)
        text_data = _notes_to_text(selected_notes)
        pdf_data = _notes_to_pdf(selected_notes)

        export_col1, export_col2, export_col3 = st.columns(3)
        with export_col1:
            st.download_button(
                "Scarica in Markdown",
                data=markdown_data.encode("utf-8"),
                file_name="appunti.md",
                mime="text/markdown",
            )
        with export_col2:
            st.download_button(
                "Scarica in TXT",
                data=text_data.encode("utf-8"),
                file_name="appunti.txt",
                mime="text/plain",
            )
        with export_col3:
            st.download_button(
                "Scarica in PDF",
                data=pdf_data,
                file_name="appunti.pdf",
                mime="application/pdf",
            )

        st.markdown("### Azioni rapide")
        selected_to_copy = st.selectbox(
            "Scegli l'appunto da copiare negli appunti",
            options=selected_notes,
            format_func=lambda note: f"{note['Titolo']} ({note['Categoria']})",
            key="note_copy_selector",
        )

        if selected_to_copy:
            copy_payload = json.dumps(selected_to_copy["Contenuto"]).replace("'", "&#39;")
            components.html(
                f"""
                <button style='padding:0.4rem 0.8rem;border-radius:0.25rem;border:1px solid #ccc;'
                        onclick='navigator.clipboard.writeText({copy_payload});'>
                    Copia contenuto selezionato
                </button>
                """,
                height=40,
            )

        if st.button("Genera sintesi"):
            summary_lines = [
                f"- **{note['Titolo']}** ({note['Categoria']}): {note['Contenuto']}"
                for note in selected_notes
            ]
            summary_text = "\n".join(summary_lines)
            st.session_state["notes_summary"] = summary_text

    summary_text = st.session_state.get("notes_summary")
    if summary_text:
        st.markdown("### Sintesi generata")
        st.text_area(
            "Schema di ripasso rapido",
            value=summary_text,
            height=200,
        )


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

    tab_labels = list(CATEGORY_PROMPTS.keys()) + ["Appunti", "Piano di studio", "Quiz"]
    tabs = st.tabs(tab_labels)

    for tab, label in zip(tabs, tab_labels):
        with tab:
            if label in CATEGORY_PROMPTS:
                if query:
                    st.session_state["last_query"] = query
                    st.caption(f"Ricerca in corso: **{query}** → {label.lower()}")
                    results = run_search(query, CATEGORY_PROMPTS[label], max_results=max_results)
                    render_results(results)
                else:
                    st.info("Digita un argomento per iniziare la ricerca.")
            elif label == "Appunti":
                render_notes_tab()
            elif label == "Piano di studio":
                render_study_plan_tab()
            else:
                render_quiz_tab()


if __name__ == "__main__":
    main()
