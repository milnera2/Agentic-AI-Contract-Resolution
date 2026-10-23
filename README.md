# Agentic-AI-Contract-Resolution

An agentic AI workflow for automated contract resolution. Upload a contract PDF, add your company clauses/rules and specific concerns, and the system will flag problematic clauses with reasons using a multi-agent pipeline powered by Ollama (`llama3.1`).

## Features

- **PDF Upload** — Upload contract PDFs (digital or scanned) for analysis
- **Company Rules & Concerns** — Enter your company clauses/rules and specific concerns to check against
- **Agentic Pipeline** — 4-agent workflow: OCR extraction → clause splitting → LLM interpretation → report generation
- **Flagged Concerns** — Clauses conflicting with your rules are flagged with severity (low/medium/high) and a reason
- **Downloadable PDF Report** — Generate a Markdown-formatted PDF report with all flagged concerns
- **Decision Log** — Append-only audit trail of every agent decision (`logs/decisions.jsonl`)
- **Ollama Integration** — Runs entirely on local LLM via Ollama (`llama3.1`); no external API calls

## Agent Workflow

The full workflow is documented in [Workflow-Chart.md](./Workflow-Chart.md) with two Mermaid diagrams:

1. **High-level communication flow** — Human → Supervisor → Worker Agents → Messenger → Frontend Output
2. **Detailed workflow** — All 8 steps including Ollama pre-flight check, per-agent responsibilities, decision log integration, and report generation

### Agents

| Agent | Role |
|-------|------|
| **Supervisor Agent 0** | Coordinates workers, performs Ollama health check, logs decisions |
| **Agent 1 — OCR** | Extracts text from PDF (digital pages + OCR fallback for scanned) |
| **Agent 2 — Split** | Segments contract into individual clauses |
| **Agent 3 — Interpret** | Compares each clause against your rules/concerns using `llama3.1`; flags with reason + severity |
| **Agent 4 — Messenger** | Generates a downloadable PDF report; optional decision log inclusion |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | [NiceGUI](https://nicegui.io/) (Python) |
| LLM | [Ollama](https://ollama.com/) — `llama3.1` |
| Agent Orchestration | Custom Python supervisor loop |
| PDF Parsing | `pymupdf` (digital PDFs); `pdf2image` + `pytesseract` (scanned PDFs, OCR) |
| PDF Generation | `fpdf2` (PDF reports) |
| Decision Log | Append-only `logs/decisions.jsonl` |

## Prerequisites

- **Python 3.10+**
- **Ollama** installed and running
  - Install: https://ollama.com
  - Pull the model: `ollama pull llama3.1`
- **(Scanned PDFs only)** Tesseract OCR
  - Windows: https://github.com/UB-Mannheim/tesseract/wiki
  - macOS: `brew install tesseract`
  - Linux: `sudo apt install tesseract-ocr`

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Agentic-AI-Contract-Resolution.git
cd Agentic-AI-Contract-Resolution

# Create and activate a virtual environment
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r code/requirements.txt
```

## Usage

```bash
# 1. Start Ollama (ensure it's running with llama3.1)
ollama serve
ollama pull llama3.1

# 2. Start the application
python code/main.py

# 3. Open your browser to http://localhost:8080

# 4. Upload a contract PDF, enter your company clauses/rules and concerns

# 5. Click "Run Resolution"

# 6. Review flagged concerns in the UI

# 7. Click "Download Report" to save a PDF report (optionally include the decision log)

# 8. Click "View Decision Log" to see the full audit trail of every agent decision
```

## File Structure

```
Agentic-AI-Contract-Resolution/
├── Workflow-Chart.md          # Mermaid workflow diagrams (view on GitHub)
├── Documentation & Setup.md   # Detailed setup and usage guide
├── LICENSE.md                 # License information
├── README.md                  # This file
└── code/
    ├── main.py                # NiceGUI frontend entry point
    ├── orchestrator.py        # Workflow orchestrator
    ├── log.py                 # Decision logger (append-only JSONL)
    ├── requirements.txt       # Python dependencies
    ├── agents/
    │   ├── supervisor.py      # Supervisor Agent 0 (coordinates workers)
    │   ├── ocr.py             # Agent 1 — PDF text extraction
    │   ├── splitter.py        # Agent 2 — Clause segmentation
    │   ├── interpreter.py     # Agent 3 — LLM-based flagging via Ollama
    │   └── messenger.py       # Agent 4 — PDF report generation
    ├── tools/
    │   └── ocr_scanner.py     # PDF text extraction + OCR fallback
    ├── uploads/               # Uploaded PDFs (created at runtime)
    ├── reports/               # Generated PDF reports (created at runtime)
    └── logs/                  # Decision audit trail (created at runtime)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama llama3.1 is not running" | Start Ollama (`ollama serve`) and pull the model (`ollama pull llama3.1`) |
| "No text could be extracted from the PDF" | Ensure the PDF is not password-protected; scanned PDFs require Tesseract OCR |
| "LLM timeout after 2 attempts" | Ollama may be slow on CPU-only hardware; try again or reduce contract size |
| PDF generation fails | Ensure `fpdf2` is installed (`pip install -r code/requirements.txt`) |
| Decision log not appearing | Click "View Decision Log" to toggle the accordion panel |

## License

This project is licensed under the terms in [LICENSE.md](./LICENSE.md).

## Author

Aaron Milner
