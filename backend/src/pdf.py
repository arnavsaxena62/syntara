import fitz
from starlette.concurrency import run_in_threadpool
from fastapi import HTTPException, UploadFile


async def get_pdf_text(file: UploadFile) -> str:
    pdf_bytes = await file.read()
    try:
        return await run_in_threadpool(
            extract_pdf_text_with_pymupdf,
            pdf_bytes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc



def extract_pdf_text_with_pymupdf(pdf_bytes: bytes) -> str:
    """
    Extract selectable text from a PDF.

    Image-only/scanned PDFs will usually return little or no text and
    should be sent to an OCR service as a fallback.
    """
    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("The uploaded content is not a valid PDF.")

    extracted_pages: list[str] = []

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            for page_index in range(document.page_count):
                page = document.load_page(page_index)
                page_text = page.get_text("text").strip()

                if page_text:
                    extracted_pages.append(
                        f"--- Page {page_index + 1} ---\n{page_text}"
                    )

    except fitz.FileDataError as exc:
        raise ValueError("Could not open the PDF file.") from exc

    return "\n\n".join(extracted_pages)