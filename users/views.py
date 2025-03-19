from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django import forms

# Форма для авторизации
class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('profile')
            else:
                form.add_error(None, "Неверный email или пароль")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.phone = request.POST.get('phone', user.phone)
        user.location = request.POST.get('location', user.location)
        user.bio = request.POST.get('bio', user.bio)
        user.instagram = request.POST.get('instagram', user.instagram)
        user.telegram = request.POST.get('telegram', user.telegram)
        user.whatsapp = request.POST.get('whatsapp', user.whatsapp)
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        user.save()
        return redirect('profile')
    return render(request, 'users/profile.html', {'user': request.user})
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')