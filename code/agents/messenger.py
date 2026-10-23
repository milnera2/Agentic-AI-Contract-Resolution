import concurrent.futures
import unicodedata
from datetime import datetime
from pathlib import Path
from log import log_decision, read_logs
from fpdf import FPDF

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
PDF_TIMEOUT_SECONDS = 60


def _ensure_dir():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_text(text: str) -> str:
    """Replace Unicode characters not supported by Helvetica (Latin-1) with ASCII equivalents."""
    if not text:
        return text
    # Common Unicode → ASCII replacements
    replacements = {
        "\u2018": "'",   # left single quotation mark
        "\u2019": "'",   # right single quotation mark
        "\u201a": "'",   # single low-9 quotation mark
        "\u201b": "'",   # single high-reversed-9 quotation mark
        "\u201c": '"',   # left double quotation mark
        "\u201d": '"',   # right double quotation mark
        "\u201e": '"',   # double low-9 quotation mark
        "\u201f": '"',   # double high-reversed-9 quotation mark
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u2026": "...", # horizontal ellipsis
        "\u00a0": " ",   # non-breaking space
        "\u200b": "",    # zero-width space
        "\u200c": "",    # zero-width non-joiner
        "\u200d": "",    # zero-width joiner
        "\ufeff": "",    # byte order mark
        "\u00a1": "!",   # inverted exclamation mark
        "\u00bf": "?",   # inverted question mark
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    # Encode to Latin-1, replacing any remaining unsupported chars with '?'
    return text.encode("latin-1", errors="replace").decode("latin-1")


def build_message(flags: list) -> str:
    flagged = [f for f in flags if f["flagged"]]
    if not flagged:
        return "No concerns flagged. The contract appears consistent with your rules and concerns."
    lines = [f"{len(flagged)} concern(s) flagged:\n"]
    for f in flagged:
        lines.append(
            f"- Clause #{f['clause_index']} [{f['severity']}]: {sanitize_text(f['reason'])}\n"
            f'  Excerpt: {sanitize_text(f["clause"][:200])}...\n'
        )
    return "\n".join(lines)


class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Contract Review Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", new_x="LMARGIN", new_y="NEXT", align="C")


def _generate_pdf_sync(flags: list, contract_name: str, include_log: bool) -> str:
    _ensure_dir()
    safe_name = "".join(c for c in contract_name if c.isalnum() or c in (" ", "-", "_")).strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"{safe_name}_{timestamp}_review_report.pdf"

    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Contract: {sanitize_text(contract_name)}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Total clauses reviewed: {len(flags)}", new_x="LMARGIN", new_y="NEXT")
    flagged = [f for f in flags if f["flagged"]]
    pdf.cell(0, 7, f"Concerns flagged: {len(flagged)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Flagged Concerns", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    if not flagged:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, "No concerns were flagged.", new_x="LMARGIN", new_y="NEXT")
    else:
        for f in flagged:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(
                0,
                7,
                f"Clause #{f['clause_index']} - Severity: {f['severity'].upper()}",
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, f"Reason: {sanitize_text(f['reason'])}")
            pdf.ln(1)
            pdf.multi_cell(0, 6, f"Clause excerpt: {sanitize_text(f['clause'][:500])}")
            pdf.ln(3)

    if include_log:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Decision Log", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        logs = read_logs()
        if not logs:
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, "No decisions logged.", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "", 8)
            for entry in logs[-100:]:
                ts = sanitize_text(entry.get("timestamp", ""))
                agent = sanitize_text(entry.get("agent", ""))
                action = sanitize_text(entry.get("action", ""))
                result = sanitize_text(str(entry.get("result", ""))[:200])
                line = f"[{ts}] {agent} | {action} | {result}"
                pdf.multi_cell(0, 5, line)
                pdf.ln(1)

    pdf.output(str(report_path))
    return str(report_path)


def generate_report(
    flags: list,
    contract_name: str,
    include_log: bool = False,
    progress_callback=None,
) -> str:
    def _progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    _progress("Creating PDF report...")

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                _generate_pdf_sync, flags, contract_name, include_log
            )
            report_path = future.result(timeout=PDF_TIMEOUT_SECONDS)
    except concurrent.futures.TimeoutError:
        _progress("PDF generation timed out.")
        raise TimeoutError(f"PDF generation timed out after {PDF_TIMEOUT_SECONDS}s")
    except Exception as e:
        _progress(f"PDF generation failed: {str(e)}")
        raise

    _progress("PDF report ready.")

    log_decision(
        agent="Agent 4 - Messenger",
        action="generate_report",
        details={
            "contract_name": contract_name,
            "num_flagged": len([f for f in flags if f["flagged"]]),
            "include_log": include_log,
        },
        result={"report_path": report_path},
    )
    return report_path


def run(
    flags: list,
    contract_name: str,
    include_log: bool = False,
    progress_callback=None,
) -> dict:
    message = build_message(flags)
    report_path = generate_report(
        flags, contract_name, include_log=include_log, progress_callback=progress_callback
    )
    return {"message": message, "report_path": report_path}
