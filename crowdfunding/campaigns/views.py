from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views import View
from django.db.models import Q, Sum, Count
from django.utils.text import slugify
from .models import Campaign, Category

class CampaignListView(ListView):
    model = Campaign
    template_name = 'campaigns/campaign_list.html'
    context_object_name = 'campaigns'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Campaign.objects.filter(status='active')
        
        # Filtros
        category = self.request.GET.get('category')
        search = self.request.GET.get('q')
        sort = self.request.GET.get('sort', 'newest')
        
        if category:
            queryset = queryset.filter(category__name=category)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(creator__username__icontains=search)
            )
        
        # Ordenação
        if sort == 'popular':
            queryset = queryset.annotate(
                donations_count=Count('donation')
            ).order_by('-donations_count')
        elif sort == 'ending_soon':
            queryset = queryset.order_by('end_date')
        elif sort == 'most_funded':
            queryset = queryset.order_by('-amount_raised')
        else:  # newest (padrão)
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['featured_campaigns'] = Campaign.objects.filter(
            status='active'
        ).order_by('-amount_raised')[:3]
        
        # Estatísticas
        stats = Campaign.objects.aggregate(
            total_campaigns=Count('id'),
            total_raised=Sum('amount_raised'),
            active_campaigns=Count('id', filter=Q(status='active'))
        )
        context.update(stats)
        
        return context

class CampaignDetailView(DetailView):
    model = Campaign
    template_name = 'campaigns/campaign_detail.html'
    context_object_name = 'campaign'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaign = self.get_object()
        
        # Doações recentes
        context['recent_donations'] = campaign.donation_set.filter(
            status='completed'
        ).select_related('donor').order_by('-created_at')[:10]
        
        # Contagem de doadores
        context['donors_count'] = campaign.get_donors_count()
        
        # Campanhas similares
        context['similar_campaigns'] = Campaign.objects.filter(
            category=campaign.category,
            status='active'
        ).exclude(id=campaign.id)[:4]
        
        return context

class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    template_name = 'campaigns/campaign_form.html'
    fields = ['title', 'description', 'goal', 'end_date', 'category', 'image']
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.status = 'draft'  # Começa como rascunho
        
        messages.success(
            self.request, 
            'Campanha criada com sucesso! Ela ficará como rascunho até você publicá-la.'
        )
        
        response = super().form_valid(form)
        
        # Atualizar contador no perfil
        profile = self.request.user.profile
        profile.campaigns_created += 1
        profile.save()
        
        return response

class CampaignUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Campaign
    template_name = 'campaigns/campaign_form.html'
    fields = ['title', 'description', 'goal', 'end_date', 'category', 'image', 'status']
    
    def test_func(self):
        campaign = self.get_object()
        return self.request.user == campaign.creator
    
    def form_valid(self, form):
        messages.success(self.request, 'Campanha atualizada com sucesso!')
        return super().form_valid(form)

class CampaignPublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        campaign = get_object_or_404(Campaign, slug=self.kwargs['slug'])
        return self.request.user == campaign.creator
    
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, slug=self.kwargs['slug'])
        
        if campaign.status == 'draft':
            campaign.status = 'active'
            campaign.save()
            messages.success(request, 'Campanha publicada com sucesso!')
        else:
            messages.warning(request, 'Esta campanha já está publicada.')
        
        return redirect('campaign-detail', slug=campaign.slug)