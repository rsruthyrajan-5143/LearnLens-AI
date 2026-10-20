
import json
import time

import streamlit as st
from google import genai
from google.genai import errors


def generate_questions(
    document_text,
    marks,
    count=5,
    difficulty="Medium",
    unit="All Units",
    question_paper=False,
):
    """Generate exam questions from uploaded study material."""

    if not document_text or not document_text.strip():
        raise ValueError(
            "Please upload a PDF containing readable study material."
        )

    api_key = st.secrets.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key is missing. Check your local secrets file."
        )

    client = genai.Client(api_key=api_key)

    answer_styles = {
        2: "short definitions and concise explanations",
        5: "brief structured answers with key points",
        12: "detailed answers with headings and examples",
        16: (
            "comprehensive answers with headings, subtopics, "
            "examples, and relevant diagrams to draw"
        ),
    }

    answer_style = answer_styles.get(
        marks, "clear, structured exam-style answers"
    )

    if question_paper:
        task = (
            "Create a model question paper with a title, numbered "
            "questions, and a clear marks structure."
        )
    else:
        task = "Generate individual exam-practice questions."

    prompt = f"""
You are LearnLens AI, an exam preparation assistant.

TASK:
{task}

Generate exactly {count} questions.
Marks per question: {marks}
Difficulty: {difficulty}
Unit or topic: {unit}

Use only relevant information from the study material.
Do not invent facts or label generated questions as actual
previous-year questions.

For each question, provide:
- A clear exam-style question
- A model answer suitable for {marks} marks
- The unit or topic, if identifiable

Answer style: {answer_style}

If the source does not contain enough information for an answer,
say so clearly instead of inventing details.

Return valid JSON only, in this format:
{{
  "title": "Practice Questions",
  "questions": [
    {{
      "question": "Question text",
      "marks": {marks},
      "answer": "Model answer",
      "unit": "Unit or topic"
    }}
  ]
}}

STUDY MATERIAL:
{document_text[:24000]}
"""

    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            break

        except errors.APIError as error:
            status_code = getattr(error, "code", None)

            if status_code == 503 and attempt < 2:
                time.sleep(2 * (attempt + 1))
            else:
                raise

    if response is None or not response.text:
        raise ValueError(
            "The AI returned an empty response. Please try again."
        )

    result_text = response.text.strip()

    if result_text.startswith("```"):
        lines = result_text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        result_text = "\n".join(lines).strip()

    try:
        result = json.loads(result_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The AI response was not valid JSON. Please try again."
        ) from error

    if not isinstance(result, dict):
        raise ValueError("The AI returned an unexpected response.")

    questions = result.get("questions")

    if not isinstance(questions, list) or not questions:
        raise ValueError(
            "No questions were returned. Please try again."
        )

    return result
