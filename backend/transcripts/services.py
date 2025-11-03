import os
import tempfile
import requests
import whisper
from django.conf import settings
from django.core.files import File
from .audio_preprocessing import AudioPreprocessingService, TextPostprocessingService


class SpeechToTextService:
    """Service for converting speech to text using OpenAI Whisper."""
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            self.model = whisper.load_model(settings.WHISPER_MODEL)
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            raise
    
    def transcribe_audio(self, cleaned_audio_path):
        """
        Transcribe cleaned audio file to text.
        
        Args:
            cleaned_audio_path: Path to preprocessed audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            print(f"DEBUG: Transcribing audio from: {cleaned_audio_path}")
            print(f"DEBUG: Audio file size: {os.path.getsize(cleaned_audio_path)} bytes")

            # Transcribe using Whisper with optimized parameters
            result = self.model.transcribe(
                cleaned_audio_path, 
                language='en', 
                temperature=0, 
                no_speech_threshold=0.6, 
                compression_ratio_threshold=2.4, 
                logprob_threshold=-1.0,
                word_timestamps=False  # Disable for faster processing
            )
            
            print(f"DEBUG: Raw Whisper transcription result: {result}")
            transcribed_text = result["text"].strip()
            
            print(f"DEBUG: Whisper transcribed text: '{transcribed_text}'")
            
            return transcribed_text
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            raise


class GrammarCorrectionService:
    """Service for grammar correction using LanguageTool."""
    
    def __init__(self):
        self.languagetool_url = settings.LANGUAGETOOL_URL
    
    def correct_grammar(self, text):
        """
        Correct grammar in the given text using LanguageTool.
        
        Args:
            text (str): Text to correct
            
        Returns:
            str: Grammar-corrected text
        """
        try:
            # Prepare request to LanguageTool
            payload = {
                'text': text,
                'language': 'en-US'
            }
            
            # Make request to LanguageTool server
            response = requests.post(self.languagetool_url, data=payload, timeout=10)
            response.raise_for_status()
            
            # Process corrections
            result = response.json()
            corrected_text = self._apply_corrections(text, result.get('matches', []))
            
            return corrected_text
            
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to LanguageTool: {e}")
            # Return original text if LanguageTool is not available
            return text
        except Exception as e:
            print(f"Error correcting grammar: {e}")
            return text
    
    def _apply_corrections(self, text, matches):
        """
        Apply grammar corrections to the text.
        
        Args:
            text (str): Original text
            matches (list): List of grammar matches from LanguageTool
            
        Returns:
            str: Corrected text
        """
        if not matches:
            return text
        
        # Sort matches by offset in reverse order to avoid index issues
        matches.sort(key=lambda x: x['offset'], reverse=True)
        
        corrected_text = text
        
        for match in matches:
            if 'replacements' in match and match['replacements']:
                # Get the best replacement
                replacement = match['replacements'][0]['value']
                offset = match['offset']
                length = match['length']
                
                # Apply the correction
                corrected_text = (
                    corrected_text[:offset] + 
                    replacement + 
                    corrected_text[offset + length:]
                )
        
        return corrected_text


class TranscriptService:
    """Main service for handling transcript operations with simplified but robust processing."""
    
    def __init__(self):
        self.speech_service = SpeechToTextService()
        self.grammar_service = GrammarCorrectionService()
        # Initialize preprocessing services with error handling
        try:
            self.audio_preprocessor = AudioPreprocessingService()
            self.text_postprocessor = TextPostprocessingService()
        except Exception as e:
            print(f"Warning: Could not initialize preprocessing services: {e}")
            self.audio_preprocessor = None
            self.text_postprocessor = None
    
    def process_audio(self, audio_file):
        """
        Process audio file with simplified pipeline: direct transcription and grammar correction.
        Falls back gracefully if advanced preprocessing fails.
        
        Args:
            audio_file: Django UploadedFile object
            
        Returns:
            tuple: (converted_text, corrected_text)
        """
        temp_file_path = None
        
        try:
            print("DEBUG: Starting simplified audio processing pipeline...")
            
            # Step 1: Save uploaded file temporarily for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            print(f"DEBUG: Audio file saved to: {temp_file_path}")
            print(f"DEBUG: Audio file size: {os.path.getsize(temp_file_path)} bytes")
            
            # Step 2: Direct transcription with Whisper
            print("DEBUG: Starting Whisper transcription...")
            try:
                raw_transcribed_text = self.speech_service.transcribe_audio(temp_file_path)
                print(f"DEBUG: Raw Whisper result: '{raw_transcribed_text}'")
            except Exception as whisper_error:
                print(f"ERROR: Whisper transcription failed: {whisper_error}")
                raise
            
            # Step 3: Basic text cleaning (if postprocessor available)
            if self.text_postprocessor and hasattr(self.text_postprocessor, 'clean_transcription'):
                try:
                    converted_text = self.text_postprocessor.clean_transcription(raw_transcribed_text)
                    print(f"DEBUG: Cleaned text: '{converted_text}'")
                except Exception as clean_error:
                    print(f"Warning: Text cleaning failed, using raw text: {clean_error}")
                    converted_text = raw_transcribed_text.strip()
            else:
                # Basic cleaning without postprocessor
                converted_text = raw_transcribed_text.strip()
                print(f"DEBUG: Basic cleaning applied: '{converted_text}'")
            
            # Step 4: Grammar correction (with fallback)
            try:
                print("DEBUG: Starting grammar correction...")
                corrected_text = self.grammar_service.correct_grammar(converted_text)
                print(f"DEBUG: Grammar corrected: '{corrected_text}'")
            except Exception as grammar_error:
                print(f"Warning: Grammar correction failed, using cleaned text: {grammar_error}")
                corrected_text = converted_text
            
            print(f"DEBUG: Final results - Converted: '{converted_text}' -> Corrected: '{corrected_text}'")
            
            return converted_text, corrected_text
            
        except Exception as e:
            print(f"ERROR: Audio processing failed: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to process audio: {str(e)}")
        
        finally:
            # Always clean up temporary files
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    print(f"DEBUG: Cleaned up temporary file: {temp_file_path}")
                except Exception as cleanup_error:
                    print(f"Warning: Failed to cleanup temporary file {temp_file_path}: {cleanup_error}")

