from rest_framework import serializers
from .models import Transcript


class TranscriptSerializer(serializers.ModelSerializer):
    """Serializer for Transcript model."""
    
    audio_filename = serializers.ReadOnlyField()
    
    class Meta:
        model = Transcript
        fields = [
            'id', 
            'original_audio', 
            'converted_text', 
            'corrected_text', 
            'created_at', 
            'updated_at',
            'audio_filename'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'audio_filename']


class TranscriptCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new transcripts."""
    
    class Meta:
        model = Transcript
        fields = ['original_audio']

