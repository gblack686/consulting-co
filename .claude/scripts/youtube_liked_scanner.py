"""
Daily YouTube Scanner
- Fetches videos liked in the past 24 hours from gblack686@gmail.com
- Checks whitelisted channels for new uploads
- Checks whitelisted playlists for new episodes
- Extracts transcripts via yt-dlp
- Generates a daily summary .md with links to repos/sources
- Output: .claude/context/youtube-likes/YYYY-MM-DD/
"""
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
import requests

# --- Config ---
SECRET_NAME = "gbautomation/google/youtube-gblack686"
YTDLP = "C:/Users/gblac/AppData/Local/Programs/Python/Python312/Scripts/yt-dlp"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_ROOT = PROJECT_ROOT / ".claude" / "context" / "youtube-likes"
STATE_FILE = OUTPUT_ROOT / "state.json"
CHANNELS_FILE = OUTPUT_ROOT / "channels.json"


def get_access_token():
    """Get a fresh access token using the stored refresh token."""
    sm = boto3.client("secretsmanager", region_name="us-east-1")
    secret = json.loads(
        sm.get_secret_value(SecretId=SECRET_NAME)["SecretString"]
    )
    resp = requests.post(secret["token_uri"], data={
        "client_id": secret["client_id"],
        "client_secret": secret["client_secret"],
        "refresh_token": secret["refresh_token"],
        "grant_type": "refresh_token",
    })
    resp.raise_for_status()
    return resp.json()["access_token"]


def load_channels():
    """Load whitelisted channels and playlists."""
    if CHANNELS_FILE.exists():
        return json.loads(CHANNELS_FILE.read_text(encoding="utf-8"))
    return {"channels": [], "playlists": []}


def load_state():
    """Load seen video IDs to avoid re-processing."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"seen": [], "last_run": None}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def fetch_recent_likes(access_token, since_hours=26):
    """Fetch liked videos from the past N hours (26h to overlap safely)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    headers = {"Authorization": f"Bearer {access_token}"}
    videos = []
    page_token = None

    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": "LL",
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params, headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("items", []):
            published = datetime.fromisoformat(
                item["snippet"]["publishedAt"].replace("Z", "+00:00")
            )
            if published < cutoff:
                return videos

            videos.append({
                "video_id": item["snippet"]["resourceId"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"].get("videoOwnerChannelTitle", "Unknown"),
                "liked_at": item["snippet"]["publishedAt"],
                "description": item["snippet"].get("description", ""),
                "source": "liked",
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return videos


def fetch_channel_uploads(access_token, channel, since_hours=26):
    """Fetch recent uploads from a whitelisted channel."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    cutoff_rfc = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    headers = {"Authorization": f"Bearer {access_token}"}
    videos = []

    # Search for recent uploads from this channel
    params = {
        "part": "snippet",
        "channelId": channel["id"],
        "order": "date",
        "publishedAfter": cutoff_rfc,
        "maxResults": 10,
        "type": "video",
    }
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params=params, headers=headers,
    )
    resp.raise_for_status()
    data = resp.json()

    for item in data.get("items", []):
        vid_id = item["id"].get("videoId")
        if not vid_id:
            continue
        videos.append({
            "video_id": vid_id,
            "title": item["snippet"]["title"],
            "channel": channel["name"],
            "published_at": item["snippet"]["publishedAt"],
            "description": item["snippet"].get("description", ""),
            "source": f"channel:{channel['handle']}",
            "category": channel.get("category", ""),
        })

    return videos


def fetch_playlist_new(access_token, playlist, seen_ids, max_check=10):
    """Check a playlist for videos we haven't seen yet (newest first)."""
    headers = {"Authorization": f"Bearer {access_token}"}
    videos = []

    params = {
        "part": "snippet",
        "playlistId": playlist["id"],
        "maxResults": max_check,
    }
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/playlistItems",
        params=params, headers=headers,
    )
    resp.raise_for_status()
    data = resp.json()

    for item in data.get("items", []):
        vid_id = item["snippet"]["resourceId"]["videoId"]
        if vid_id in seen_ids:
            continue
        videos.append({
            "video_id": vid_id,
            "title": item["snippet"]["title"],
            "channel": item["snippet"].get("videoOwnerChannelTitle", playlist["channel"]),
            "published_at": item["snippet"]["publishedAt"],
            "description": item["snippet"].get("description", ""),
            "source": f"playlist:{playlist['name']}",
            "category": playlist.get("category", ""),
        })

    return videos


def extract_transcript(video_id, out_dir):
    """Use yt-dlp to download subtitles + info, parse into clean transcript."""
    out_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run([
        YTDLP,
        "--write-auto-subs", "--write-info-json", "--skip-download",
        "--sub-langs", "en", "--sub-format", "json3",
        "--output", str(out_dir / "%(id)s"),
        f"https://www.youtube.com/watch?v={video_id}",
    ], capture_output=True, text=True, timeout=60)

    json3_path = out_dir / f"{video_id}.en.json3"
    transcript_path = out_dir / f"{video_id}_transcript.txt"

    if json3_path.exists():
        subs = json.loads(json3_path.read_text(encoding="utf-8"))
        segments = []
        seen_text = set()
        for event in subs.get("events", []):
            if "segs" not in event:
                continue
            text = "".join(s.get("utf8", "") for s in event["segs"]).strip()
            text = text.replace("\n", " ")
            if not text or text in seen_text:
                continue
            seen_text.add(text)
            ms = event.get("tStartMs", 0)
            mins, secs = divmod(ms // 1000, 60)
            segments.append(f"[{mins}:{secs:02d}] {text}")

        transcript_text = "\n".join(segments)
        transcript_path.write_text(transcript_text, encoding="utf-8")

        # Clean up raw files, keep only transcript
        json3_path.unlink(missing_ok=True)
        info_path = out_dir / f"{video_id}.info.json"
        metadata = {}
        if info_path.exists():
            try:
                info = json.loads(info_path.read_text(encoding="utf-8"))
                metadata = {
                    "duration_seconds": info.get("duration"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "upload_date": info.get("upload_date"),
                    "tags": info.get("tags", [])[:10],
                }
            except Exception:
                pass
            info_path.unlink(missing_ok=True)

        return transcript_text, metadata

    return None, {}


def extract_links(description):
    """Pull GitHub repos, websites, and other useful links from description."""
    github_links = re.findall(r'https?://github\.com/[^\s)\]]+', description)
    other_links = re.findall(r'https?://(?!youtube|youtu\.be|google)[^\s)\]]+', description)
    github_links = list(dict.fromkeys(github_links))
    other_links = list(dict.fromkeys(l for l in other_links if l not in github_links))
    return github_links, other_links


def generate_daily_summary(date_str, liked, channel_vids, playlist_vids, out_dir):
    """Generate a concise daily summary .md file with sections per source."""
    lines = [
        f"# YouTube Daily Digest — {date_str}",
        f"",
        f"**Scanned**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Liked**: {len(liked)} | **Channel uploads**: {len(channel_vids)} | **Playlist new**: {len(playlist_vids)}",
        f"",
    ]

    def render_video_section(videos, section_title):
        if not videos:
            return
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"# {section_title}")
        lines.append(f"")
        for v in videos:
            url = f"https://youtube.com/watch?v={v['video_id']}"
            lines.append(f"## {v['title']}")
            lines.append(f"")
            lines.append(f"- **Channel**: {v['channel']}")
            lines.append(f"- **URL**: {url}")
            if v.get("source"):
                lines.append(f"- **Source**: {v['source']}")
            if v.get("liked_at"):
                lines.append(f"- **Liked**: {v['liked_at']}")
            if v.get("published_at"):
                lines.append(f"- **Published**: {v['published_at']}")
            if v.get("duration_seconds"):
                m, s = divmod(v["duration_seconds"], 60)
                lines.append(f"- **Duration**: {m}m {s}s")
            if v.get("view_count"):
                lines.append(f"- **Views**: {v['view_count']:,}")

            has_transcript = v.get("has_transcript", False)
            lines.append(f"- **Transcript**: {'`{vid}_transcript.txt`'.format(vid=v['video_id']) if has_transcript else 'unavailable'}")

            github_links, other_links = extract_links(v.get("description", ""))
            if github_links:
                lines.append(f"- **GitHub**:")
                for link in github_links[:5]:
                    lines.append(f"  - {link}")
            if other_links:
                lines.append(f"- **Links**:")
                for link in other_links[:5]:
                    lines.append(f"  - {link}")
            lines.append(f"")

    render_video_section(liked, "Liked Videos")
    render_video_section(channel_vids, "Channel Uploads")
    render_video_section(playlist_vids, "Playlist Updates")

    summary_path = out_dir / "daily-summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path


def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    day_dir = OUTPUT_ROOT / date_str

    print(f"YouTube Daily Scanner — {date_str}")
    print(f"Output: {day_dir}\n")

    state = load_state()
    seen = set(state.get("seen", []))
    config = load_channels()

    print("Authenticating...")
    access_token = get_access_token()

    # --- 1. Liked videos ---
    print("Fetching liked videos from past 24h...")
    liked_videos = fetch_recent_likes(access_token)
    new_liked = [v for v in liked_videos if v["video_id"] not in seen]
    print(f"  {len(new_liked)} new liked video(s)")

    # --- 2. Whitelisted channel uploads ---
    channel_videos = []
    channels = config.get("channels", [])
    if channels:
        print(f"Checking {len(channels)} whitelisted channels...")
        for ch in channels:
            try:
                uploads = fetch_channel_uploads(access_token, ch)
                new_uploads = [v for v in uploads if v["video_id"] not in seen]
                # Don't double-count videos already in liked
                liked_ids = {v["video_id"] for v in new_liked}
                new_uploads = [v for v in new_uploads if v["video_id"] not in liked_ids]
                if new_uploads:
                    print(f"  {ch['name']}: {len(new_uploads)} new")
                    channel_videos.extend(new_uploads)
            except Exception as e:
                print(f"  {ch['name']}: ERROR - {e}")

    # --- 3. Whitelisted playlists ---
    playlist_videos = []
    playlists = config.get("playlists", [])
    if playlists:
        print(f"Checking {len(playlists)} whitelisted playlists...")
        all_new_ids = {v["video_id"] for v in new_liked + channel_videos}
        for pl in playlists:
            try:
                new_pl = fetch_playlist_new(access_token, pl, seen)
                new_pl = [v for v in new_pl if v["video_id"] not in all_new_ids]
                if new_pl:
                    print(f"  {pl['name']}: {len(new_pl)} new")
                    playlist_videos.extend(new_pl)
            except Exception as e:
                print(f"  {pl['name']}: ERROR - {e}")

    # --- Combine and process ---
    all_new = new_liked + channel_videos + playlist_videos
    if not all_new:
        print("\nNo new videos found across all sources.")
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        return

    print(f"\nProcessing {len(all_new)} total new video(s)...\n")

    for v in all_new:
        vid = v["video_id"]
        print(f"  [{vid}] {v['title']}")
        print(f"    Extracting transcript...")

        transcript, metadata = extract_transcript(vid, day_dir)
        v.update(metadata)

        if transcript:
            v["has_transcript"] = True
            print(f"    > Transcript: {len(transcript)} chars")
        else:
            v["has_transcript"] = False
            print(f"    x No transcript available")

        seen.add(vid)

    # Generate summary
    summary_path = generate_daily_summary(date_str, new_liked, channel_videos, playlist_videos, day_dir)
    print(f"\nSummary: {summary_path}")

    # Update state
    state["seen"] = list(seen)[-2000:]
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    print(f"\nDone! {len(all_new)} video(s) processed.")


if __name__ == "__main__":
    main()
