# Workflow Chart

## High-Level Communication Flow

```mermaid
flowchart TD
    H["Human + Info Needed<br/>Upload PDF contract<br/>Enter rules/concerns"]
    S["Supervisor Agent 0<br/>Coordinate workers"]
    W["Worker Agents<br/>OCR → Split → Interpret<br/>(Agent 1, 2, 3)"]
    M["Agent 4 — Messenger<br/>Generate PDF report"]
    O["Frontend Output<br/>Review & Download"]

    H --> S
    S --> W
    W --> M
    M --> O

    style H fill:#e1f5e1,stroke:#2e7d32
    style S fill:#fff3e0,stroke:#f57c00
    style W fill:#e3f2fd,stroke:#1565c0
    style M fill:#fce4ec,stroke:#c2185b
    style O fill:#e8f5e9,stroke:#2e7d32
```

## Detailed Workflow

```mermaid
flowchart TD
    H["1. Human + Info Needed<br/>Upload contract PDF<br/>Enter company rules/concerns<br/>Check 'Include decision log'"]

    S["2. Supervisor Agent 0<br/>Pre-flight: Check Ollama running<br/>Coordinate worker agents<br/>Log all decisions"]

    OCR["3. Agent 1 — OCR<br/>Extract text from PDF<br/>(pymupdf + OCR fallback)"]
    Split["4. Agent 2 — Split<br/>Segment into clauses"]
    Interpret["5. Agent 3 — Interpret<br/>Compare vs rules/concerns<br/>llama3.1 via Ollama<br/>20s timeout, 1 retry<br/>Max 2 concurrent"]
    Msg["6. Agent 4 — Messenger<br/>Generate PDF report<br/>Unicode-safe sanitize_text<br/>Timestamped filename"]

    FE["7. Frontend Output<br/>Display flagged/OK cards<br/>Download report<br/>Decision log accordion"]

    DL["8. Decision Log<br/>decisions.jsonl<br/>Append-only audit trail"]

    H --> S
    S --> OCR
    S --> Split
    S --> Interpret
    S --> Msg
    Msg --> FE
    S --> DL
    OCR --> DL
    Split --> DL
    Interpret --> DL
    Msg --> DL

    style H fill:#e1f5e1,stroke:#2e7d32
    style S fill:#fff3e0,stroke:#f57c00
    style OCR fill:#e3f2fd,stroke:#1565c0
    style Split fill:#e3f2fd,stroke:#1565c0
    style Interpret fill:#fce4ec,stroke:#c2185b
    style Msg fill:#f3e5f5,stroke:#7b1fa2
    style FE fill:#e8f5e9,stroke:#2e7d32
    style DL fill:#ffebee,stroke:#c62828
```

---

## How to View

This file uses [Mermaid](https://mermaid.js.org/) syntax, which is rendered natively on GitHub. Open `Workflow-Chart.md` in the GitHub web UI to see the diagrams rendered as flowcharts.
