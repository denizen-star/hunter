/**
 * Dashboard Manager v2.1.0
 * Handles dashboard-specific functionality and interactions
 */

class DashboardManager {
    constructor() {
        this.applications = [];
        this.currentSort = 'updated_desc';
        this.currentTab = 'all';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadApplications();
    }

    setupEventListeners() {
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.matches('.tab')) {
                const status = e.target.dataset.status;
                this.switchTab(status);
            }
        });

        // Sort dropdown changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('.sort-select')) {
                const sortBy = e.target.value;
                this.sortApplications(sortBy);
            }
        });

        // Application card interactions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.card-btn')) {
                e.preventDefault();
                const url = e.target.href;
                // Don't navigate if URL is invalid
                if (!url || url === '#' || url === '') {
                    return;
                }
                this.openSummary(url);
            }
        });
    }

    async loadApplications() {
        try {
            const response = await fetch('/api/applications');
            this.applications = await response.json();
            this.renderApplications();
        } catch (error) {
            console.error('Failed to load applications:', error);
            this.showError('Failed to load applications. Please refresh the page.');
        }
    }

    switchTab(status) {
        this.currentTab = status;
        
        // Update tab appearance
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-status="${status}"]`).classList.add('active');
        
        // Show/hide tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        document.getElementById(`tab-${status}`).style.display = 'block';
        
        // Update sort options for current tab
        this.updateSortOptions(status);
        
        // Re-sort applications for current tab
        this.sortApplications(this.currentSort);
    }

    updateSortOptions(status) {
        const sortSelect = document.getElementById(`sort-select-${status}`);
        if (sortSelect) {
            sortSelect.value = this.currentSort;
        }
    }

    sortApplications(sortBy) {
        this.currentSort = sortBy;
        
        const currentTabContent = document.getElementById(`tab-${this.currentTab}`);
        const applicationsGrid = currentTabContent.querySelector('.applications-grid');
        
        if (!applicationsGrid) return;
        
        const cards = Array.from(applicationsGrid.querySelectorAll('.card'));
        
        cards.sort((a, b) => {
            switch(sortBy) {
                case 'updated_desc':
                    return new Date(b.dataset.updatedAt) - new Date(a.dataset.updatedAt);
                case 'updated_asc':
                    return new Date(a.dataset.updatedAt) - new Date(b.dataset.updatedAt);
                case 'applied_desc':
                    return new Date(b.dataset.appliedAt) - new Date(a.dataset.appliedAt);
                case 'applied_asc':
                    return new Date(a.dataset.appliedAt) - new Date(b.dataset.appliedAt);
                case 'job_posted_desc':
                    return new Date(b.dataset.appliedAt) - new Date(a.dataset.appliedAt);
                case 'job_posted_asc':
                    return new Date(a.dataset.appliedAt) - new Date(b.dataset.appliedAt);
                case 'match_desc':
                    return parseFloat(b.dataset.matchScore) - parseFloat(a.dataset.matchScore);
                case 'match_asc':
                    return parseFloat(a.dataset.matchScore) - parseFloat(b.dataset.matchScore);
                default:
                    return 0;
            }
        });
        
        // Re-append sorted cards
        cards.forEach(card => applicationsGrid.appendChild(card));
    }

    openSummary(url) {
        // Don't navigate if URL is "#" or empty
        if (!url || url === '#' || url === '') {
            console.log('Summary unavailable for this application');
            return;
        }
        // Open summary in same window with back button
        window.location.href = url;
    }

    renderApplications() {
        // This would typically render the applications
        // For now, we'll just log that applications are loaded
        console.log(`Loaded ${this.applications.length} applications`);
    }

    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #dc3545;
            color: white;
            padding: 1rem;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
        `;
        
        document.body.appendChild(errorDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Public methods
    refreshApplications() {
        this.loadApplications();
    }

    getCurrentTab() {
        return this.currentTab;
    }

    getCurrentSort() {
        return this.currentSort;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on the dashboard page
    if (document.getElementById('dashboard-page')) {
        window.dashboardManager = new DashboardManager();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
}

