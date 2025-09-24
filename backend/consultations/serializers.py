from rest_framework import serializers
from .models import Consultation, ConsultationMessage, EmergencyAlert
from django.contrib.auth import get_user_model

User = get_user_model()

class ConsultationSerializer(serializers.ModelSerializer):
    """
    Serializer for Consultation model
    """
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    severity_level_display = serializers.CharField(source='get_severity_score_display', read_only=True)
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'patient', 'patient_name', 'consultation_type', 'language',
            'symptoms_text', 'audio_file', 'ai_response', 'severity_score',
            'severity_level_display', 'emergency_detected', 'recommended_actions',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'patient_name', 'severity_level_display']

    def create(self, validated_data):
        # Set the patient to the current user
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)

class ConsultationMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ConsultationMessage model
    """
    class Meta:
        model = ConsultationMessage
        fields = [
            'id', 'consultation', 'message_type', 'content', 
            'audio_file', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

class EmergencyAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for EmergencyAlert model
    """
    consultation_id = serializers.CharField(source='consultation.id', read_only=True)
    patient_name = serializers.CharField(source='consultation.patient.get_full_name', read_only=True)
    
    class Meta:
        model = EmergencyAlert
        fields = [
            'id', 'consultation', 'consultation_id', 'patient_name',
            'alert_level', 'symptoms_detected', 'ai_recommendation',
            'status', 'created_at', 'acknowledged_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'created_at', 'consultation_id', 'patient_name']

class ConsultationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new consultation
    """
    symptoms_text = serializers.CharField(max_length=2000)
    consultation_type = serializers.ChoiceField(
        choices=['text', 'voice'], 
        default='text'
    )
    language = serializers.ChoiceField(
        choices=['en', 'lg'], 
        default='en'
    )
    audio_file = serializers.FileField(required=False, allow_null=True)

    def validate_symptoms_text(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please provide more detailed symptoms (at least 10 characters)."
            )
        return value

    def validate(self, attrs):
        consultation_type = attrs.get('consultation_type', 'text')
        audio_file = attrs.get('audio_file')
        symptoms_text = attrs.get('symptoms_text', '')

        if consultation_type == 'voice' and not audio_file:
            raise serializers.ValidationError(
                "Audio file is required for voice consultations."
            )
        
        if consultation_type == 'text' and not symptoms_text.strip():
            raise serializers.ValidationError(
                "Symptoms text is required for text consultations."
            )

        return attrs

class ConsultationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing consultations
    """
    severity_level_display = serializers.CharField(source='get_severity_score_display', read_only=True)
    message_count = serializers.SerializerMethodField()
    has_emergency_alert = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'consultation_type', 'language', 'severity_score',
            'severity_level_display', 'emergency_detected', 'message_count',
            'has_emergency_alert', 'created_at', 'is_active'
        ]

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_has_emergency_alert(self, obj):
        return obj.emergency_alerts.filter(status='pending').exists()
