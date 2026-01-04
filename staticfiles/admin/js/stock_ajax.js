(function($) {
    $(document).ready(function() {
        // Handle stock increase/decrease buttons
        $(document).on('click', '.stock-btn', function(e) {
            e.preventDefault();
            
            const button = $(this);
            const stockId = button.data('stock-id');
            const isIncrease = button.hasClass('stock-increase');
            const action = isIncrease ? 'increase' : 'decrease';
            
            // Show loader
            const loader = button.siblings('.stock-loader');
            loader.show();
            button.prop('disabled', true);
            
            // Make AJAX request
            $.ajax({
                url: `/admin/myapp/vehiclemodel/stock/${action}/${stockId}/`,
                method: 'GET',
                success: function(response) {
                    if (response.success) {
                        // Find the stock display for this stock ID
                        const stockDisplay = $(`.stock-display[data-stock-id="${stockId}"]`);
                        
                        // Update quantity with animation
                        stockDisplay.find('.stock-quantity')
                            .text(response.quantity)
                            .css('color', response.color)
                            .effect('highlight', {color: '#90EE90'}, 500);
                        
                        // Update status
                        stockDisplay.find('.stock-status').text(response.status);
                        
                        // Enable/disable decrease button based on quantity
                        const decreaseBtn = button.siblings('.stock-decrease');
                        if (response.quantity === 0) {
                            decreaseBtn.prop('disabled', true);
                        } else {
                            decreaseBtn.prop('disabled', false);
                        }
                        
                        // Show brief success message
                        showMessage('✓ Updated', 'success');
                    } else {
                        showMessage(response.message, 'error');
                    }
                },
                error: function() {
                    showMessage('Error updating stock', 'error');
                },
                complete: function() {
                    loader.hide();
                    button.prop('disabled', false);
                }
            });
        });
        
        // Show temporary message
        function showMessage(text, type) {
            const color = type === 'success' ? '#28a745' : '#dc3545';
            const msg = $('<div>')
                .text(text)
                .css({
                    position: 'fixed',
                    top: '80px',
                    right: '20px',
                    background: color,
                    color: 'white',
                    padding: '12px 20px',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    zIndex: 9999,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                })
                .appendTo('body')
                .fadeIn(200)
                .delay(1500)
                .fadeOut(300, function() {
                    $(this).remove();
                });
        }
    });
})(django.jQuery);
