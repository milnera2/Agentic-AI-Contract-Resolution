import re
from log import log_decision


def run(text: str) -> dict:
    raw_parts = re.split(r"\n\s*\n", text)
    clauses = []
    for part in raw_parts:
        part = part.strip()
        if part:
            clauses.append(part)

    refined = []
    for clause in clauses:
        if len(clause) > 2000:
            sub_parts = re.split(r"(?=\n\d+\.)", clause)
            for sp in sub_parts:
                sp = sp.strip()
                if sp:
                    refined.append(sp)
        else:
            refined.append(clause)

    log_decision(
        agent="Agent 2 - Split",
        action="split_clauses",
        details={"text_length": len(text)},
        result={"num_clauses": len(refined)},
    )
    return {"clauses": refined}
