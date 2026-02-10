from django.urls import path
from . import views

app_name = 'wallets'

urlpatterns = [
    path('', views.AccountListView.as_view(), name='list'),
    path('create/', views.AccountCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AccountDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AccountUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.AccountDeleteView.as_view(), name='delete'),
    # Credit card payment URLs
    path('<int:pk>/pay/', views.CreditCardPaymentView.as_view(), name='cc_payment'),
    path('<int:pk>/payment-history/', views.CreditCardPaymentHistoryView.as_view(), name='cc_payment_history'),
]
