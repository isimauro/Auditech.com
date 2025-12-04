# donations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from decimal import Decimal
from .models import Donation
from campaigns.models import Campaign
from django.db.models import Sum

@login_required
def create_donation(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug)
    
    if not campaign.is_active:
        messages.error(request, 'Esta campanha não está ativa para doações.')
        return redirect('campaign-detail', slug=slug)
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        message = request.POST.get('message', '')
        
        # Criar doação
        donation = Donation.objects.create(
            donor=request.user,
            campaign=campaign,
            amount=amount,
            is_anonymous=is_anonymous,
            message=message,
            status='pending'
        )
        
        # Processar pagamento (exemplo com Stripe)
        return process_payment(request, donation)
    
    # Valores sugeridos
    suggested_amounts = [10, 25, 50, 100, 250, 500]
    
    return render(request, 'donations/donation_form.html', {
        'campaign': campaign,
        'suggested_amounts': suggested_amounts
    })

@login_required
def user_donations(request):
    donations = Donation.objects.filter(
        donor=request.user
    ).select_related('campaign').order_by('-created_at')
    
    total_donated = donations.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return render(request, 'donations/user_donations.html', {
        'donations': donations,
        'total_donated': total_donated
    })

def process_payment(request, donation):
    """
    Integração com Stripe (exemplo simplificado)
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': f'Doação para: {donation.campaign.title}',
                        'description': donation.campaign.description[:100] + '...',
                    },
                    'unit_amount': int(donation.amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                f'/donations/success/{donation.id}/'
            ),
            cancel_url=request.build_absolute_uri(
                f'/campaigns/{donation.campaign.slug}/'
            ),
            metadata={
                'donation_id': donation.id,
                'user_id': request.user.id,
                'campaign_id': donation.campaign.id,
            }
        )
        
        donation.transaction_id = checkout_session.id
        donation.save()
        
        return redirect(checkout_session.url)
        
    except Exception as e:
        messages.error(request, f'Erro ao processar pagamento: {str(e)}')
        return redirect('campaign-detail', slug=donation.campaign.slug)

@login_required
def donation_success(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user)
    
    # Verificar se pagamento foi concluído
    if donation.status == 'pending':
        messages.info(request, 'Aguardando confirmação do pagamento...')
    
    return render(request, 'donations/donation_success.html', {
        'donation': donation
    })