"""
YouTube Data API fallback for when yt-dlp authentication fails
This provides an alternative method to extract video information and transcripts
"""

import os
import requests
import json
from typing import Optional, Dict, Any
import re

class YouTubeAPIFallback:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube API fallback
        Args:
            api_key: YouTube Data API key (optional, will try to get from env)
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
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
    
    def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video information using YouTube Data API"""
        if not self.api_key:
            print("Warning: No YouTube API key provided")
            return None
            
        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('items'):
                return data['items'][0]
            return None
            
        except Exception as e:
            print(f"Error getting video info from API: {e}")
            return None
    
    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Try to get transcript using various methods
        This is a simplified approach - in production you might want to use
        youtube_transcript_api or similar libraries
        """
        # Method 1: Try to get from YouTube's transcript endpoint
        try:
            transcript_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en"
            response = requests.get(transcript_url, timeout=10)
            
            if response.status_code == 200 and response.text.strip():
                # Parse XML transcript (simplified)
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(response.text)
                    text_parts = []
                    for text in root.findall('.//text'):
                        text_parts.append(text.text or '')
                    return ' '.join(text_parts)
                except:
                    pass
        except:
            pass
        
        # Method 2: Try to get auto-generated captions
        try:
            auto_url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en&fmt=srv3"
            response = requests.get(auto_url, timeout=10)
            
            if response.status_code == 200 and response.text.strip():
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(response.text)
                    text_parts = []
                    for text in root.findall('.//text'):
                        text_parts.append(text.text or '')
                    return ' '.join(text_parts)
                except:
                    pass
        except:
            pass
        
        return None
    
    def create_srt_content(self, transcript: str, video_title: str) -> str:
        """Create SRT format content from transcript"""
        if not transcript:
            return ""
        
        # Split transcript into sentences (simplified)
        sentences = transcript.split('. ')
        
        srt_content = []
        for i, sentence in enumerate(sentences, 1):
            if sentence.strip():
                # Create simple timing (1 second per sentence)
                start_time = i - 1
                end_time = i
                
                srt_content.append(f"{i}")
                srt_content.append(f"{start_time:02d}:00:00,000 --> {end_time:02d}:00:00,000")
                srt_content.append(sentence.strip())
                srt_content.append("")
        
        return "\n".join(srt_content)
    
    def download_subtitles_fallback(self, video_url: str, output_dir: str = 'subtitles') -> Optional[str]:
        """
        Fallback method to download subtitles using YouTube Data API
        Returns the path to the created SRT file or None if failed
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            print("Could not extract video ID from URL")
            return None
        
        # Get video info
        video_info = self.get_video_info(video_id)
        if not video_info:
            print("Could not get video information")
            return None
        
        video_title = video_info['snippet']['title']
        print(f"Processing video: {video_title}")
        
        # Try to get transcript
        transcript = self.get_transcript(video_id)
        if not transcript:
            print("Could not get transcript from YouTube")
            return None
        
        # Create SRT content
        srt_content = self.create_srt_content(transcript, video_title)
        if not srt_content:
            print("Could not create SRT content")
            return None
        
        # Save to file
        os.makedirs(output_dir, exist_ok=True)
        srt_filename = f"{video_id}-{video_title[:50]}.srt"
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
    fallback = YouTubeAPIFallback()
    result = fallback.download_subtitles_fallback("https://www.youtube.com/watch?v=va4cAYvTvzI")
    print(f"Result: {result}") 