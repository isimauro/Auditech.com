# donations/models.py
from django.db import models
from django.contrib.auth.models import User
from campaigns.models import Campaign

class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
        ('refunded', 'Reembolsada'),
    ]
    
    donor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Doador")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, verbose_name="Campanha")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    is_anonymous = models.BooleanField(default=False, verbose_name="Anônima")
    message = models.TextField(blank=True, verbose_name="Mensagem")
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="ID da Transação")
    
    class Meta:
        verbose_name = "Doação"
        verbose_name_plural = "Doações"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Doação de R${self.amount} para {self.campaign.title}"
    
    def save(self, *args, **kwargs):
        # Quando uma doação é concluída, atualiza o valor arrecadado da campanha
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            old_donation = Donation.objects.get(pk=self.pk)
            old_status = old_donation.status
        
        super().save(*args, **kwargs)
        
        # Atualizar campanha se status mudou para completed
        if self.status == 'completed' and old_status != 'completed':
            self.campaign.amount_raised += self.amount
            self.campaign.save()