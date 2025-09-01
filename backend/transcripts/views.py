from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from django.shortcuts import get_object_or_404

from .models import Transcript
from .serializers import TranscriptSerializer, TranscriptCreateSerializer
from .services import TranscriptService


class TranscriptListView(ListCreateAPIView):
    """View for listing and creating transcripts."""
    
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TranscriptCreateSerializer
        return TranscriptSerializer


class TranscriptDetailView(RetrieveDestroyAPIView):
    """View for retrieving and deleting individual transcripts."""
    
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer


@api_view(['POST'])
def transcribe_audio(request):
    """
    Transcribe uploaded audio file and correct grammar.
    
    Expected format:
    - Multipart form data with 'audio' field containing WAV file
    """
    try:
        # Check if audio file is provided
        if 'audio' not in request.FILES:
            return Response(
                {'error': 'No audio file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audio_file = request.FILES['audio']
        print(f"DEBUG: Received audio file - Name: {audio_file.name}, Size: {audio_file.size} bytes") # Added logging

        # Temporarily save the received audio file to media/audio for debugging
        from django.core.files.storage import default_storage
        from django.conf import settings
        import os

        media_audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_file.name)
        with default_storage.open(media_audio_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        print(f"DEBUG: Saved received audio file to: {media_audio_path}") # Added logging

        # Validate file type
        if not audio_file.name.lower().endswith('.wav'):
            return Response(
                {'error': 'Only WAV files are supported'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process audio using service
        transcript_service = TranscriptService()
        converted_text, corrected_text = transcript_service.process_audio(audio_file)
        
        # Create transcript record
        transcript = Transcript.objects.create(
            original_audio=audio_file,
            converted_text=converted_text,
            corrected_text=corrected_text
        )
        
        # Return response
        serializer = TranscriptSerializer(transcript)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Processing failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint to verify services are running."""
    try:
        # Test LanguageTool configuration
        transcript_service = TranscriptService()
        # We don't test Whisper directly here as it's temporarily disabled
        
        return Response({
            'status': 'healthy',
            'services': {
                'languagetool': 'configured',
                'whisper': 'configured'
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

