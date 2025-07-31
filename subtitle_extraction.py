import yt_dlp
import os
import tempfile
import json

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

    # Detect if we're in a deployment environment (like Render)
    is_deployment = os.getenv('RENDER') or os.getenv('HEROKU') or os.getenv('RAILWAY') or '/opt/render' in os.getcwd()
    
    if is_deployment:
        print("Detected deployment environment, using optimized approach...")
    
    # Set options for yt-dlp with better bot detection avoidance
    ydl_opts = {
        'writeautomaticsub': True,        # Download auto-generated subtitles if manual not available
        'writesubtitles': True,           # Download subtitles if available
        'subtitleslangs': [language],     # Language preference
        'skip_download': True,            # Do not download video
        'outtmpl': os.path.join(output_dir, f'{video_id}-%(title)s.%(ext)s'),  # Output path and filename pattern
        'subtitlesformat': 'srt',         # Subtitle format
        # Bot detection avoidance
        'no_check_certificate': True,     # Skip certificate verification
        'ignoreerrors': True,             # Continue on download errors
        'quiet': False,                   # Show progress
        'no_warnings': False,             # Show warnings for debugging
        # Enhanced headers to avoid bot detection
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        # Additional options to avoid bot detection
        'extractor_retries': 3,
        'fragment_retries': 3,
        'retries': 3,
        'sleep_interval': 1,
        'max_sleep_interval': 5,
    }

    # Define approaches based on environment
    if is_deployment:
        # For deployment, use more aggressive bot avoidance
        approaches = [
            # Approach 1: Mobile user agent (often works better on servers)
            {'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
            }},
            # Approach 2: Desktop user agent with enhanced headers
            {'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }},
            # Approach 3: Simple user agent
            {'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }},
        ]
    else:
        # For local development, try cookie-based approaches
        approaches = [
            # Approach 1: Try with browser cookies
            {'cookiesfrombrowser': ('chrome',)},
            # Approach 2: Try with Firefox cookies
            {'cookiesfrombrowser': ('firefox',)},
            # Approach 3: Try without cookies but with enhanced headers
            {'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"macOS"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            }},
            # Approach 4: Try with mobile user agent
            {'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
            }},
        ]

    for i, approach in enumerate(approaches):
        try:
            print(f"Trying yt-dlp approach {i+1}/{len(approaches)}...")
            
            # Update options with current approach
            current_opts = ydl_opts.copy()
            current_opts.update(approach)
            
            with yt_dlp.YoutubeDL(current_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    raise Exception("Failed to extract video info")
                
                title = info.get('title', 'video')
                print(f"Successfully extracted info for: {title}")
                
                # Check if subtitles are available
                subtitles = info.get('subtitles', {})
                auto_subtitles = info.get('automatic_captions', {})
                
                if not subtitles and not auto_subtitles:
                    print(f"Warning: No subtitles found for video: {title}")
                    # Continue anyway, might get auto-generated ones
                    
                ydl.download([video_url])
                print(f"Subtitles downloaded successfully using yt-dlp approach {i+1}")
                return  # Success, exit the function
                
        except Exception as e:
            error_msg = str(e).lower()
            print(f"yt-dlp approach {i+1} failed: {e}")
            
            # If it's a sign-in error, try the next approach
            if 'sign in' in error_msg or 'bot' in error_msg or 'authentication' in error_msg:
                continue
            else:
                # For other errors, try the next approach but log the error
                continue
    
    # If all approaches failed, try a very basic approach
    print("All approaches failed, trying basic approach...")
    try:
        basic_opts = {
            'writeautomaticsub': True,
            'writesubtitles': True,
            'subtitleslangs': [language],
            'skip_download': True,
            'outtmpl': os.path.join(output_dir, f'{video_id}.%(ext)s'),
            'subtitlesformat': 'srt',
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'extractor_retries': 5,
            'fragment_retries': 5,
            'retries': 5,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            }
        }
        
        with yt_dlp.YoutubeDL(basic_opts) as ydl:
            ydl.download([video_url])
            print("Basic approach succeeded")
            
    except Exception as final_error:
        print(f"All methods failed. Final error: {final_error}")
        raise Exception(f"Failed to download subtitles after trying all approaches: {final_error}")

# Example usage
# video_url = "https://www.youtube.com/watch?v=va4cAYvTvzI"
# download_youtube_subtitles(video_url, language='en')
