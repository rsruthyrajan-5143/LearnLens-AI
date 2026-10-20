import fitz


def extract_text_from_pdf(uploaded_file):
    """Extract readable text from an uploaded PDF."""
    try:
        pdf_bytes = uploaded_file.getvalue()

        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            pages = []

            for page_number, page in enumerate(document, start=1):
                page_text = page.get_text("text").strip()

                if page_text:
                    pages.append(
                        f"--- Page {page_number} ---\n{page_text}"
                    )

        return "\n\n".join(pages)

    except Exception as error:
        raise ValueError(
            "Unable to read this PDF. Please upload a valid, "
            "text-based PDF file."
        ) from error
