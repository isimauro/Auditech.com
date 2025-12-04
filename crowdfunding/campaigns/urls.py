from django.urls import path
from . import views

urlpatterns = [
    path('', views.CampaignListView.as_view(), name='home'),
    path('campaigns/', views.CampaignListView.as_view(), name='campaign-list'),
    path('campaigns/create/', views.CampaignCreateView.as_view(), name='campaign-create'),
    path('campaigns/<slug:slug>/', views.CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<slug:slug>/edit/', views.CampaignUpdateView.as_view(), name='campaign-update'),
    path('campaigns/<slug:slug>/publish/', views.CampaignPublishView.as_view(), name='campaign-publish'),
    path('campaigns/category/<str:category>/', views.CampaignListView.as_view(), name='campaigns-by-category'),
]