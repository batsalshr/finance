from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse

from .models import Category, SubCategory
from .forms import CategoryForm, SubCategoryForm


class CategoryListView(LoginRequiredMixin, ListView):
    """List all categories (shared across all users)"""
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).prefetch_related('subcategories')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Categories'
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Create new category (available to all users)"""
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    success_url = reverse_lazy('categories:list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Category "{form.instance.name}" created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Category'
        context['button_text'] = 'Create Category'
        context['page_title'] = 'New Category'
        return context


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing category"""
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    success_url = reverse_lazy('categories:list')
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Category'
        context['button_text'] = 'Update Category'
        context['page_title'] = 'Edit Category'
        return context


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete category"""
    model = Category
    template_name = 'categories/confirm_delete.html'
    success_url = reverse_lazy('categories:list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{self.object.name}" deleted successfully!')
        return super().form_valid(form)


class SubCategoryCreateView(LoginRequiredMixin, CreateView):
    """Create new subcategory"""
    model = SubCategory
    form_class = SubCategoryForm
    template_name = 'categories/subcategory_form.html'
    success_url = reverse_lazy('categories:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f'Subcategory "{form.instance.name}" created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Subcategory'
        context['button_text'] = 'Create Subcategory'
        context['page_title'] = 'New Subcategory'
        return context


class SubCategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete subcategory"""
    model = SubCategory
    template_name = 'categories/confirm_delete.html'
    success_url = reverse_lazy('categories:list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Subcategory deleted successfully!')
        return super().form_valid(form)


def get_subcategories(request, category_id):
    """AJAX view to get subcategories for a category"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    subcategories = SubCategory.objects.filter(
        category_id=category_id,
        is_active=True
    ).values('id', 'name')
    
    return JsonResponse({'subcategories': list(subcategories)})


def search_categories(request):
    """AJAX view to search/autocomplete categories"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    query = request.GET.get('q', '').strip()
    category_type = request.GET.get('type', '')  # 'income', 'expense', or ''
    
    categories = Category.objects.filter(is_active=True)
    
    if query:
        categories = categories.filter(name__icontains=query)
    
    if category_type:
        categories = categories.filter(category_type__in=[category_type, 'both'])
    
    results = []
    for cat in categories[:10]:  # Limit to 10 results
        results.append({
            'id': cat.id,
            'name': cat.name,
            'color': cat.color,
            'icon': cat.icon,
            'type': cat.category_type,
        })
    
    return JsonResponse({'categories': results})
