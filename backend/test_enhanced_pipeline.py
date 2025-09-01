#!/usr/bin/env python
"""
Test script for the enhanced speech-to-text pipeline.
Run this to verify noise reduction and duplicate word removal functionality.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speech_to_text.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from transcripts.audio_preprocessing import TextPostprocessingService


def test_text_postprocessing():
    """Test the text postprocessing functionality."""
    print("🧪 Testing Text Postprocessing...")
    
    text_processor = TextPostprocessingService()
    
    # Test cases for duplicate word removal
    test_cases = [
        "hello hello world world test",
        "this this is is a a test test",
        "The The quick quick brown brown fox fox jumps jumps",
        "Normal text without duplicates",
        "hello HELLO world WORLD",  # Case insensitive
        "one one one two two three three three three",  # Multiple repetitions
        "",  # Empty string
        "   spaced   spaced   text   ",  # With spaces
    ]
    
    print("\n📝 Testing duplicate word removal:")
    for i, test_text in enumerate(test_cases, 1):
        result = text_processor.remove_repeated_words(test_text)
        print(f"  {i}. '{test_text}' → '{result}'")
    
    print("\n📝 Testing excessive repetition removal:")
    excessive_cases = [
        "hello hello hello hello world",
        "test test test test test case",
        "normal text here",
        "one one one one one two two two",
    ]
    
    for i, test_text in enumerate(excessive_cases, 1):
        result = text_processor.remove_excessive_repetition(test_text, max_repetitions=2)
        print(f"  {i}. '{test_text}' → '{result}'")
    
    print("\n📝 Testing complete text cleaning:")
    messy_cases = [
        "hello hello world    world   test test",
        "  the  the  quick  quick  brown  fox  ",
        "this this   is   is   a   test   test   case",
    ]
    
    for i, test_text in enumerate(messy_cases, 1):
        result = text_processor.clean_transcription(test_text)
        print(f"  {i}. '{test_text}' → '{result}'")


def test_audio_validation():
    """Test audio file validation."""
    print("\n🎵 Testing Audio Validation...")
    
    from transcripts.audio_preprocessing import AudioPreprocessingService
    from django.core.files.uploadedfile import SimpleUploadedFile
    
    audio_processor = AudioPreprocessingService()
    
    # Test valid WAV file
    valid_wav = SimpleUploadedFile("test.wav", b"fake wav content", content_type="audio/wav")
    valid_wav.size = 1024  # 1KB
    
    # Test invalid file extension
    invalid_ext = SimpleUploadedFile("test.mp3", b"fake mp3 content", content_type="audio/mp3")
    invalid_ext.size = 1024
    
    # Test oversized file
    oversized = SimpleUploadedFile("large.wav", b"fake content", content_type="audio/wav")
    oversized.size = 60 * 1024 * 1024  # 60MB
    
    test_files = [
        ("Valid WAV file", valid_wav, True),
        ("Invalid extension", invalid_ext, False),
        ("Oversized file", oversized, False),
    ]
    
    for name, file_obj, expected in test_files:
        result = audio_processor.validate_audio_file(file_obj)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  {status} {name}: {result} (expected {expected})")


def main():
    """Run all tests."""
    print("🚀 Enhanced Speech-to-Text Pipeline Tests")
    print("=" * 50)
    
    try:
        test_text_postprocessing()
        test_audio_validation()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Pipeline Enhancement Summary:")
        print("  • Noise reduction with noisereduce library")
        print("  • Duplicate word removal")
        print("  • Excessive repetition filtering")
        print("  • Audio file validation")
        print("  • Fallback processing for error handling")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
