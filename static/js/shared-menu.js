/**
 * Shared Sidebar Menu Injection
 * Injects a consistent sidebar menu across all pages
 */

(function() {
    'use strict';

    // Don't inject menu if we're in an iframe (embedded views)
    if (window.self !== window.top) {
        return;
    }

    // Menu configuration
    const mainItems = [
        { href: '/dashboard', label: 'App Dash' },
        { href: '/networking', label: 'Network Dash' },
        { href: '/progress', label: 'Progress Dash' },
        { href: '/reports', label: 'Reports' },
        { href: '/analytics', label: 'Analytics' },
        { href: '/daily-activities', label: 'Daily Activities' }
    ];

    const adminItems = [
        { href: '/templates', label: 'Templates' },
        { href: '#', label: 'Check AI Status', onclick: 'showAIStatus(); return false;' },
        { href: '/archived', label: 'Archive Dash' },
        { href: '/new-application?resume=true', label: 'Manage Resume' }
    ];

    // Determine active menu item based on current path
    function getActiveMenuItem() {
        const path = window.location.pathname;
        const search = window.location.search;
        const fullPath = path + search;

        // Helper list of all items
        const allItems = [...mainItems, ...adminItems];

        // Check for exact matches first
        for (const item of allItems) {
            if (item.href === fullPath || item.href === path) {
                return item.href;
            }
        }

        // Check for partial matches (e.g., /applications/* should highlight dashboard)
        if (path.startsWith('/applications/')) {
            return '/dashboard';
        }
        if (path.startsWith('/networking/')) {
            return '/networking';
        }

        return path;
    }

    // Generate menu HTML
    function generateMenuHTML() {
        const activePath = getActiveMenuItem();
        
        let menuHTML = `
        <div class="sidebar">
            <div class="sidebar-header">
                <h3>Hunter</h3>
            </div>
            <ul class="sidebar-menu sidebar-menu-main">
        `;

        // Main navigation items
        mainItems.forEach(item => {
            const isActive = item.href === activePath || 
                           (item.href !== '#' && window.location.pathname.startsWith(item.href));
            const activeClass = isActive ? 'active' : '';
            const onclickAttr = item.onclick ? ` onclick="${item.onclick}"` : '';
            
            menuHTML += `
                <li>
                    <a href="${item.href}" class="nav-link ${activeClass}"${onclickAttr}>${item.label}</a>
                </li>
            `;
        });

        // Admin section
        menuHTML += `
            </ul>
            <div class="sidebar-admin-section">
                <div class="sidebar-section-label">Admin</div>
                <ul class="sidebar-menu sidebar-menu-admin">
        `;

        adminItems.forEach(item => {
            const isActive = item.href === activePath || 
                           (item.href !== '#' && window.location.pathname.startsWith(item.href));
            const activeClass = isActive ? 'active' : '';
            const onclickAttr = item.onclick ? ` onclick="${item.onclick}"` : '';
            
            menuHTML += `
                <li>
                    <a href="${item.href}" class="nav-link ${activeClass}"${onclickAttr}>${item.label}</a>
                </li>
            `;
        });

        menuHTML += `
                </ul>
            </div>
        </div>
        `;

        return menuHTML;
    }

    // Generate menu CSS
    function generateMenuCSS() {
        return `
        <style id="shared-menu-styles">
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 180px;
            height: 100vh;
            background: #ffffff;
            border-right: 1px solid #e5e7eb;
            z-index: 1000;
            padding: 16px 0;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-header {
            padding: 16px 24px;
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 16px;
            flex-shrink: 0;
        }
        
        .sidebar-header h3 {
            color: #1f2937;
            font-size: 18px;
            font-weight: 600;
            margin: 0;
        }
        
        .sidebar-menu {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .sidebar-menu-main {
            flex: 1;
            overflow-y: auto;
        }
        
        .sidebar-menu li {
            margin: 0;
        }
        
        .sidebar-menu a {
            display: block;
            padding: 12px 24px;
            color: #6b7280;
            text-decoration: none;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
            font-weight: 500;
            font-size: 14px;
        }
        
        .sidebar-menu a:hover {
            background: #f9fafb;
            color: #1f2937;
            border-left-color: #3b82f6;
        }
        
        .sidebar-menu a.active {
            background: #f3f4f6;
            color: #1f2937;
            border-left-color: #3b82f6;
            font-weight: 600;
        }

        .sidebar-admin-section {
            margin-top: auto;
            padding-top: 24px;
            border-top: 1px solid #e5e7eb;
            flex-shrink: 0;
        }

        .sidebar-section-label {
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #9ca3af;
            padding: 0 24px 8px 24px;
        }
        
        /* Adjust body margin if sidebar is injected */
        body:has(.sidebar) {
            margin-left: 180px;
        }
        
        /* Fallback for browsers that don't support :has() */
        body.with-sidebar {
            margin-left: 180px;
        }
        </style>
        `;
    }

    // Inject menu into page
    function injectMenu() {
        // Check if sidebar already exists - if it does, replace it
        const existingSidebar = document.querySelector('.sidebar');
        if (existingSidebar) {
            // Remove existing sidebar
            existingSidebar.remove();
        }

        // Inject CSS
        if (!document.getElementById('shared-menu-styles')) {
            document.head.insertAdjacentHTML('beforeend', generateMenuCSS());
        }

        // Inject menu HTML at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', generateMenuHTML());
        
        // Add class to body for margin adjustment (fallback)
        document.body.classList.add('with-sidebar');

        // Handle showAIStatus function if it doesn't exist
        if (typeof showAIStatus === 'undefined') {
            window.showAIStatus = async function() {
                try {
                    const response = await fetch('/api/check-ollama');
                    const data = await response.json();
                    
                    if (data.connected) {
                        alert(`AI Connected - Model: ${data.current_model}`);
                    } else {
                        alert('AI Not Connected - Please start Ollama');
                    }
                } catch (error) {
                    alert('Error checking AI status');
                }
            };
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectMenu);
    } else {
        injectMenu();
    }
})();
