from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import Company, PriceHistory

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'name', 
            'symbol', 
            'email', 
            'sector', 
            'website', 
            'address', 
            'phone', 
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_symbol(self, value):
        return value.upper()


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = [
            'id',
            'date',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume',
            'created_at'
        ]
        read_only_fields = ['created_at']