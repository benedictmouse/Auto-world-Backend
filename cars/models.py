from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Car categories like SUV, Sedan, Truck, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Car(models.Model):
    SELLER_TYPE_CHOICES = [
        ('private', 'Private Seller'),
        ('dealer', 'Dealer'),
        ('verified_dealer', 'Verified Dealer'),
    ]

    DRIVE_CHOICES = [
        ('2wd', '2WD'),
        ('4wd', '4WD'),
        ('awd', 'AWD'),
        ('fwd', 'FWD'),
        ('rwd', 'RWD'),
    ]

    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
        ('plug_in_hybrid', 'Plug-in Hybrid'),
    ]

    TRANSMISSION_CHOICES = [
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('cvt', 'CVT'),
        ('semi_automatic', 'Semi-Automatic'),
    ]

    ASPIRATION_CHOICES = [
        ('naturally_aspirated', 'Naturally Aspirated'),
        ('turbo', 'Turbo'),
        ('twin_turbo', 'Twin Turbo'),
        ('supercharged', 'Supercharged'),
    ]

    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
        ('reserved', 'Reserved'),
    ]

    # Basic Information
    title = models.CharField(max_length=255, help_text="e.g., Toyota Land Cruiser V8")
    description = models.TextField()
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Price in KES"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='cars'
    )
    
    # Seller Information
    seller_type = models.CharField(
        max_length=20,
        choices=SELLER_TYPE_CHOICES,
        default='private'
    )
    condition_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text="Rating out of 5.0",
        null=True,
        blank=True
    )
    
    # Car Details
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        help_text="Manufacturing year"
    )
    location = models.CharField(
        max_length=255,
        help_text="e.g., Nairobi, Kenya"
    )
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    
    # Technical Specifications
    drive = models.CharField(
        max_length=10,
        choices=DRIVE_CHOICES,
        help_text="Drive type"
    )
    mileage = models.PositiveIntegerField(
        help_text="Mileage in KM"
    )
    engine_size = models.PositiveIntegerField(
        help_text="Engine size in CC"
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_TYPE_CHOICES
    )
    horse_power = models.PositiveIntegerField(
        help_text="Engine power in HP",
        null=True,
        blank=True
    )
    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES
    )
    torque = models.PositiveIntegerField(
        help_text="Torque in Nm",
        null=True,
        blank=True
    )
    aspiration = models.CharField(
        max_length=30,
        choices=ASPIRATION_CHOICES,
        null=True,
        blank=True
    )
    acceleration = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        help_text="0-100 Kph in seconds",
        null=True,
        blank=True
    )
    
    # Timestamps and User
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cars'
    )

    class Meta:
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.year})"

    @property
    def primary_image(self):
        """Get the primary image for this car"""
        return self.images.filter(is_primary=True).first()

    @property
    def image_count(self):
        """Get total number of images"""
        return self.images.count()

    @property
    def formatted_price(self):
        """Return formatted price with KSh"""
        return f"KSh {self.price:,.0f}"

    @property
    def formatted_mileage(self):
        """Return formatted mileage"""
        return f"{self.mileage:,} KM"

    @property
    def formatted_engine_size(self):
        """Return formatted engine size"""
        return f"{self.engine_size} CC"

    @property
    def formatted_horse_power(self):
        """Return formatted horse power"""
        if self.horse_power:
            return f"{self.horse_power} Hp"
        return None

    @property
    def formatted_torque(self):
        """Return formatted torque"""
        if self.torque:
            return f"{self.torque} Nm"
        return None

    @property
    def formatted_acceleration(self):
        """Return formatted acceleration"""
        if self.acceleration:
            return f"{self.acceleration} Secs (0-100 Kph)"
        return None

    @property
    def formatted_condition_score(self):
        """Return formatted condition score"""
        if self.condition_score:
            return f"{self.condition_score}/5"
        return None


class CarImage(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='cars/%Y/%m/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Car Image'
        verbose_name_plural = 'Car Images'
        ordering = ['-is_primary', 'order', 'uploaded_at']
        unique_together = ['car', 'order']

    def __str__(self):
        return f"{self.car.title} - Image {self.order}"

    def save(self, *args, **kwargs):
        # If this is the first image, make it primary
        if not self.pk and not self.car.images.exists():
            self.is_primary = True
            self.order = 1
        
        # If setting this as primary, unset other primary images
        if self.is_primary:
            CarImage.objects.filter(
                car=self.car,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # Enforce maximum 10 images per car
        if not self.pk:  # New image
            existing_count = self.car.images.count()
            if existing_count >= 10:
                raise ValueError(f"Cannot add more than 10 images per car. Current count: {existing_count}")
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # If deleting primary image, promote next image
        if self.is_primary:
            next_image = self.car.images.exclude(pk=self.pk).first()
            if next_image:
                next_image.is_primary = True
                next_image.save()
        
        super().delete(*args, **kwargs)

    def clean(self):
        """Validate that we don't exceed 10 images"""
        if not self.pk:  # Only for new images
            existing_count = CarImage.objects.filter(car=self.car).count()
            if existing_count >= 10:
                from django.core.exceptions import ValidationError
                raise ValidationError("A car can have a maximum of 10 images.")