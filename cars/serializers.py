from rest_framework import serializers
from .models import Category, Car, CarImage
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    car_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'car_count']
        read_only_fields = ['id', 'created_at']

    def get_car_count(self, obj):
        return obj.cars.count()


class CarImageSerializer(serializers.ModelSerializer):
    # Use SerializerMethodField to get the full URL
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarImage
        fields = ['id', 'image_url', 'image', 'is_primary', 'order', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def get_image_url(self, obj):
        """Get the full URL for the image"""
        request = self.context.get('request')
        if obj.image:
            # Get the image URL
            image_url = obj.image.url
            # Build absolute URL if request context is available
            if request is not None:
                return request.build_absolute_uri(image_url)
            return image_url
        return None

    def validate(self, attrs):
        # Check max 10 images per car
        if not self.instance:  # Creating new image
            car = attrs.get('car') or self.context.get('car')
            if car and car.images.count() >= 10:
                raise serializers.ValidationError(
                    "Maximum 10 images allowed per car"
                )
        return attrs


class CarListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = CarImageSerializer(many=True, read_only=True)  # IMPORTANT: Include images
    primary_image = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    image_count = serializers.SerializerMethodField()
    
    # Formatted fields
    formatted_price = serializers.SerializerMethodField()
    formatted_mileage = serializers.SerializerMethodField()
    seller_type_display = serializers.CharField(source='get_seller_type_display', read_only=True)
    availability_display = serializers.CharField(source='get_availability_display', read_only=True)

    class Meta:
        model = Car
        fields = [
            'id', 'title', 'description', 'price', 'formatted_price', 'category', 'category_name',
            'seller_type', 'seller_type_display', 'condition_score', 
            'year', 'location', 'availability',
            'availability_display', 'mileage', 'formatted_mileage', 'fuel_type',
            'transmission', 'drive', 'images', 'primary_image', 'image_count', 'created_by_name',
            'created_at', 'updated_at'
        ]

    def get_primary_image(self, obj):
        primary = obj.primary_image
        if primary:
            serializer = CarImageSerializer(primary, context=self.context)
            return serializer.data
        return None
    
    def get_image_count(self, obj):
        return obj.images.count()
    
    def get_formatted_price(self, obj):
        return f"KSh {obj.price:,.0f}"
    
    def get_formatted_mileage(self, obj):
        return f"{obj.mileage:,} KM"


class CarDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = CarImageSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    
    # Formatted fields
    formatted_price = serializers.SerializerMethodField()
    formatted_mileage = serializers.SerializerMethodField()
    formatted_engine_size = serializers.SerializerMethodField()
    formatted_horse_power = serializers.SerializerMethodField()
    formatted_torque = serializers.SerializerMethodField()
    formatted_acceleration = serializers.SerializerMethodField()
    formatted_condition_score = serializers.SerializerMethodField()
    
    # Display names for choices
    seller_type_display = serializers.CharField(source='get_seller_type_display', read_only=True)
    drive_display = serializers.CharField(source='get_drive_display', read_only=True)
    fuel_type_display = serializers.CharField(source='get_fuel_type_display', read_only=True)
    transmission_display = serializers.CharField(source='get_transmission_display', read_only=True)
    aspiration_display = serializers.CharField(source='get_aspiration_display', read_only=True)
    availability_display = serializers.CharField(source='get_availability_display', read_only=True)

    class Meta:
        model = Car
        fields = [
            'id', 'title', 'description', 'price', 'formatted_price', 
            'category', 'category_name', 'seller_type', 'seller_type_display',
            'condition_score', 'formatted_condition_score', 'year', 'location',
            'availability', 'availability_display', 'drive', 'drive_display',
            'mileage', 'formatted_mileage', 'engine_size', 'formatted_engine_size',
            'fuel_type', 'fuel_type_display', 'horse_power', 'formatted_horse_power',
            'transmission', 'transmission_display', 'torque', 'formatted_torque',
            'aspiration', 'aspiration_display', 'acceleration', 'formatted_acceleration',
            'images', 'created_by', 'created_by_name', 'created_by_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_formatted_price(self, obj):
        return f"KSh {obj.price:,.0f}"
    
    def get_formatted_mileage(self, obj):
        return f"{obj.mileage:,} KM"
    
    def get_formatted_engine_size(self, obj):
        return f"{obj.engine_size} CC"
    
    def get_formatted_horse_power(self, obj):
        if obj.horse_power:
            return f"{obj.horse_power} Hp"
        return None
    
    def get_formatted_torque(self, obj):
        if obj.torque:
            return f"{obj.torque} Nm"
        return None
    
    def get_formatted_acceleration(self, obj):
        if obj.acceleration:
            return f"{obj.acceleration} Secs (0-100 Kph)"
        return None
    
    def get_formatted_condition_score(self, obj):
        if obj.condition_score:
            return f"{obj.condition_score}/5"
        return None


class CarCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            'id', 'title', 'description', 'price', 'category', 'seller_type',
            'condition_score', 'year', 'location', 'availability', 'drive',
            'mileage', 'engine_size', 'fuel_type', 'horse_power', 'transmission',
            'torque', 'aspiration', 'acceleration'
        ]
        read_only_fields = ['id']

    def validate_category(self, value):
        if not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid category")
        return value
    
    def validate_price(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError("Price cannot be negative")
        return value
    
    def validate_year(self, value):
        from datetime import datetime
        current_year = datetime.now().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Year must be between 1900 and {current_year + 1}"
            )
        return value
    
    def validate_mileage(self, value):
        if value < 0:
            raise serializers.ValidationError("Mileage cannot be negative")
        return value
    
    def validate_engine_size(self, value):
        if value < 0:
            raise serializers.ValidationError("Engine size cannot be negative")
        return value
    
    def validate_condition_score(self, value):
        if value is not None and (value < Decimal('0') or value > Decimal('5')):
            raise serializers.ValidationError("Condition score must be between 0 and 5")
        return value
    
    def validate_horse_power(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Horse power cannot be negative")
        return value
    
    def validate_torque(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Torque cannot be negative")
        return value
    
    def validate_acceleration(self, value):
        if value is not None and value < Decimal('0'):
            raise serializers.ValidationError("Acceleration cannot be negative")
        return value


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['image', 'order']

    def validate(self, attrs):
        # Validate file size (max 5MB)
        image = attrs.get('image')
        if image and image.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                {"image": "Image file size cannot exceed 5MB"}
            )
        return attrs


class ImageReorderSerializer(serializers.Serializer):
    image_orders = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        help_text="List of {'id': image_id, 'order': new_order}"
    )

    def validate_image_orders(self, value):
        if not value:
            raise serializers.ValidationError("image_orders cannot be empty")
        
        # Validate structure
        for item in value:
            if 'id' not in item or 'order' not in item:
                raise serializers.ValidationError(
                    "Each item must have 'id' and 'order' keys"
                )
        
        return value


class ChoicesSerializer(serializers.Serializer):
    """Serializer to return available choices for dropdowns"""
    value = serializers.CharField()
    label = serializers.CharField()


class CarFiltersSerializer(serializers.Serializer):
    """Serializer for car filtering options"""
    min_price = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        required=False,
        min_value=Decimal('0')
    )
    max_price = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        required=False,
        min_value=Decimal('0')
    )
    min_year = serializers.IntegerField(required=False, min_value=1900)
    max_year = serializers.IntegerField(required=False, max_value=2030)
    category = serializers.IntegerField(required=False)
    seller_type = serializers.ChoiceField(choices=Car.SELLER_TYPE_CHOICES, required=False)
    fuel_type = serializers.ChoiceField(choices=Car.FUEL_TYPE_CHOICES, required=False)
    transmission = serializers.ChoiceField(choices=Car.TRANSMISSION_CHOICES, required=False)
    drive = serializers.ChoiceField(choices=Car.DRIVE_CHOICES, required=False)
    availability = serializers.ChoiceField(choices=Car.AVAILABILITY_CHOICES, required=False)
    location = serializers.CharField(required=False, max_length=255)
    min_mileage = serializers.IntegerField(required=False, min_value=0)
    max_mileage = serializers.IntegerField(required=False, min_value=0)