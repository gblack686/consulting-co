"""
Generate an agency/autonomy comparison chart for n8n, Claude Code, and OpenClaw.
Outputs: agency_comparison.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent.parent / "output"
OUT.mkdir(exist_ok=True)

# ---------- Data ----------
tools = [
    {
        "name": "Zapier / Make",
        "agency": 1.2,
        "control": 9.2,
        "cost_mo": 50,
        "color": "#888888",
        "size": 300,
        "label_offset": (-0.1, 0.55),
        "desc": "No-code triggers\n& actions",
    },
    {
        "name": "n8n",
        "agency": 2.8,
        "control": 8.0,
        "cost_mo": 80,
        "color": "#e05b3a",
        "size": 420,
        "label_offset": (0.1, 0.55),
        "desc": "Visual workflow\norchestrator",
    },
    {
        "name": "Claude Code",
        "agency": 6.8,
        "control": 4.5,
        "cost_mo": 200,
        "color": "#4a9eff",
        "size": 600,
        "label_offset": (0.1, 0.55),
        "desc": "Autonomous dev\nagent (human loop)",
    },
    {
        "name": "OpenClaw",
        "agency": 9.2,
        "control": 1.5,
        "cost_mo": 150,
        "color": "#9b59b6",
        "size": 700,
        "label_offset": (-2.2, 0.55),
        "desc": "24/7 autonomous\nagent (no loop)",
    },
]

# ---------- Plot ----------
fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor("#111111")
ax.set_facecolor("#1a1a1a")

# Grid
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 10.5)
ax.grid(color="#333333", linestyle="--", linewidth=0.6, alpha=0.8)
ax.spines[:].set_color("#444444")
ax.tick_params(colors="#888888", labelsize=10)

# Gradient background bands
for x_start, x_end, label, alpha in [
    (0, 3.5, "Workflow Automation", 0.06),
    (3.5, 7.5, "Agentic Workflows", 0.06),
    (7.5, 10.5, "Fully Autonomous", 0.08),
]:
    ax.axvspan(x_start, x_end, alpha=alpha, color="#ffffff")
    ax.text(
        (x_start + x_end) / 2, 10.0, label,
        ha="center", va="top", fontsize=9, color="#555555",
        fontstyle="italic"
    )

# Zone dividers
for x in [3.5, 7.5]:
    ax.axvline(x, color="#333333", linewidth=1, linestyle=":")

# Plot each tool
for t in tools:
    ax.scatter(
        t["agency"], t["control"],
        s=t["size"], color=t["color"],
        alpha=0.85, zorder=5, edgecolors="#ffffff", linewidths=0.8
    )
    ox, oy = t["label_offset"]
    ax.text(
        t["agency"] + ox, t["control"] + oy,
        t["name"],
        color="#ffffff", fontsize=12, fontweight="bold",
        ha="center", va="bottom"
    )
    ax.text(
        t["agency"] + ox, t["control"] + oy - 0.85,
        t["desc"],
        color="#aaaaaa", fontsize=8.5,
        ha="center", va="bottom"
    )

# Axis labels
ax.set_xlabel(
    "← Low Agency                    AGENCY / AUTONOMY                    High Agency →",
    color="#cccccc", fontsize=11, labelpad=12
)
ax.set_ylabel(
    "← Hands-Off          HUMAN OVERSIGHT REQUIRED          Full Control →",
    color="#cccccc", fontsize=11, labelpad=12
)

# X-axis tick labels
ax.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
ax.set_xticklabels(
    ["1\nManual", "2", "3", "4", "5\nHybrid", "6", "7", "8", "9", "10\nAuto"],
    color="#777777", fontsize=8
)
ax.set_yticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
ax.set_yticklabels(
    ["1\nNone", "2", "3", "4", "5\nModerate", "6", "7", "8", "9", "10\nFull"],
    color="#777777", fontsize=8
)

# Title
ax.set_title(
    "AI Tool Agency Comparison: n8n  ·  Claude Code  ·  OpenClaw",
    color="#ffffff", fontsize=15, fontweight="bold", pad=18
)

# Callout annotation — Fish Group recommendation
ax.annotate(
    "  Fish Group Phase 1\n  Start here →",
    xy=(6.8, 4.5), xytext=(5.0, 2.5),
    color="#4a9eff", fontsize=9,
    arrowprops=dict(arrowstyle="->", color="#4a9eff", lw=1.5),
)
ax.annotate(
    "  Fish Group Phase 2\n  Deploy here →",
    xy=(9.2, 1.5), xytext=(7.2, 3.2),
    color="#9b59b6", fontsize=9,
    arrowprops=dict(arrowstyle="->", color="#9b59b6", lw=1.5),
)

# Legend: bubble size = relative monthly cost
legend_elements = [
    mpatches.Patch(color="#888888", label="Zapier/Make — ~$50/mo"),
    mpatches.Patch(color="#e05b3a", label="n8n — ~$80/mo"),
    mpatches.Patch(color="#4a9eff", label="Claude Code — ~$200/mo"),
    mpatches.Patch(color="#9b59b6", label="OpenClaw — ~$150/mo"),
]
legend = ax.legend(
    handles=legend_elements,
    loc="lower right", framealpha=0.15, labelcolor="#cccccc",
    facecolor="#222222", edgecolor="#444444", fontsize=9
)

plt.tight_layout()
out_path = OUT / "agency_comparison.png"
plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="#111111")
plt.close()
print(f"Saved: {out_path}")
