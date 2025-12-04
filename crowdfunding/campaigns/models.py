# campaigns/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(verbose_name="Descrição")
    icon = models.CharField(max_length=50, blank=True, help_text="Classe do FontAwesome")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    
    def __str__(self):
        return self.name

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('active', 'Ativa'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
        ('expired', 'Expirada'),
    ]
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criador")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    goal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Meta")
    amount_raised = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor Arrecadado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    end_date = models.DateField(verbose_name="Data de Término")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Categoria")
    image = models.ImageField(upload_to='campaigns/', verbose_name="Imagem")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name = "Campanha"
        verbose_name_plural = "Campanhas"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.creator.username}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('campaign-detail', kwargs={'slug': self.slug})
    
    @property
    def progress(self):
        """Retorna o progresso da campanha em porcentagem"""
        if self.goal > 0:
            return (self.amount_raised / self.goal) * 100
        return 0
    
    @property
    def days_left(self):
        """Retorna dias restantes"""
        delta = self.end_date - timezone.now().date()
        return max(delta.days, 0)
    
    @property
    def is_active(self):
        """Verifica se campanha está ativa"""
        return self.status == 'active' and self.days_left > 0
    
    def get_donors_count(self):
        """Retorna número de doadores únicos"""
        from donations.models import Donation
        return Donation.objects.filter(
            campaign=self, 
            status='completed'
        ).values('donor').distinct().count()