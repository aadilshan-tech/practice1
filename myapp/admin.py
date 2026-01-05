from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from .models import VehicleModel, Part, PartStock


# ----------------------------- 
# Simple Part Inline with Stock
# ----------------------------- 
class PartWithStockInline(admin.TabularInline):
    model = Part
    extra = 0
    fields = ('name', 'category', 'condition', 'stock_display', 'stock_buttons')
    readonly_fields = ('stock_display', 'stock_buttons')
    can_delete = True
    
    def stock_display(self, obj):
        """Show current stock quantity with color coding"""
        if not obj.pk:
            return "-"
        
        try:
            stock = obj.stock
            quantity = stock.quantity
            
            if quantity == 0:
                color = '#dc3545'  # Red
                status = 'OUT OF STOCK'
            elif stock.is_low_stock:
                color = '#ffc107'  # Yellow
                status = f'LOW STOCK'
            else:
                color = '#28a745'  # Green
                status = 'IN STOCK'
            
            return format_html(
                '<div class="stock-display" id="stock-display-{}">'
                '<strong style="color: {}; font-size: 18px;" class="stock-quantity">{}</strong><br>'
                '<span style="color: #666; font-size: 12px;" class="stock-status">{}</span>'
                '</div>',
                stock.pk, color, quantity, status
            )
        except PartStock.DoesNotExist:
            return format_html('<span style="color: #dc3545;">No Stock Record</span>')
    
    stock_display.short_description = "Current Stock"
    
    def stock_buttons(self, obj):
        """Add/Remove stock buttons with inline JavaScript"""
        if not obj.pk:
            return "-"
        
        try:
            stock = obj.stock
            disabled = 'disabled' if stock.quantity == 0 else ''
            
            # Include JavaScript only once
            script = ''
            if not hasattr(self, '_script_added'):
                self._script_added = True
                script = '''
                <script>
                function adjustStock(stockId, action) {
                    const button = event.target;
                    const loader = document.getElementById('loader-' + stockId);
                    const decreaseBtn = document.getElementById('decrease-' + stockId);
                    
                    loader.style.display = 'inline';
                    button.disabled = true;
                    if (decreaseBtn) decreaseBtn.disabled = true;
                    
                    fetch('/admin/myapp/vehiclemodel/stock/' + action + '/' + stockId + '/', {
                        method: 'GET',
                        headers: {'X-Requested-With': 'XMLHttpRequest'}
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            const display = document.getElementById('stock-display-' + stockId);
                            const quantityEl = display.querySelector('.stock-quantity');
                            const statusEl = display.querySelector('.stock-status');
                            
                            quantityEl.textContent = data.quantity;
                            quantityEl.style.color = data.color;
                            statusEl.textContent = data.status;
                            
                            quantityEl.style.transition = 'background-color 0.3s';
                            quantityEl.style.backgroundColor = '#90EE90';
                            setTimeout(() => {
                                quantityEl.style.backgroundColor = 'transparent';
                            }, 500);
                            
                            if (decreaseBtn) {
                                decreaseBtn.disabled = data.quantity === 0;
                            }
                            
                            showMessage('✓ Stock: ' + data.quantity, 'success');
                        } else {
                            showMessage('✗ ' + data.message, 'error');
                        }
                    })
                    .catch(error => {
                        showMessage('✗ Error', 'error');
                        console.error('Error:', error);
                    })
                    .finally(() => {
                        loader.style.display = 'none';
                        button.disabled = false;
                        if (decreaseBtn && data && data.quantity > 0) {
                            decreaseBtn.disabled = false;
                        }
                    });
                }
                
                function increaseAllStock() {
                    const vehicleId = document.querySelector('[name="_continue"]').value.match(/\\d+/)?.[0];
                    if (!vehicleId) {
                        const pathParts = window.location.pathname.split('/');
                        const id = pathParts[pathParts.length - 3];
                        if (id && !isNaN(id)) {
                            processIncreaseAll(id);
                        }
                    } else {
                        processIncreaseAll(vehicleId);
                    }
                }
                
                function processIncreaseAll(vehicleId) {
                    const button = document.getElementById('bulk-add-btn');
                    const loader = document.getElementById('bulk-loader');
                    
                    button.disabled = true;
                    loader.style.display = 'inline';
                    
                    fetch('/admin/myapp/vehiclemodel/stock/increase-all/' + vehicleId + '/', {
                        method: 'GET',
                        headers: {'X-Requested-With': 'XMLHttpRequest'}
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Update all stock displays
                            data.updates.forEach(update => {
                                const display = document.getElementById('stock-display-' + update.stock_id);
                                if (display) {
                                    const quantityEl = display.querySelector('.stock-quantity');
                                    const statusEl = display.querySelector('.stock-status');
                                    
                                    quantityEl.textContent = update.quantity;
                                    quantityEl.style.color = update.color;
                                    statusEl.textContent = update.status;
                                    
                                    quantityEl.style.transition = 'background-color 0.3s';
                                    quantityEl.style.backgroundColor = '#90EE90';
                                    setTimeout(() => {
                                        quantityEl.style.backgroundColor = 'transparent';
                                    }, 500);
                                    
                                    // Enable decrease buttons
                                    const decreaseBtn = document.getElementById('decrease-' + update.stock_id);
                                    if (decreaseBtn) {
                                        decreaseBtn.disabled = false;
                                    }
                                }
                            });
                            
                            showMessage('✓ All ' + data.updates.length + ' parts increased', 'success');
                        } else {
                            showMessage('✗ ' + data.message, 'error');
                        }
                    })
                    .catch(error => {
                        showMessage('✗ Error updating stock', 'error');
                        console.error('Error:', error);
                    })
                    .finally(() => {
                        loader.style.display = 'none';
                        button.disabled = false;
                    });
                }
                
                function showMessage(text, type) {
                    const existing = document.getElementById('stock-message');
                    if (existing) existing.remove();
                    
                    const color = type === 'success' ? '#28a745' : '#dc3545';
                    const msg = document.createElement('div');
                    msg.id = 'stock-message';
                    msg.textContent = text;
                    msg.style.cssText = `
                        position: fixed; top: 80px; right: 20px;
                        background: ${color}; color: white;
                        padding: 12px 20px; border-radius: 4px;
                        font-weight: bold; z-index: 9999;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                        animation: slideIn 0.3s ease-out;
                    `;
                    
                    const style = document.createElement('style');
                    style.textContent = `
                        @keyframes slideIn {
                            from { transform: translateX(400px); opacity: 0; }
                            to { transform: translateX(0); opacity: 1; }
                        }
                    `;
                    if (!document.getElementById('stock-style')) {
                        style.id = 'stock-style';
                        document.head.appendChild(style);
                    }
                    
                    document.body.appendChild(msg);
                    setTimeout(() => msg.remove(), 2000);
                }
                
                // Add bulk button when page loads
                document.addEventListener('DOMContentLoaded', function() {
                    const partsInline = document.querySelector('.inline-group');
                    if (partsInline && !document.getElementById('bulk-stock-container')) {
                        const bulkContainer = document.createElement('div');
                        bulkContainer.id = 'bulk-stock-container';
                        bulkContainer.innerHTML = `
                            <style>
                                #bulk-stock-container {
                                    background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%);
                                    padding: 20px;
                                    border-radius: 8px;
                                    margin: 20px 0;
                                    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
                                    text-align: center;
                                }
                                #bulk-add-btn {
                                    background: white;
                                    color: #ff6f00;
                                    padding: 12px 30px;
                                    border: none;
                                    border-radius: 6px;
                                    font-weight: bold;
                                    font-size: 16px;
                                    cursor: pointer;
                                    transition: all 0.3s ease;
                                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                                }
                                #bulk-add-btn:hover {
                                    transform: translateY(-2px);
                                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                                }
                                #bulk-add-btn:active {
                                    transform: translateY(0);
                                }
                                #bulk-add-btn:disabled {
                                    opacity: 0.6;
                                    cursor: not-allowed;
                                }
                                .bulk-description {
                                    color: white;
                                    margin-top: 10px;
                                    font-size: 13px;
                                    opacity: 0.9;
                                }
                            </style>
                            <button type="button" id="bulk-add-btn" onclick="increaseAllStock()">
                                📦 Add +1 to ALL Parts Stock
                            </button>
                            <span id="bulk-loader" style="display:none; margin-left: 10px; font-size: 20px;">⏳</span>
                            <div class="bulk-description">
                                Increase stock quantity by 1 for all parts at once
                            </div>
                        `;
                        partsInline.parentNode.insertBefore(bulkContainer, partsInline);
                    }
                });
                </script>
                '''
            
            return mark_safe(f'''
                {script}
                <style>
                    .stock-btn-add {{
                        background: #28a745;
                        color: white;
                        padding: 8px 16px;
                        border: none;
                        cursor: pointer;
                        border-radius: 4px;
                        font-weight: bold;
                        margin-right: 5px;
                        transition: all 0.2s ease;
                    }}
                    .stock-btn-add:hover {{
                        background: #218838;
                        transform: translateY(-2px);
                        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
                    }}
                    .stock-btn-add:active {{
                        transform: translateY(0);
                    }}
                    .stock-btn-remove {{
                        background: #dc3545;
                        color: white;
                        padding: 8px 16px;
                        border: none;
                        cursor: pointer;
                        border-radius: 4px;
                        font-weight: bold;
                        transition: all 0.2s ease;
                    }}
                    .stock-btn-remove:hover:not(:disabled) {{
                        background: #c82333;
                        transform: translateY(-2px);
                        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
                    }}
                    .stock-btn-remove:active:not(:disabled) {{
                        transform: translateY(0);
                    }}
                    .stock-btn-remove:disabled {{
                        background: #6c757d;
                        cursor: not-allowed;
                        opacity: 0.5;
                    }}
                </style>
                <div style="white-space: nowrap;">
                    <button type="button" 
                        class="stock-btn-add"
                        onclick="adjustStock({stock.pk}, 'increase')">
                        + Add
                    </button>
                    <button type="button" 
                        class="stock-btn-remove"
                        id="decrease-{stock.pk}"
                        onclick="adjustStock({stock.pk}, 'decrease')"
                        {disabled}>
                        − Remove
                    </button>
                    <span id="loader-{stock.pk}" style="display:none; margin-left: 10px;">⏳</span>
                </div>
            ''')
        except PartStock.DoesNotExist:
            return format_html('<span style="color: #999;">Create part first</span>')
    
    stock_buttons.short_description = "Adjust Stock"


# ----------------------------- 
# Vehicle Admin (MAIN VIEW)
# ----------------------------- 
@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_type', 'manufacturer', 'total_parts_count')
    list_filter = ('vehicle_type', 'manufacturer')
    search_fields = ('name', 'manufacturer')
    inlines = [PartWithStockInline]
    
    def total_parts_count(self, obj):
        """Show how many parts this vehicle has"""
        count = obj.parts.count()
        return format_html(
            '<strong style="color: #0066cc;">{} parts</strong>',
            count
        )
    
    total_parts_count.short_description = "Parts"
    
    # Stock adjustment URLs (AJAX endpoints)
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('stock/increase/<int:stock_id>/', self.admin_site.admin_view(self.increase_stock)),
            path('stock/decrease/<int:stock_id>/', self.admin_site.admin_view(self.decrease_stock)),
            path('stock/increase-all/<int:vehicle_id>/', self.admin_site.admin_view(self.increase_all_stock)),
        ]
        return custom + urls
    
    def increase_stock(self, request, stock_id):
        """Add 1 to stock - returns JSON"""
        stock = get_object_or_404(PartStock, pk=stock_id)
        stock.quantity += 1
        stock.save()
        
        # Determine status
        if stock.quantity == 0:
            status = 'OUT OF STOCK'
            color = '#dc3545'
        elif stock.is_low_stock:
            status = 'LOW STOCK'
            color = '#ffc107'
        else:
            status = 'IN STOCK'
            color = '#28a745'
        
        return JsonResponse({
            'success': True,
            'quantity': stock.quantity,
            'status': status,
            'color': color
        })
    
    def decrease_stock(self, request, stock_id):
        """Remove 1 from stock - returns JSON"""
        stock = get_object_or_404(PartStock, pk=stock_id)
        
        if stock.quantity > 0:
            stock.quantity -= 1
            stock.save()
            
            # Determine status
            if stock.quantity == 0:
                status = 'OUT OF STOCK'
                color = '#dc3545'
            elif stock.is_low_stock:
                status = 'LOW STOCK'
                color = '#ffc107'
            else:
                status = 'IN STOCK'
                color = '#28a745'
            
            return JsonResponse({
                'success': True,
                'quantity': stock.quantity,
                'status': status,
                'color': color
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Stock is already 0'
            })
    
    def increase_all_stock(self, request, vehicle_id):
        """Increase stock for all parts of this vehicle by 1"""
        vehicle = get_object_or_404(VehicleModel, pk=vehicle_id)
        parts = vehicle.parts.all()
        
        updates = []
        for part in parts:
            try:
                stock = part.stock
                stock.quantity += 1
                stock.save()
                
                # Determine status
                if stock.quantity == 0:
                    status = 'OUT OF STOCK'
                    color = '#dc3545'
                elif stock.is_low_stock:
                    status = 'LOW STOCK'
                    color = '#ffc107'
                else:
                    status = 'IN STOCK'
                    color = '#28a745'
                
                updates.append({
                    'stock_id': stock.pk,
                    'quantity': stock.quantity,
                    'status': status,
                    'color': color
                })
            except PartStock.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'Updated {len(updates)} parts',
            'updates': updates
        })


# ----------------------------- 
# Optional: Simple Part Admin
# ----------------------------- 
@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_model', 'category', 'condition', 'quick_stock_info')
    list_filter = ('vehicle_model', 'category', 'condition')
    search_fields = ('name', 'vehicle_model__name')
    
    def quick_stock_info(self, obj):
        """Quick stock overview"""
        try:
            stock = obj.stock
            if stock.quantity == 0:
                return format_html('<span style="color: #dc3545;">OUT (0)</span>')
            elif stock.is_low_stock:
                return format_html('<span style="color: #ffc107;">LOW ({})</span>', stock.quantity)
            return format_html('<span style="color: #28a745;">OK ({})</span>', stock.quantity)
        except PartStock.DoesNotExist:
            return '-'
    
    quick_stock_info.short_description = "Stock"