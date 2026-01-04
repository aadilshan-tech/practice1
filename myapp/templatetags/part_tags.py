from django import template
from django.templatetags.static import static

register = template.Library()

# ============================================================================
# LOCAL PART IMAGES - Using your own downloaded isolated part photos
# Store images in: myapp/static/images/parts/
# ============================================================================

DEFAULT_PART_IMAGES = {
    
    # ========== AC (1 part) ==========
    'ac compressor': 'images/parts/ac-compressor.jpg',
    
    # ========== BODY PARTS (13 parts) ==========
    'bonnet': 'images/parts/bonnet.jpg',
    'boot lid': 'images/parts/boot-lid.jpg',
    
    'front bumper': 'images/parts/bumper-front.jpg',
    'rear bumper': 'images/parts/bumper-rear.jpg',  # Or use same as front
    
    'front left door': 'images/parts/door.jpg',
    'front right door': 'images/parts/door.jpg',  # Same image
    'rear left door': 'images/parts/door.jpg',  # Same image
    'rear right door': 'images/parts/door.jpg',  # Same image
    
    'front left fender': 'images/parts/fender.jpg',
    'front right fender': 'images/parts/fender.jpg',  # Same image
    
    'side mirror left': 'images/parts/side-mirror.jpg',
    'side mirror right': 'images/parts/side-mirror.jpg',  # Same image
    
    # ========== COOLING (1 part) ==========
    'radiator': 'images/parts/radiator.jpg',  # Like your example!
    
    # ========== ELECTRICAL PARTS (9 parts) ==========
    'alternator': 'images/parts/alternator.jpg',
    'battery': 'images/parts/battery.jpg',
    
    'headlight left': 'images/parts/headlight.jpg',
    'headlight right': 'images/parts/headlight.jpg',  # Same image
    
    'tail light left': 'images/parts/taillight.jpg',
    'tail light right': 'images/parts/taillight.jpg',  # Same image
    
    'starter motor': 'images/parts/starter-motor.jpg',
    'wiper motor': 'images/parts/wiper-motor.jpg',
    
    # ========== ENGINE (1 part) ==========
    'engine': 'images/parts/engine.jpg',
    
    # ========== EXHAUST (2 parts) ==========
    'catalytic converter': 'images/parts/catalytic-converter.jpg',
    'exhaust system': 'images/parts/exhaust-system.jpg',
    
    # ========== FUEL SYSTEM (1 part) ==========
    'fuel pump': 'images/parts/fuel-pump.jpg',
    
    # ========== GLASS (6 parts) ==========
    'windshield': 'images/parts/windshield.jpg',
    'rear windshield': 'images/parts/rear-windshield.jpg',
    
    'front left window': 'images/parts/window.jpg',
    'front right window': 'images/parts/window.jpg',  # Same image
    'rear left window': 'images/parts/window.jpg',  # Same image
    'rear right window': 'images/parts/window.jpg',  # Same image
    
    # ========== INTERIOR (4 parts) ==========
    'dashboard': 'images/parts/dashboard.jpg',
    'steering wheel': 'images/parts/steering-wheel.jpg',
    'front seats': 'images/parts/car-seat.jpg',
    'rear seats': 'images/parts/car-seat.jpg',  # Same image
    
    # ========== SUSPENSION (2 parts) ==========
    'suspension (front)': 'images/parts/suspension.jpg',
    'suspension (rear)': 'images/parts/suspension.jpg',  # Same image
    
    # ========== TRANSMISSION (1 part) ==========
    'gearbox': 'images/parts/gearbox.jpg',
    
    # ========== WHEELS (2 parts) ==========
    'alloy wheels (set of 4)': 'images/parts/alloy-wheel.jpg',
    'spare wheel': 'images/parts/alloy-wheel.jpg',  # Same image
    
    # ========== BIKE PARTS ==========
    'fuel tank': 'images/parts/bike-fuel-tank.jpg',
    'front fender': 'images/parts/bike-fender.jpg',
    'rear fender': 'images/parts/bike-fender.jpg',
    'side panel left': 'images/parts/bike-side-panel.jpg',
    'side panel right': 'images/parts/bike-side-panel.jpg',
    'tail panel': 'images/parts/bike-tail-panel.jpg',
    'seat': 'images/parts/bike-seat.jpg',
    'footrest left': 'images/parts/bike-footrest.jpg',
    'footrest right': 'images/parts/bike-footrest.jpg',
    'stand (main)': 'images/parts/bike-stand.jpg',
    'stand (side)': 'images/parts/bike-stand.jpg',
    'headlight': 'images/parts/bike-headlight.jpg',
    'tail light': 'images/parts/bike-taillight.jpg',
    'indicator lights (set)': 'images/parts/bike-indicator.jpg',
    'spark plug': 'images/parts/spark-plug.jpg',
    'cdi unit': 'images/parts/cdi-unit.jpg',
    'wiring harness': 'images/parts/wiring-harness.jpg',
    'speedometer': 'images/parts/speedometer.jpg',
    'handlebar': 'images/parts/handlebar.jpg',
    'handle grips': 'images/parts/handle-grips.jpg',
    'clutch lever': 'images/parts/clutch-lever.jpg',
    'brake lever': 'images/parts/brake-lever.jpg',
    'throttle assembly': 'images/parts/throttle.jpg',
    'front wheel': 'images/parts/bike-wheel.jpg',
    'rear wheel': 'images/parts/bike-wheel.jpg',
    'front tyre': 'images/parts/bike-tyre.jpg',
    'rear tyre': 'images/parts/bike-tyre.jpg',
    'front brake disc': 'images/parts/brake-disc.jpg',
    'rear brake disc': 'images/parts/brake-disc.jpg',
    'front brake caliper': 'images/parts/brake-caliper.jpg',
    'rear brake caliper': 'images/parts/brake-caliper.jpg',
    'carburetor': 'images/parts/carburetor.jpg',
    'exhaust pipe': 'images/parts/exhaust-pipe.jpg',
    'silencer': 'images/parts/silencer.jpg',
    'chain': 'images/parts/bike-chain.jpg',
    'sprocket set': 'images/parts/sprocket.jpg',
    'front fork': 'images/parts/front-fork.jpg',
    'rear shock absorber': 'images/parts/shock-absorber.jpg',
}


def get_default_part_image(part_name_or_category):
    """Get default image URL based on part name or category"""
    search_text = part_name_or_category.lower().strip()
    
    # Try exact match
    if search_text in DEFAULT_PART_IMAGES:
        return static(DEFAULT_PART_IMAGES[search_text])
    
    # Try partial match
    for keyword, image_path in DEFAULT_PART_IMAGES.items():
        if keyword in search_text or search_text in keyword:
            return static(image_path)
    
    # Default fallback - placeholder
    return static('images/parts/placeholder.jpg')


@register.simple_tag
def part_default_image(part):
    """Get default image URL for a part"""
    image_url = get_default_part_image(part.name)
    
    # If fallback, try category
    if 'placeholder' in image_url and hasattr(part, 'category'):
        category_image = get_default_part_image(part.category)
        if 'placeholder' not in category_image:
            return category_image
    
    return image_url


@register.filter
def has_image(obj):
    """Check if object has an uploaded image"""
    return bool(obj.image and hasattr(obj.image, 'url'))


# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================
"""
FOLDER STRUCTURE:
myapp/
├── static/
│   └── images/
│       └── parts/
│           ├── ac-compressor.jpg
│           ├── alternator.jpg
│           ├── battery.jpg
│           ├── bonnet.jpg
│           ├── boot-lid.jpg
│           ├── bumper-front.jpg
│           ├── door.jpg
│           ├── fender.jpg
│           ├── radiator.jpg  ← Like your example!
│           ├── headlight.jpg
│           ├── taillight.jpg
│           ├── engine.jpg
│           ├── gearbox.jpg
│           └── placeholder.jpg  ← Fallback image
│           ... (25-30 total images)

STEPS TO IMPLEMENT:
1. Create folder: myapp/static/images/parts/
2. Download isolated part photos (see sources below)
3. Name them exactly as shown above
4. Run: python manage.py collectstatic
5. Replace your part_tags.py with this code
6. Restart Django server

IMAGES YOU NEED (25-30 total):
✓ ac-compressor.jpg
✓ alternator.jpg
✓ battery.jpg
✓ bonnet.jpg
✓ boot-lid.jpg
✓ bumper-front.jpg (can use for rear too)
✓ door.jpg (use for all 4 doors)
✓ fender.jpg (use for both sides)
✓ side-mirror.jpg (use for both sides)
✓ radiator.jpg
✓ headlight.jpg (use for both)
✓ taillight.jpg (use for both)
✓ starter-motor.jpg
✓ wiper-motor.jpg
✓ engine.jpg
✓ catalytic-converter.jpg
✓ exhaust-system.jpg
✓ fuel-pump.jpg
✓ windshield.jpg
✓ rear-windshield.jpg
✓ window.jpg (use for all 4)
✓ dashboard.jpg
✓ steering-wheel.jpg
✓ car-seat.jpg (use for front & rear)
✓ suspension.jpg (use for front & rear)
✓ gearbox.jpg
✓ alloy-wheel.jpg (use for both)
✓ placeholder.jpg (fallback)

WHERE TO DOWNLOAD (Best Sources):
1. Pixabay.com - Search "car [part name]"
2. Pexels.com - Filter by "isolated" or "white background"
3. AliExpress.com - Save product images (great quality!)
4. eBay.com - Seller product photos
5. Freepik.com - Premium quality (free tier available)
"""