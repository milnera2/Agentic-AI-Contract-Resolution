import pymupdf as fitz


def extract_text(pdf_path: str) -> str:
    """Extract text from a digital PDF using pymupdf."""
    text_parts = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()


def extract_text_with_ocr_fallback(pdf_path: str) -> str:
    """Extract text from a PDF, falling back to OCR if no text is found."""
    text = extract_text(pdf_path)
    if text:
        return text
    try:
        import pytesseract
        from PIL import Image
        import pdf2image
        images = pdf2image.convert_from_path(pdf_path)
        ocr_texts = []
        for img in images:
            ocr_texts.append(pytesseract.image_to_string(img))
        return "\n".join(ocr_texts).strip()
    except Exception:
        return text


def has_text(pdf_path: str) -> bool:
    return bool(extract_text(pdf_path))
