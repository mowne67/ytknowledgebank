import yt_dlp
import os

def download_youtube_subtitles(video_url, language='en', output_dir='subtitles'):
    """
    Download subtitles from a YouTube video.
    Args:
        video_url (str): YouTube URL or video ID.
        language (str): Subtitle language code, default is 'en'.
        output_dir (str): Directory to save subtitles.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract video ID from URL
    import re
    match = re.search(r'(?:v=|youtu.be/)([\w-]+)', video_url)
    video_id = match.group(1) if match else 'video'

    # Set options for yt-dlp
    ydl_opts = {
        'writeautomaticsub': True,        # Download auto-generated subtitles if manual not available
        'writesubtitles': True,           # Download subtitles if available
        'subtitleslangs': [language],     # Language preference
        'skip_download': True,            # Do not download video
        'outtmpl': os.path.join(output_dir, f'{video_id}-%(title)s.%(ext)s'),  # Output path and filename pattern
        'subtitlesformat': 'srt',         # Subtitle format
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'video')
            print(f"Downloading subtitles for: {title}")
            ydl.download([video_url])
            print(f"Subtitles saved in: {output_dir}")
    except Exception as e:
        print(f"Error during subtitle download: {e}")

# Example usage
# video_url = "https://www.youtube.com/watch?v=va4cAYvTvzI"
# download_youtube_subtitles(video_url, language='en')
