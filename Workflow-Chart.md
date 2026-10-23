# Workflow Chart

## High-Level Communication Flow

```mermaid
flowchart TD
    H["1. Human +<br/>Info Needed<br/>Upload PDF<br/>contract<br/>Enter rules/<br/>concerns"]
    S["2. Supervisor<br/>Agent 0<br/>Coordinate<br/>workers"]
    W["3. Worker<br/>Agents<br/>OCR → Split →<br/>Interpret<br/>(Agent 1, 2, 3)"]
    M["4. Agent 4 —<br/>Messenger<br/>Generate PDF<br/>report"]
    O["5. Frontend<br/>Output<br/>Review &<br/>Download"]

    H --> S
    S --> W
    W --> M
    M --> O

    style H fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000000
    style S fill:#ffcc80,stroke:#bf360c,stroke-width:2px,color:#000000
    style W fill:#bbdefb,stroke:#0d47a1,stroke-width:2px,color:#000000
    style M fill:#f8bbd0,stroke:#ad1457,stroke-width:2px,color:#000000
    style O fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000000
```

## Detailed Workflow

```mermaid
flowchart TD
    H["1. Human +<br/>Info Needed<br/>Upload contract<br/>PDF<br/>Enter company<br/>rules/concerns<br/>Check 'Include<br/>decision log'"]

    S["2. Supervisor<br/>Agent 0<br/>Pre-flight:<br/>Check Ollama<br/>running<br/>Coordinate<br/>workers<br/>Log all<br/>decisions"]

    OCR["3. Agent 1 —<br/>OCR<br/>Extract text<br/>from PDF<br/>(pymupdf +<br/>OCR fallback)"]
    Split["4. Agent 2 —<br/>Split<br/>Segment into<br/>clauses"]
    Interpret["5. Agent 3 —<br/>Interpret<br/>Compare vs<br/>rules/concerns<br/>llama3.1 via<br/>Ollama<br/>20s timeout,<br/>1 retry<br/>Max 2<br/>concurrent"]
    Msg["6. Agent 4 —<br/>Messenger<br/>Generate PDF<br/>report<br/>Unicode-safe<br/>sanitize_text<br/>Timestamped<br/>filename"]

    FE["7. Frontend<br/>Output<br/>Display<br/>flagged/OK<br/>cards<br/>Download<br/>report<br/>Decision log<br/>accordion"]

    DL["8. Decision<br/>Log<br/>decisions.jsonl<br/>Append-only<br/>audit trail"]

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

    style H fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000000
    style S fill:#ffcc80,stroke:#bf360c,stroke-width:2px,color:#000000
    style OCR fill:#bbdefb,stroke:#0d47a1,stroke-width:2px,color:#000000
    style Split fill:#bbdefb,stroke:#0d47a1,stroke-width:2px,color:#000000
    style Interpret fill:#f8bbd0,stroke:#ad1457,stroke-width:2px,color:#000000
    style Msg fill:#e1bee7,stroke:#4a148c,stroke-width:2px,color:#000000
    style FE fill:#c8e6c9,stroke:#1b5e20,stroke-width:2px,color:#000000
    style DL fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px,color:#000000
```

---

## How to View

This file uses [Mermaid](https://mermaid.js.org/) syntax, which is rendered natively on GitHub. Open `Workflow-Chart.md` in the GitHub web UI to see the diagrams rendered as flowcharts.
