from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # Frontend URLs
    path('', views.home, name='home'),
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<slug:vehicle_slug>/', views.parts_list, name='parts_list'),
    path('vehicles/<slug:vehicle_slug>/<slug:part_slug>/', views.part_detail, name='part_detail'),
    path('search/', views.search, name='search'),
    
    # Admin AJAX endpoints for stock management
    path('admin-api/stock/<int:stock_id>/increase/', views.increase_stock, name='increase_stock'),
    path('admin-api/stock/<int:stock_id>/decrease/', views.decrease_stock, name='decrease_stock'),
]