from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import CompanySerializer, PriceHistorySerializer
from django.db.models import Q
from .models import PriceHistory, Company
from datetime import datetime
from .utils import PriceHistoryScrapper
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsAdminOrEditorReadOnly


DRIVER_PATH = '/usr/bin/chromedriver'


class CompanyListCreateAPIView(APIView):
    """
    List all companies or create a new company
    """
    permission_classes = [IsAuthenticated, IsAdminOrEditorReadOnly]

    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyDetailAPIView(APIView):
    """
    Retrieve, update or delete a company instance
    """

    permission_classes = [IsAuthenticated, IsAdminOrEditorReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Company, pk=pk)

    def get(self, request, pk):
        company = self.get_object(pk)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def put(self, request, pk):
        company = self.get_object(pk)
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        company = self.get_object(pk)
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Price History

class PriceHistoryAPIView(APIView):
    """
    Retrieve price history with filtering capabilities
    """

    permission_classes = [IsAuthenticated, IsAdminOrEditorReadOnly]

    def get(self, request):
        try:
            company_symbol = request.query_params.get('symbol')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            min_price = request.query_params.get('min_price')
            max_price = request.query_params.get('max_price')

            # Validate company symbol
            if not company_symbol:
                return Response(
                    {'error': 'Company symbol is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get company
            try:
                company = Company.objects.get(symbol=company_symbol.upper())
            except Company.DoesNotExist:
                return Response(
                    {'error': f'Company with symbol {company_symbol} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Build query
            query = Q(company=company)

            # Add date filters if provided
            if start_date:
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    query &= Q(date__gte=start_date)
                except ValueError:
                    return Response(
                        {'error': 'Invalid start_date format. Use YYYY-MM-DD'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if end_date:
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query &= Q(date__lte=end_date)
                except ValueError:
                    return Response(
                        {'error': 'Invalid end_date format. Use YYYY-MM-DD'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # price range filters if provided
            if min_price:
                try:
                    min_price = float(min_price)
                    query &= (
                        Q(open_price__gte=min_price) |
                        Q(close_price__gte=min_price) |
                        Q(high_price__gte=min_price) |
                        Q(low_price__gte=min_price)
                    )
                except ValueError:
                    return Response(
                        {'error': 'Invalid min_price format. Must be a number'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if max_price:
                try:
                    max_price = float(max_price)
                    query &= (
                        Q(open_price__lte=max_price) |
                        Q(close_price__lte=max_price) |
                        Q(high_price__lte=max_price) |
                        Q(low_price__lte=max_price)
                    )
                except ValueError:
                    return Response(
                        {'error': 'Invalid max_price format. Must be a number'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Get price history
            price_history = PriceHistory.objects.filter(query).order_by('-date')

            # Check if any data exists
            if not price_history.exists():
                return Response(
                    {'error': 'No price history found for the specified criteria'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize data
            serializer = PriceHistorySerializer(price_history, many=True)

            response_data = {
                'company_symbol': company.symbol,
                'company_name': company.name,
                'total_records': price_history.count(),
                'price_history': serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# view for scraping and updating price history
class UpdatePriceHistoryAPIView(APIView):
    """
    API endpoint for manually triggering price history update for a company
    """
    permission_classes = [IsAuthenticated, IsAdminOrEditorReadOnly]

    def post(self, request):
        try:
            company_symbol = request.data.get('company')
            
            if not company_symbol:
                return Response(
                    {'error': 'Company symbol is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                company = Company.objects.get(symbol=company_symbol.upper())
            except Company.DoesNotExist:
                return Response(
                    {'error': f'Company with symbol {company_symbol} not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Initialize scraper and update data
            scraper = None
            try:
                scraper = PriceHistoryScrapper(
                    url=company.website, 
                    driver_path=DRIVER_PATH
                )
                scraped_data = scraper.scrap_data()
                
                if not scraped_data:
                    return Response(
                        {'error': 'No data found to update'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Save scraped data
                saved_entries = self._save_price_history(company, scraped_data)
                
                return Response({
                    'message': 'Price history updated successfully',
                    'company_symbol': company.symbol,
                    'records_updated': len(saved_entries)
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response(
                    {'error': f'Error updating price history: {str(e)}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            finally:
                if scraper and scraper.driver:
                    scraper.driver.quit()

        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # @transaction.atomic
    def _save_price_history(self, company, scrapped_data):
        """
        Save scraped data to database
        """
        saved_entries = []
        
        for entry in scrapped_data:
            try:
                # Convert date string to date object if needed
                date_str = entry.get('date')
                if isinstance(date_str, str):
                    try:
                        for date_format in ['%Y-%m-%d', '%d/%m/%Y']:
                            try:
                                date_obj = datetime.strptime(date_str, date_format).date()
                                break
                            except ValueError:
                                continue
                    except ValueError:
                        print(f"Invalid date format: {date_str}")
                        continue
                else:
                    date_obj = date_str

                # Create or update price history entry
                price_history, created = PriceHistory.objects.update_or_create(
                    company=company,
                    date=date_obj,
                    defaults={
                        'open_price': entry.get('open_price', 0.0),
                        'high_price': entry.get('high_price', 0.0),
                        'low_price': entry.get('low_price', 0.0),
                        'close_price': entry.get('close_price', 0.0),
                        'volume': entry.get('total_traded_quantity', 0)
                    }
                )
                
                saved_entries.append(price_history)
                
            except Exception as e:
                print(f"Error saving entry for date {entry.get('date')}: {e}")
                continue

        return saved_entries