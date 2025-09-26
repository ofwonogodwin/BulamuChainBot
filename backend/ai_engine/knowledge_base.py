"""
Medical Knowledge Base for Ugandan Healthcare Context
Contains comprehensive medical information with multilingual support
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Django imports
from django.conf import settings

logger = logging.getLogger(__name__)

class MedicalKnowledgeBase:
    """
    Comprehensive medical knowledge base with Ugandan healthcare context
    Supports multiple languages: English, Luganda, Swahili
    """
    
    def __init__(self):
        """Initialize medical knowledge base"""
        self.knowledge_dir = os.path.join(
            settings.BASE_DIR, 'ai_engine', 'knowledge_base'
        )
        Path(self.knowledge_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize knowledge data
        self.medical_conditions = self._load_medical_conditions()
        self.symptoms_mapping = self._load_symptoms_mapping()
        self.emergency_protocols = self._load_emergency_protocols()
        self.preventive_care = self._load_preventive_care()
        self.medication_guide = self._load_medication_guide()
        self.cultural_practices = self._load_cultural_practices()
        
        # Language mappings
        self.language_translations = self._load_translations()
    
    def _load_medical_conditions(self) -> Dict[str, Any]:
        """Load comprehensive medical conditions database"""
        return {
            "infectious_diseases": [
                {
                    "condition": "Malaria",
                    "local_names": {
                        "luganda": "Omusujja gw'ensiri",
                        "swahili": "Malaria"
                    },
                    "symptoms": [
                        "Fever and chills",
                        "Headache",
                        "Muscle aches",
                        "Nausea and vomiting",
                        "Fatigue"
                    ],
                    "local_symptoms": {
                        "luganda": ["Omusujja", "Omutwe gukuba", "Okudduka", "Okusesema"],
                        "swahili": ["Homa", "Maumivu ya kichwa", "Kutapika", "Uchovu"]
                    },
                    "treatment": "Seek immediate medical attention. Use prescribed antimalarial medications like Artemether-Lumefantrine (Coartem).",
                    "prevention": "Use insecticide-treated bed nets, eliminate stagnant water, use repellents",
                    "emergency_signs": [
                        "Severe headache",
                        "Convulsions",
                        "Repeated vomiting",
                        "Difficulty breathing",
                        "Loss of consciousness"
                    ],
                    "prevalence_uganda": "High - especially in endemic areas",
                    "seasonal_patterns": "Peak during rainy seasons (March-May, September-November)"
                },
                {
                    "condition": "Typhoid Fever",
                    "local_names": {
                        "luganda": "Omusujja gw'ekyenda",
                        "swahili": "Homa ya typhoid"
                    },
                    "symptoms": [
                        "Sustained high fever",
                        "Headache",
                        "Abdominal pain",
                        "Constipation or diarrhea",
                        "Rose-colored rash"
                    ],
                    "treatment": "Antibiotic therapy (Ciprofloxacin, Azithromycin). Hospital admission may be required.",
                    "prevention": "Safe water, proper sanitation, typhoid vaccination",
                    "emergency_signs": [
                        "High fever over 39°C",
                        "Severe abdominal pain",
                        "Bleeding",
                        "Confusion"
                    ]
                },
                {
                    "condition": "Tuberculosis (TB)",
                    "local_names": {
                        "luganda": "Akafuba",
                        "swahili": "Kifua kikuu"
                    },
                    "symptoms": [
                        "Persistent cough for >3 weeks",
                        "Coughing up blood",
                        "Chest pain",
                        "Weight loss",
                        "Night sweats",
                        "Fatigue"
                    ],
                    "treatment": "6-month course of anti-TB medications. Directly Observed Treatment (DOTS).",
                    "prevention": "BCG vaccination, avoid crowded spaces, good ventilation",
                    "emergency_signs": [
                        "Coughing up large amounts of blood",
                        "Severe breathing difficulty",
                        "Chest pain"
                    ]
                }
            ],
            "maternal_child_health": [
                {
                    "condition": "Pregnancy Care",
                    "local_names": {
                        "luganda": "Okubba olubuto",
                        "swahili": "Huduma za uzazi"
                    },
                    "care_guidelines": [
                        "Attend at least 4 antenatal visits",
                        "Take folic acid and iron supplements",
                        "Get tested for HIV, syphilis, malaria",
                        "Avoid alcohol and smoking",
                        "Eat nutritious foods"
                    ],
                    "warning_signs": [
                        "Severe headache",
                        "Blurred vision",
                        "Swelling of face and hands",
                        "Severe abdominal pain",
                        "Bleeding",
                        "Reduced fetal movements"
                    ],
                    "delivery_preparation": "Identify skilled birth attendant, prepare emergency transport"
                },
                {
                    "condition": "Child Immunization",
                    "schedule": {
                        "birth": "BCG, OPV0, Hepatitis B",
                        "6_weeks": "OPV1, DPT1, Hepatitis B1, Pneumococcal1",
                        "10_weeks": "OPV2, DPT2, Hepatitis B2, Pneumococcal2",
                        "14_weeks": "OPV3, DPT3, Hepatitis B3, Pneumococcal3",
                        "9_months": "Measles, Yellow Fever",
                        "18_months": "Measles2, DPT4, OPV4"
                    }
                }
            ],
            "non_communicable_diseases": [
                {
                    "condition": "Hypertension",
                    "local_names": {
                        "luganda": "Omusaayi ogukwaata",
                        "swahili": "Shinikizo la damu"
                    },
                    "symptoms": [
                        "Often asymptomatic",
                        "Headaches",
                        "Dizziness",
                        "Chest pain",
                        "Shortness of breath"
                    ],
                    "management": [
                        "Regular blood pressure monitoring",
                        "Lifestyle modifications",
                        "Medication adherence",
                        "Reduce salt intake",
                        "Regular exercise",
                        "Weight management"
                    ],
                    "complications": [
                        "Stroke",
                        "Heart attack",
                        "Kidney disease",
                        "Eye damage"
                    ]
                },
                {
                    "condition": "Diabetes",
                    "local_names": {
                        "luganda": "Endwadde y'asukali",
                        "swahili": "Kisukari"
                    },
                    "symptoms": [
                        "Excessive thirst",
                        "Frequent urination",
                        "Extreme hunger",
                        "Unexplained weight loss",
                        "Blurred vision",
                        "Slow-healing wounds"
                    ],
                    "management": [
                        "Blood sugar monitoring",
                        "Healthy diet",
                        "Regular exercise",
                        "Medication adherence",
                        "Foot care",
                        "Regular medical checkups"
                    ]
                }
            ],
            "mental_health": [
                {
                    "condition": "Depression",
                    "local_names": {
                        "luganda": "Okunakuwala ennyo",
                        "swahili": "Unyogovu"
                    },
                    "symptoms": [
                        "Persistent sadness",
                        "Loss of interest",
                        "Fatigue",
                        "Sleep disturbances",
                        "Appetite changes",
                        "Difficulty concentrating",
                        "Feelings of worthlessness"
                    ],
                    "support": [
                        "Talk to trusted friend or counselor",
                        "Join support groups",
                        "Maintain regular routine",
                        "Exercise regularly",
                        "Seek professional help"
                    ],
                    "cultural_considerations": "Address stigma, involve family support, respect traditional healing practices"
                }
            ]
        }
    
    def _load_symptoms_mapping(self) -> Dict[str, List[str]]:
        """Load symptom to condition mapping"""
        return {
            "fever": ["Malaria", "Typhoid", "Pneumonia", "UTI", "Dengue"],
            "headache": ["Malaria", "Typhoid", "Hypertension", "Migraine", "Meningitis"],
            "cough": ["Tuberculosis", "Pneumonia", "Asthma", "Common cold", "COVID-19"],
            "abdominal_pain": ["Typhoid", "Appendicitis", "Gastritis", "UTI", "Food poisoning"],
            "diarrhea": ["Cholera", "Food poisoning", "Dysentery", "IBS", "Gastroenteritis"],
            "chest_pain": ["Heart attack", "Pneumonia", "Asthma", "GERD", "Anxiety"],
            "shortness_of_breath": ["Asthma", "Pneumonia", "Heart failure", "Anemia", "COVID-19"],
            "weight_loss": ["Tuberculosis", "Diabetes", "Cancer", "HIV/AIDS", "Hyperthyroidism"],
            "fatigue": ["Malaria", "Anemia", "Depression", "Diabetes", "Thyroid disorders"]
        }
    
    def _load_emergency_protocols(self) -> Dict[str, Any]:
        """Load emergency medical protocols"""
        return {
            "cardiac_arrest": {
                "signs": ["No pulse", "Unconscious", "Not breathing"],
                "action": [
                    "Call emergency services immediately",
                    "Start CPR if trained",
                    "Use AED if available",
                    "Continue until help arrives"
                ]
            },
            "severe_bleeding": {
                "action": [
                    "Apply direct pressure",
                    "Elevate injured area",
                    "Use clean cloth or bandage",
                    "Seek immediate medical help"
                ]
            },
            "stroke": {
                "signs": ["Face drooping", "Arm weakness", "Speech difficulty"],
                "action": [
                    "Note time of symptom onset",
                    "Call emergency services",
                    "Do not give food or water",
                    "Keep patient calm and lying down"
                ]
            },
            "severe_allergic_reaction": {
                "signs": ["Difficulty breathing", "Swelling", "Rapid pulse", "Dizziness"],
                "action": [
                    "Use epinephrine if available",
                    "Call emergency services",
                    "Loosen tight clothing",
                    "Monitor breathing and pulse"
                ]
            }
        }
    
    def _load_preventive_care(self) -> Dict[str, Any]:
        """Load preventive care guidelines"""
        return {
            "general_health": [
                "Regular health checkups",
                "Maintain healthy diet",
                "Exercise regularly",
                "Adequate sleep (7-9 hours)",
                "Manage stress",
                "Avoid tobacco and excessive alcohol",
                "Practice safe sex",
                "Maintain good hygiene"
            ],
            "vaccination_schedule": {
                "adults": [
                    "Annual flu vaccine",
                    "COVID-19 boosters",
                    "Hepatitis B (if at risk)",
                    "Yellow fever (for travel)",
                    "Meningitis (for high-risk areas)"
                ]
            },
            "screening_guidelines": {
                "blood_pressure": "Every 2 years if normal",
                "cholesterol": "Every 5 years after age 20",
                "diabetes": "Every 3 years after age 45",
                "cervical_cancer": "Every 3 years (ages 21-65)",
                "breast_cancer": "Annual mammogram after age 50",
                "colorectal_cancer": "Every 10 years after age 50"
            }
        }
    
    def _load_medication_guide(self) -> Dict[str, Any]:
        """Load medication guidelines"""
        return {
            "common_medications": {
                "paracetamol": {
                    "uses": "Pain relief, fever reduction",
                    "dosage": "Adults: 500-1000mg every 4-6 hours, max 4g/day",
                    "precautions": "Check for liver disease, avoid alcohol"
                },
                "ibuprofen": {
                    "uses": "Pain relief, inflammation, fever",
                    "dosage": "Adults: 200-400mg every 4-6 hours, max 1200mg/day",
                    "precautions": "Avoid with stomach ulcers, kidney disease"
                },
                "oral_rehydration_salts": {
                    "uses": "Dehydration from diarrhea/vomiting",
                    "preparation": "Mix 1 sachet with 1 liter clean water",
                    "administration": "Small frequent sips"
                }
            },
            "medication_safety": [
                "Always complete antibiotic courses",
                "Don't share prescription medications",
                "Check expiry dates",
                "Store medications properly",
                "Follow dosage instructions carefully",
                "Report side effects to healthcare provider"
            ]
        }
    
    def _load_cultural_practices(self) -> Dict[str, Any]:
        """Load cultural health practices and considerations"""
        return {
            "traditional_medicine": {
                "integration": "Work alongside modern medicine when safe",
                "safety_concerns": [
                    "Verify herb safety and interactions",
                    "Don't delay emergency treatment",
                    "Inform healthcare providers about traditional remedies"
                ],
                "common_practices": {
                    "steam_inhalation": "For respiratory symptoms",
                    "herbal_teas": "For digestive issues",
                    "massage": "For muscle pain"
                }
            },
            "cultural_sensitivities": {
                "family_involvement": "Include family in healthcare decisions",
                "gender_considerations": "Respect preferences for same-gender providers",
                "religious_practices": "Accommodate prayer times and dietary restrictions",
                "language_barriers": "Provide interpretation services"
            },
            "community_health": {
                "health_education": "Use community leaders and local languages",
                "health_promotion": "Integrate with existing community structures",
                "disease_prevention": "Community-based interventions"
            }
        }
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load medical term translations"""
        return {
            "common_terms": {
                "english": {
                    "doctor": "Doctor",
                    "medicine": "Medicine",
                    "hospital": "Hospital",
                    "pain": "Pain",
                    "fever": "Fever",
                    "treatment": "Treatment"
                },
                "luganda": {
                    "doctor": "Omusawo",
                    "medicine": "Eddagala",
                    "hospital": "Eddwaliro",
                    "pain": "Obulumi",
                    "fever": "Omusujja",
                    "treatment": "Obujjanjabi"
                },
                "swahili": {
                    "doctor": "Daktari",
                    "medicine": "Dawa",
                    "hospital": "Hospitali",
                    "pain": "Maumivu",
                    "fever": "Homa",
                    "treatment": "Matibabu"
                }
            }
        }
    
    def get_condition_info(self, condition_name: str, language: str = "english") -> Optional[Dict[str, Any]]:
        """
        Get information about a medical condition
        
        Args:
            condition_name: Name of the condition
            language: Language for response
            
        Returns:
            Condition information or None
        """
        condition_name_lower = condition_name.lower()
        
        # Search through all condition categories
        for category, conditions in self.medical_conditions.items():
            for condition in conditions:
                if isinstance(condition, dict) and 'condition' in condition:
                    if condition_name_lower in condition['condition'].lower():
                        return self._translate_condition_info(condition, language)
                    
                    # Check local names
                    if 'local_names' in condition:
                        for lang, local_name in condition['local_names'].items():
                            if condition_name_lower in local_name.lower():
                                return self._translate_condition_info(condition, language)
        
        return None
    
    def get_symptoms_analysis(self, symptoms: List[str]) -> Dict[str, Any]:
        """
        Analyze symptoms and suggest possible conditions
        
        Args:
            symptoms: List of symptoms
            
        Returns:
            Analysis results with possible conditions
        """
        possible_conditions = {}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for key, conditions in self.symptoms_mapping.items():
                if key in symptom_lower or any(word in symptom_lower for word in key.split('_')):
                    for condition in conditions:
                        if condition not in possible_conditions:
                            possible_conditions[condition] = 0
                        possible_conditions[condition] += 1
        
        # Sort by likelihood (number of matching symptoms)
        sorted_conditions = sorted(
            possible_conditions.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            'possible_conditions': sorted_conditions[:5],  # Top 5 matches
            'recommendation': self._get_symptom_recommendation(symptoms),
            'emergency_check': self._check_emergency_symptoms(symptoms)
        }
    
    def _translate_condition_info(self, condition: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Translate condition information to specified language"""
        # For now, return as is. In production, implement full translation
        return condition
    
    def _get_symptom_recommendation(self, symptoms: List[str]) -> str:
        """Get recommendation based on symptoms"""
        emergency_keywords = [
            'chest pain', 'difficulty breathing', 'unconscious', 
            'severe bleeding', 'seizure', 'stroke'
        ]
        
        for symptom in symptoms:
            if any(keyword in symptom.lower() for keyword in emergency_keywords):
                return "EMERGENCY: Seek immediate medical attention"
        
        if len(symptoms) >= 3:
            return "Multiple symptoms detected. Consult healthcare provider soon."
        
        return "Monitor symptoms. Consult healthcare provider if they worsen or persist."
    
    def _check_emergency_symptoms(self, symptoms: List[str]) -> Dict[str, Any]:
        """Check if symptoms indicate emergency"""
        emergency_symptoms = [
            'chest pain', 'difficulty breathing', 'severe bleeding',
            'unconscious', 'seizure', 'stroke symptoms', 'severe headache',
            'high fever', 'severe abdominal pain'
        ]
        
        detected_emergencies = []
        for symptom in symptoms:
            for emergency in emergency_symptoms:
                if emergency in symptom.lower():
                    detected_emergencies.append(emergency)
        
        return {
            'is_emergency': len(detected_emergencies) > 0,
            'emergency_symptoms': detected_emergencies,
            'action': "Call emergency services immediately" if detected_emergencies else "Continue monitoring"
        }
    
    def get_preventive_care_info(self, category: str = "general") -> Dict[str, Any]:
        """Get preventive care information"""
        if category in self.preventive_care:
            return self.preventive_care[category]
        return self.preventive_care.get('general_health', {})
    
    def get_medication_info(self, medication: str) -> Optional[Dict[str, Any]]:
        """Get medication information"""
        medication_lower = medication.lower()
        
        if 'common_medications' in self.medication_guide:
            for med_name, info in self.medication_guide['common_medications'].items():
                if medication_lower in med_name or med_name in medication_lower:
                    return info
        
        return None
    
    def get_emergency_protocol(self, emergency_type: str) -> Optional[Dict[str, Any]]:
        """Get emergency protocol information"""
        emergency_lower = emergency_type.lower()
        
        for protocol_name, protocol in self.emergency_protocols.items():
            if emergency_lower in protocol_name or protocol_name in emergency_lower:
                return protocol
        
        return None
    
    def search_knowledge(self, query: str, language: str = "english") -> Dict[str, Any]:
        """
        Search across all knowledge base content
        
        Args:
            query: Search query
            language: Preferred language
            
        Returns:
            Search results
        """
        query_lower = query.lower()
        results = {
            'conditions': [],
            'emergency_info': [],
            'preventive_care': [],
            'medications': [],
            'cultural_info': []
        }
        
        # Search conditions
        for category, conditions in self.medical_conditions.items():
            for condition in conditions:
                if isinstance(condition, dict):
                    # Search in condition name and symptoms
                    searchable_text = json.dumps(condition).lower()
                    if query_lower in searchable_text:
                        results['conditions'].append(condition)
        
        # Search emergency protocols
        for protocol_name, protocol in self.emergency_protocols.items():
            if query_lower in protocol_name or query_lower in json.dumps(protocol).lower():
                results['emergency_info'].append({protocol_name: protocol})
        
        # Search medications
        if 'common_medications' in self.medication_guide:
            for med_name, med_info in self.medication_guide['common_medications'].items():
                if query_lower in med_name or query_lower in json.dumps(med_info).lower():
                    results['medications'].append({med_name: med_info})
        
        return results
    
    def get_all_knowledge_as_documents(self) -> List[Dict[str, Any]]:
        """Get all knowledge base content formatted as documents"""
        documents = []
        
        # Add medical conditions
        for category, conditions in self.medical_conditions.items():
            for condition in conditions:
                if isinstance(condition, dict):
                    doc = {
                        'content': json.dumps(condition, indent=2),
                        'metadata': {
                            'type': 'medical_condition',
                            'category': category,
                            'condition_name': condition.get('condition', 'Unknown')
                        }
                    }
                    documents.append(doc)
        
        # Add emergency protocols
        for protocol_name, protocol in self.emergency_protocols.items():
            doc = {
                'content': json.dumps(protocol, indent=2),
                'metadata': {
                    'type': 'emergency_protocol',
                    'protocol_name': protocol_name
                }
            }
            documents.append(doc)
        
        # Add medication info
        if 'common_medications' in self.medication_guide:
            for med_name, med_info in self.medication_guide['common_medications'].items():
                doc = {
                    'content': json.dumps(med_info, indent=2),
                    'metadata': {
                        'type': 'medication',
                        'medication_name': med_name
                    }
                }
                documents.append(doc)
        
        # Add preventive care
        for care_type, care_info in self.preventive_care.items():
            doc = {
                'content': json.dumps(care_info, indent=2),
                'metadata': {
                    'type': 'preventive_care',
                    'care_type': care_type
                }
            }
            documents.append(doc)
        
        return documents
