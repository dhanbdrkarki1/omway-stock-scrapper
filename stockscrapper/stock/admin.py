from django.contrib import admin
from .models import Company, PriceHistory
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol', 'sector', 'email', 'created_at', 'updated_at')
    list_filter = ('sector', 'created_at', 'updated_at')
    search_fields = ('name', 'symbol', 'email', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'symbol', 'sector')
        }),
        ('Contact Information', {
            'fields': ('email', 'website', 'phone', 'address')
        }),
        ('Additional Information', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('symbol',)
        return self.readonly_fields


from rest_framework import serializers
from .models import PriceHistory

class PriceHistorySerializer(serializers.ModelSerializer):
    company_symbol = serializers.CharField(source='company.symbol', read_only=True)
    
    class Meta:
        model = PriceHistory
        fields = [
            'id',
            'company',
            'company_symbol',
            'date',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def validate(self, data):
        """
        Check that the high price is greater than low price and
        open/close prices are between high and low
        """
        if data['high_price'] < data['low_price']:
            raise serializers.ValidationError("High price must be greater than low price")
        
        if not (data['low_price'] <= data['open_price'] <= data['high_price']):
            raise serializers.ValidationError("Open price must be between high and low prices")
            
        if not (data['low_price'] <= data['close_price'] <= data['high_price']):
            raise serializers.ValidationError("Close price must be between high and low prices")
            
        return data


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('company', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume')
    list_filter = ('company', 'date')
    search_fields = ('company__name', 'company__symbol')
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company',)
        }),
        ('Price Data', {
            'fields': (
                'date',
                ('open_price', 'close_price'),
                ('high_price', 'low_price'),
                'volume'
            )
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def get_readonly_fields(self, request, obj=None):
        # Make company and date readonly if editing existing object
        if obj:
            return self.readonly_fields + ('company', 'date')
        return self.readonly_fields

    # Data validation
    def save_model(self, request, obj, form, change):
        if obj.high_price < obj.low_price:
            self.message_user(request, "High price must be greater than low price", level='ERROR')
            return
        
        if not (obj.low_price <= obj.open_price <= obj.high_price):
            self.message_user(request, "Open price must be between high and low prices", level='ERROR')
            return
            
        if not (obj.low_price <= obj.close_price <= obj.high_price):
            self.message_user(request, "Close price must be between high and low prices", level='ERROR')
            return
            
        super().save_model(request, obj, form, change)

    # # Custom list display formatting
    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related('company')
