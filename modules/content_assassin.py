import os
import re
import glob
import subprocess
import yt_dlp
from utils.logger import get_logger

logger = get_logger()

class ContentAssassin:
    def __init__(self):
        self.output_dir = os.path.join(os.path.expanduser("~"), "Desktop")

    def extract_script(self, url):
        """Download and clean subtitles/transcript text from a YouTube URL."""
        ydl_opts = {
            "skip_download": True,
            "writeautomaticsub": True,
            "writesubtitles": True,
            "subtitleslangs": ["en", "en-US", "en-GB", "en.*"],
            "subtitlesformat": "vtt",
            "outtmpl": "/tmp/jarvis_study_%(id)s",
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get("title", "Unknown_Video")
                video_id = info.get("id")

            subtitle_files = glob.glob(f"/tmp/jarvis_study_{video_id}*.vtt")
            if not subtitle_files:
                logger.warning(f"ContentAssassin: no subtitles downloaded for {url}")
                return None, None

            # Choose the largest subtitle file (usually fullest track).
            vtt_path = max(subtitle_files, key=lambda p: os.path.getsize(p))
            with open(vtt_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            text = self._clean_vtt(content)
            if not text.strip():
                logger.warning(f"ContentAssassin: cleaned transcript empty for {url}")
                self._cleanup_temp_files(video_id)
                return None, None

            self._cleanup_temp_files(video_id)
            return video_title, text

        except Exception as e:
            logger.error(f"ContentAssassin extract error: {e}")
            return None, None

    def _clean_vtt(self, raw_content):
        # Remove WEBVTT header metadata blocks only, not full content.
        text = re.sub(r"^WEBVTT[^\n]*\n", "", raw_content, flags=re.IGNORECASE)
        text = re.sub(r"^\s*NOTE.*$", "", text, flags=re.MULTILINE)
        text = re.sub(
            r"^\s*\d{1,2}:\d{2}(?::\d{2})?\.\d{3}\s*-->\s*\d{1,2}:\d{2}(?::\d{2})?\.\d{3}.*$",
            "",
            text,
            flags=re.MULTILINE,
        )
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&nbsp;", " ", text)

        # Remove numeric cue indices.
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

        # De-duplicate consecutive lines.
        cleaned_lines = []
        prev_line = ""
        for line in text.splitlines():
            clean_line = re.sub(r"\s+", " ", line).strip()
            if clean_line and clean_line != prev_line:
                cleaned_lines.append(clean_line)
                prev_line = clean_line

        return " ".join(cleaned_lines).strip()

    def _cleanup_temp_files(self, video_id):
        for path in glob.glob(f"/tmp/jarvis_study_{video_id}*"):
            try:
                os.remove(path)
            except Exception:
                pass

    def create_notes(self, title, summary_text):
        """Save AI summary to Desktop."""
        clean_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()
        clean_title = clean_title or "video"
        filename = f"Study_Notes_{clean_title}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Study Notes: {title}\n\n")
            f.write(summary_text)

        try:
            subprocess.run(["open", filepath], check=False)
        except Exception:
            logger.warning(f"ContentAssassin: could not auto-open {filepath}")

        return filename
