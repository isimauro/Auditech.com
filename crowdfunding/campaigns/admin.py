from django.contrib import admin
from .models import Category, Campaign

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign_count')
    search_fields = ('name', 'description')
    
    def campaign_count(self, obj):
        return obj.campaign_set.count()
    campaign_count.short_description = 'Número de Campanhas'

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'goal', 'amount_raised', 
                    'progress_display', 'end_date', 'status')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'creator__username')
    readonly_fields = ('slug', 'created_at', 'amount_raised')
    list_editable = ('status',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'description', 'category', 'image')
        }),
        ('Finanças', {
            'fields': ('goal', 'amount_raised')
        }),
        ('Datas', {
            'fields': ('created_at', 'end_date')
        }),
        ('Status', {
            'fields': ('status', 'creator')
        }),
    )
    
    def progress_display(self, obj):
        return f"{obj.progress:.1f}%"
    progress_display.short_description = 'Progresso'