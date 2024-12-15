from django.db import models
from django.core.validators import MinValueValidator

class Company(models.Model):
    SECTOR_CHOICES = [
        ('HYDROPOWER', 'Hydropower'),
        ('INSURANCE', 'Insurance'),
        ('NON-LIFE-INSURANCE', 'Non Life Insurance'),
        ('INVESTMENT', 'Investment'),
        ('BANKING', 'Banking'),
        ('MANUFACTURING', 'Manufacturing'),
        ('HOTEL-AND-TOURISM', 'Hotels And Tourism'),
        ('OTHERS', 'Others'),
    ]

    name = models.CharField(max_length=200, unique=True)
    symbol = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    sector = models.CharField(
        max_length=50,
        choices=SECTOR_CHOICES,
        default='OTHERS'
    )
    website = models.URLField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class PriceHistory(models.Model):
    company = models.ForeignKey(
        'Company', 
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    date = models.DateField()
    open_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    high_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    low_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    close_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    volume = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['company', 'date']
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.company.symbol} - {self.date}"
