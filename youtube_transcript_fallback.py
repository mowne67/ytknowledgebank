"""
YouTube Transcript API fallback for when yt-dlp authentication fails
This uses youtube-transcript-api which is more reliable for getting transcripts
"""

import os
import re
from typing import Optional, List, Dict, Any

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import SRTFormatter
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    print("Warning: youtube-transcript-api not available. Install with: pip install youtube-transcript-api")

class YouTubeTranscriptFallback:
    def __init__(self):
        """Initialize YouTube Transcript fallback"""
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            print("Warning: youtube-transcript-api not installed")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_transcript(self, video_id: str, language: str = 'en') -> Optional[List[Dict[str, Any]]]:
        """
        Get transcript using youtube-transcript-api
        Returns list of transcript segments or None if failed
        """
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            print("youtube-transcript-api not available")
            return None
        
        try:
            # Try to get transcript in specified language
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            return transcript_list
        except Exception as e:
            print(f"Error getting transcript for language {language}: {e}")
            
            # Try to get available languages
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                available_languages = [t.language_code for t in transcript_list]
                print(f"Available languages: {available_languages}")
                
                # Try English first, then any available language
                for lang in ['en', 'en-US', 'en-GB'] + available_languages:
                    try:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                        print(f"Successfully got transcript in language: {lang}")
                        return transcript
                    except:
                        continue
                        
            except Exception as e2:
                print(f"Error listing available transcripts: {e2}")
        
        return None
    
    def format_as_srt(self, transcript: List[Dict[str, Any]]) -> str:
        """Format transcript as SRT content"""
        if not transcript:
            return ""
        
        formatter = SRTFormatter()
        return formatter.format_transcript(transcript)
    
    def download_subtitles_fallback(self, video_url: str, output_dir: str = 'subtitles', language: str = 'en') -> Optional[str]:
        """
        Fallback method to download subtitles using youtube-transcript-api
        Returns the path to the created SRT file or None if failed
        """
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            print("youtube-transcript-api not available")
            return None
        
        video_id = self.extract_video_id(video_url)
        if not video_id:
            print("Could not extract video ID from URL")
            return None
        
        print(f"Getting transcript for video ID: {video_id}")
        
        # Get transcript
        transcript = self.get_transcript(video_id, language)
        if not transcript:
            print("Could not get transcript from YouTube")
            return None
        
        # Format as SRT
        srt_content = self.format_as_srt(transcript)
        if not srt_content:
            print("Could not format transcript as SRT")
            return None
        
        # Save to file
        os.makedirs(output_dir, exist_ok=True)
        srt_filename = f"{video_id}.srt"
        srt_path = os.path.join(output_dir, srt_filename)
        
        try:
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"SRT file created: {srt_path}")
            return srt_path
        except Exception as e:
            print(f"Error saving SRT file: {e}")
            return None

# Usage example
if __name__ == "__main__":
    fallback = YouTubeTranscriptFallback()
    result = fallback.download_subtitles_fallback("https://www.youtube.com/watch?v=va4cAYvTvzI")
    print(f"Result: {result}") 