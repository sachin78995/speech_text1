import os
import tempfile
import numpy as np
from django.conf import settings

# Optional imports with fallback
try:
    import noisereduce as nr
    NOISE_REDUCTION_AVAILABLE = True
except ImportError:
    print("WARNING: noisereduce not available. Noise reduction will be skipped.")
    NOISE_REDUCTION_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    print("WARNING: soundfile not available. Advanced audio processing will be limited.")
    SOUNDFILE_AVAILABLE = False


class AudioPreprocessingService:
    """Service for audio preprocessing including noise reduction."""
    
    def __init__(self):
        self.target_sample_rate = 16000  # Whisper's preferred sample rate
    
    def reduce_noise(self, audio_file):
        """
        Apply noise reduction to audio file.
        
        Args:
            audio_file: Django UploadedFile object
            
        Returns:
            str: Path to the cleaned audio file
        """
        # If noise reduction libraries are not available, return original file
        if not NOISE_REDUCTION_AVAILABLE or not SOUNDFILE_AVAILABLE:
            print("DEBUG: Noise reduction libraries not available, using original audio")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_fallback:
                for chunk in audio_file.chunks():
                    temp_fallback.write(chunk)
                return temp_fallback.name
        
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_input:
                for chunk in audio_file.chunks():
                    temp_input.write(chunk)
                temp_input_path = temp_input.name
            
            print(f"DEBUG: Input audio file saved to: {temp_input_path}")
            
            # Load audio using soundfile
            audio_data, sample_rate = sf.read(temp_input_path)
            print(f"DEBUG: Original audio - Sample rate: {sample_rate}, Shape: {audio_data.shape}")
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
                print("DEBUG: Converted stereo to mono")
            
            # Resample to target sample rate if needed
            if sample_rate != self.target_sample_rate:
                # Simple resampling (for production, consider using librosa.resample)
                ratio = self.target_sample_rate / sample_rate
                new_length = int(len(audio_data) * ratio)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), new_length),
                    np.arange(len(audio_data)),
                    audio_data
                )
                sample_rate = self.target_sample_rate
                print(f"DEBUG: Resampled to {self.target_sample_rate}Hz")
            
            # Apply noise reduction
            print("DEBUG: Applying noise reduction...")
            reduced_audio = nr.reduce_noise(
                y=audio_data, 
                sr=sample_rate,
                stationary=False,  # Non-stationary noise reduction
                prop_decrease=0.8  # Reduce noise by 80%
            )
            
            # Save cleaned audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='_cleaned.wav') as temp_output:
                temp_output_path = temp_output.name
            
            sf.write(temp_output_path, reduced_audio, sample_rate)
            print(f"DEBUG: Cleaned audio saved to: {temp_output_path}")
            
            # Clean up input temp file
            os.unlink(temp_input_path)
            
            return temp_output_path
            
        except Exception as e:
            print(f"Error in noise reduction: {e}")
            # If noise reduction fails, return original file path
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_fallback:
                for chunk in audio_file.chunks():
                    temp_fallback.write(chunk)
                return temp_fallback.name
    
    def validate_audio_file(self, audio_file):
        """
        Validate audio file format and properties.
        
        Args:
            audio_file: Django UploadedFile object
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check file extension
            if not audio_file.name.lower().endswith('.wav'):
                return False
            
            # Check file size (max 50MB)
            if audio_file.size > 50 * 1024 * 1024:
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating audio file: {e}")
            return False


class TextPostprocessingService:
    """Service for text postprocessing including duplicate word removal."""
    
    def remove_repeated_words(self, text: str) -> str:
        """
        Remove consecutive duplicate words from text.
        
        Args:
            text (str): Input text with potential duplicate words
            
        Returns:
            str: Text with consecutive duplicates removed
        """
        if not text or not text.strip():
            return text
        
        import re
        
        words = text.split()
        cleaned = []
        
        for i, word in enumerate(words):
            # Remove punctuation for comparison but keep original word
            current_word_clean = re.sub(r'[^\w]', '', word.lower())
            
            if i == 0:
                cleaned.append(word)
            else:
                previous_word_clean = re.sub(r'[^\w]', '', words[i-1].lower())
                # Keep the word if it's different from the previous word (ignoring punctuation)
                if current_word_clean != previous_word_clean:
                    cleaned.append(word)
        
        result = " ".join(cleaned)
        print(f"DEBUG: Duplicate removal - Original: '{text}' -> Cleaned: '{result}'")
        return result
    
    def remove_excessive_repetition(self, text: str, max_repetitions: int = 2) -> str:
        """
        Remove excessive word repetitions (more than max_repetitions).
        
        Args:
            text (str): Input text
            max_repetitions (int): Maximum allowed consecutive repetitions
            
        Returns:
            str: Text with excessive repetitions removed
        """
        if not text or not text.strip():
            return text
        
        words = text.split()
        cleaned = []
        current_word = None
        count = 0
        
        for word in words:
            if word.lower() == current_word:
                count += 1
                if count <= max_repetitions:
                    cleaned.append(word)
            else:
                current_word = word.lower()
                count = 1
                cleaned.append(word)
        
        result = " ".join(cleaned)
        print(f"DEBUG: Excessive repetition removal - Original: '{text}' -> Cleaned: '{result}'")
        return result
    
    def clean_transcription(self, text: str) -> str:
        """
        Apply all text cleaning operations.
        
        Args:
            text (str): Raw transcription text
            
        Returns:
            str: Cleaned text
        """
        # Remove consecutive duplicates
        text = self.remove_repeated_words(text)
        
        # Remove excessive repetitions
        text = self.remove_excessive_repetition(text)
        
        # Basic text cleanup
        text = text.strip()
        
        # Remove multiple spaces
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text
