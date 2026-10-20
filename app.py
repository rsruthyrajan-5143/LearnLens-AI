import streamlit as st
from pathlib import Path

from utils.pdf_tools import extract_text_from_pdf
from utils.ai_engine import ask_ai
from utils.quiz_engine import generate_questions


st.set_page_config(
    page_title="LearnLens AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom styling
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True
    )

# Session state
if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "documents" not in st.session_state:
    st.session_state.documents = []

if "quiz_history" not in st.session_state:
    st.session_state.quiz_history = []

if "study_messages" not in st.session_state:
    st.session_state.study_messages = []


def show_header(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="learnlens-hero">
            <div class="eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-copy">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def feature_card(icon, title, description):
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-copy">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Sidebar navigation
with st.sidebar:
    st.markdown(
        """
        <div style="padding:12px 4px 24px;">
            <div style="font-size:2rem;">✦</div>
            <div style="font-size:1.55rem;font-weight:800;color:#fff;">
                LearnLens <span style="color:#a78bfa;">AI</span>
            </div>
            <div class="small-muted">YOUR INTELLIGENT STUDY SPACE</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.caption("WORKSPACE")

    pages = {
        "Overview": "⌂",
        "AI Study Room": "✧",
        "PDF Library": "▤",
        "Quiz Studio": "◈",
        "Flashcards": "▧",
        "Analytics": "◷"
    }

    for page_name, page_icon in pages.items():
        if st.button(
            f"{page_icon}  {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == page_name
                else "secondary"
            )
        ):
            st.session_state.page = page_name
            st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div class="feature-card" style="min-height:auto;padding:16px;">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Your AI study partner</div>
            <div class="feature-copy">
                Learn smarter. Understand deeper. Prepare better.
            </div>
        </div>
        <div class="small-muted">LEARNLENS AI · PERSONAL WORKSPACE</div>
        """,
        unsafe_allow_html=True
    )


# OVERVIEW
if st.session_state.page == "Overview":
    show_header(
        "YOUR PERSONAL AI LEARNING PLATFORM",
        "Learn beyond the notes.",
        "Transform your study materials into clear explanations, "
        "interactive quizzes and smarter revision sessions."
    )

    st.markdown("### Your learning overview")
    st.caption("Your workspace at a glance.")

    total_docs = len(st.session_state.documents)
    total_quizzes = len(st.session_state.quiz_history)

    if total_quizzes:
        average_score = sum(
            item["percentage"]
            for item in st.session_state.quiz_history
        ) / total_quizzes
    else:
        average_score = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Documents", total_docs)

    with col2:
        st.metric("Quizzes completed", total_quizzes)

    with col3:
        st.metric("Average score", f"{average_score:.0f}%")

    with col4:
        st.metric("AI workspace", "Ready")

    st.markdown("### Explore your workspace")

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        feature_card(
            "📚",
            "AI Study Room",
            "Ask questions and explore difficult topics."
        )
        if st.button("Open study room →", key="open_room",
                     use_container_width=True):
            st.session_state.page = "AI Study Room"
            st.rerun()

    with c2:
        feature_card(
            "🧠",
            "Quiz Studio",
            "Practice questions and track your scores."
        )
        if st.button("Explore quizzes →", key="open_quiz",
                     use_container_width=True):
            st.session_state.page = "Quiz Studio"
            st.rerun()

    with c3:
        feature_card(
            "📈",
            "Learning Analytics",
            "Review your learning progress."
        )
        if st.button("View analytics →", key="open_analytics",
                     use_container_width=True):
            st.session_state.page = "Analytics"
            st.rerun()

    st.markdown("### Your study materials")

    if not st.session_state.documents:
        st.info(
            "Your PDF library is empty. Open PDF Library to upload a document."
        )
    else:
        for document in st.session_state.documents:
            st.markdown(f"📄 **{document['name']}**")


# AI STUDY ROOM
elif st.session_state.page == "AI Study Room":
    show_header(
        "INTELLIGENT LEARNING",
        "AI Study Room",
        "Ask questions and learn with your AI study companion."
    )

    document_names = ["General AI tutor"] + [
        document["name"]
        for document in st.session_state.documents
    ]

    selected_document = st.selectbox(
        "Choose your learning source",
        document_names
    )

    document_text = ""

    if selected_document != "General AI tutor":
        for document in st.session_state.documents:
            if document["name"] == selected_document:
                document_text = document["text"]
                break

    for message in st.session_state.study_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask LearnLens AI a question...")

    if question:
        st.session_state.study_messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("LearnLens AI is thinking..."):
                try:
                    answer = ask_ai(question, document_text)

                    st.markdown(answer)

                    st.session_state.study_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as error:
                    st.error("AI response failed.")
                    st.code(str(error))


# PDF LIBRARY
elif st.session_state.page == "PDF Library":
    show_header(
        "YOUR KNOWLEDGE BASE",
        "PDF Library",
        "Upload your study notes and extract text for smarter learning."
    )

    uploaded_pdf = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"],
        help="Choose a text-based PDF document."
    )

    if uploaded_pdf is not None:
        if st.button("Import PDF", use_container_width=True):
            try:
                extracted_text = extract_text_from_pdf(uploaded_pdf)

                if not extracted_text.strip():
                    st.warning(
                        "No readable text found. "
                        "The PDF may contain scanned pages."
                    )
                else:
                    existing_names = [
                        item["name"]
                        for item in st.session_state.documents
                    ]

                    if uploaded_pdf.name in existing_names:
                        st.warning("This PDF is already in your library.")
                    else:
                        st.session_state.documents.append({
                            "name": uploaded_pdf.name,
                            "text": extracted_text
                        })
                        st.success("PDF imported successfully!")
                        st.rerun()

            except Exception as error:
                st.error("Could not import this PDF.")
                st.code(str(error))

    st.markdown("### Your documents")

    if not st.session_state.documents:
        st.info("No documents yet. Upload a PDF to get started.")
    else:
        for index, document in enumerate(st.session_state.documents):
            with st.expander(f"📄 {document['name']}"):
                st.caption(
                    f"{len(document['text']):,} characters extracted"
                )
                st.text_area(
                    "Extracted text preview",
                    value=document["text"][:5000],
                    height=220,
                    key=f"pdf_preview_{index}"
                )



# QUIZ STUDIO
elif st.session_state.page == "Quiz Studio":
    show_header(
        "SMART QUESTION PAPER GENERATOR",
        "Quiz Studio",
        "Turn your study PDFs into exam-ready questions and answers."
    )

    if not st.session_state.documents:
        st.warning(
            "First, upload a study PDF in PDF Library."
        )
        if st.button("Open PDF Library"):
            st.session_state.page = "PDF Library"
            st.rerun()

    else:
        document_names = [
            document["name"]
            for document in st.session_state.documents
        ]

        with st.container(border=True):
            st.markdown("### Configure your questions")

            selected_name = st.selectbox(
                "Choose study material",
                document_names,
                key="quiz_document"
            )

            col1, col2 = st.columns(2)

            with col1:
                marks = st.selectbox(
                    "Question marks",
                    [2, 5, 12, 16],
                    format_func=lambda value: f"{value}-mark questions"
                )

                question_count = st.selectbox(
                    "Number of questions",
                    [5, 10, 15, 20],
                    index=0
                )

            with col2:
                difficulty = st.selectbox(
                    "Difficulty level",
                    ["Easy", "Medium", "Advanced"],
                    index=1
                )

                unit = st.text_input(
                    "Unit or topic (optional)",
                    placeholder="e.g. Unit 1 - Introduction"
                )

            include_answers = st.checkbox(
                "Generate model answers",
                value=True
            )

            make_paper = st.checkbox(
                "Format as a model question paper",
                value=False
            )

            generate_clicked = st.button(
                "✦ Generate Questions",
                type="primary",
                use_container_width=True
            )

        if generate_clicked:
            selected_doc = next(
                (
                    document
                    for document in st.session_state.documents
                    if document["name"] == selected_name
                ),
                None
            )

            if selected_doc is None:
                st.error("Please select a valid document.")

            else:
                with st.spinner(
                    "LearnLens AI is preparing your questions..."
                ):
                    try:
                        result = generate_questions(
                            document_text=selected_doc["text"],
                            marks=marks,
                            count=question_count,
                            difficulty=difficulty,
                            unit=unit.strip() or "All Units",
                            question_paper=make_paper
                        )

                        st.session_state["generated_quiz"] = {
                            "title": result.get(
                                "title", "Practice Questions"
                            ),
                            "questions": result["questions"],
                            "source": selected_name,
                            "marks": marks,
                            "difficulty": difficulty,
                            "include_answers": include_answers
                        }

                    except Exception as error:
                        st.error(
                            "Question generation failed. "
                            "Please check your API setup and try again."
                        )
                        st.caption(str(error))

        quiz = st.session_state.get("generated_quiz")

        if quiz:
            st.markdown("---")
            st.markdown(f"## {quiz['title']}")
            st.caption(
                f"Source: {quiz['source']} · "
                f"Difficulty: {quiz['difficulty']}"
            )

            for index, question in enumerate(
                quiz["questions"], start=1
            ):
                with st.expander(
                    f"Q{index}. {question.get('question', 'Question')} "
                    f"({question.get('marks', quiz['marks'])} marks)",
                    expanded=True
                ):
                    st.markdown(question.get("question", ""))

                    if quiz["include_answers"]:
                        st.markdown("**Model Answer**")
                        st.markdown(question.get("answer", ""))

                    if question.get("unit"):
                        st.caption(f"Topic: {question['unit']}")

            export_text = f"{quiz['title']}\n\n"

            for index, question in enumerate(
                quiz["questions"], start=1
            ):
                export_text += (
                    f"Q{index}. {question.get('question', '')}\n"
                    f"Marks: {question.get('marks', quiz['marks'])}\n"
                )

                if quiz["include_answers"]:
                    export_text += (
                        f"Answer: {question.get('answer', '')}\n"
                    )

                export_text += "\n"

            st.download_button(
                "⬇ Download Questions and Answers",
                data=export_text,
                file_name="learnlens_practice_questions.txt",
                mime="text/plain",
                use_container_width=True
            )



# FLASHCARDS
elif st.session_state.page == "Flashcards":
    show_header(
        "SMART REVISION",
        "Flashcards",
        "Turn key concepts into quick revision cards."
    )
    st.info("Flashcard generation will be added in the next development step.")


# ANALYTICS
elif st.session_state.page == "Analytics":
    show_header(
        "YOUR LEARNING INSIGHTS",
        "Learning Analytics",
        "Understand your practice history and progress."
    )

    if st.session_state.quiz_history:
        st.bar_chart(
            [
                item["percentage"]
                for item in st.session_state.quiz_history
            ]
        )
    else:
        st.info("Complete quizzes to start building your analytics.")
