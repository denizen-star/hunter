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
        { href: '/index.html', label: 'App Dash', icon: 'AppDash.jpg' },
        { href: '/networking.html', label: 'Network Dash', icon: 'NetworkDash.jpg' },
        { href: '/progress.html', label: 'Progress Dash', icon: 'ProgressDash.png' },
        { href: '/reports.html', label: 'Reports', icon: 'Reports.png' },
        { href: '/analytics.html', label: 'Analytics', icon: 'Analytics.png' },
        { href: '/daily-activities.html', label: 'Daily Activities', icon: 'DailyActivities.jpg' }
    ];

    const adminItems = [
        { href: '/templates.html', label: 'Templates', icon: 'Templates.png' },
        { href: '#', label: 'Check AI Status', onclick: 'showAIStatus(); return false;', icon: 'CheckAiStatus.png' },
        { href: '/archived.html', label: 'Archive Dash', icon: 'ArchiveDash.png' },
        { href: 'manage-resume.html', label: 'Manage Resume', icon: 'ManageResume.png' }
    ];

    const helpItems = [
        { href: '/how-to-hunter.html', label: 'How to Hunter?', icon: 'HowtoHunter.jpg' },
        { href: '/dashes-guide.html', label: 'Dashes', icon: 'DashesGuide.jpg' },
        { href: '/templating-guide.html', label: 'Templating', icon: 'TemplatingGuide.jpg' },
        { href: '/rewards.html', label: 'Rewards', icon: 'Rewards.png' },
        { href: '/tracking-guide.html', label: 'Tracking', icon: 'TrackingGuide.jpg' }
    ];

    // Determine active menu item based on current path
    function getActiveMenuItem() {
        const path = window.location.pathname;
        const search = window.location.search;
        const fullPath = path + search;

        // Helper list of all items (for active path detection)
        const allItems = [...mainItems, ...adminItems, ...helpItems];

        // Check for exact matches first
        for (const item of allItems) {
            if (item.href === fullPath || item.href === path) {
                return item.href;
            }
        }

        // Check for partial matches (e.g., /applications/* should highlight dashboard)
        if (path.startsWith('/applications/')) {
            return '/index.html';
        }
        if (path.startsWith('/networking/')) {
            return '/networking.html';
        }
        // Handle root path
        if (path === '/' || path === '/index.html') {
            return '/index.html';
        }

        return path;
    }

    // Generate menu HTML
    function generateMenuHTML() {
        const activePath = getActiveMenuItem();
        
        let menuHTML = `
        <div class="sidebar">
        `;

        // Help section (expanded by default) - FIRST
        menuHTML += `
            <div class="sidebar-help-section">
                <div class="sidebar-section-header" onclick="toggleSection('help')">
                    <span class="sidebar-section-label">Help</span>
                    <svg class="sidebar-section-chevron" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <ul class="sidebar-menu sidebar-menu-help sidebar-section-expanded" id="help-section">
        `;

        helpItems.forEach(item => {
            const isActive = item.href === activePath || 
                           (item.href !== '#' && window.location.pathname.startsWith(item.href));
            const activeClass = isActive ? 'active' : '';
            const onclickAttr = item.onclick ? ` onclick="${item.onclick}"` : '';
            const iconHTML = item.icon ? `<img src="/static/images/icons/${item.icon}" alt="" class="nav-icon">` : '';
            
            menuHTML += `
                <li>
                    <a href="${item.href}" class="nav-link ${activeClass}"${onclickAttr}>${iconHTML}${item.label}</a>
                </li>
            `;
        });

        menuHTML += `
                </ul>
            </div>
        `;

        // Main section (expanded by default) - SECOND
        menuHTML += `
            <div class="sidebar-main-section">
                <div class="sidebar-section-header" onclick="toggleSection('main')">
                    <span class="sidebar-section-label">Main</span>
                    <svg class="sidebar-section-chevron" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <ul class="sidebar-menu sidebar-menu-main sidebar-section-expanded" id="main-section">
        `;

        mainItems.forEach(item => {
            const isActive = item.href === activePath || 
                           (item.href !== '#' && window.location.pathname.startsWith(item.href));
            const activeClass = isActive ? 'active' : '';
            const onclickAttr = item.onclick ? ` onclick="${item.onclick}"` : '';
            const iconHTML = item.icon ? `<img src="/static/images/icons/${item.icon}" alt="" class="nav-icon">` : '';
            
            menuHTML += `
                <li>
                    <a href="${item.href}" class="nav-link ${activeClass}"${onclickAttr}>${iconHTML}${item.label}</a>
                </li>
            `;
        });

        menuHTML += `
                </ul>
            </div>
        `;

        // Admin section (collapsed by default) - THIRD
        menuHTML += `
            <div class="sidebar-admin-section">
                <div class="sidebar-section-header" onclick="toggleSection('admin')">
                    <span class="sidebar-section-label">Admin</span>
                    <svg class="sidebar-section-chevron" width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <ul class="sidebar-menu sidebar-menu-admin sidebar-section-collapsed" id="admin-section">
        `;

        adminItems.forEach(item => {
            const isActive = item.href === activePath || 
                           (item.href !== '#' && window.location.pathname.startsWith(item.href));
            const activeClass = isActive ? 'active' : '';
            const onclickAttr = item.onclick ? ` onclick="${item.onclick}"` : '';
            const iconHTML = item.icon ? `<img src="/static/images/icons/${item.icon}" alt="" class="nav-icon">` : '';
            
            menuHTML += `
                <li>
                    <a href="${item.href}" class="nav-link ${activeClass}"${onclickAttr}>${iconHTML}${item.label}</a>
                </li>
            `;
        });

        menuHTML += `
                </ul>
            </div>
            
            <div class="sidebar-header">
                <img src="/static/images/icons/Hunter.png" alt="Hunter" class="sidebar-header-icon" title="Hunter">
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
            border-top: 1px solid #e5e7eb;
            margin-top: auto;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        
        .sidebar-header-icon {
            width: 80px;
            height: 80px;
            object-fit: contain;
            flex-shrink: 0;
            position: relative;
            cursor: pointer;
        }
        
        .sidebar-header-icon::after {
            content: 'Hunter';
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            font-size: 48px;
            font-weight: 700;
            color: rgba(31, 41, 55, 0.1);
            pointer-events: none;
            white-space: nowrap;
            z-index: -1;
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .sidebar-header h3 {
            display: none;
        }
        
        .sidebar-menu {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .sidebar-menu-main {
            overflow-y: auto;
        }
        
        .sidebar-menu li {
            margin: 0;
        }
        
        .sidebar-menu a {
            display: flex;
            align-items: center;
            padding: 12px 24px;
            color: #6b7280;
            text-decoration: none;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
            font-weight: 500;
            font-size: 14px;
        }
        
        .sidebar-menu a .nav-icon {
            width: 20px;
            height: 20px;
            margin-right: 8px;
            object-fit: contain;
            flex-shrink: 0;
            opacity: 0.8;
            transition: opacity 0.2s ease;
        }
        
        .sidebar-menu a:hover {
            background: #f9fafb;
            color: #1f2937;
            border-left-color: #3b82f6;
        }
        
        .sidebar-menu a:hover .nav-icon {
            opacity: 1;
        }
        
        .sidebar-menu a.active {
            background: #f3f4f6;
            color: #1f2937;
            border-left-color: #3b82f6;
            font-weight: 600;
        }
        
        .sidebar-menu a.active .nav-icon {
            opacity: 1;
        }

        .sidebar-admin-section,
        .sidebar-help-section,
        .sidebar-main-section {
            padding-top: 24px;
            border-top: 1px solid #e5e7eb;
            flex-shrink: 0;
        }

        .sidebar-section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px 8px 24px;
            cursor: pointer;
            user-select: none;
            transition: opacity 0.2s ease;
        }

        .sidebar-section-header:hover {
            opacity: 0.7;
        }

        .sidebar-section-label {
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #9ca3af;
        }

        .sidebar-section-chevron {
            color: #9ca3af;
            transition: transform 0.3s ease;
            flex-shrink: 0;
        }

        .sidebar-section-header[data-expanded="true"] .sidebar-section-chevron {
            transform: rotate(180deg);
        }

        .sidebar-section-collapsed {
            display: none;
        }

        .sidebar-section-expanded {
            display: block;
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

    // Track Help's state before Admin opens
    let helpWasExpandedBeforeAdmin = true;

    // Toggle section visibility
    function toggleSection(sectionName) {
        const section = document.getElementById(sectionName + '-section');
        const header = section.previousElementSibling;
        
        if (!section || !header) return;

        const isCollapsed = section.classList.contains('sidebar-section-collapsed');
        
        // Special handling for Admin section
        if (sectionName === 'admin') {
            const helpSection = document.getElementById('help-section');
            const helpHeader = helpSection ? helpSection.previousElementSibling : null;
            
            if (isCollapsed) {
                // Admin is opening - collapse Help if it's expanded
                if (helpSection && helpHeader) {
                    const helpIsExpanded = helpSection.classList.contains('sidebar-section-expanded');
                    if (helpIsExpanded) {
                        helpWasExpandedBeforeAdmin = true;
                        helpSection.classList.remove('sidebar-section-expanded');
                        helpSection.classList.add('sidebar-section-collapsed');
                        helpHeader.setAttribute('data-expanded', 'false');
                    } else {
                        helpWasExpandedBeforeAdmin = false;
                    }
                }
                
                // Open Admin
                section.classList.remove('sidebar-section-collapsed');
                section.classList.add('sidebar-section-expanded');
                header.setAttribute('data-expanded', 'true');
            } else {
                // Admin is closing - restore Help if it was expanded before
                section.classList.remove('sidebar-section-expanded');
                section.classList.add('sidebar-section-collapsed');
                header.setAttribute('data-expanded', 'false');
                
                if (helpWasExpandedBeforeAdmin && helpSection && helpHeader) {
                    helpSection.classList.remove('sidebar-section-collapsed');
                    helpSection.classList.add('sidebar-section-expanded');
                    helpHeader.setAttribute('data-expanded', 'true');
                }
            }
        } else {
            // Normal toggle for other sections (Help, Main)
            if (isCollapsed) {
                section.classList.remove('sidebar-section-collapsed');
                section.classList.add('sidebar-section-expanded');
                header.setAttribute('data-expanded', 'true');
            } else {
                section.classList.remove('sidebar-section-expanded');
                section.classList.add('sidebar-section-collapsed');
                header.setAttribute('data-expanded', 'false');
            }
        }
    }

    // Make toggleSection available globally
    window.toggleSection = toggleSection;

    // Inject menu into page
    function injectMenu() {
        // Check if sidebar already exists - if it does, replace it
        const existingSidebar = document.querySelector('.sidebar');
        if (existingSidebar) {
            // Remove existing sidebar
            existingSidebar.remove();
        }

        // Inject CSS first (before menu HTML) to prevent flickering
        if (!document.getElementById('shared-menu-styles')) {
            document.head.insertAdjacentHTML('beforeend', generateMenuCSS());
        }

        // Add class to body for margin adjustment BEFORE injecting menu (prevents flicker)
        document.body.classList.add('with-sidebar');

        // Inject menu HTML at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', generateMenuHTML());

        // Set initial collapsed state for sections
        const adminHeader = document.querySelector('#admin-section').previousElementSibling;
        const helpHeader = document.querySelector('#help-section').previousElementSibling;
        const mainHeader = document.querySelector('#main-section').previousElementSibling;
        
        // Admin: collapsed by default
        if (adminHeader) {
            adminHeader.setAttribute('data-expanded', 'false');
        }
        
        // Help: expanded by default
        if (helpHeader) {
            helpHeader.setAttribute('data-expanded', 'true');
        }
        
        // Main: expanded by default
        if (mainHeader) {
            mainHeader.setAttribute('data-expanded', 'true');
        }

        // Handle showAIStatus function if it doesn't exist
        if (typeof showAIStatus === 'undefined') {
            window.showAIStatus = async function() {
                try {
                    // Demo version - hardcoded response
                    alert('AI Connected - Model: llama3:latest\nStatus: Operational');
                    return;
                    // Original API call commented out for demo
                    // const response = await fetch('/api/check-ollama');
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

    // Inject CSS immediately to prevent flickering (before DOM is ready)
    if (document.head && !document.getElementById('shared-menu-styles')) {
        document.head.insertAdjacentHTML('beforeend', generateMenuCSS());
        // Add body class immediately if body exists to prevent layout shift
        if (document.body) {
            document.body.classList.add('with-sidebar');
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectMenu);
    } else {
        injectMenu();
    }
})();
