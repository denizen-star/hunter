/**
 * Navigation Manager v2.1.0
 * Handles single-page navigation and state management
 */

class NavigationManager {
    constructor() {
        this.currentPage = 'dashboard';
        this.pageHistory = ['dashboard'];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.showPage('dashboard-page');
        this.updateBreadcrumb();
    }

    setupEventListeners() {
        // Navigation link clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-link')) {
                e.preventDefault();
                const page = e.target.dataset.page;
                if (page) {
                    this.navigateToPage(page);
                }
            }
        });

        // Breadcrumb clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.breadcrumb a')) {
                e.preventDefault();
                const page = e.target.dataset.page;
                if (page) {
                    this.navigateToPage(page);
                }
            }
        });

        // Browser back/forward buttons
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.page) {
                this.showPage(e.state.page, false);
            }
        });
    }

    navigateToPage(pageName, addToHistory = true) {
        if (addToHistory) {
            this.pageHistory.push(pageName);
            // Update browser history
            history.pushState({ page: pageName }, '', `#${pageName}`);
        }
        
        // Map page names to actual page IDs
        const pageIdMap = {
            'dashboard': 'dashboard-page',
            'new-application': 'new-application-page',
            'resume-manager': 'resume-manager-page',
            'reports': 'reports-page',
            'settings': 'settings-page'
        };
        
        const actualPageId = pageIdMap[pageName] || pageName;
        this.showPage(actualPageId);
        this.updateBreadcrumb();
        this.updateActiveNav();
    }

    showPage(pageName, addToHistory = true) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.style.display = 'none';
            page.classList.remove('active');
        });

        // Show target page
        const targetPage = document.getElementById(pageName);
        if (targetPage) {
            targetPage.style.display = 'block';
            targetPage.classList.add('active');
            this.currentPage = pageName;
        } else {
            console.warn(`Page '${pageName}' not found`);
        }

        // Scroll to top
        window.scrollTo(0, 0);
    }

    updateBreadcrumb() {
        const breadcrumb = document.getElementById('breadcrumb');
        if (!breadcrumb) return;

        const breadcrumbMap = {
            'dashboard': 'Dashboard',
            'new-application': 'New Application',
            'resume-manager': 'Resume Manager',
            'reports': 'Reports',
            'settings': 'Settings'
        };

        const breadcrumbItems = this.pageHistory.map(page => {
            const name = breadcrumbMap[page] || page;
            return `<li><a href="#" data-page="${page}">${name}</a></li>`;
        }).join('');

        breadcrumb.querySelector('ol').innerHTML = breadcrumbItems;
    }

    updateActiveNav() {
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to current page nav link
        const activeLink = document.querySelector(`[data-page="${this.currentPage}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    goBack() {
        if (this.pageHistory.length > 1) {
            this.pageHistory.pop(); // Remove current page
            const previousPage = this.pageHistory[this.pageHistory.length - 1];
            this.navigateToPage(previousPage, false);
        }
    }

    // Public methods for external use
    getCurrentPage() {
        return this.currentPage;
    }

    getPageHistory() {
        return [...this.pageHistory];
    }
}

/**
 * Page Manager - Handles page-specific functionality
 */
class PageManager {
    constructor() {
        this.pages = new Map();
        this.init();
    }

    init() {
        // Register default pages
        this.registerPage('dashboard', {
            onShow: () => this.loadDashboard(),
            onHide: () => this.cleanupDashboard()
        });

        this.registerPage('new-application', {
            onShow: () => this.loadNewApplication(),
            onHide: () => this.cleanupNewApplication()
        });

        this.registerPage('resume-manager', {
            onShow: () => this.loadResumeManager(),
            onHide: () => this.cleanupResumeManager()
        });
    }

    registerPage(pageName, handlers) {
        this.pages.set(pageName, handlers);
    }

    showPage(pageName) {
        // Hide current page
        const currentPage = window.navManager?.getCurrentPage();
        if (currentPage && this.pages.has(currentPage)) {
            const currentHandlers = this.pages.get(currentPage);
            if (currentHandlers.onHide) {
                currentHandlers.onHide();
            }
        }

        // Show new page
        if (this.pages.has(pageName)) {
            const handlers = this.pages.get(pageName);
            if (handlers.onShow) {
                handlers.onShow();
            }
        }
    }

    // Page-specific handlers
    loadDashboard() {
        console.log('Loading dashboard...');
        // Dashboard-specific initialization
    }

    cleanupDashboard() {
        console.log('Cleaning up dashboard...');
        // Dashboard cleanup
    }

    loadNewApplication() {
        console.log('Loading new application form...');
        // New application form initialization
    }

    cleanupNewApplication() {
        console.log('Cleaning up new application form...');
        // New application form cleanup
    }

    loadResumeManager() {
        console.log('Loading resume manager...');
        // Resume manager initialization
    }

    cleanupResumeManager() {
        console.log('Cleaning up resume manager...');
        // Resume manager cleanup
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize navigation manager
    window.navManager = new NavigationManager();
    
    // Initialize page manager
    window.pageManager = new PageManager();
    
    // Handle initial page load
    const hash = window.location.hash.substring(1);
    if (hash && hash !== 'dashboard') {
        window.navManager.navigateToPage(hash);
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NavigationManager, PageManager };
}
