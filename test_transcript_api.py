#!/usr/bin/env python3
"""
Test script to verify YouTube Transcript API functionality
This helps debug the authentication issues on Render
"""

import os
import sys

def test_youtube_transcript_api():
    """Test the YouTube Transcript API directly"""
    print("Testing YouTube Transcript API...")
    
    # Test video URL (a popular video that should have transcripts)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - should have transcripts
    
    try:
        from youtube_transcript_fallback import YouTubeTranscriptFallback
        
        fallback = YouTubeTranscriptFallback()
        
        # Test video ID extraction
        video_id = fallback.extract_video_id(test_url)
        print(f"Extracted video ID: {video_id}")
        
        if not video_id:
            print("❌ Failed to extract video ID")
            return False
        
        # Test transcript retrieval
        print("Getting transcript...")
        transcript = fallback.get_transcript(video_id, 'en')
        
        if transcript:
            print(f"✅ Successfully got transcript with {len(transcript)} segments")
            
            # Test SRT formatting
            srt_content = fallback.format_as_srt(transcript)
            if srt_content:
                print(f"✅ Successfully formatted as SRT ({len(srt_content)} characters)")
                
                # Test file saving
                test_output_dir = 'test_output'
                os.makedirs(test_output_dir, exist_ok=True)
                
                srt_path = fallback.download_subtitles_fallback(test_url, test_output_dir, 'en')
                if srt_path:
                    print(f"✅ Successfully saved SRT file: {srt_path}")
                    
                    # Clean up test file
                    try:
                        os.remove(srt_path)
                        print("✅ Test file cleaned up")
                    except:
                        pass
                    
                    return True
                else:
                    print("❌ Failed to save SRT file")
                    return False
            else:
                print("❌ Failed to format as SRT")
                return False
        else:
            print("❌ Failed to get transcript")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure youtube-transcript-api is installed: pip install youtube-transcript-api")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_environment_detection():
    """Test environment detection logic"""
    print("\nTesting environment detection...")
    
    # Test deployment detection
    is_deployment = os.getenv('RENDER') or os.getenv('HEROKU') or os.getenv('RAILWAY') or '/opt/render' in os.getcwd()
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"RENDER env var: {os.getenv('RENDER')}")
    print(f"HEROKU env var: {os.getenv('HEROKU')}")
    print(f"RAILWAY env var: {os.getenv('RAILWAY')}")
    print(f"Detected as deployment: {is_deployment}")
    
    return is_deployment

def main():
    """Main test function"""
    print("=== YouTube Transcript API Test ===")
    
    # Test environment detection
    is_deployment = test_environment_detection()
    
    # Test transcript API
    success = test_youtube_transcript_api()
    
    if success:
        print("\n✅ All tests passed! YouTube Transcript API is working correctly.")
        if is_deployment:
            print("✅ Deployment environment detected - will use optimized approach")
        else:
            print("✅ Local environment detected - will try cookie-based approaches first")
    else:
        print("\n❌ Tests failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 