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
    """Main service for handling transcript operations with enhanced preprocessing."""
    
    def __init__(self):
        self.speech_service = SpeechToTextService()
        self.grammar_service = GrammarCorrectionService()
        self.audio_preprocessor = AudioPreprocessingService()
        self.text_postprocessor = TextPostprocessingService()
    
    def process_audio(self, audio_file):
        """
        Process audio file with enhanced pipeline: noise reduction, transcription, text cleaning, and grammar correction.
        
        Args:
            audio_file: Django UploadedFile object
            
        Returns:
            tuple: (converted_text, corrected_text)
        """
        cleaned_audio_path = None
        
        try:
            # Step 1: Validate audio file
            if not self.audio_preprocessor.validate_audio_file(audio_file):
                raise ValueError("Invalid audio file format or size")
            
            # Step 2: Apply noise reduction and preprocessing
            print("DEBUG: Starting audio preprocessing...")
            cleaned_audio_path = self.audio_preprocessor.reduce_noise(audio_file)
            
            # Step 3: Transcribe cleaned audio to text
            print("DEBUG: Starting transcription...")
            raw_transcribed_text = self.speech_service.transcribe_audio(cleaned_audio_path)
            
            # Step 4: Clean transcribed text (remove duplicates, etc.)
            print("DEBUG: Starting text postprocessing...")
            converted_text = self.text_postprocessor.clean_transcription(raw_transcribed_text)
            
            # Step 5: Apply grammar correction
            print("DEBUG: Starting grammar correction...")
            corrected_text = self.grammar_service.correct_grammar(converted_text)
            
            print(f"DEBUG: Final pipeline results - Original: '{raw_transcribed_text}' -> Cleaned: '{converted_text}' -> Corrected: '{corrected_text}'")
            
            return converted_text, corrected_text
            
        except Exception as e:
            print(f"Error in enhanced audio processing pipeline: {e}")
            # Fallback to basic processing if enhanced pipeline fails
            try:
                print("DEBUG: Falling back to basic processing...")
                # Save audio file temporarily for basic processing
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                    for chunk in audio_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name
                
                # Basic transcription
                raw_text = self.speech_service.transcribe_audio(temp_file_path)
                cleaned_text = self.text_postprocessor.clean_transcription(raw_text)
                corrected_text = self.grammar_service.correct_grammar(cleaned_text)
                
                # Cleanup
                os.unlink(temp_file_path)
                
                return cleaned_text, corrected_text
                
            except Exception as fallback_error:
                print(f"Fallback processing also failed: {fallback_error}")
                raise
        
        finally:
            # Clean up preprocessed audio file
            if cleaned_audio_path and os.path.exists(cleaned_audio_path):
                try:
                    os.unlink(cleaned_audio_path)
                    print(f"DEBUG: Cleaned up temporary file: {cleaned_audio_path}")
                except Exception as cleanup_error:
                    print(f"Warning: Failed to cleanup temporary file {cleaned_audio_path}: {cleanup_error}")

