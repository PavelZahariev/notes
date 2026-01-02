# -*- coding: utf-8 -*-
"""
Test script for the transcribe endpoint
Creates a sample audio file and sends it to the API
"""
import httpx
import sys
import io
import os

# Ensure UTF-8 encoding for print statements
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')




def test_transcribe_endpoint(audio_file="test_audio.wav"):
    """Test the /api/voice/transcribe endpoint"""
    import os
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"❌ Error: Audio file '{audio_file}' not found")
        return None
    
    url = "http://localhost:8000/api/voice/transcribe"
    
    print(f"\n📤 Sending request to {url}")
    print(f"   Audio File: {audio_file}")
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': (audio_file, f, 'audio/wav')}
            response = httpx.post(url, files=files, timeout=30.0)
        
        print(f"✓ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📝 Transcription Result:")
            print(f"   Text: {result.get('text', 'N/A')}")
            print(f"   Language: {result.get('language', 'N/A')}")
        else:
            print(f"\n❌ Error: {response.text}")
            
        return response
        
    except httpx.ConnectError:
        print("❌ Could not connect to server. Make sure the backend is running at http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🎤 Voice Transcription Test")
    print("=" * 50)
    
    # Use existing audio file
    audio_file = "note1.wav"

    # print the full path of the audio file

    print(f"Using audio file: {os.path.abspath(audio_file)}")
    
    # Test the endpoint
    test_transcribe_endpoint(audio_file)
    
    
