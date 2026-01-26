"""
URL configuration for Personal Finance Tracker
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls', namespace='dashboard')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('wallets/', include('apps.wallets.urls', namespace='wallets')),
    path('transactions/', include('apps.transactions.urls', namespace='transactions')),
    path('categories/', include('apps.categories.urls', namespace='categories')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
