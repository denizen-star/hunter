/**
 * Upgrade Handler for Demo Version
 * Handles disabled buttons with upgrade tooltips and alerts
 */

(function() {
    'use strict';

    // CSS for disabled buttons
    const disabledButtonCSS = `
        <style id="upgrade-handler-styles">
        .btn-disabled {
            opacity: 0.5;
            cursor: not-allowed !important;
            pointer-events: auto;
            position: relative;
        }
        
        .btn-disabled:hover {
            opacity: 0.6;
        }
        
        .btn-disabled::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            cursor: not-allowed;
        }
        </style>
    `;

    // Inject CSS
    if (!document.getElementById('upgrade-handler-styles')) {
        document.head.insertAdjacentHTML('beforeend', disabledButtonCSS);
    }

    // Show upgrade message
    window.showUpgradeMessage = function() {
        alert('Purchase Upgrade for Functionality');
        return false;
    };

    // Initialize disabled buttons on page load
    function initializeDisabledButtons() {
        // Find all buttons with btn-disabled class
        const disabledButtons = document.querySelectorAll('.btn-disabled');
        disabledButtons.forEach(button => {
            // Set tooltip
            if (!button.getAttribute('title')) {
                button.setAttribute('title', 'Purchase Upgrade for Functionality');
            }
            
            // Ensure onclick handler
            if (!button.onclick) {
                button.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    showUpgradeMessage();
                    return false;
                };
            }
        });
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeDisabledButtons);
    } else {
        initializeDisabledButtons();
    }

    // Also run after a short delay to catch dynamically added buttons
    setTimeout(initializeDisabledButtons, 500);
})();
