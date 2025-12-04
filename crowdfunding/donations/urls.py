from django.urls import path
from . import views

urlpatterns = [
    path('create/<slug:slug>/', views.create_donation, name='donation-create'),
    path('my-donations/', views.user_donations, name='user-donations'),
    path('success/<int:donation_id>/', views.donation_success, name='donation-success'),
  #  path('webhook/stripe/', views.stripe_webhook, name='stripe-webhook'),
]