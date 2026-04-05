#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "elevenlabs",
#     "python-dotenv",
#     "pygame",
# ]
# ///
"""
ElevenLabs Text-to-Speech Module for Claude Code Hooks
Speaks notifications using ElevenLabs API with pygame playback.

Uses Flash v2.5 model for ultra-low latency (~75ms).
Voice can be configured via ELEVENLABS_VOICE_ID environment variable.
"""

import os
import sys
import json
import platform
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Setup logging
LOG_FILE = Path(__file__).parent.parent.parent / "logs" / "tts_debug.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log(message):
    """Write to log file immediately."""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    except Exception as e:
        print(f"LOG ERROR: {e}", file=sys.stderr)

# Load environment variables
load_dotenv()


def speak_notification(text: str):
    """Convert text to speech using ElevenLabs API and play it."""

    log(f"speak_notification() called with: {text}")

    # Check if API key is set
    api_key = os.getenv("ELEVENLABS_API_KEY")
    log(f"API key found: {bool(api_key)} (length: {len(api_key) if api_key else 0})")

    if not api_key:
        msg = "ELEVENLABS_API_KEY not set"
        log(msg)
        print(msg, file=sys.stderr)
        return False

    try:
        log("Importing elevenlabs...")
        from elevenlabs import ElevenLabs, VoiceSettings
        log("Import successful")

        # Initialize client
        log("Creating ElevenLabs client...")
        client = ElevenLabs(api_key=api_key)
        log("Client created")

        # Get voice ID from env or use default
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "CaJslL1xziwefCeTNzHv")
        log(f"Using voice_id: {voice_id}")

        # Convert text to speech using Flash v2.5 for low latency
        log("Calling text_to_speech.convert()...")
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(
                speed=float(os.getenv("ELEVENLABS_SPEED", "1.1")),
                stability=float(os.getenv("ELEVENLABS_STABILITY", "0.5")),
                similarity_boost=float(os.getenv("ELEVENLABS_SIMILARITY", "0.75")),
            ),
        )
        log("Audio generated successfully")

        # Save audio to temporary file
        output_file = Path(__file__).parent.parent.parent / "logs" / "tts_output.mp3"
        log(f"Saving audio to: {output_file}")
        with open(output_file, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        log(f"Audio saved ({output_file.stat().st_size} bytes)")

        # Play the audio file (platform-specific)
        log("Playing audio...")
        play_audio(output_file)

        log(f"Spoke: {text}")
        return True

    except ImportError as e:
        msg = f"elevenlabs package not installed: {e}"
        log(msg)
        log(traceback.format_exc())
        print(msg, file=sys.stderr)
        return False
    except Exception as e:
        msg = f"Failed to generate speech: {e}"
        log(msg)
        log(traceback.format_exc())
        print(msg, file=sys.stderr)
        return False


def play_audio(audio_file: Path):
    """Play audio file using pygame (silent playback without opening external player)."""
    system = platform.system()
    log(f"play_audio() on {system}")

    try:
        if system == "Windows":
            # Use pygame for silent playback
            log(f"Using pygame to play: {audio_file}")

            import pygame
            import time

            # Initialize pygame mixer with settings optimized for MP3
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            log("pygame.mixer initialized")

            try:
                sound = pygame.mixer.Sound(str(audio_file))
                duration = sound.get_length()
                log(f"Audio file loaded as Sound (length: {duration:.2f}s)")

                # Play the sound
                channel = sound.play()
                log("Playback started")

                # Wait for completion
                time.sleep(duration + 0.5)
                log("Playback completed")

            except Exception as e:
                log(f"Sound playback failed, falling back to music: {e}")
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

            pygame.mixer.quit()
            log("pygame.mixer cleaned up")

        elif system == "Darwin":  # macOS
            log("Using afplay")
            subprocess.run(["afplay", str(audio_file)], check=True)
        elif system == "Linux":
            players = ["mpg123", "ffplay", "mplayer", "vlc"]
            for player in players:
                try:
                    log(f"Trying {player}")
                    subprocess.run([player, str(audio_file)], check=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    log(f"Played with {player}")
                    break
                except FileNotFoundError:
                    continue
    except Exception as e:
        msg = f"Failed to play audio: {e}"
        log(msg)
        log(traceback.format_exc())
        print(msg, file=sys.stderr)


def main():
    """Main entry point - can be called directly with text argument."""
    log("="*60)
    log("TTS MODULE STARTED")

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        speak_notification(text)
    else:
        # Read from stdin (hook mode)
        try:
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                hook_data = json.loads(stdin_data)
                message = hook_data.get("message", "Task complete")
                speak_notification(message)
        except Exception as e:
            log(f"Error: {e}")
            speak_notification("Task complete")

    log("="*60 + "\n")


if __name__ == "__main__":
    main()
