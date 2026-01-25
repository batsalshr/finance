from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='list'),
    path('create/', views.TransactionCreateView.as_view(), name='create'),
    path('bulk-import/', views.BulkImportView.as_view(), name='bulk_import'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='delete'),
    
    # Receipts
    path('<int:transaction_id>/receipts/upload/', views.ReceiptUploadView.as_view(), name='receipt_upload'),
    path('receipts/<int:pk>/delete/', views.ReceiptDeleteView.as_view(), name='receipt_delete'),
    
    # Transaction Templates (Quick Add)
    path('quick-add/', views.TemplateListView.as_view(), name='template_list'),
    path('quick-add/new/', views.TemplateCreateView.as_view(), name='template_create'),
    path('quick-add/<int:pk>/use/', views.QuickAddView.as_view(), name='quick_add'),
    path('quick-add/<int:pk>/edit/', views.TemplateUpdateView.as_view(), name='template_edit'),
    path('quick-add/<int:pk>/delete/', views.TemplateDeleteView.as_view(), name='template_delete'),
]
