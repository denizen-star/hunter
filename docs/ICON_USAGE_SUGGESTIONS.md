# Icon Usage Suggestions

This document provides suggestions for where and how to use the app icons throughout the Hunter application to enhance visual appeal and user experience.

## Available Icons

All icons are located in `/static/images/icons/`:
- `AppDash.jpg` - Application Dashboard
- `NetworkDash.jpg` - Networking Dashboard
- `ProgressDash.png` - Progress Dashboard (deprecated - feature removed)
- `Reports.png` - Reports
- `Analytics.png` - Analytics
- `DailyActivities.jpg` - Daily Activities
- `Templates.png` - Templates
- `HowtoHunter.jpg` - How to Hunter Guide
- `TrackingGuide.jpg` - Tracking Guide
- `DashesGuide.jpg` - Dashes Guide
- `TemplatingGuide.jpg` - Templating Guide
- `Rewards.png` - Rewards
- `Hunter.png` - Main Hunter logo/favicon

## Implementation Suggestions

### 1. User Guide Pages

#### Page Headers
Add large icons (48-64px) next to page titles in `.page-header` sections:

```html
<div class="page-header">
    <div style="display: flex; align-items: center; gap: 16px;">
        <img src="/static/images/icons/TrackingGuide.jpg" alt="Tracking" style="width: 64px; height: 64px;">
        <h1>Tracking Guide</h1>
    </div>
    <p>Learn how to track your job applications...</p>
</div>
```

**Files to update:**
- `app/templates/web/tracking_guide.html`
- `app/templates/web/dashes_guide.html`
- `app/templates/web/templating_guide.html`
- `app/templates/web/how_to_hunter.html`
- `app/templates/web/rewards.html`

#### Section Headers
Add medium icons (32px) next to section h2 headings:

```html
<h2 style="display: flex; align-items: center; gap: 12px;">
    <img src="/static/images/icons/TrackingGuide.jpg" alt="" style="width: 32px; height: 32px;">
    Application Status Tracking
</h2>
```

#### Feature Cards
Add icons to feature highlight cards or callout boxes:

```html
<div class="feature-card">
    <img src="/static/images/icons/AppDash.jpg" alt="Dashboard" style="width: 48px; height: 48px;">
    <h3>Quick Access</h3>
    <p>Access all your applications from the dashboard...</p>
</div>
```

#### Navigation Breadcrumbs
Add small icons (16px) to breadcrumb items for visual navigation:

```html
<nav class="breadcrumb">
    <ol>
        <li>
            <img src="/static/images/icons/AppDash.jpg" alt="" style="width: 16px; height: 16px; vertical-align: middle;">
            <a href="/dashboard">Dashboard</a>
        </li>
    </ol>
</nav>
```

### 2. Generated Dashboard Pages

#### Card Headers
Add icons to dashboard card titles in `app/services/dashboard_generator.py`:

```python
card_html = f'''
<div class="dashboard-card">
    <div class="card-header">
        <img src="/static/images/icons/AppDash.jpg" alt="" class="card-icon">
        <h3>Application Overview</h3>
    </div>
    ...
</div>
'''
```

#### Quick Action Buttons
Enhance action buttons with relevant icons:

```html
<button class="action-btn">
    <img src="/static/images/icons/Templates.png" alt="" style="width: 20px; height: 20px;">
    Create Template
</button>
```

#### Status Indicators
Use icons to enhance status visualizations:

```html
<div class="status-badge">
    <img src="/static/images/icons/AppDash.jpg" alt="" style="width: 16px; height: 16px;">
    <span>In Progress</span>
</div>
```

### 3. Application Detail Pages

#### Tab Icons
Add icons to tab navigation in application detail views:

```html
<div class="tab-nav">
    <button class="tab-btn active">
        <img src="/static/images/icons/AppDash.jpg" alt="" style="width: 18px; height: 18px;">
        Overview
    </button>
    <button class="tab-btn">
        <img src="/static/images/icons/Templates.png" alt="" style="width: 18px; height: 18px;">
        Documents
    </button>
</div>
```

#### Action Buttons
Enhance buttons with relevant icons:

```html
<button class="btn-primary">
    <img src="/static/images/icons/Templates.png" alt="" style="width: 20px; height: 20px;">
    Generate Cover Letter
</button>
```

#### Empty States
Use icons in empty state messages:

```html
<div class="empty-state">
    <img src="/static/images/icons/AppDash.jpg" alt="" style="width: 64px; height: 64px; opacity: 0.5;">
    <p>No applications yet. Start by adding your first application!</p>
</div>
```

### 4. Networking Pages

#### Contact Cards
Add icons to networking contact cards:

```html
<div class="contact-card">
    <img src="/static/images/icons/NetworkDash.jpg" alt="Network" class="contact-icon">
    <h3>John Doe</h3>
    <p>Software Engineer at Tech Corp</p>
</div>
```

### 5. Reports and Analytics Pages

#### Chart Headers
Add icons to chart/section headers:

```html
<div class="chart-section">
    <h3>
        <img src="/static/images/icons/Analytics.png" alt="" style="width: 24px; height: 24px;">
        Application Trends
    </h3>
    <div class="chart">...</div>
</div>
```

#### Metric Cards
Add icons to metric display cards:

```html
<div class="metric-card">
    <img src="/static/images/icons/Reports.png" alt="" class="metric-icon">
    <div class="metric-value">42</div>
    <div class="metric-label">Total Applications</div>
</div>
```

## CSS Styling Recommendations

Add these styles to ensure icons display consistently:

```css
/* Icon base styles */
.icon {
    display: inline-block;
    object-fit: contain;
    vertical-align: middle;
}

.icon-small {
    width: 16px;
    height: 16px;
}

.icon-medium {
    width: 24px;
    height: 24px;
}

.icon-large {
    width: 32px;
    height: 32px;
}

.icon-xlarge {
    width: 48px;
    height: 48px;
}

.icon-xxlarge {
    width: 64px;
    height: 64px;
}

/* Icon with text alignment */
.icon-text {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

/* Icon opacity for disabled/empty states */
.icon-muted {
    opacity: 0.5;
}
```

## Implementation Priority

1. **High Priority:**
   - Page headers in guide pages
   - Dashboard card headers
   - Main navigation (already implemented)

2. **Medium Priority:**
   - Section headers in guides
   - Action buttons
   - Tab navigation

3. **Low Priority:**
   - Breadcrumbs
   - Empty states
   - Decorative elements

## Notes

- All icons should have appropriate `alt` attributes for accessibility
- Icons should maintain aspect ratio (use `object-fit: contain`)
- Consider icon size relative to text size for visual balance
- Use consistent spacing (8px gap recommended) between icons and text
- Icons in disabled/empty states should have reduced opacity (0.5)
