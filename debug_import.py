#!/usr/bin/env python3
"""
Debug script to test YouTube Transcript API import and usage
"""

import sys

print("Python version:", sys.version)
print("Python path:", sys.path[:3])  # First 3 entries

try:
    print("\nTrying to import youtube_transcript_api...")
    import youtube_transcript_api
    print("✅ youtube_transcript_api imported successfully")
    print("Package version:", youtube_transcript_api.__version__)
    
    print("\nTrying to import YouTubeTranscriptApi...")
    from youtube_transcript_api import YouTubeTranscriptApi
    print("✅ YouTubeTranscriptApi imported successfully")
    
    print("\nTrying to import SRTFormatter...")
    from youtube_transcript_api.formatters import SRTFormatter
    print("✅ SRTFormatter imported successfully")
    
    print("\nTesting basic functionality...")
    
    # Test with a simple video
    video_id = "dQw4w9WgXcQ"  # Rick Roll
    
    print(f"Testing with video ID: {video_id}")
    
    # Try to get transcript
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        print(f"✅ Successfully got transcript with {len(transcript)} segments")
        
        # Test SRT formatting
        formatter = SRTFormatter()
        srt_content = formatter.format_transcript(transcript)
        print(f"✅ Successfully formatted as SRT ({len(srt_content)} characters)")
        
    except Exception as e:
        print(f"❌ Error getting transcript: {e}")
        print(f"Error type: {type(e)}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Error type: {type(e)}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"Error type: {type(e)}")

print("\nDebug complete!") 