from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Category, Car, CarImage
from .serializers import (
    CategorySerializer,
    CarListSerializer,
    CarDetailSerializer,
    CarCreateUpdateSerializer,
    CarImageSerializer,
    ImageUploadSerializer,
    ImageReorderSerializer,
    ChoicesSerializer
)
from users.permissions import IsApprovedWorkerOrAdmin


# ============= Category Views =============

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories
    POST: Create new category (Workers + Admin)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsApprovedWorkerOrAdmin]

    def get_permissions(self):
        if self.request.method == 'GET':
            return []  # Allow anyone to view categories
        return super().get_permissions()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Category detail
    PUT/PATCH: Update category
    DELETE: Delete category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsApprovedWorkerOrAdmin]

    def get_permissions(self):
        if self.request.method == 'GET':
            return []  # Allow anyone to view category details
        return super().get_permissions()


# ============= Car Views =============

class CarListCreateView(generics.ListCreateAPIView):
    """
    GET: List all cars with filtering
    POST: Create new car (Workers + Admin)
    """
    permission_classes = [IsApprovedWorkerOrAdmin]

    def get_queryset(self):
        queryset = Car.objects.select_related('category', 'created_by').prefetch_related('images')
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Search by title
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by year range
        min_year = self.request.query_params.get('min_year')
        max_year = self.request.query_params.get('max_year')
        if min_year:
            queryset = queryset.filter(year__gte=min_year)
        if max_year:
            queryset = queryset.filter(year__lte=max_year)
        
        # Filter by mileage range
        min_mileage = self.request.query_params.get('min_mileage')
        max_mileage = self.request.query_params.get('max_mileage')
        if min_mileage:
            queryset = queryset.filter(mileage__gte=min_mileage)
        if max_mileage:
            queryset = queryset.filter(mileage__lte=max_mileage)
        
        # Filter by seller type
        seller_type = self.request.query_params.get('seller_type')
        if seller_type:
            queryset = queryset.filter(seller_type=seller_type)
        
        # Filter by fuel type
        fuel_type = self.request.query_params.get('fuel_type')
        if fuel_type:
            queryset = queryset.filter(fuel_type=fuel_type)
        
        # Filter by transmission
        transmission = self.request.query_params.get('transmission')
        if transmission:
            queryset = queryset.filter(transmission=transmission)
        
        # Filter by drive type
        drive = self.request.query_params.get('drive')
        if drive:
            queryset = queryset.filter(drive=drive)
        
        # Filter by availability
        availability = self.request.query_params.get('availability')
        if availability:
            queryset = queryset.filter(availability=availability)
        
        # Sorting
        ordering = self.request.query_params.get('ordering', '-created_at')
        allowed_orderings = [
            'price', '-price', 'year', '-year', 'mileage', '-mileage',
            'created_at', '-created_at', 'title', '-title'
        ]
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)
        
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CarCreateUpdateSerializer
        return CarListSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []  # Allow anyone to view cars
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CarDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Car detail
    PUT/PATCH: Update car
    DELETE: Delete car
    """
    queryset = Car.objects.select_related('category', 'created_by').prefetch_related('images')
    permission_classes = [IsApprovedWorkerOrAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CarCreateUpdateSerializer
        return CarDetailSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []  # Allow anyone to view car details
        return super().get_permissions()


# ============= Choices Views =============

class SellerTypeChoicesView(views.APIView):
    """GET: Get available seller type choices"""
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Car.SELLER_TYPE_CHOICES
        ]
        serializer = ChoicesSerializer(choices, many=True)
        return Response(serializer.data)


class DriveChoicesView(views.APIView):
    """GET: Get available drive type choices"""
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Car.DRIVE_CHOICES
        ]
        serializer = ChoicesSerializer(choices, many=True)
        return Response(serializer.data)


class FuelTypeChoicesView(views.APIView):
    """GET: Get available fuel type choices"""
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Car.FUEL_TYPE_CHOICES
        ]
        serializer = ChoicesSerializer(choices, many=True)
        return Response(serializer.data)


class TransmissionChoicesView(views.APIView):
    """GET: Get available transmission choices"""
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Car.TRANSMISSION_CHOICES
        ]
        serializer = ChoicesSerializer(choices, many=True)
        return Response(serializer.data)


class AspirationChoicesView(views.APIView):
    """GET: Get available aspiration choices"""
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Car.ASPIRATION_CHOICES
        ]
        serializer = ChoicesSerializer(choices, many=True)
        return Response(serializer.data)


class AvailabilityChoicesView(views.APIView):
    """GET: Get available availability status choices"""
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        choices = [
            {'value': choice[0], 'label': choice[1]}
            for choice in Car.AVAILABILITY_CHOICES
        ]
        serializer = ChoicesSerializer(choices, many=True)
        return Response(serializer.data)


# ============= Car Image Views =============

class CarImageUploadView(views.APIView):
    """
    POST: Upload image(s) to a car (max 10 total)
    """
    permission_classes = [IsApprovedWorkerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, car_id):
        car = get_object_or_404(Car, id=car_id)
        
        # Check current image count
        current_count = car.images.count()
        if current_count >= 10:
            return Response(
                {"error": "Maximum 10 images allowed per car"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"error": "No image file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get order or auto-increment
        order = request.data.get('order', current_count + 1)
        
        # Create image
        is_primary = current_count == 0  # First image is primary
        
        car_image = CarImage.objects.create(
            car=car,
            image=image_file,
            is_primary=is_primary,
            order=order
        )
        
        serializer = CarImageSerializer(car_image, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CarImageBulkUploadView(views.APIView):
    """
    POST: Upload multiple images at once (up to 10 total)
    """
    permission_classes = [IsApprovedWorkerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, car_id):
        car = get_object_or_404(Car, id=car_id)
        
        # Get all uploaded files
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {"error": "No image files provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check total count doesn't exceed 10
        current_count = car.images.count()
        total_count = current_count + len(images)
        
        if total_count > 10:
            return Response(
                {"error": f"Cannot upload {len(images)} images. Maximum 10 images allowed per car (currently {current_count})"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create images
        created_images = []
        with transaction.atomic():
            for idx, image_file in enumerate(images):
                is_primary = current_count == 0 and idx == 0  # First image is primary
                order = current_count + idx + 1
                
                car_image = CarImage.objects.create(
                    car=car,
                    image=image_file,
                    is_primary=is_primary,
                    order=order
                )
                created_images.append(car_image)
        
        serializer = CarImageSerializer(created_images, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CarImageDetailView(views.APIView):
    """
    PATCH: Update/replace an image
    DELETE: Delete an image
    """
    permission_classes = [IsApprovedWorkerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, car_id, image_id):
        car = get_object_or_404(Car, id=car_id)
        image = get_object_or_404(CarImage, id=image_id, car=car)
        
        # Update image file if provided
        new_image = request.FILES.get('image')
        if new_image:
            # Delete old image file
            if image.image:
                image.image.delete(save=False)
            image.image = new_image
            image.save()
        
        serializer = CarImageSerializer(image, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, car_id, image_id):
        car = get_object_or_404(Car, id=car_id)
        image = get_object_or_404(CarImage, id=image_id, car=car)
        
        # Delete will auto-promote next image if this was primary
        image.delete()
        
        return Response(
            {"message": "Image deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )


class CarImageSetPrimaryView(views.APIView):
    """
    PATCH: Set an image as the primary image
    """
    permission_classes = [IsApprovedWorkerOrAdmin]

    def patch(self, request, car_id, image_id):
        car = get_object_or_404(Car, id=car_id)
        image = get_object_or_404(CarImage, id=image_id, car=car)
        
        # Unset current primary
        CarImage.objects.filter(
            car=car,
            is_primary=True
        ).update(is_primary=False)
        
        # Set new primary
        image.is_primary = True
        image.save()
        
        serializer = CarImageSerializer(image, context={'request': request})
        return Response(serializer.data)


class CarImageReorderView(views.APIView):
    """
    PATCH: Reorder car images
    Body: {"image_orders": [{"id": 1, "order": 1}, {"id": 2, "order": 2}, ...]}
    """
    permission_classes = [IsApprovedWorkerOrAdmin]

    def patch(self, request, car_id):
        car = get_object_or_404(Car, id=car_id)
        
        serializer = ImageReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        image_orders = serializer.validated_data['image_orders']
        
        # Update in transaction
        with transaction.atomic():
            for item in image_orders:
                try:
                    image = CarImage.objects.get(
                        id=item['id'],
                        car=car
                    )
                    image.order = item['order']
                    image.save()
                except CarImage.DoesNotExist:
                    return Response(
                        {"error": f"Image with id {item['id']} not found for this car"},
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        # Return updated images
        images = car.images.all()
        serializer = CarImageSerializer(
            images,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)