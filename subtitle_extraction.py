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

    # Set options for yt-dlp with better error handling for deployment
    ydl_opts = {
        'writeautomaticsub': True,        # Download auto-generated subtitles if manual not available
        'writesubtitles': True,           # Download subtitles if available
        'subtitleslangs': [language],     # Language preference
        'skip_download': True,            # Do not download video
        'outtmpl': os.path.join(output_dir, f'{video_id}-%(title)s.%(ext)s'),  # Output path and filename pattern
        'subtitlesformat': 'srt',         # Subtitle format
        # Add options to handle authentication issues on deployment
        'no_check_certificate': True,     # Skip certificate verification
        'ignoreerrors': True,             # Continue on download errors
        'quiet': False,                   # Show progress
        'no_warnings': False,             # Show warnings for debugging
        # Add user agent to avoid some blocking
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if not info:
                raise Exception("Failed to extract video info")
            
            title = info.get('title', 'video')
            print(f"Downloading subtitles for: {title}")
            
            # Check if subtitles are available
            subtitles = info.get('subtitles', {})
            auto_subtitles = info.get('automatic_captions', {})
            
            if not subtitles and not auto_subtitles:
                print(f"Warning: No subtitles found for video: {title}")
                # Try to download anyway, might get auto-generated ones
                
            ydl.download([video_url])
            print(f"Subtitles saved in: {output_dir}")
            
    except Exception as e:
        print(f"Error during subtitle download: {e}")
        # Try with more permissive options
        try:
            print("Retrying with more permissive options...")
            ydl_opts['ignoreerrors'] = True
            ydl_opts['quiet'] = True
            ydl_opts['no_warnings'] = True
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                print(f"Retry successful - subtitles saved in: {output_dir}")
        except Exception as retry_error:
            print(f"Retry also failed: {retry_error}")
            raise e

# Example usage
# video_url = "https://www.youtube.com/watch?v=va4cAYvTvzI"
# download_youtube_subtitles(video_url, language='en')
