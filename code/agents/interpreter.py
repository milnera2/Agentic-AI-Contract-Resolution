import asyncio
import concurrent.futures
import json
from pathlib import Path

import ollama
from log import log_decision

MODEL = "llama3.1"
TIMEOUT_SECONDS = 20
MAX_CONCURRENT = 2


def _check_clause_sync(clause: str, rules: str, concerns: str) -> dict:
    prompt = f"""
You are a contract review agent. Compare the following contract clause against the user's company rules and specific concerns.

Clause:
{clause}

Company Rules:
{rules or "(none provided)"}

Specific Concerns:
{concerns or "(none provided)"}

Determine if this clause should be FLAGGED because it conflicts with the company rules or matches a concern. Respond ONLY with valid JSON in this exact format:
{{
  "flagged": true/false,
  "reason": "brief explanation of why it is flagged or not",
  "severity": "low/medium/high"
}}
"""
    try:
        for attempt in range(2):
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        ollama.chat,
                        model=MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        format="json",
                    )
                    resp = future.result(timeout=TIMEOUT_SECONDS)
                content = resp["message"]["content"]
                return json.loads(content)
            except concurrent.futures.TimeoutError:
                if attempt == 0:
                    continue
                return {
                    "flagged": False,
                    "reason": "LLM timeout after 2 attempts — Ollama not responding or too slow",
                    "severity": "low",
                }
    except Exception as e:
        return {
            "flagged": False,
            "reason": f"Error evaluating clause: {str(e)}",
            "severity": "low",
        }


def run(clauses: list, rules: str, concerns: str, progress_callback=None) -> dict:
    def _progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    flags = []
    total = len(clauses)

    # Skip interpretation entirely if no rules or concerns provided
    if not rules.strip() and not concerns.strip():
        _progress("No rules or concerns — skipping interpretation.")
        for i, clause in enumerate(clauses):
            flag_entry = {
                "clause_index": i,
                "clause": clause,
                "flagged": False,
                "reason": "No company rules or concerns provided to check against.",
                "severity": "low",
            }
            flags.append(flag_entry)
            log_decision(
                agent="Agent 3 - Interpret",
                action="evaluate_clause",
                details={"clause_index": i, "clause_preview": clause[:120]},
                result=flag_entry,
            )
        return {"flags": flags}

    # Process clauses in parallel (MAX_CONCURRENT at a time)
    results = [None] * total
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def _check_one(i: int, clause: str):
        async with semaphore:
            result = await asyncio.to_thread(_check_clause_sync, clause, rules, concerns)
            results[i] = result

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    tasks = [_check_one(i, c) for i, c in enumerate(clauses)]
    loop.run_until_complete(asyncio.gather(*tasks))

    for i, (clause, result) in enumerate(zip(clauses, results)):
        if result is None:
            result = {
                "flagged": False,
                "reason": "Error evaluating clause: unknown",
                "severity": "low",
            }
        flag_entry = {
            "clause_index": i,
            "clause": clause,
            "flagged": result.get("flagged", False),
            "reason": result.get("reason", ""),
            "severity": result.get("severity", "low"),
        }
        flags.append(flag_entry)
        log_decision(
            agent="Agent 3 - Interpret",
            action="evaluate_clause",
            details={"clause_index": i, "clause_preview": clause[:120]},
            result=flag_entry,
        )

    return {"flags": flags}
