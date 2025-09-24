from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class Consultation(models.Model):
    """
    Model to store health consultation sessions
    """
    CONSULTATION_TYPES = [
        ('text', 'Text Consultation'),
        ('voice', 'Voice Consultation'),
    ]
    
    SEVERITY_LEVELS = [
        (1, 'Very Low'),
        (2, 'Low'), 
        (3, 'Mild'),
        (4, 'Moderate Low'),
        (5, 'Moderate'),
        (6, 'Moderate High'),
        (7, 'High'),
        (8, 'Severe'),
        (9, 'Very Severe'),
        (10, 'Critical Emergency'),
    ]
    
    LANGUAGES = [
        ('en', 'English'),
        ('lg', 'Luganda'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations')
    consultation_type = models.CharField(max_length=10, choices=CONSULTATION_TYPES, default='text')
    language = models.CharField(max_length=2, choices=LANGUAGES, default='en')
    
    # Patient input
    symptoms_text = models.TextField()
    audio_file = models.FileField(upload_to='consultations/audio/', blank=True, null=True)
    
    # AI Analysis
    ai_response = models.TextField()
    severity_score = models.IntegerField(choices=SEVERITY_LEVELS, null=True, blank=True)
    emergency_detected = models.BooleanField(default=False)
    recommended_actions = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
    
    def __str__(self):
        return f"Consultation {self.id} - {self.patient.username} ({self.created_at.date()})"

class ConsultationMessage(models.Model):
    """
    Model to store individual messages in a consultation chat
    """
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('assistant', 'AI Assistant'),
        ('system', 'System Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    audio_file = models.FileField(upload_to='consultations/messages/audio/', blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class EmergencyAlert(models.Model):
    """
    Model to track emergency situations detected by AI
    """
    ALERT_LEVELS = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='emergency_alerts')
    alert_level = models.CharField(max_length=10, choices=ALERT_LEVELS)
    symptoms_detected = models.TextField()
    ai_recommendation = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(default=timezone.now)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Emergency Alert {self.id} - {self.alert_level} ({self.status})"
