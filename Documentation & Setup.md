# Documentation & Setup

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | [NiceGUI](https://nicegui.io/) (Python) |
| LLM | [Ollama](https://ollama.com/) — `llama3.1` |
| Agent Orchestration | Custom Python supervisor loop (agent pattern matching Workflow-Chart.md) |
| PDF Parsing | `pymupdf` (digital PDFs); `pdf2image` + `pytesseract` (scanned PDFs, OCR) |
| Decision Log | Append-only `logs/decisions.jsonl` |
| PDF Generation | `fpdf2` (PDF reports) |

## Agent Workflow

The full agent workflow is documented in [Workflow-Chart.md](./Workflow-Chart.md) with two Mermaid diagrams:

1. **High-level communication flow** — Human → Supervisor → Worker Agents → Messenger → Frontend Output
2. **Detailed workflow** — All 8 steps including Ollama pre-flight check, per-agent responsibilities, decision log integration, and report generation


## Prerequisites

1. **Python 3.10+**
2. **Ollama** installed and running
   - Install: https://ollama.com
   - Pull the model: `ollama pull llama3.1`
3. **(Scanned PDFs only) Tesseract OCR**
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

## Installation

1. Clone this repository.
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1      # Windows PowerShell
   # or
   source venv/bin/activate         # macOS / Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r code/requirements.txt
   ```

## Running the Application

1. Start Ollama (required before running the app):
   - **Windows / macOS:** Ollama runs as a background service after installation. Open the Ollama app to confirm it's running.
   - **Linux:** Run `ollama serve` in a terminal, or start the Ollama application.
   - **Verify:** Run `ollama list` — it should show `llama3.1`. If not, pull it: `ollama pull llama3.1`
2. Start the app:
   ```bash
   python code/main.py
   ```
3. Open your browser to `http://localhost:8080`.

## Using the Tool

1. Upload a contract PDF.
2. Enter your company clauses/rules and any specific concerns.
3. Click **Run Resolution**.
4. The workflow runs through the agents and flags any concerns with a reason.
5. Review flagged concerns in the UI.
6. Click **Download Report** to save a PDF report. Optionally check **Include decision log** to append the full agent decision audit trail to the PDF.
7. Click **View Decision Log** to see the full audit trail of every agent decision.

## File Structure

- `code/main.py` — NiceGUI frontend entry point
- `code/orchestrator.py` — Session state and workflow entry
- `code/agents/supervisor.py` — Supervisor Agent 0 (coordinates workers)
- `code/agents/ocr.py` — Agent 1 (PDF text extraction)
- `code/agents/splitter.py` — Agent 2 (clause segmentation)
- `code/agents/interpreter.py` — Agent 3 (LLM-based flagging via Ollama)
- `code/agents/messenger.py` — Agent 4 (frontend message + download report)
- `code/tools/ocr_scanner.py` — PDF text extraction + OCR fallback
- `code/log.py` — Append-only decision logger
- `logs/decisions.jsonl` — Decision audit trail (created at runtime)
- `reports/` — Generated PDF reports (created at runtime)
- `uploads/` — Uploaded PDFs (created at runtime)
