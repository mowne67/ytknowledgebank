# Pipeline to generate summary from a YouTube video URL

import os
import sys
from subtitle_extraction import download_youtube_subtitles
from summarizer import summarize_srt_file
from loguru import logger

subtitles_dir = 'subtitles'

# Simple colored logging
def log_info(msg):
    print(f"\033[96m[INFO]\033[0m {msg}")

def log_success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")

def log_warning(msg):
    print(f"\033[93m[WARNING]\033[0m {msg}")

def log_error(msg):
    print(f"\033[91m[ERROR]\033[0m {msg}", file=sys.stderr)

def final_pipeline(video_url, language='en'):
    logger.info(f"Starting pipeline for URL: {video_url}")
    log_info(f"Downloading subtitles for: {video_url}")
    download_youtube_subtitles(video_url, language=language, output_dir=subtitles_dir)

    srt_files = [f for f in os.listdir(subtitles_dir) if f.endswith('.srt')]
    if not srt_files:
        log_error('No SRT file found after download.')
        return None
    srt_files = sorted(srt_files, key=lambda x: os.path.getmtime(os.path.join(subtitles_dir, x)), reverse=True)
    srt_file = os.path.join(subtitles_dir, srt_files[0])

    log_info(f"Summarizing: {srt_file}")
    # summarize_srt_file returns the markdown file path, but we want the summary string
    from summarizer import extract_text_from_srt, get_output
    clean_text = extract_text_from_srt(srt_file)
    summary = get_output(clean_text)
    # Save as before
    video_name = os.path.splitext(os.path.basename(srt_file))[0]
    summary_dir = 'summary'
    os.makedirs(summary_dir, exist_ok=True)
    md_output_path = os.path.join(summary_dir, f'{video_name}.md')
    with open(md_output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    log_success(f"Summary saved to {md_output_path}")
    logger.info("Pipeline completed successfully")
    return summary


def get_video_urls_from_channel(channel_url):
    import yt_dlp

    def extract_urls(entries):
        urls = []
        for entry in entries:
            if entry.get('_type') == 'url' and 'url' in entry:
                # If it's a full URL, use it directly
                urls.append(entry['url'])
            elif 'url' in entry and entry['url'].startswith('http'):
                urls.append(entry['url'])
            elif 'id' in entry:
                # Compose full video URL from ID
                urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
            # Recursively check for nested entries
            if 'entries' in entry and isinstance(entry['entries'], list):
                urls.extend(extract_urls(entry['entries']))
        return urls

    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'logger': None,
    }
    # Suppress yt-dlp warnings and errors
    class DummyLogger:
        def debug(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass
    ydl_opts['logger'] = DummyLogger()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        entries = info.get('entries', [])
        return extract_urls(entries)

def summarize_channel(channel_url, language='en'):
    video_urls = get_video_urls_from_channel(channel_url)
    log_info(f"Found {len(video_urls)} videos in channel.")
    import time
    for idx, url in enumerate(video_urls):
        log_info(f"Processing: {url}")
        try:
            final_pipeline(url, language=language)
        except Exception as e:
            log_error(f"Failed to process {url}: {e}")
        if idx < len(video_urls) - 1:
            log_warning("Waiting 15 seconds before next video...")
            time.sleep(15)

# Example usage:
if __name__ == "__main__":
    # For a single video:
    video_url = "https://www.youtube.com/watch?v=AQD1iNh57Mo"
    final_pipeline(video_url, language='en')

    # For a channel:
    # channel_url = "https://www.youtube.com/@kaalraam"
    # summarize_channel(channel_url, language='en')
