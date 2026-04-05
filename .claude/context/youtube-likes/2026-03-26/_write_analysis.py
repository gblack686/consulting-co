
import pathlib

out = pathlib.Path(r"C:\Users\gblac\OneDrive\Desktop\consulting-co\.claude\context\youtube-likes\2026-03-26\HTu1OGWAn5w_analysis.md")

lines = []
lines.append("---")
lines.append("title: \"How to Use Claude Cowork Better Than 99% of People (Full Guide)\"")
lines.append("creator: Ben van Sprundel")
lines.append("channel: Ben AI")
lines.append("channel_url: https://www.youtube.com/channel/UC3KK7ENB_ierAXvrxVNnbZQ")
lines.append("video_url: https://www.youtube.com/watch?v=HTu1OGWAn5w")
lines.append("video_id: HTu1OGWAn5w")
lines.append("upload_date: 2026-01-31")
lines.append("duration: \"21:07\"")
lines.append("views: 256662")
lines.append("likes: 4264")
lines.append("date_accessed: 2026-03-26")
lines.append("type: deep-dive-analysis")
lines.append("companion_video: qo4YZvC1q5I (Obsidian Second Brain)")
lines.append("tags:")
for t in ["claude-cowork","claude-code","skills","mcp","ai-automation","workflow-automation","browser-use","connectors","content-repurposing","ai-consulting"]:
    lines.append(f"  - {t}")
lines.append("---")
lines.append("")

out.write_text(chr(10).join(lines), encoding="utf-8")
print("frontmatter written")
