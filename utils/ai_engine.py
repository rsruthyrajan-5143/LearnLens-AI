import streamlit as st
from google import genai


def get_ai_client():
    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key missing. Add GEMINI_API_KEY to "
            ".streamlit/secrets.toml."
        )

    return genai.Client(api_key=api_key)


def ask_ai(question, document_text=""):
    """Answer a study question using Gemini AI."""
    if not question.strip():
        return "Please enter a question."

    client = get_ai_client()

    if document_text.strip():
        prompt = f"""
You are LearnLens AI, a friendly study tutor.
Answer using the student's study material when relevant.
If the answer is not covered in the material, say so clearly.
Explain difficult concepts in simple English with examples.

STUDY MATERIAL:
{document_text[:20000]}

STUDENT QUESTION:
{question}
"""
    else:
        prompt = f"""
You are LearnLens AI, a friendly study tutor.
Explain the answer in simple English with examples.

STUDENT QUESTION:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text or "I couldn't generate an answer. Please try again."
