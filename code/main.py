import asyncio
from pathlib import Path
from nicegui import ui, run
from orchestrator import orchestrator
from log import read_logs, clear_logs
from agents import messenger
from agents.messenger import sanitize_text

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

REPORT_DIR = Path(__file__).resolve().parent / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

result_card = None
message_label = None
stats_label = None
flags_container = None
download_btn = None
log_card = None
log_container = None
status_label = None
status_spinner = None
include_log_checkbox = None
ollama_status_label = None
log_visible = False


def check_ollama() -> bool:
    """Return True if Ollama is reachable and has llama3.1 available."""
    try:
        import ollama
        models = ollama.list()
        model_names = [m.get("model", "") for m in models.get("models", [])]
        return any("llama3.1" in name for name in model_names)
    except Exception:
        return False


@ui.page("/")
def index():
    global result_card, message_label, stats_label, flags_container, download_btn, log_card, log_container, status_label, status_spinner, include_log_checkbox, ollama_status_label, log_visible

    ui.query("body").style("font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;")

    with ui.column().classes("w-full max-w-5xl mx-auto p-4 gap-4"):
        ui.label("Agentic Contract Resolution").classes("text-2xl font-bold mb-2")
        ui.label(
            "Upload a contract PDF, add your company clauses/rules and concerns. "
            "Agents will extract, split, interpret, and flag issues with reasons."
        ).classes("text-gray-600 mb-4")

        # Ollama status indicator
        ollama_ok = check_ollama()
        ollama_status_label = ui.label(
            "Ollama llama3.1: " + ("ready" if ollama_ok else "NOT RUNNING — run 'ollama serve' and 'ollama pull llama3.1'")
        ).classes("text-xs font-mono mb-2").style(
            "color: green;" if ollama_ok else "color: red;"
        )

        uploaded_file = {}

        async def handle_upload(e):
            content = await e.file.read()
            uploaded_file["content"] = content
            uploaded_file["name"] = e.file.name

        pdf_upload = ui.upload(
            label="Upload Contract PDF",
            auto_upload=True,
            on_upload=handle_upload,
        ).classes("w-full")
        rules_input = ui.textarea(
            label="Company Clauses / Rules",
            placeholder="e.g. No auto-renewal clauses without 90-day notice; indemnity capped at contract value.",
        ).classes("w-full")
        concerns_input = ui.textarea(
            label="Specific Concerns",
            placeholder="e.g. Termination clauses, liability limits, non-compete restrictions.",
        ).classes("w-full")

        # Checkbox moved to form area (before run)
        include_log_checkbox = ui.checkbox("Include decision log in PDF report").classes("mb-2")

        status_spinner = ui.spinner(size="lg").classes("mb-2")
        status_spinner.style("display: none")
        status_label = ui.label("Ready").classes("text-xs text-gray-500 mb-4 font-mono")

        run_btn = ui.button("Run Resolution", icon="play_arrow").classes("w-full")

        result_card = ui.card().classes("w-full")
        result_card.style("display: none")
        with result_card:
            ui.label("Review Results").classes("text-lg font-bold mb-2")
            message_label = ui.label().classes("whitespace-pre-wrap mb-4")
            stats_label = ui.label().classes("text-sm text-gray-600 mb-2")
            flags_container = ui.column().classes("w-full gap-2")
            download_btn = ui.button("Download Report", icon="download").classes("w-full mb-4")

        def clear_decision_log():
            try:
                clear_logs()
                log_container.clear()
                ui.notify("Decision log cleared.", type="positive")
            except Exception as e:
                ui.notify(f"Error clearing log: {str(e)}", type="negative")

        log_card = ui.card().classes("w-full")
        log_card.style("display: none")
        with log_card:
            ui.label("Decision Log").classes("text-lg font-bold mb-2")
            log_container = ui.column().classes("w-full gap-1")
            ui.button("Clear Decision Log", icon="delete", on_click=clear_decision_log).classes("w-full mt-2")

        def toggle_logs():
            global log_visible
            log_visible = not log_visible
            try:
                if log_visible:
                    log_card.style("display: block")
                    log_container.clear()
                    with log_container:
                        for entry in read_logs()[-50:]:
                            with ui.card().classes("w-full bg-gray-50 border border-gray-200"):
                                ui.label(
                                    f"{entry['timestamp']} | {entry['agent']} | {entry['action']}"
                                ).classes("text-xs text-gray-600 font-mono mb-1")
                                ui.label(str(entry.get("result", ""))[:400]).classes(
                                    "text-xs text-gray-800 break-words"
                                )
                    logs_btn.text = "Hide Decision Log"
                else:
                    log_card.style("display: none")
                    logs_btn.text = "View Decision Log"
            except RuntimeError:
                ui.notify("Page session expired. Please refresh and try again.", type="negative")
                log_visible = False

        logs_btn = ui.button("View Decision Log", icon="history", on_click=toggle_logs).classes("w-full mt-2")

        async def on_run():
            if "content" not in uploaded_file:
                ui.notify("Please upload a PDF first.", type="negative")
                return

            # Validate file type
            if not uploaded_file["name"].lower().endswith(".pdf"):
                ui.notify("Please upload a PDF file.", type="negative")
                return

            # Ollama health check — fail fast instead of waiting per-clause timeouts
            if not check_ollama():
                ui.notify(
                    "Ollama llama3.1 is not running. Start Ollama and run 'ollama pull llama3.1'.",
                    type="negative",
                )
                return

            # Disable run button to prevent double-submission
            run_btn.disable()

            content = uploaded_file["content"]
            upload_path = UPLOAD_DIR / uploaded_file["name"]
            upload_path.write_bytes(content)

            submission = {
                "pdf_path": str(upload_path),
                "rules": rules_input.value or "",
                "concerns": concerns_input.value or "",
                "contract_name": uploaded_file["name"],
                "include_log": include_log_checkbox.value,
            }

            notification = ui.notify("Running agents...", type="ongoing", timeout=None)

            def progress_callback(msg: str):
                status_spinner.style("display: block")
                status_label.text = msg

            progress_callback("Reading contract...")
            try:
                result = await asyncio.wait_for(
                    run.io_bound(
                        orchestrator.run, submission, progress_callback=progress_callback
                    ),
                    timeout=300,
                )
                if notification is not None:
                    notification.dismiss()

                if result.get("error") or result.get("more_info_needed"):
                    status_spinner.style("display: none")
                    ui.notify(result.get("error", "More info needed."), type="warning")
                    return

                result_card.style("display: block")
                message_label.text = result["message"]
                stats_label.text = (
                    f"Clauses reviewed: {result['num_clauses']}  |  "
                    f"Flagged: {result['num_flagged']}"
                )

                flags_container.clear()
                with flags_container:
                    for f in result["flags"]:
                        if f["flagged"]:
                            with ui.card().classes("w-full border border-red-200 bg-red-50"):
                                ui.label(f"Clause #{f['clause_index']} - {f['severity'].upper()}").classes(
                                    "text-sm font-bold text-red-800 mb-1"
                                )
                                ui.label(sanitize_text(f["reason"])).classes("text-sm mb-1")
                                ui.label(sanitize_text(f["clause"][:400] + ("..." if len(f["clause"]) > 400 else ""))).classes(
                                    "text-xs text-gray-700 italic"
                                )
                        else:
                            with ui.card().classes("w-full border border-green-100 bg-green-50"):
                                ui.label(f"Clause #{f['clause_index']} - OK").classes(
                                    "text-sm font-bold text-green-800 mb-1"
                                )
                                ui.label(sanitize_text(f["reason"])).classes("text-xs text-gray-600")

                def on_download():
                    ui.download(result["report_path"])

                download_btn.on_click(on_download)
                status_spinner.style("display: none")
            except asyncio.TimeoutError:
                status_spinner.style("display: none")
                if notification is not None:
                    notification.dismiss()
                ui.notify(
                    "Workflow timed out after 5 minutes. Ollama may be too slow or unresponsive.",
                    type="negative",
                )
            except Exception as e:
                status_spinner.style("display: none")
                if notification is not None:
                    notification.dismiss()
                ui.notify(f"Error: {str(e)}", type="negative")
            finally:
                run_btn.enable()

        run_btn.on_click(on_run)


ui.run(title="Contract Resolution", host="localhost", port=8080)
