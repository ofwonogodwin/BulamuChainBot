from django.urls import path
from . import views

urlpatterns = [
    # Medicine verification
    path('medicine/verify/', views.MedicineVerificationView.as_view(), name='medicine-verify'),
    path('medicine/verifications/', views.MedicineVerificationListView.as_view(), name='medicine-verifications'),
    path('medicine/batch/<str:batch_number>/', views.get_medicine_batch_info, name='medicine-batch-info'),
    
    # Blockchain transactions
    path('transactions/', views.BlockchainTransactionListView.as_view(), name='blockchain-transactions'),
    path('transactions/status/', views.check_transaction_status, name='transaction-status'),
    
    # Patient consent
    path('consent/', views.PatientConsentListCreateView.as_view(), name='patient-consent'),
    path('consent/<uuid:consent_id>/revoke/', views.revoke_consent, name='revoke-consent'),
    
    # Smart contracts
    path('contracts/', views.SmartContractListView.as_view(), name='smart-contracts'),
    
    # Network status
    path('status/', views.BlockchainStatusView.as_view(), name='blockchain-status'),
    
    # Consultation Blockchain Endpoints
    path('consultations/', views.get_patient_consultation_records, name='consultation-records'),
    path('consultations/<uuid:consultation_record_id>/', views.get_consultation_details, name='consultation-details'),
    path('consultations/grant-access/', views.grant_provider_access, name='grant-provider-access'),
    path('consultations/revoke-access/', views.revoke_provider_access, name='revoke-provider-access'),
]
