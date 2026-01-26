from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.MonthlyReportsView.as_view(), name='monthly_list'),
    path('<int:pk>/', views.MonthlyReportDetailView.as_view(), name='monthly_detail'),
    path('refresh/', views.RefreshReportsView.as_view(), name='refresh'),
]
