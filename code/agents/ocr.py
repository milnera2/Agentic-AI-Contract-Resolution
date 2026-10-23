from tools.ocr_scanner import extract_text_with_ocr_fallback
from log import log_decision


def run(pdf_path: str) -> dict:
    text = extract_text_with_ocr_fallback(pdf_path)
    log_decision(
        agent="Agent 1 - OCR",
        action="extract_text",
        details={"pdf_path": pdf_path},
        result={"text_length": len(text), "has_text": bool(text)},
    )
    return {"text": text}
