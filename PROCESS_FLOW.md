# CredCard AI — Process Flow (Diagram + Walkthrough)

## High-level process flow
```mermaid
flowchart TD
  U[User / Relationship Manager] -->|1. Fills telemetry inputs or selects JSON persona| UI[Browser UI: templates/index.html]

  UI -->|2. POST /calculate| FLASK[Flask backend: app_flask.py]
  FLASK -->|3. Reads dataset values| SE[Scoring engine: scoring_engine.py]
  SE -->|4. Computes scores + verdict + radar metrics| FLASK
  FLASK -->|5. Returns credit profile JSON| UI

  UI -->|6. Calls POST /generate_upfront_brief| FLASK
  FLASK -->|7. Calls local LLM chat endpoint (Ollama)| OLLAMA[Ollama @ localhost:11434]
  FLASK -->|8. Returns short upfront brief HTML/text| UI

  UI -->|9. Enables “Export Formal Sanction Memo (PDF)” button| UI
  UI -->|10. POST /export_pdf| FLASK
  FLASK -->|11. Generates PDF binary| PDFGEN[ReportLab: pdf_generator.py]
  PDFGEN -->|12. Adds underwriting verdict, scorecard, telemetry, and chat log| PDFOUT[PDF bytes]
  FLASK -->|13. Returns application/pdf for download| UI

  UI -->|14. (Optional) POST /query_ai for chat| FLASK
  FLASK -->|15. Maintains trimmed chat_history + prompts| CHATMODEL[Ollama chat]
  CHATMODEL -->|16. Returns assistant response| UI
```

## Step-by-step walkthrough

### A) Data entry → underwriting core
1. **UI** (`templates/index.html`) collects telemetry inputs or loads a persona preset.
2. UI sends those values to **Flask** via `POST /calculate`.
3. Flask calls the **scoring engine** (`scoring_engine.py`) to compute:
   - underwriting verdict (YES GO / MANUAL REVIEW / NO GO)
   - credit health score and integrity density
   - early distress probability and opportunity score
   - explainability notes / raw metrics used by the UI
4. Flask returns a JSON payload to the UI.

### B) Upfront brief generation (LLM)
5. UI immediately triggers **`POST /generate_upfront_brief`**.
6. Flask calls **Ollama** (`localhost:11434`) to generate a tight 1–2 sentence underwriting narrative.
7. Once the brief arrives, the UI **enables** the PDF export button.

### C) PDF export
8. UI sends **`POST /export_pdf`** to Flask.
9. Flask calls **`pdf_generator.py`** (ReportLab) to build the sanction memo PDF containing:
   - header + verdict stamp
   - scorecard metrics grid
   - telemetry inputs table
   - consultation log (filtered)
   - footer warning line in italics/small font
10. Flask returns `application/pdf`, and the browser downloads it.

### D) Optional interactive chat
11. UI can send additional questions via **`POST /query_ai`**.
12. Flask maintains `chat_history`, trims it to a safe window, and calls Ollama for the next assistant response.
13. UI renders the conversation.

## Files involved (by responsibility)
- **`templates/index.html`**: Frontend UI + triggers `/calculate`, `/generate_upfront_brief`, `/export_pdf`, `/query_ai`
- **`app_flask.py`**: Flask routes + Ollama calls + passes computed metrics into PDF generation
- **`scoring_engine.py`**: Deterministic rules/heuristics for credit scoring + verdict
- **`ai_engine.py` / `ai_training.py`**: LLM prompt shaping + (in the broader project) underwriting/chat templates
- **`pdf_generator.py`**: ReportLab PDF construction

## Notes
- This project uses **mock JSON payloads** (`mock_msme_*.json`) to simulate regulated data sources during development/testing.
- The PDF button is intentionally **disabled until the brief finishes generating** to ensure the memo contains the expected “brief-generated” context.
