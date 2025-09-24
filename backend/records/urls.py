from django.urls import path
from . import views

urlpatterns = [
    # Patient profile
    path('profile/', views.PatientProfileView.as_view(), name='patient-profile'),
    
    # Medical records CRUD
    path('', views.MedicalRecordListCreateView.as_view(), name='medical-records'),
    path('<uuid:pk>/', views.MedicalRecordDetailView.as_view(), name='medical-record-detail'),
    
    # Specialized endpoints
    path('store/', views.StoreMedicalRecordView.as_view(), name='store-record'),
    path('<uuid:record_id>/retrieve/', views.RetrieveMedicalRecordView.as_view(), name='retrieve-record'),
    path('<uuid:record_id>/verify/', views.verify_blockchain_record, name='verify-record'),
    
    # Access logs
    path('<uuid:record_id>/access-logs/', views.RecordAccessLogView.as_view(), name='record-access-logs'),
]
