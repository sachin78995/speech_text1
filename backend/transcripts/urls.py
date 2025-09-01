from django.urls import path
from . import views

urlpatterns = [
    path('transcripts/', views.TranscriptListView.as_view(), name='transcript-list'),
    path('transcripts/<int:pk>/', views.TranscriptDetailView.as_view(), name='transcript-detail'),
    path('transcribe/', views.transcribe_audio, name='transcribe-audio'),
    path('health/', views.health_check, name='health-check'),
]

