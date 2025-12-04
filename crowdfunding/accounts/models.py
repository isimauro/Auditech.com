# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    bio = models.TextField(blank=True, verbose_name="Biografia")
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Foto")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    country = CountryField(blank=True, verbose_name="País")
    city = models.CharField(max_length=100, blank=True, verbose_name="Cidade")
    website = models.URLField(blank=True, verbose_name="Website")
    
    # Stats (atualizados periodicamente)
    total_donated = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total Doado")
    campaigns_created = models.IntegerField(default=0, verbose_name="Campanhas Criadas")
    
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
    
    def __str__(self):
        return self.user.username
    
    def get_campaigns_created(self):
        """Retorna campanhas criadas pelo usuário"""
        from campaigns.models import Campaign
        return Campaign.objects.filter(creator=self.user)
    
    def get_total_donations(self):
        """Retorna total doado pelo usuário"""
        from donations.models import Donation
        return Donation.objects.filter(
            donor=self.user, 
            status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0

# Signals para criar/atualizar perfil automaticamente
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()