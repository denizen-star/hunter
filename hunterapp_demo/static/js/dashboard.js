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
            // Demo version - wait for DEMO_DATA to load
            let attempts = 0;
            const maxAttempts = 50; // Wait up to 5 seconds
            
            while (attempts < maxAttempts) {
                if (typeof window.DEMO_DATA !== 'undefined' && window.DEMO_DATA.applications) {
                    this.applications = window.DEMO_DATA.applications;
                    try {
                        this.renderApplications();
                    } catch (renderError) {
                        console.error('Error rendering applications:', renderError);
                        // Don't show "Failed to load" error for rendering issues
                    }
                    return;
                }
                await new Promise(resolve => setTimeout(resolve, 100));
                attempts++;
            }
            
            // If DEMO_DATA still not available, show empty state
            this.applications = [];
            try {
                this.renderApplications();
            } catch (renderError) {
                console.error('Error rendering applications:', renderError);
            }
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
        const grid = document.getElementById('applications-grid');
        if (!grid) {
            console.error('Applications grid not found');
            return;
        }
        
        if (!this.applications || this.applications.length === 0) {
            grid.innerHTML = '<div class="empty-state"><p>No applications found</p></div>';
            return;
        }
        
        // Helper functions
        const formatDate = (dateString) => {
            if (!dateString) return 'N/A';
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric', 
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }) + ' EST';
        };
        
        const escapeHtml = (text) => {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };
        
        const getStatusClass = (status) => {
            if (!status) return 'status-applied';
            const statusLower = status.toLowerCase();
            if (statusLower.includes('applied') && !statusLower.includes('company')) return 'status-applied';
            if (statusLower.includes('company response')) return 'status-company-response';
            if (statusLower.includes('scheduled interview')) return 'status-scheduled-interview';
            if (statusLower.includes('interview')) return 'status-interview-notes';
            if (statusLower.includes('pending')) return 'status-pending';
            if (statusLower.includes('rejected')) return 'status-rejected';
            if (statusLower.includes('accepted')) return 'status-accepted';
            return 'status-applied';
        };
        
        // Render application cards
        grid.innerHTML = this.applications.map(app => {
            const statusClass = getStatusClass(app.status);
            const matchScore = Math.round(app.match_score || 0);
            const appliedDate = formatDate(app.applied_at);
            const updatedDate = formatDate(app.updated_at);
            const companyName = app.company || 'Unknown Company';
            const jobTitle = app.job_title || 'Unknown Position';
            const status = app.status || 'Unknown';
            const folderName = app.folder_name || `${companyName.replace(/\s+/g, '-')}-${jobTitle.replace(/\s+/g, '')}`;
            
            return `
                <div class="card" 
                     data-updated-at="${app.updated_at || app.applied_at || ''}" 
                     data-applied-at="${app.applied_at || ''}" 
                     data-match-score="${matchScore}"
                     data-flagged="false">
                    <div class="card-header">
                        <div class="card-company">
                            ${escapeHtml(companyName)}
                            <span class="match-score">${matchScore}%</span>
                        </div>
                        <button class="flag-btn unflagged" 
                                onclick="toggleFlag('${app.id || ''}', false)" 
                                title="Flag this job">
                            ⚐
                        </button>
                    </div>
                    <div class="card-title">${escapeHtml(jobTitle)}</div>
                    <div class="card-status-container">
                        <span class="card-status ${statusClass}">${escapeHtml(status)}</span>
                    </div>
                    <div class="card-meta">
                        📅 Applied: ${appliedDate}
                    </div>
                    ${app.location ? `<div class="card-meta">📍 ${escapeHtml(app.location)}</div>` : ''}
                    <div class="card-meta">
                        🔄 Updated: ${updatedDate}
                    </div>
                    <div class="card-actions">
                        <a href="/applications/${folderName}/index.html" class="card-btn">View Summary →</a>
                    </div>
                </div>
            `;
        }).join('');
        
        // Apply current filter
        if (this.currentTab) {
            this.switchTab(this.currentTab);
        }
        
        console.log(`Rendered ${this.applications.length} applications`);
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
    // Initialize on index.html (dashboard page)
    if (document.getElementById('applications-grid')) {
        window.dashboardManager = new DashboardManager();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
}

