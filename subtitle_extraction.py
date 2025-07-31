import yt_dlp
import os
import tempfile
import json
import time
import random

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
        print("Detected deployment environment, using rate-limited approach...")
    
    # Set options for yt-dlp with better rate limiting and bot detection avoidance
    ydl_opts = {
        'writeautomaticsub': True,        # Download auto-generated subtitles if manual not available
        'writesubtitles': True,           # Download subtitles if available
        'subtitleslangs': [language],     # Language preference
        'skip_download': True,            # Do not download video
        'outtmpl': os.path.join(output_dir, f'{video_id}-%(title)s.%(ext)s'),  # Output path and filename pattern
        'subtitlesformat': 'srt',         # Subtitle format
        # Rate limiting and bot detection avoidance
        'no_check_certificate': True,     # Skip certificate verification
        'ignoreerrors': True,             # Continue on download errors
        'quiet': False,                   # Show progress
        'no_warnings': False,             # Show warnings for debugging
        # Rate limiting
        'sleep_interval': 2,              # Sleep between requests
        'max_sleep_interval': 10,         # Maximum sleep interval
        'retries': 5,                     # Number of retries
        'fragment_retries': 5,            # Fragment retries
        'extractor_retries': 5,           # Extractor retries
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
    }

    # Define approaches with better rate limiting
    if is_deployment:
        # For deployment, use more conservative approaches with delays
        approaches = [
            # Approach 1: Conservative approach with delays
            {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                },
                'sleep_interval': 5,
                'max_sleep_interval': 15,
            },
            # Approach 2: Mobile user agent with delays
            {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                },
                'sleep_interval': 3,
                'max_sleep_interval': 10,
            },
            # Approach 3: Desktop user agent with minimal headers
            {
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                },
                'sleep_interval': 2,
                'max_sleep_interval': 8,
            },
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
            
            # Add delay between attempts to avoid rate limiting
            if i > 0:
                delay = random.uniform(2, 5)
                print(f"Waiting {delay:.1f} seconds before next attempt...")
                time.sleep(delay)
            
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
            
            # If it's a rate limiting error, wait longer
            if '429' in error_msg or 'too many requests' in error_msg:
                print("Rate limited detected, waiting longer...")
                time.sleep(random.uniform(10, 20))
                continue
            
            # If it's a sign-in error, try the next approach
            if 'sign in' in error_msg or 'bot' in error_msg or 'authentication' in error_msg:
                continue
            else:
                # For other errors, try the next approach but log the error
                continue
    
    # If all yt-dlp approaches failed, try alternative method
    print("All yt-dlp approaches failed, trying alternative transcript extraction...")
    try:
        from alternative_transcript import AlternativeTranscriptExtractor
        
        extractor = AlternativeTranscriptExtractor()
        srt_path = extractor.extract_subtitles_alternative(video_url, output_dir, language)
        
        if srt_path:
            print(f"Alternative method succeeded: {srt_path}")
            return
        else:
            print("Alternative method also failed")
            
    except ImportError:
        print("Alternative transcript extraction not available (alternative_transcript.py not found)")
    except Exception as fallback_error:
        print(f"Alternative transcript extraction error: {fallback_error}")
    
    # If all approaches failed, try a very basic approach with longer delays
    print("All approaches failed, trying basic approach with longer delays...")
    try:
        # Wait before final attempt
        time.sleep(random.uniform(5, 10))
        
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
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retries': 3,
            'sleep_interval': 5,
            'max_sleep_interval': 15,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            }
        }
        
        with yt_dlp.YoutubeDL(basic_opts) as ydl:
            ydl.download([video_url])
            print("Basic approach succeeded")
            
    except Exception as final_error:
        print(f"All methods failed. Final error: {final_error}")
        
        # Provide helpful error message
        if '429' in str(final_error) or 'too many requests' in str(final_error).lower():
            raise Exception("YouTube is rate limiting requests. Please try again later or use a different video.")
        elif 'sign in' in str(final_error).lower() or 'bot' in str(final_error).lower():
            raise Exception("YouTube is requiring authentication for this video. Try a different video or try again later.")
        else:
            raise Exception(f"Failed to download subtitles after trying all approaches: {final_error}")

# Example usage
# video_url = "https://www.youtube.com/watch?v=va4cAYvTvzI"
# download_youtube_subtitles(video_url, language='en')
