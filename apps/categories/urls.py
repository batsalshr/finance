from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='list'),
    path('create/', views.CategoryCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='delete'),
    path('subcategory/create/', views.SubCategoryCreateView.as_view(), name='subcategory_create'),
    path('subcategory/<int:pk>/delete/', views.SubCategoryDeleteView.as_view(), name='subcategory_delete'),
    path('api/subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('api/search/', views.search_categories, name='search_categories'),
]
