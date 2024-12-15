from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # Company API endpoints
    path('', 
         views.CompanyListCreateAPIView.as_view(), 
         name='company-list-create'),
    
    path('<int:pk>/', 
         views.CompanyDetailAPIView.as_view(), 
         name='company-detail'),

    # Price History endpoints
    path('price-history/', 
         views.PriceHistoryAPIView.as_view(), 
         name='price-history'),
    path('price-history/update/', 
         views.UpdatePriceHistoryAPIView.as_view(), 
         name='update-price-history'),
]
