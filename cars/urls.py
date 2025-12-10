from django.urls import path
from .views import (
    # Category views
    CategoryListCreateView,
    CategoryDetailView,
    
    # Car views
    CarListCreateView,
    CarDetailView,
    
    # Choices views
    SellerTypeChoicesView,
    DriveChoicesView,
    FuelTypeChoicesView,
    TransmissionChoicesView,
    AspirationChoicesView,
    AvailabilityChoicesView,
    
    # Car image views
    CarImageUploadView,
    CarImageBulkUploadView,
    CarImageDetailView,
    CarImageSetPrimaryView,
    CarImageReorderView,
)

app_name = 'cars'

urlpatterns = [
  
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
  
    path('', CarListCreateView.as_view(), name='car-list-create'),
    path('<int:pk>/', CarDetailView.as_view(), name='car-detail'),
   
    path('choices/seller-types/', SellerTypeChoicesView.as_view(), name='seller-type-choices'),
    path('choices/drives/', DriveChoicesView.as_view(), name='drive-choices'),
    path('choices/fuel-types/', FuelTypeChoicesView.as_view(), name='fuel-type-choices'),
    path('choices/transmissions/', TransmissionChoicesView.as_view(), name='transmission-choices'),
    path('choices/aspirations/', AspirationChoicesView.as_view(), name='aspiration-choices'),
    path('choices/availability/', AvailabilityChoicesView.as_view(), name='availability-choices'),
    
   
    path('<int:car_id>/images/', CarImageUploadView.as_view(), name='car-image-upload'),
    path('<int:car_id>/images/bulk/', CarImageBulkUploadView.as_view(), name='car-image-bulk-upload'),
    path('<int:car_id>/images/<int:image_id>/', CarImageDetailView.as_view(), name='car-image-detail'),
    path('<int:car_id>/images/<int:image_id>/set-primary/', CarImageSetPrimaryView.as_view(), name='car-image-set-primary'),
    path('<int:car_id>/images/reorder/', CarImageReorderView.as_view(), name='car-image-reorder'),
]
