"""
Alternative transcript extraction method when yt-dlp is blocked
This uses a different approach to get YouTube transcripts
"""

import os
import re
import requests
import time
import random
from typing import Optional, Dict, Any

class AlternativeTranscriptExtractor:
    def __init__(self):
        """Initialize alternative transcript extractor"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
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
    
    def get_transcript_urls(self, video_id: str) -> list:
        """Get possible transcript URLs for a video"""
        urls = []
        
        # Try different transcript endpoints
        base_urls = [
            f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en",
            f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en&fmt=srv3",
            f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en&fmt=srv1",
            f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en&fmt=vtt",
        ]
        
        for url in base_urls:
            urls.append(url)
        
        return urls
    
    def download_transcript(self, url: str, timeout: int = 10) -> Optional[str]:
        """Download transcript from a URL"""
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            if response.text.strip():
                return response.text
            return None
            
        except Exception as e:
            print(f"Failed to download from {url}: {e}")
            return None
    
    def parse_xml_transcript(self, xml_content: str) -> str:
        """Parse XML transcript content into plain text"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
            
            text_parts = []
            for text_elem in root.findall('.//text'):
                text = text_elem.text or ''
                if text.strip():
                    text_parts.append(text.strip())
            
            return ' '.join(text_parts)
            
        except Exception as e:
            print(f"Failed to parse XML: {e}")
            # Fallback: try to extract text using regex
            text_matches = re.findall(r'<text[^>]*>(.*?)</text>', xml_content, re.DOTALL)
            return ' '.join(text_matches)
    
    def create_srt_content(self, transcript_text: str, video_id: str) -> str:
        """Create SRT format content from transcript text"""
        if not transcript_text:
            return ""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcript_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        srt_content = []
        for i, sentence in enumerate(sentences, 1):
            if sentence:
                # Create simple timing (2 seconds per sentence)
                start_time = (i - 1) * 2
                end_time = i * 2
                
                srt_content.append(f"{i}")
                srt_content.append(f"{start_time:02d}:00:00,000 --> {end_time:02d}:00:00,000")
                srt_content.append(sentence)
                srt_content.append("")
        
        return "\n".join(srt_content)
    
    def extract_subtitles_alternative(self, video_url: str, output_dir: str = 'subtitles', language: str = 'en') -> Optional[str]:
        """
        Alternative method to extract subtitles when yt-dlp is blocked
        Returns the path to the created SRT file or None if failed
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            print("Could not extract video ID from URL")
            return None
        
        print(f"Trying alternative method for video ID: {video_id}")
        
        # Get possible transcript URLs
        transcript_urls = self.get_transcript_urls(video_id)
        
        for i, url in enumerate(transcript_urls):
            print(f"Trying transcript URL {i+1}/{len(transcript_urls)}...")
            
            xml_content = self.download_transcript(url)
            if xml_content:
                print(f"Successfully downloaded transcript from URL {i+1}")
                
                # Parse XML content
                transcript_text = self.parse_xml_transcript(xml_content)
                if transcript_text:
                    print(f"Successfully parsed transcript ({len(transcript_text)} characters)")
                    
                    # Create SRT content
                    srt_content = self.create_srt_content(transcript_text, video_id)
                    if srt_content:
                        # Save to file
                        os.makedirs(output_dir, exist_ok=True)
                        srt_filename = f"{video_id}_alternative.srt"
                        srt_path = os.path.join(output_dir, srt_filename)
                        
                        try:
                            with open(srt_path, 'w', encoding='utf-8') as f:
                                f.write(srt_content)
                            print(f"Alternative SRT file created: {srt_path}")
                            return srt_path
                        except Exception as e:
                            print(f"Error saving SRT file: {e}")
                            return None
                    else:
                        print("Failed to create SRT content")
                else:
                    print("Failed to parse transcript text")
            else:
                print(f"Failed to download from URL {i+1}")
        
        print("All alternative transcript URLs failed")
        return None

# Usage example
if __name__ == "__main__":
    extractor = AlternativeTranscriptExtractor()
    result = extractor.extract_subtitles_alternative("https://www.youtube.com/watch?v=va4cAYvTvzI")
    print(f"Result: {result}") 