"""
Intake Form Filler
==================
Uses Claude to analyze client documents and generate assumptions for the
5 intake form questions from pre-session-prep.md.

Returns a structured dict of assumed answers + a confidence note per question.
"""
import boto3
import json
import anthropic


def _get_api_key() -> str:
    """Fetch the real Anthropic API key from AWS Secrets Manager."""
    sm = boto3.client("secretsmanager", region_name="us-east-1")
    secret = sm.get_secret_value(SecretId="claude-observability/anthropic")["SecretString"]
    # Secret may be a JSON object or a plain string
    try:
        data = json.loads(secret)
        return data.get("api_key") or data.get("ANTHROPIC_API_KEY") or list(data.values())[0]
    except (json.JSONDecodeError, IndexError):
        return secret.strip()

INTAKE_QUESTIONS = {
    "tools": "What apps or tools does this person use at least weekly? List each tool and what they use it for.",
    "departments": "If this person hired 3-5 people to replace themselves, what departments or roles would they create? Give each role a name.",
    "annoying_task": "What recurring task takes 30+ minutes and follows the same steps every time that they'd want automated?",
    "morning_briefing": "What would a perfect morning briefing from their AI agent include? (data, format, tone)",
    "agent_personality": "What should their AI agent call them? What vibe/personality should it have? Any name ideas?",
}

SYSTEM_PROMPT = """You are a consulting analyst helping Greg Black at GBAutomation.
Greg is an AI automation consultant who has received documents from a new client.
Your job is to analyze those documents and make educated assumptions about the client's
answers to a standard intake form — so Greg can send a pre-filled draft for the client to review.

Be specific and concrete. Pull real details from the documents. If you can't determine an answer
with confidence, say so clearly with "LOW CONFIDENCE:" prefix. Don't make things up.

Return your answer as a JSON object with these exact keys:
- tools: list of {tool, purpose} objects
- departments: list of {role_name, description} objects
- annoying_task: {task, frequency, steps: [list of step strings]}
- morning_briefing: {items: [list of items they'd want], format_notes: string, tone: string}
- agent_personality: {name: string or null, nickname: string, vibe: string}
- confidence_notes: {tools: string, departments: string, annoying_task: string, morning_briefing: string, agent_personality: string}
"""


def fill_intake(client_name: str, documents: dict[str, str]) -> dict:
    """
    Analyze client documents and return assumed intake answers.

    Args:
        client_name: Full name of the client
        documents: Dict mapping {filename/source: text_content}

    Returns:
        Dict with keys: tools, departments, annoying_task, morning_briefing,
        agent_personality, confidence_notes
    """
    client = anthropic.Anthropic(api_key=_get_api_key())

    # Build the document context
    doc_sections = []
    for source, text in documents.items():
        if text.strip():
            truncated = text[:4000] if len(text) > 4000 else text
            doc_sections.append(f"=== {source} ===\n{truncated}\n")

    if not doc_sections:
        return _empty_result("No documents provided")

    docs_text = "\n".join(doc_sections)

    user_prompt = f"""Client: {client_name}

I've scanned {len(documents)} document(s) from this client. Please analyze them and fill out
the intake form assumptions.

DOCUMENTS:
{docs_text}

Based on these documents, answer each intake question as specifically as possible.
Return valid JSON only (no markdown, no code blocks).
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    import json
    raw = response.content[0].text.strip()

    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return _empty_result(f"Failed to parse Claude response: {raw[:200]}")


def _empty_result(reason: str) -> dict:
    return {
        "tools": [],
        "departments": [],
        "annoying_task": {"task": "Unknown", "frequency": "Unknown", "steps": []},
        "morning_briefing": {"items": [], "format_notes": "", "tone": ""},
        "agent_personality": {"name": None, "nickname": "", "vibe": ""},
        "confidence_notes": {
            "tools": reason,
            "departments": reason,
            "annoying_task": reason,
            "morning_briefing": reason,
            "agent_personality": reason,
        },
    }


def format_assumptions_markdown(client_name: str, assumptions: dict, source_files: list[str]) -> str:
    """Format assumptions as a clean markdown document for the Google Doc."""
    first_name = client_name.split()[0]
    lines = [
        f"# Intake Analysis — {client_name}",
        "",
        f"*Auto-generated from {len(source_files)} document(s): {', '.join(source_files)}*",
        "",
        "---",
        "",
        "## Q1: Your Tools",
        "",
    ]

    tools = assumptions.get("tools", [])
    if tools:
        lines.append("| Tool | What You Use It For |")
        lines.append("|------|---------------------|")
        for t in tools:
            if isinstance(t, dict):
                lines.append(f"| {t.get('tool', '')} | {t.get('purpose', '')} |")
            else:
                lines.append(f"| {t} | |")
    else:
        lines.append("*Could not determine tools from provided documents.*")

    note = assumptions.get("confidence_notes", {}).get("tools", "")
    if note:
        lines.append(f"\n*Confidence: {note}*")

    lines += ["", "## Q2: Your Departments", ""]
    depts = assumptions.get("departments", [])
    for i, d in enumerate(depts, 1):
        if isinstance(d, dict):
            lines.append(f"{i}. **{d.get('role_name', '')}** — {d.get('description', '')}")
        else:
            lines.append(f"{i}. {d}")

    if not depts:
        lines.append("*Could not determine departments from provided documents.*")

    note = assumptions.get("confidence_notes", {}).get("departments", "")
    if note:
        lines.append(f"\n*Confidence: {note}*")

    lines += ["", "## Q3: Your Most Annoying Task", ""]
    task = assumptions.get("annoying_task", {})
    if isinstance(task, dict) and task.get("task"):
        lines.append(f"**Task**: {task.get('task', '')}")
        lines.append(f"**How often**: {task.get('frequency', '')}")
        steps = task.get("steps", [])
        if steps:
            lines.append("**Steps:**")
            for s in steps:
                lines.append(f"- {s}")
    else:
        lines.append("*Could not determine from provided documents.*")

    note = assumptions.get("confidence_notes", {}).get("annoying_task", "")
    if note:
        lines.append(f"\n*Confidence: {note}*")

    lines += ["", "## Q4: Your Perfect Morning Briefing", ""]
    briefing = assumptions.get("morning_briefing", {})
    items = briefing.get("items", []) if isinstance(briefing, dict) else []
    for item in items:
        lines.append(f"- {item}")
    format_notes = briefing.get("format_notes", "") if isinstance(briefing, dict) else ""
    tone = briefing.get("tone", "") if isinstance(briefing, dict) else ""
    if format_notes:
        lines.append(f"\n*Format preference: {format_notes}*")
    if tone:
        lines.append(f"*Tone: {tone}*")
    if not items:
        lines.append("*Could not determine from provided documents.*")

    note = assumptions.get("confidence_notes", {}).get("morning_briefing", "")
    if note:
        lines.append(f"\n*Confidence: {note}*")

    lines += ["", "## Q5: Your Agent's Personality", ""]
    persona = assumptions.get("agent_personality", {})
    if isinstance(persona, dict):
        if persona.get("nickname"):
            lines.append(f"**What to call you**: {persona['nickname']}")
        if persona.get("name"):
            lines.append(f"**Agent name**: {persona['name']}")
        if persona.get("vibe"):
            lines.append(f"**Vibe**: {persona['vibe']}")
    if not persona or (isinstance(persona, dict) and not any(persona.values())):
        lines.append("*Could not determine from provided documents.*")

    note = assumptions.get("confidence_notes", {}).get("agent_personality", "")
    if note:
        lines.append(f"\n*Confidence: {note}*")

    return "\n".join(lines)
