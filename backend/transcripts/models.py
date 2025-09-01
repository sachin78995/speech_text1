from django.db import models
from django.utils import timezone


class Transcript(models.Model):
    """Model for storing speech-to-text transcripts with grammar correction."""
    
    original_audio = models.FileField(upload_to='audio/', null=True, blank=True)
    converted_text = models.TextField(help_text="Original transcribed text")
    corrected_text = models.TextField(help_text="Grammar-corrected text")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transcript'
        verbose_name_plural = 'Transcripts'
    
    def __str__(self):
        return f"Transcript {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def audio_filename(self):
        """Get the filename of the uploaded audio file."""
        if self.original_audio:
            return self.original_audio.name.split('/')[-1]
        return None

