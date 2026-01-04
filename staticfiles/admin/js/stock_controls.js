// Stock Control Buttons for Django Admin
(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initStockControls);
    } else {
        initStockControls();
    }

    function initStockControls() {
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');

        // Add event listeners to all stock control buttons
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('stock-increase')) {
                e.preventDefault();
                const stockId = e.target.dataset.id;
                updateStock(stockId, 'increase', e.target, csrftoken);
            } else if (e.target.classList.contains('stock-decrease')) {
                e.preventDefault();
                const stockId = e.target.dataset.id;
                updateStock(stockId, 'decrease', e.target, csrftoken);
            }
        });
    }

    function updateStock(stockId, action, button, csrftoken) {
        // Disable button during request
        button.disabled = true;
        button.style.opacity = '0.5';

        // Get the quantity display element (sibling span)
        const quantityDisplay = button.parentElement.querySelector('span');
        const currentQuantity = parseInt(quantityDisplay.textContent);

        // Determine URL based on action
        const url = `/admin-api/stock/${stockId}/${action}/`;

        // Make AJAX request
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the quantity display
                quantityDisplay.textContent = data.new_quantity;
                
                // Add success animation
                quantityDisplay.style.color = '#28a745';
                quantityDisplay.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    quantityDisplay.style.color = '';
                    quantityDisplay.style.transform = '';
                }, 300);

                // Show success message (optional)
                showMessage('Stock updated successfully!', 'success');
            } else {
                // Show error message
                showMessage(data.error || 'Failed to update stock', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Network error. Please try again.', 'error');
        })
        .finally(() => {
            // Re-enable button
            button.disabled = false;
            button.style.opacity = '1';
        });
    }

    function showMessage(message, type) {
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.textContent = message;
        messageDiv.style.position = 'fixed';
        messageDiv.style.top = '20px';
        messageDiv.style.right = '20px';
        messageDiv.style.padding = '12px 20px';
        messageDiv.style.borderRadius = '4px';
        messageDiv.style.zIndex = '9999';
        messageDiv.style.fontWeight = 'bold';
        messageDiv.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
        messageDiv.style.transition = 'opacity 0.3s';

        if (type === 'success') {
            messageDiv.style.backgroundColor = '#28a745';
            messageDiv.style.color = 'white';
        } else {
            messageDiv.style.backgroundColor = '#dc3545';
            messageDiv.style.color = 'white';
        }

        document.body.appendChild(messageDiv);

        // Remove after 3 seconds
        setTimeout(() => {
            messageDiv.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(messageDiv);
            }, 300);
        }, 3000);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
})();