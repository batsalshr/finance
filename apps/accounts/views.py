from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import UserProfile


class UserRegisterView(CreateView):
    """User registration view"""
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard:index')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'Welcome {user.first_name}! Your account has been created.')
        return redirect(self.success_url)


class UserLoginView(LoginView):
    """User login view"""
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:index')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """User logout view"""
    next_page = reverse_lazy('accounts:login')
    http_method_names = ['get', 'post', 'options']
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            # Log the user out on GET request as well
            from django.contrib.auth import logout
            logout(request)
            messages.info(request, 'You have been logged out.')
            return redirect(self.next_page)
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    """User profile view"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        return self.request.user.profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Settings'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
