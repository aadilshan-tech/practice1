from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from .models import VehicleModel, Part, PartStock, VehicleStock

print("🔥 Signals module loaded!")

# Predefined parts for each vehicle type
CAR_PARTS = [
    {'name': 'Front Bumper', 'category': 'Body'},
    {'name': 'Rear Bumper', 'category': 'Body'},
    {'name': 'Bonnet', 'category': 'Body'},
    {'name': 'Front Left Door', 'category': 'Body'},
    {'name': 'Front Right Door', 'category': 'Body'},
    {'name': 'Rear Left Door', 'category': 'Body'},
    {'name': 'Rear Right Door', 'category': 'Body'},
    {'name': 'Boot Lid', 'category': 'Body'},
    {'name': 'Front Left Fender', 'category': 'Body'},
    {'name': 'Front Right Fender', 'category': 'Body'},
    {'name': 'Headlight Left', 'category': 'Electrical'},
    {'name': 'Headlight Right', 'category': 'Electrical'},
    {'name': 'Tail Light Left', 'category': 'Electrical'},
    {'name': 'Tail Light Right', 'category': 'Electrical'},
    {'name': 'Side Mirror Left', 'category': 'Body'},
    {'name': 'Side Mirror Right', 'category': 'Body'},
    {'name': 'Windshield', 'category': 'Glass'},
    {'name': 'Rear Windshield', 'category': 'Glass'},
    {'name': 'Front Left Window', 'category': 'Glass'},
    {'name': 'Front Right Window', 'category': 'Glass'},
    {'name': 'Rear Left Window', 'category': 'Glass'},
    {'name': 'Rear Right Window', 'category': 'Glass'},
    {'name': 'Engine', 'category': 'Engine'},
    {'name': 'Gearbox', 'category': 'Transmission'},
    {'name': 'Radiator', 'category': 'Cooling'},
    {'name': 'AC Compressor', 'category': 'AC'},
    {'name': 'Steering Wheel', 'category': 'Interior'},
    {'name': 'Dashboard', 'category': 'Interior'},
    {'name': 'Front Seats', 'category': 'Interior'},
    {'name': 'Rear Seats', 'category': 'Interior'},
    {'name': 'Alloy Wheels (Set of 4)', 'category': 'Wheels'},
    {'name': 'Spare Wheel', 'category': 'Wheels'},
    {'name': 'Battery', 'category': 'Electrical'},
    {'name': 'Alternator', 'category': 'Electrical'},
    {'name': 'Starter Motor', 'category': 'Electrical'},
    {'name': 'Wiper Motor', 'category': 'Electrical'},
    {'name': 'Fuel Pump', 'category': 'Fuel System'},
    {'name': 'Exhaust System', 'category': 'Exhaust'},
    {'name': 'Catalytic Converter', 'category': 'Exhaust'},
    {'name': 'Suspension (Front)', 'category': 'Suspension'},
    {'name': 'Suspension (Rear)', 'category': 'Suspension'},
]

BIKE_PARTS = [
    {'name': 'Fuel Tank', 'category': 'Body'},
    {'name': 'Front Fender', 'category': 'Body'},
    {'name': 'Rear Fender', 'category': 'Body'},
    {'name': 'Side Panel Left', 'category': 'Body'},
    {'name': 'Side Panel Right', 'category': 'Body'},
    {'name': 'Tail Panel', 'category': 'Body'},
    {'name': 'Headlight', 'category': 'Electrical'},
    {'name': 'Tail Light', 'category': 'Electrical'},
    {'name': 'Indicator Lights (Set)', 'category': 'Electrical'},
    {'name': 'Speedometer', 'category': 'Instruments'},
    {'name': 'Handlebar', 'category': 'Controls'},
    {'name': 'Handle Grips', 'category': 'Controls'},
    {'name': 'Clutch Lever', 'category': 'Controls'},
    {'name': 'Brake Lever', 'category': 'Controls'},
    {'name': 'Throttle Assembly', 'category': 'Controls'},
    {'name': 'Front Wheel', 'category': 'Wheels'},
    {'name': 'Rear Wheel', 'category': 'Wheels'},
    {'name': 'Front Tyre', 'category': 'Tyres'},
    {'name': 'Rear Tyre', 'category': 'Tyres'},
    {'name': 'Front Brake Disc', 'category': 'Brakes'},
    {'name': 'Rear Brake Disc', 'category': 'Brakes'},
    {'name': 'Front Brake Caliper', 'category': 'Brakes'},
    {'name': 'Rear Brake Caliper', 'category': 'Brakes'},
    {'name': 'Engine', 'category': 'Engine'},
    {'name': 'Carburetor', 'category': 'Fuel System'},
    {'name': 'Exhaust Pipe', 'category': 'Exhaust'},
    {'name': 'Silencer', 'category': 'Exhaust'},
    {'name': 'Chain', 'category': 'Drive Train'},
    {'name': 'Sprocket Set', 'category': 'Drive Train'},
    {'name': 'Battery', 'category': 'Electrical'},
    {'name': 'Spark Plug', 'category': 'Electrical'},
    {'name': 'CDI Unit', 'category': 'Electrical'},
    {'name': 'Wiring Harness', 'category': 'Electrical'},
    {'name': 'Front Fork', 'category': 'Suspension'},
    {'name': 'Rear Shock Absorber', 'category': 'Suspension'},
    {'name': 'Seat', 'category': 'Body'},
    {'name': 'Footrest Left', 'category': 'Body'},
    {'name': 'Footrest Right', 'category': 'Body'},
    {'name': 'Stand (Main)', 'category': 'Body'},
    {'name': 'Stand (Side)', 'category': 'Body'},
]


@receiver(post_save, sender=VehicleModel)
def create_default_parts_for_vehicle(sender, instance, created, **kwargs):
    """Automatically create all standard parts when a new vehicle model is added"""
    if created:
        print(f"✅ Creating parts for NEW vehicle: {instance.name}")
        
        parts_list = CAR_PARTS if instance.vehicle_type == 'car' else BIKE_PARTS
        
        parts_created = 0
        for part_data in parts_list:
            try:
                base_slug = slugify(part_data['name'])
                slug = base_slug
                counter = 1
                
                while Part.objects.filter(vehicle_model=instance, slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                Part.objects.create(
                    vehicle_model=instance,
                    name=part_data['name'],
                    category=part_data['category'],
                    slug=slug,
                    condition='Used - Good'
                )
                parts_created += 1
                
            except Exception as e:
                print(f"❌ Error creating part {part_data['name']}: {e}")
        
        print(f"🎉 Successfully created {parts_created} parts for {instance.name}!")


@receiver(post_save, sender=Part)
def create_part_stock(sender, instance, created, **kwargs):
    """Automatically create PartStock when a new Part is created"""
    if created:
        stock, stock_created = PartStock.objects.get_or_create(
            part=instance,
            defaults={'quantity': 0}
        )
        if stock_created:
            print(f"📦 Created stock entry for: {instance.name}")


@receiver(post_save, sender=VehicleStock)
def increment_parts_stock_on_processing(sender, instance, created, raw, **kwargs):
    """
    Increment stock for ALL parts when vehicle is marked as processed
    FIXED: Only increment once when is_processed changes from False to True
    """
    if raw:  # Don't run during fixtures/loaddata
        return
        
    if instance.is_processed:
        # Use a flag to prevent double processing
        if not hasattr(instance, '_stock_incremented'):
            # Check if this is a new instance or status just changed
            should_increment = False
            
            if created:
                # New vehicle stock created as processed
                should_increment = True
                print(f"📦 NEW Vehicle added as processed: {instance.chassis_number}")
            else:
                # Existing vehicle - check if status just changed
                try:
                    # Get the old instance from database
                    old_instance = VehicleStock.objects.get(pk=instance.pk)
                    # Check if is_processed changed from False to True
                    if not old_instance.is_processed and instance.is_processed:
                        should_increment = True
                        print(f"📦 Vehicle marked as processed: {instance.chassis_number}")
                except VehicleStock.DoesNotExist:
                    pass
            
            if should_increment:
                parts = instance.vehicle_model.parts.all()
                updated = 0
                
                for part in parts:
                    try:
                        stock, _ = PartStock.objects.get_or_create(
                            part=part,
                            defaults={'quantity': 0}
                        )
                        stock.quantity += 1
                        stock.last_restocked = timezone.now()
                        stock.save()
                        updated += 1
                    except Exception as e:
                        print(f"❌ Error updating stock for {part.name}: {e}")
                
                print(f"✅ Incremented stock for {updated} parts!")
                
                # Set the flag to prevent double increment
                instance._stock_incremented = True
                
                # Update processed date if not set
                if not instance.processed_date:
                    VehicleStock.objects.filter(pk=instance.pk).update(
                        processed_date=timezone.now()
                    )

print("✅ All signal handlers registered!")