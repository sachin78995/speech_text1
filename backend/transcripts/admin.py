from django.contrib import admin
from .models import Transcript


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ['id', 'converted_text', 'corrected_text', 'created_at']
    list_filter = ['created_at']
    search_fields = ['converted_text', 'corrected_text']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Audio File', {
            'fields': ('original_audio',)
        }),
        ('Text Content', {
            'fields': ('converted_text', 'corrected_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

