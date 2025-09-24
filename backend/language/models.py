from django.db import models
from django.utils import timezone
import uuid

class Translation(models.Model):
    """
    Store translations for multilingual support
    """
    LANGUAGES = [
        ('en', 'English'),
        ('lg', 'Luganda'),
    ]
    
    CATEGORIES = [
        ('medical', 'Medical Terms'),
        ('symptoms', 'Symptoms'),
        ('ui', 'User Interface'),
        ('system', 'System Messages'),
        ('emergency', 'Emergency Messages'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=200, unique=True)  # Translation key
    category = models.CharField(max_length=15, choices=CATEGORIES, default='system')
    
    # Translations
    english_text = models.TextField()
    luganda_text = models.TextField()
    
    # Context
    context = models.TextField(blank=True, help_text="Additional context for translators")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category']),
        ]
    
    def get_translation(self, language='en'):
        if language == 'lg':
            return self.luganda_text
        return self.english_text
    
    def __str__(self):
        return f"{self.key} ({self.category})"

class AudioProcessingLog(models.Model):
    """
    Log audio processing requests for speech-to-text and text-to-speech
    """
    PROCESSING_TYPES = [
        ('stt', 'Speech to Text'),
        ('tts', 'Text to Speech'),
    ]
    
    LANGUAGES = [
        ('en', 'English'),
        ('lg', 'Luganda'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('authsystem.CustomUser', on_delete=models.CASCADE, related_name='audio_logs')
    processing_type = models.CharField(max_length=3, choices=PROCESSING_TYPES)
    language = models.CharField(max_length=2, choices=LANGUAGES)
    
    # Input/Output
    input_file = models.FileField(upload_to='audio/input/', blank=True, null=True)
    input_text = models.TextField(blank=True)
    output_file = models.FileField(upload_to='audio/output/', blank=True, null=True)
    output_text = models.TextField(blank=True)
    
    # Processing details
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    processing_duration = models.FloatField(null=True, blank=True)  # in seconds
    confidence_score = models.FloatField(null=True, blank=True)  # 0-1 for STT accuracy
    
    # Service provider
    service_provider = models.CharField(max_length=50, blank=True)  # Google, Azure, etc.
    api_response = models.JSONField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'processing_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.processing_type} - {self.language} ({self.status})"

class MedicalTermsGlossary(models.Model):
    """
    Glossary of medical terms with translations and explanations
    """
    TERM_CATEGORIES = [
        ('anatomy', 'Anatomy'),
        ('symptoms', 'Symptoms'),
        ('diseases', 'Diseases'),
        ('treatments', 'Treatments'),
        ('medications', 'Medications'),
        ('procedures', 'Procedures'),
        ('emergency', 'Emergency Terms'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=15, choices=TERM_CATEGORIES)
    
    # English version
    english_term = models.CharField(max_length=200)
    english_definition = models.TextField()
    english_pronunciation = models.CharField(max_length=300, blank=True)
    
    # Luganda version
    luganda_term = models.CharField(max_length=200)
    luganda_definition = models.TextField()
    luganda_pronunciation = models.CharField(max_length=300, blank=True)
    
    # Alternative terms
    english_synonyms = models.TextField(blank=True, help_text="Comma-separated synonyms")
    luganda_synonyms = models.TextField(blank=True, help_text="Comma-separated synonyms")
    
    # Usage
    usage_context = models.TextField(blank=True)
    severity_level = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], null=True, blank=True)
    
    # Audio files
    english_audio = models.FileField(upload_to='glossary/audio/en/', blank=True, null=True)
    luganda_audio = models.FileField(upload_to='glossary/audio/lg/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['english_term', 'category']
        indexes = [
            models.Index(fields=['english_term']),
            models.Index(fields=['luganda_term']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.english_term} / {self.luganda_term}"

class LanguageDetection(models.Model):
    """
    Track language detection for incoming messages
    """
    DETECTED_LANGUAGES = [
        ('en', 'English'),
        ('lg', 'Luganda'),
        ('mixed', 'Mixed Languages'),
        ('unknown', 'Unknown'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text_input = models.TextField()
    detected_language = models.CharField(max_length=10, choices=DETECTED_LANGUAGES)
    confidence_score = models.FloatField()  # 0-1
    
    # Detection method
    detection_method = models.CharField(max_length=50, default='auto')  # langdetect, google, manual
    
    # User feedback (for improving detection)
    user_confirmed_language = models.CharField(max_length=10, choices=DETECTED_LANGUAGES, blank=True)
    is_correct_detection = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        indexes = [
            models.Index(fields=['detected_language']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"Detected: {self.detected_language} (confidence: {self.confidence_score:.2f})"
