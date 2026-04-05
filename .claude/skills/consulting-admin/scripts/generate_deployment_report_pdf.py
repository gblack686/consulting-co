"""Generate Fish Group deployment options report as PDF using reportlab."""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER

OUT = Path(__file__).parent.parent.parent.parent / "skills/consulting-intake/client-sessions/20260305-michael-fisch/session_output"
OUT.mkdir(exist_ok=True)
out_path = OUT / "fish_group_deployment_report.pdf"

# Colors
DARK   = colors.HexColor("#1a1a1a")
PURPLE = colors.HexColor("#9b59b6")
MGRAY  = colors.HexColor("#e0e0e0")
LGRAY  = colors.HexColor("#f4f4f4")
WHITE  = colors.white
REC_BG = colors.HexColor("#d4f0dc")
REC_FG = colors.HexColor("#1a7c3a")
GOOD_BG= colors.HexColor("#dce8ff")
GOOD_FG= colors.HexColor("#1a50a0")
LIM_BG = colors.HexColor("#fff0d0")
LIM_FG = colors.HexColor("#8a5a00")

def S(name, **kw):
    return ParagraphStyle(name, **kw)

title_s  = S("T",  fontName="Helvetica-Bold", fontSize=20, textColor=WHITE,       leading=26, spaceAfter=4)
sub_s    = S("Su", fontName="Helvetica",      fontSize=10, textColor=colors.HexColor("#aaaaaa"), leading=14, spaceAfter=2)
tag_s    = S("Ta", fontName="Helvetica",      fontSize=8,  textColor=colors.HexColor("#888888"), leading=12)
h2_s     = S("H2", fontName="Helvetica-Bold", fontSize=13, textColor=DARK,        leading=17, spaceBefore=16, spaceAfter=5)
h3_s     = S("H3", fontName="Helvetica-Bold", fontSize=11, textColor=DARK,        leading=14, spaceBefore=10, spaceAfter=3)
body_s   = S("B",  fontName="Helvetica",      fontSize=9.5,textColor=colors.HexColor("#333333"), leading=14, spaceAfter=5)
small_s  = S("Sm", fontName="Helvetica",      fontSize=8,  textColor=colors.HexColor("#666666"), leading=11, spaceAfter=2)
code_s   = S("Co", fontName="Courier",        fontSize=7.5,textColor=colors.HexColor("#cccccc"), leading=10, backColor=DARK, leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=4)
footer_s = S("Fo", fontName="Helvetica",      fontSize=8,  textColor=colors.HexColor("#aaaaaa"), leading=11, alignment=TA_CENTER)
ph_h_s   = S("PH", fontName="Helvetica-Bold", fontSize=9,  textColor=colors.HexColor("#d4aaff"), leading=12, spaceAfter=2)
ph_b_s   = S("PB", fontName="Helvetica",      fontSize=8.5,textColor=colors.HexColor("#cccccc"), leading=12, leftIndent=10, spaceAfter=1)
rec_h_s  = S("RH", fontName="Helvetica-Bold", fontSize=13, textColor=WHITE,       leading=17, spaceAfter=3)
rec_b_s  = S("RB", fontName="Helvetica",      fontSize=9,  textColor=colors.HexColor("#cccccc"), leading=13, spaceAfter=6)
tbl_h_s  = S("TH", fontName="Helvetica-Bold", fontSize=8.5,textColor=WHITE,       leading=11)
b_rec_s  = S("BR", fontName="Helvetica-Bold", fontSize=7.5,textColor=REC_FG,      leading=10)
b_good_s = S("BG", fontName="Helvetica-Bold", fontSize=7.5,textColor=GOOD_FG,     leading=10)
b_lim_s  = S("BL", fontName="Helvetica-Bold", fontSize=7.5,textColor=LIM_FG,      leading=10)

def hr():
    return HRFlowable(width="100%", thickness=0.8, color=MGRAY, spaceAfter=5, spaceBefore=2)

def option_card(num, title, subtitle, badge_txt, badge_style, badge_bg,
                body, pros, cons, cost, arch=None):
    W = 6.6 * inch
    rows = []

    # Title + badge
    badge_tbl = Table([[Paragraph(badge_txt, badge_style)]], colWidths=[1.05*inch])
    badge_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), badge_bg),
        ("TOPPADDING",    (0,0),(-1,-1), 3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",   (0,0),(-1,-1), 7), ("RIGHTPADDING", (0,0),(-1,-1),7),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
    ]))
    hdr = Table([[Paragraph(f"<b>Option {num} — {title}</b>", h3_s), badge_tbl]],
                colWidths=[5.2*inch, 1.15*inch])
    hdr.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",  (0,0),(-1,-1),0),
        ("RIGHTPADDING", (0,0),(-1,-1),0),
    ]))
    rows.append([hdr])
    rows.append([Paragraph(subtitle, small_s)])
    rows.append([Spacer(1,3)])
    rows.append([Paragraph(body, body_s)])

    if arch:
        rows.append([Paragraph(arch, code_s)])
        rows.append([Spacer(1,3)])

    # Pros/cons
    def pc_col(items, label, fg, bg):
        cells = [[Paragraph(f"<b>{label}</b>", S("l", fontName="Helvetica-Bold", fontSize=7.5, textColor=fg, leading=10))]]
        for item in items:
            cells.append([Paragraph(f"+ {item}" if "PRO" in label else f"- {item}",
                                    S("i", fontName="Helvetica", fontSize=8.5, textColor=fg, leading=12))])
        t = Table(cells, colWidths=[3.05*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), bg),
            ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",   (0,0),(-1,-1), 8), ("RIGHTPADDING", (0,0),(-1,-1),8),
            ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#cccccc")),
        ]))
        return t

    pc = Table([[pc_col(pros,"PROS",REC_FG,colors.HexColor("#f0faf3")),
                 pc_col(cons,"CONS",colors.HexColor("#c0392b"),colors.HexColor("#fff5f5"))]],
               colWidths=[3.1*inch, 3.1*inch])
    pc.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    rows.append([pc])
    rows.append([Spacer(1,5)])
    rows.append([Paragraph(f"<b>Cost:</b> {cost}", small_s)])

    card = Table(rows, colWidths=[W])
    card.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 0.8, MGRAY),
        ("BACKGROUND",    (0,0),(-1,-1), WHITE),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
    ]))
    return KeepTogether([card, Spacer(1,10)])


doc = SimpleDocTemplate(
    str(out_path), pagesize=letter,
    leftMargin=0.85*inch, rightMargin=0.85*inch,
    topMargin=0.85*inch, bottomMargin=0.85*inch
)
story = []

# Header
hdr_rows = [
    [Paragraph("GBAutomation Consulting  ·  Confidential", tag_s)],
    [Paragraph("Fish Group — AI Architecture &amp; Deployment Options", title_s)],
    [Paragraph("A guide to the different ways Fish Group can interact with Claude and the codebase,<br/>from local development to fully autonomous cloud agents.", sub_s)],
    [Paragraph("AWS EC2  ·  Claude Code  ·  OpenClaw  ·  March 2026  ·  Prepared for Michael Fisch", tag_s)],
]
hdr_tbl = Table(hdr_rows, colWidths=[6.6*inch])
hdr_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), DARK),
    ("TOPPADDING",    (0,0),(-1,-1), 10), ("BOTTOMPADDING",(0,0),(-1,-1),10),
    ("LEFTPADDING",   (0,0),(-1,-1), 22), ("RIGHTPADDING", (0,0),(-1,-1),22),
]))
story += [hdr_tbl, Spacer(1,16)]

# Section 1 — Spectrum
story.append(Paragraph("The Tool Spectrum: From Workflow to Autonomous", h2_s))
story.append(hr())
story.append(Paragraph(
    "Before choosing a deployment model, it helps to understand where each tool sits on the agency spectrum.",
    body_s))
spec = [
    [Paragraph(t, tbl_h_s) for t in ["Tool","Who defines steps?","Runs 24/7?","Best for","~Cost/mo"]],
    ["n8n","You — visually","Yes (server)","Deterministic triggers","$80–150"],
    ["Claude Code","You set goal; AI plans","No (needs human)","Builds, code gen, dev work","$20–200"],
    ["OpenClaw","Agent autonomously","Yes (cloud)","Autonomous repeatable ops","$100–200"],
]
spec_tbl = Table(spec, colWidths=[0.85*inch,1.6*inch,1.0*inch,2.1*inch,0.85*inch])

spec_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,0), DARK),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LGRAY]),
    ("FONTNAME",      (0,1),(-1,-1),"Helvetica"), ("FONTSIZE",(0,1),(-1,-1),9),
    ("GRID",          (0,0),(-1,-1), 0.5, MGRAY),
    ("TOPPADDING",    (0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",   (0,0),(-1,-1), 7), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
]))
story += [spec_tbl, Spacer(1,7)]
story.append(Paragraph(
    "<b>The winning strategy: use all three.</b> Claude Code builds and maintains the skills. "
    "OpenClaw runs them autonomously. n8n handles webhook triggers if needed.",
    body_s))
story.append(Spacer(1,10))

# Seats pricing matrix
story.append(Paragraph("Claude Seat Pricing — 2 Seats (Michael + Emil)", h2_s))
story.append(hr())
story.append(Paragraph(
    "Both Michael and Emil need Claude Code and Cowork access. "
    "All paid plans include both features — the difference is token limits and reset windows. "
    "For active Claude Code development, Pro's 5-hour window caps out fast during coding sessions.",
    body_s))

seats_data = [
    [Paragraph(t, tbl_h_s) for t in ["Plan","Price/seat","Token Limit","Reset","Claude Code","Cowork","Best for"]],
    ["Pro",     "$20/mo", "~44K tokens / ~45 msgs", "Every 5 hrs", "Yes", "Yes", "Business analysts"],
    ["Max 5x",  "$100/mo","~88K tokens (5x Pro)",   "Weekly",      "Yes", "Yes", "Developers & leads"],
    ["Max 20x", "$200/mo","~220K tokens (20x Pro)",  "Weekly",      "Yes", "Yes", "Power users"],
]
seats_tbl = Table(seats_data, colWidths=[0.65*inch,0.75*inch,1.5*inch,0.75*inch,0.75*inch,0.55*inch,1.3*inch])
seats_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,0),  DARK),
    ("BACKGROUND",    (0,1),(-1,1),  colors.HexColor("#dce8ff")),   # Pro — blue tint
    ("BACKGROUND",    (0,2),(-1,2),  colors.HexColor("#d4f0dc")),   # Max 5x — green tint
    ("BACKGROUND",    (0,3),(-1,3),  LGRAY),
    ("FONTNAME",      (0,1),(-1,-1), "Helvetica"), ("FONTSIZE",(0,1),(-1,-1),8.5),
    ("FONTNAME",      (0,1),(0,1),   "Helvetica-Bold"),
    ("FONTNAME",      (0,2),(0,2),   "Helvetica-Bold"),
    ("TEXTCOLOR",     (0,1),(-1,1),  GOOD_FG),
    ("TEXTCOLOR",     (0,2),(-1,2),  REC_FG),
    ("TEXTCOLOR",     (0,3),(-1,3),  colors.HexColor("#555555")),
    ("GRID",          (0,0),(-1,-1), 0.5, MGRAY),
    ("TOPPADDING",    (0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",   (0,0),(-1,-1), 7), ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("ALIGN",         (1,0),(-1,-1), "CENTER"),
    ("ALIGN",         (6,0),(-1,-1), "LEFT"),
]))
story += [seats_tbl, Spacer(1,6)]
story.append(Paragraph(
    "<b>Recommendation for Fish Group:</b> "
    "Start with <b>1x Max 5x + 1x Pro = $120/mo total</b>. "
    "Only one person is likely deep in Claude Code at a time — share the dev load so the Max seat "
    "goes to whoever is actively building. "
    "The Pro seat covers the other for writing, analysis, and lighter Cowork tasks. "
    "Upgrade the second seat to Max 5x if both are coding simultaneously.",
    body_s))
story.append(Spacer(1,8))

# Section 2 — Options
story.append(Paragraph("Deployment Options", h2_s))
story.append(hr())

story.append(option_card(
    1,"Local Dev (Claude Code on Laptop)",
    "Michael or Emil runs Claude Code locally from their MacBook / PC",
    "GOOD START", b_good_s, GOOD_BG,
    "The simplest entry point. Install Claude Code on your machine, give it access to your APIs "
    "(Airtable, Google, etc.) and work with it like a very smart pair programmer. "
    "You describe what you want, it builds it, you review.",
    ["Zero server cost","Instant setup (you already have it)",
     "Full control — you're in the loop on every step","Best for exploration and building"],
    ["Not always-on — laptop must be open","No autonomous execution",
     "API keys stored locally","Doesn't scale to client-facing automation"],
    "$20/mo Claude Max  ·  $0 server  ·  Best for: building skills & one-time tasks"
))

story.append(option_card(
    2,"Claude Professional with Seats",
    "Multiple Claude.ai Pro accounts for Michael, Emil, and team",
    "LIMITED", b_lim_s, LIM_BG,
    "Good for writing, summarizing, and conversational AI — but <b>not suitable for automated "
    "workflows or agents</b>. No API access, no MCP servers, no persistent agents.",
    ["Easy to provision team seats","No technical setup required",
     "Good for writing, analysis, Q&A","Clients can get seats too"],
    ["No API access — can't connect to Airtable/Google/etc.",
     "No persistent agents or cron jobs","Not suitable for automation",
     "$20-25/seat/month adds up quickly"],
    "$20–25/seat/mo  ·  Best for: team writing & analysis — not automation"
))

arch3 = ("Fish Group AWS Architecture (Option 3)\n"
         "---------------------------------------------\n"
         "  [ Michael / Emil — Claude Code CLI ]\n"
         "                  |\n"
         "                  v\n"
         "  [ EC2 t3.small ~$17/mo ]\n"
         "    OpenClaw Gateway (:18789)\n"
         "    |-- Finn (orchestrator)\n"
         "    |-- Client Ops agent\n"
         "    |-- Data/Airtable agent\n"
         "    |-- Permissions agent\n"
         "    AWS KMS  /  OpenRouter\n"
         "                  |\n"
         "  [ Google Workspace / Airtable\n"
         "    AWS IAM / QuickBooks / ShipStation ]")

story.append(option_card(
    3,"EC2 + OpenClaw (Always-On Agent)",
    "Fish Group internal agent running 24/7 on AWS EC2",
    "RECOMMENDED", b_rec_s, REC_BG,
    "OpenClaw runs continuously on EC2, listening for webhook triggers and executing cron jobs "
    "without anyone needing to be at a laptop. This is the Finn agent system we scoped in the session.",
    ["Always-on — runs cron jobs, listens for webhooks",
     "Secrets stored securely in AWS KMS",
     "Scales to multiple clients (one instance each)",
     "OpenRouter models — cheaper than Anthropic direct",
     "One AWS account per client = isolated billing"],
    ["Requires initial server setup (~2hr)",
     "Small ongoing EC2 cost","Need SSH access to debug/update"],
    "$17–35/mo EC2  ·  $20–50/mo OpenRouter  ·  ~$5/mo KMS  ·  Total: ~$50–90/mo per instance",
    arch=arch3
))

arch4 = ("Hybrid Architecture\n"
         "---------------------------------------------\n"
         "  [ Michael + Emil — Claude Code (local) ]\n"
         "    git push -> GitHub repo\n"
         "                  | git pull\n"
         "                  v\n"
         "  [ EC2 Fish Group ]   [ EC2 Per Client ]\n"
         "    OpenClaw + Finn      OpenClaw\n"
         "    onboarding,          Piermont / Gary's\n"
         "    permissions, briefs\n\n"
         "  Local dev + EC2 = fast builds + always-on execution.")

story.append(option_card(
    4,"Hybrid: Local Claude Code + EC2 OpenClaw",
    "The full Fish Group architecture — build locally, run autonomously in cloud",
    "RECOMMENDED", b_rec_s, REC_BG,
    "Michael and Emil use Claude Code on their laptops to <b>build and edit skills</b>. "
    "Those skills live in a Git repo. EC2 runs OpenClaw autonomously. "
    "This is Greg's personal setup — best of both worlds.",
    ["Local dev = fast iteration, no server round trips",
     "EC2 = always-on execution, no laptop dependency",
     "Git as source of truth — easy rollback",
     "Emil can dev locally while agent runs on EC2",
     "Client EC2 accounts isolated — their bill, their data"],
    ["Slightly more setup than a single option",
     "Requires Git workflow discipline"],
    "$20/mo Claude Code  ·  $50–90/mo EC2 Fish Group  ·  $25–50/mo per client instance",
    arch=arch4
))

# Recommendation block
phases = [
    ("Phase 1 — Now (this week)", [
        "Michael + Emil: use Claude Code locally — build first 2 skills (client onboarding, Airtable lookup)",
        "Set up one AWS account for Fish Group internal with per-client account strategy",
        "Generate Airtable personal access token + Google Workspace OAuth",
    ]),
    ("Phase 2 — Follow-up Session (~2 weeks)", [
        "Deploy OpenClaw on EC2 for Fish Group internal (Finn goes live)",
        "Connect Google Workspace, Airtable, AWS IAM via secrets",
        "Wire up first autonomous workflow: new client onboarding",
        "Set up morning ops brief cron job",
    ]),
    ("Phase 3 — Piermont + Gary's (4–8 weeks)", [
        "Piermont gets own EC2 instance with QuickBooks + ShipStation + Airtable agent",
        "Build chat UI portal for Piermont",
        "Scope Gary's CS agent — email triage first, voice AI second",
    ]),
]

rec_rows = [
    [Paragraph("Our Recommendation for Fish Group", rec_h_s)],
    [Paragraph("Start with Option 1 to get hands dirty. Move to Option 4 within 2–4 weeks.", rec_b_s)],
]
for ph_title, items in phases:
    ph_cells = [[Paragraph(ph_title, ph_h_s)]]
    for item in items:
        ph_cells.append([Paragraph(f"\u2022  {item}", ph_b_s)])
    ph_tbl = Table(ph_cells, colWidths=[5.8*inch])
    ph_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#0d1526")),
        ("TOPPADDING",    (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",   (0,0),(-1,-1), 12), ("RIGHTPADDING",(0,0),(-1,-1),12),
        ("LINEBEFORE",    (0,0),(0,-1), 3, PURPLE),
    ]))
    rec_rows.append([ph_tbl])
    rec_rows.append([Spacer(1,6)])

rec_tbl = Table(rec_rows, colWidths=[6.6*inch])
rec_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#1a1a2e")),
    ("TOPPADDING",    (0,0),(-1,-1), 8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ("LEFTPADDING",   (0,0),(-1,-1), 20), ("RIGHTPADDING",(0,0),(-1,-1),20),
]))
story += [KeepTogether([rec_tbl]), Spacer(1,18)]
story.append(Paragraph(
    "Prepared by GBAutomation Consulting  ·  March 2026  ·  Confidential — Fish Group only",
    footer_s))

doc.build(story)
print(f"Saved: {out_path}")
