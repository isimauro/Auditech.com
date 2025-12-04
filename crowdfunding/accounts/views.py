from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from campaigns.models import Campaign
from donations.models import Donation

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Logar usuário automaticamente
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Conta criada com sucesso! Bem-vindo, {username}!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Obter dados do usuário
    campaigns_created = Campaign.objects.filter(creator=request.user)
    donations_made = Donation.objects.filter(donor=request.user, status='completed')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'campaigns_created': campaigns_created,
        'donations_made': donations_made,
        'total_donated': sum(d.amount for d in donations_made),
        'active_campaigns': campaigns_created.filter(status='active').count(),
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def dashboard(request):
    """Dashboard com estatísticas do usuário"""
    
    # Campanhas do usuário
    user_campaigns = Campaign.objects.filter(creator=request.user)
    
    # Estatísticas
    campaign_stats = {
        'total': user_campaigns.count(),
        'active': user_campaigns.filter(status='active').count(),
        'completed': user_campaigns.filter(status='completed').count(),
        'total_raised': user_campaigns.aggregate(
            total=Sum('amount_raised')
        )['total'] or 0,
    }
    
    # Doações recebidas nas campanhas do usuário
    donations_received = Donation.objects.filter(
        campaign__in=user_campaigns,
        status='completed'
    ).select_related('donor').order_by('-created_at')[:10]
    
    # Últimas atividades
    recent_activities = []
    
    return render(request, 'accounts/dashboard.html', {
        'campaign_stats': campaign_stats,
        'donations_received': donations_received,
        'user_campaigns': user_campaigns[:5],
    })