from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator


class VehicleModel(models.Model):
    """Represents a specific car or bike model"""
    VEHICLE_TYPE_CHOICES = [
        ('car', 'Car'),
        ('bike', 'Bike'),
    ]
    
    name = models.CharField(max_length=200)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    manufacturer = models.CharField(max_length=100)
    year_from = models.PositiveIntegerField()
    year_to = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(max_length=250, unique=True)
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['vehicle_type', 'manufacturer', 'name']
        verbose_name = 'Vehicle Model'
        verbose_name_plural = 'Vehicle Models'
    
    def __str__(self):
        return f"{self.manufacturer} {self.name} ({self.vehicle_type.upper()})"
    
    def get_absolute_url(self):
        return reverse('myapp:parts_list', kwargs={'vehicle_slug': self.slug})


class Part(models.Model):
    """Represents a specific part type for a vehicle model"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, related_name='parts')
    name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=50, default='Used - Good')
    image = models.ImageField(upload_to='parts/', null=True, blank=True)
    slug = models.SlugField(max_length=250)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = [['vehicle_model', 'slug']]
        verbose_name = 'Part'
        verbose_name_plural = 'Parts'
        indexes = [
            models.Index(fields=['vehicle_model', 'category']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.vehicle_model}"
    
    def get_absolute_url(self):
        return reverse('myapp:part_detail', kwargs={
            'vehicle_slug': self.vehicle_model.slug,
            'part_slug': self.slug
        })
    
    def get_stock_quantity(self):
        """
        Safely get stock quantity - returns 0 if no stock entry exists
        This method GUARANTEES a numeric result
        """
        try:
            # Use hasattr to check if stock relationship exists
            if hasattr(self, 'stock') and self.stock:
                return self.stock.quantity if self.stock.quantity is not None else 0
            return 0
        except PartStock.DoesNotExist:
            return 0
    
    def is_in_stock(self):
        """
        Check if part is in stock - returns Boolean
        This is the AUTHORITATIVE method for stock checks
        """
        return self.get_stock_quantity() > 0
    
    def get_stock_status(self):
        """
        Returns a dict with detailed stock information
        """
        try:
            if hasattr(self, 'stock') and self.stock:
                stock = self.stock
                return {
                    'available': stock.quantity > 0,
                    'quantity': stock.quantity,
                    'is_low': stock.is_low_stock,
                }
            return {'available': False, 'quantity': 0, 'is_low': False}
        except PartStock.DoesNotExist:
            return {'available': False, 'quantity': 0, 'is_low': False}


class PartStock(models.Model):
    """
    Tracks stock quantity for each part
    CRITICAL: This MUST be OneToOneField to ensure one stock entry per part
    """
    part = models.OneToOneField(
        Part, 
        on_delete=models.CASCADE, 
        related_name='stock',
        primary_key=True  # Enforces one-to-one at database level
    )
    quantity = models.PositiveIntegerField(
        default=0, 
        validators=[MinValueValidator(0)]
    )
    low_stock_threshold = models.PositiveIntegerField(default=2)
    last_restocked = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Part Stock'
        verbose_name_plural = 'Part Stocks'
    
    def __str__(self):
        return f"{self.part.name} - Stock: {self.quantity}"
    
    @property
    def is_in_stock(self):
        """Returns True if quantity > 0"""
        return self.quantity > 0
    
    @property
    def is_low_stock(self):
        """Returns True if in stock but below threshold"""
        return 0 < self.quantity <= self.low_stock_threshold
    
    def save(self, *args, **kwargs):
        """Override save to ensure quantity is never None"""
        if self.quantity is None:
            self.quantity = 0
        super().save(*args, **kwargs)


class VehicleStock(models.Model):
    """Tracks when complete vehicles are added to inventory"""
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, related_name='vehicle_stocks')
    chassis_number = models.CharField(max_length=100, unique=True)
    registration_number = models.CharField(max_length=50, blank=True)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50, blank=True)
    odometer_reading = models.PositiveIntegerField(null=True, blank=True)
    condition_notes = models.TextField(blank=True)
    acquired_date = models.DateField()
    acquired_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    processed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-acquired_date']
        verbose_name = 'Vehicle Stock'
        verbose_name_plural = 'Vehicle Stocks'
    
    def __str__(self):
        return f"{self.vehicle_model} - {self.chassis_number} ({self.year})"