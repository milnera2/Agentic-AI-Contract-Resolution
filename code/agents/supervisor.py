from agents.ocr import run as ocr_run
from agents.splitter import run as split_run
from agents.interpreter import run as interpret_run
from agents.messenger import run as messenger_run
from log import log_decision


def run(submission: dict, progress_callback=None) -> dict:
    def _progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    pdf_path = submission["pdf_path"]
    rules = submission.get("rules", "")
    concerns = submission.get("concerns", "")
    contract_name = submission.get("contract_name", pdf_path)

    _progress("Reading contract...")
    log_decision(
        agent="Supervisor Agent 0",
        action="start_workflow",
        details={"pdf_path": pdf_path},
        result={"status": "started"},
    )

    ocr_result = ocr_run(pdf_path)
    text = ocr_result["text"]
    if not text:
        _progress("No text found in PDF.")
        log_decision(
            agent="Supervisor Agent 0",
            action="no_text_extracted",
            details={"pdf_path": pdf_path},
            result={"more_info_needed": True},
        )
        return {
            "error": "No text could be extracted from the PDF.",
            "more_info_needed": True,
        }

    _progress("Splitting contract into clauses...")
    split_result = split_run(text)
    clauses = split_result["clauses"]

    _progress("Interpreting clauses against your rules...")
    interpret_result = interpret_run(clauses, rules, concerns, progress_callback=_progress)
    flags = interpret_result["flags"]

    _progress("Generating review report...")
    message_result = messenger_run(
        flags,
        contract_name,
        include_log=submission.get("include_log", False),
        progress_callback=_progress,
    )

    num_flagged = sum(1 for f in flags if f["flagged"])
    _progress("Done.")
    log_decision(
        agent="Supervisor Agent 0",
        action="workflow_complete",
        details={"num_clauses": len(clauses), "num_flagged": num_flagged},
        result=message_result,
    )

    return {
        "message": message_result["message"],
        "report_path": message_result["report_path"],
        "flags": flags,
        "num_clauses": len(clauses),
        "num_flagged": num_flagged,
    }
