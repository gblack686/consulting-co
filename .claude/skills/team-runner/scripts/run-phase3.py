#!/usr/bin/env python3
"""Phase 3: Run Team — execute agents via claude -p on Mac Mini through Meridian pipeline."""
import yaml, json, subprocess, sys, time

SPEC_FILE = sys.argv[1]
AGENT_IDS_FILE = sys.argv[2]

spec = yaml.safe_load(open(SPEC_FILE))
ids = json.load(open(AGENT_IDS_FILE))

MAC = "greg@100.88.4.114"
EMPIRE = "http://127.0.0.1:8800"
AUTH = "Authorization: Bearer eagle-empire-2026"

# Meridian env vars — bypass macOS Keychain, route through SDK proxy
MERIDIAN_ENV = "export ANTHROPIC_BASE_URL='http://127.0.0.1:3456'; export ANTHROPIC_API_KEY='meridian'"
CLAUDE_BIN = "/opt/homebrew/bin/claude"
PATH_EXPORT = "export PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH'"

project_path = spec["project"]["path"]
team_type = spec["team_type"]
timestamp = str(int(time.time()))
output_dir = f"{project_path}/.output/team-run-{timestamp}"

# Create output dir on Mac Mini
subprocess.run(["ssh", MAC, f"mkdir -p {output_dir}"], check=True)


def set_status(name, status):
    aid = ids.get(name, "")
    if aid:
        subprocess.run(
            ["ssh", MAC,
             f"curl -s -X PATCH -H '{AUTH}' -H 'Content-Type: application/json' "
             f"'{EMPIRE}/api/agents/{aid}' "
             f"-d '{{\"status\":\"{status}\"}}'"],
            capture_output=True
        )


def call_agent(agent, message):
    name = agent["name"]
    prompt_file = agent.get("system_prompt_file", "")
    prompt_inline = agent.get("system_prompt_inline", "")
    tools = agent.get("tools", [])
    max_turns = agent.get("max_turns", 50)
    timeout = spec.get("execution", {}).get("timeout_per_agent", 600)

    set_status(name, "working")
    print(f"  [{name}] working...", flush=True)

    # Build system prompt
    system_prompt = ""
    if prompt_file:
        system_prompt = f"$(cat {prompt_file})"
    elif prompt_inline:
        system_prompt = prompt_inline

    safe = name.lower().replace(" ", "-")
    sp_file = f"/tmp/eagle-sp-{safe}.txt"
    msg_file = f"/tmp/eagle-msg-{safe}.txt"

    # Write system prompt to temp file on Mac Mini
    if system_prompt and not system_prompt.startswith("$("):
        subprocess.run(
            ["ssh", MAC, f"cat > {sp_file}"],
            input=system_prompt, capture_output=True, text=True, timeout=30
        )
    elif system_prompt.startswith("$("):
        src = system_prompt[6:-1]
        subprocess.run(["ssh", MAC, f"cp {src} {sp_file}"], capture_output=True, timeout=30)

    # Write message to temp file on Mac Mini (no size limit)
    subprocess.run(
        ["ssh", MAC, f"cat > {msg_file}"],
        input=message, capture_output=True, text=True, timeout=30
    )

    # Determine permission mode based on agent tools
    has_write = any(t in tools for t in ["Write", "Edit"])
    perm_mode = "acceptEdits" if has_write else "plan"

    # Build claude -p command — routes through Meridian for Max plan billing
    cmd = f"{PATH_EXPORT}; {MERIDIAN_ENV}; cd {project_path}; "
    cmd += f"cat {msg_file} | {CLAUDE_BIN} -p --max-turns {max_turns} --permission-mode {perm_mode}"
    if system_prompt:
        cmd += f' --append-system-prompt "$(cat {sp_file})"'

    result = subprocess.run(["ssh", MAC, cmd], capture_output=True, text=True, timeout=timeout)
    response = result.stdout.strip() or result.stderr.strip() or "no response"

    # Save output to Mac Mini
    subprocess.run(
        ["ssh", MAC, f"cat > {output_dir}/{safe}.md"],
        input=response, capture_output=True, text=True, timeout=30
    )

    # Cleanup temp files
    subprocess.run(["ssh", MAC, f"rm -f {sp_file} {msg_file}"], capture_output=True, timeout=10)

    set_status(name, "idle")
    print(f"  [{name}] done ({len(response)} chars)", flush=True)
    return response


# Load brief
brief_dir = spec.get("brief", {}).get("dir", "")
brief_inline = spec.get("brief", {}).get("inline", "")

if brief_dir:
    result = subprocess.run(
        ["ssh", MAC, f"cat {project_path}/{brief_dir}/*.md 2>/dev/null"],
        capture_output=True, text=True
    )
    brief = result.stdout.strip()
elif brief_inline:
    brief = brief_inline
else:
    brief = "No brief provided. Proceed with project context."

# Execute based on team type
if team_type == "ceo-board":
    leader = next((a for a in spec["agents"] if a.get("role") == "team_leader"), spec["agents"][0])
    members = [a for a in spec["agents"] if a["name"] != leader["name"]]

    framing = call_agent(leader,
        f"Read this brief and produce your INITIAL FRAMING. Core tension, top 3 risks, "
        f"which board members to consult. BRIEF:\n\n{brief}")

    responses = {}
    for member in members:
        resp = call_agent(member,
            f"Review the brief and CEO framing. Give your position in 200 words MAX.\n\n"
            f"BRIEF:\n{brief}\n\nCEO FRAMING:\n{framing}")
        responses[member["name"]] = resp

    all_text = framing + "\n\n" + "\n\n".join(f"## {k}\n{v}" for k, v in responses.items())
    memo = call_agent(leader,
        f"Synthesize into FINAL DECISION MEMO: Decision, Rationale, Action Plan, "
        f"Dissent Record, Risk Register.\n\nBoard deliberation:\n{all_text}")

    subprocess.run(
        ["ssh", MAC, f"cat > {output_dir}/memo.md"],
        input=memo, capture_output=True, text=True, timeout=30
    )

elif team_type in ("multi-team", "ui-gen"):
    leader = next((a for a in spec["agents"] if a.get("role") == "team_leader"), spec["agents"][0])
    members = [a for a in spec["agents"] if a["name"] != leader["name"]]

    plan = call_agent(leader,
        f"You are the orchestrator. Plan the work for your team based on this context:\n\n{brief}")

    for member in members:
        call_agent(member,
            f"The orchestrator has planned:\n\n{plan}\n\nExecute your part based on your role.\n\nBrief:\n{brief}")

print(f"\nOutput saved to: {output_dir}")
print(f"Total agents called: {len(spec['agents'])}")
