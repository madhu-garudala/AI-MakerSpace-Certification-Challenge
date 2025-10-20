// Main JavaScript for KidSafe Food Analyzer

document.addEventListener('DOMContentLoaded', function() {
    const cerealSelect = document.getElementById('cereal-select');
    const selectedInfo = document.getElementById('selected-info');
    const selectedCerealName = document.getElementById('selected-cereal-name');
    const analyzeBtn = document.getElementById('analyze-btn');

    // Handle cereal selection
    cerealSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        
        if (selectedValue) {
            // Show the selected info section
            selectedInfo.style.display = 'block';
            selectedCerealName.textContent = selectedValue;
        } else {
            // Hide the selected info section
            selectedInfo.style.display = 'none';
        }
    });

    // Handle analyze button click
    analyzeBtn.addEventListener('click', function() {
        const selectedCereal = cerealSelect.value;
        
        if (selectedCereal) {
            // For now, just show an alert
            // This will be replaced with actual analysis functionality
            showNotification('Analysis feature coming soon!', 'info');
            console.log('Analyzing:', selectedCereal);
        }
    });

    // Notification function for future use
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'info' ? '#3B82F6' : '#10B981'};
            color: white;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            font-weight: 500;
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});

