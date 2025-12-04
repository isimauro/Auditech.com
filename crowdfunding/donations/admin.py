from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'donor', 'campaign', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'is_anonymous')
    search_fields = ('donor__username', 'campaign__title', 'transaction_id')
    readonly_fields = ('created_at', 'transaction_id')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Edição
            return self.readonly_fields + ('amount', 'donor', 'campaign')
        return self.readonly_fields