# Hunter Design System Guide

## Overview

This document provides a comprehensive guide to the Hunter application design system, inspired by the clean, minimal aesthetic of LianLian Global. The design system emphasizes simplicity, clarity, and professional appearance across all components and pages.

## Design Principles

### Core Philosophy

1. **Minimalism**: Remove unnecessary visual elements, focus on content
2. **Clarity**: High contrast, readable typography, clear hierarchy
3. **Consistency**: Uniform spacing, colors, and component styles
4. **Professional**: Clean, modern, business-appropriate aesthetic

### Color Palette

```css
:root {
    /* Backgrounds */
    --bg-primary: #ffffff;
    --bg-secondary: #fafafa;
    --bg-hover: #f9fafb;
    --bg-active: #f3f4f6;

    /* Text Colors */
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --text-tertiary: #9ca3af;

    /* Borders */
    --border-primary: #e5e7eb;
    --border-light: #f3f4f6;

    /* Accent Colors */
    --accent-blue: #3b82f6;
    --accent-blue-hover: #2563eb;
    --accent-blue-light: #eff6ff;
    --accent-green: #10b981;
}
```

### Typography

- **Font Family**: Poppins (Google Fonts) with system font fallbacks
- **Font Sizes**:
  - `--font-xs: 10px` (meta text, small labels)
  - `--font-sm: 12px` (secondary text)
  - `--font-base: 14px` (body text)
  - `--font-lg: 16px` (section headers)
  - `--font-xl: 20px` (card titles)
  - `--font-2xl: 24px` (page titles)
  - `--font-3xl: 32px` (stat numbers)

### Spacing System

```css
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
--space-2xl: 48px;
```

## Component Library

### 1. Hero Header Pattern

The hero header is a full-width header that appears at the top of pages, providing navigation context and page identification.

#### Structure

```html
<div class="hero-header">
    <div class="hero-header-top">
        <a href="/dashboard" class="back-link">
            <svg><!-- chevron icon --></svg>
            Back to Dashboard
        </a>
        <h1>Page Title</h1>
        <div class="hero-header-subtitle">Optional subtitle or description</div>
    </div>
</div>
```

#### CSS

```css
.hero-header {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 20px 32px;
    position: sticky;
    top: 0;
    z-index: 100;
    width: calc(100% - 180px);
    margin-left: 180px;
    box-sizing: border-box;
}

.hero-header-top {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
}

.back-link {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #3b82f6;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.2s ease;
    margin-bottom: 4px;
}

.back-link:hover {
    color: #2563eb;
}

.hero-header h1 {
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
    margin: 0;
    text-align: left;
}

.hero-header-subtitle {
    font-size: 14px;
    color: #6b7280;
    margin: 0;
}
```

#### Key Features

- **Full-width**: Spans from sidebar edge to right edge
- **Sticky positioning**: Stays at top when scrolling
- **Left-aligned**: All content left-aligned for consistency
- **Three-line structure**: Back link → Title → Subtitle (if applicable)

### 2. Sidebar Navigation

Fixed left sidebar with navigation links.

#### Structure

```html
<div class="sidebar">
    <div class="sidebar-header">
        <h3>Hunter</h3>
    </div>
    <ul class="sidebar-menu">
        <li><a href="/" class="nav-link">Home</a></li>
        <!-- More links -->
    </ul>
</div>
```

#### CSS

```css
.sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: 180px;
    height: 100vh;
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
    z-index: 1000;
    padding: 20px 0;
    overflow-y: auto;
}

.sidebar-header {
    padding: 0 16px 16px 16px;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 12px;
}

.sidebar-header h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
}

.sidebar-menu a {
    display: block;
    padding: 12px 16px;
    color: #6b7280;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
    border-left: 3px solid transparent;
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
}
```

#### Key Features

- **Fixed width**: 180px
- **White background**: Clean, minimal
- **Border-left indicator**: Shows active/hover state
- **No gradients**: Flat design

### 3. Stat Cards

Compact cards displaying metrics in a grid layout.

#### Structure

```html
<div class="stat-cards-grid">
    <div class="stat-card" data-status="active">
        <div class="stat-number">42</div>
        <div class="stat-label">Active</div>
    </div>
    <!-- More cards -->
</div>
```

#### CSS

```css
.stat-cards-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 16px;
    margin-bottom: 32px;
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
}

.stat-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 18px; /* 75% of 24px */
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
    cursor: pointer;
}

.stat-card:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
    border-color: #3b82f6;
}

.stat-card.active {
    border: 2px solid #3b82f6;
}

.stat-number {
    font-size: 32px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    color: #6b7280;
    font-weight: 500;
}
```

#### Key Features

- **Two rows**: 6 cards per row (12 total)
- **Centered**: Grid centered with max-width
- **Clickable**: Cards filter content when clicked
- **Reduced height**: Padding is 75% of standard (18px vs 24px)
- **Active state**: Border highlight for selected card

### 4. Application Cards

Cards displaying job application information in a grid.

#### Structure

```html
<div class="card" data-status="applied" data-flagged="false">
    <div class="card-header">
        <div class="card-company">
            Company Name
            <span class="match-score">85%</span>
        </div>
        <button class="flag-btn">⚐</button>
    </div>
    <div class="card-title">Job Title</div>
    <div class="card-status-container">
        <span class="card-status">Applied</span>
    </div>
    <div class="card-meta">📅 Applied: Nov 24, 2025</div>
    <div class="card-meta">📋 Posted: 5 days ago</div>
    <div class="card-meta">🔄 Updated: Nov 24, 2025</div>
    <div class="card-actions">
        <a href="/application/..." class="card-btn">View Summary →</a>
    </div>
</div>
```

#### CSS

```css
.applications-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 24px;
}

.card {
    background: #ffffff;
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    border: 1px solid #e5e7eb;
    transition: all 0.2s ease;
}

.card:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
}

.card-company {
    font-size: 20px;
    font-weight: 700;
    color: #1f2937;
    flex: 1;
}

.card-title {
    font-size: 14px;
    color: #1f2937;
    margin-bottom: 16px;
    font-weight: 500;
}

.card-status-container {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}

.card-status {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    text-transform: capitalize;
}

.card-meta {
    font-size: 10px;
    color: #6b7280;
    margin-bottom: 8px;
}

.card-btn {
    display: inline-block;
    background: #3b82f6;
    color: #ffffff;
    padding: 10px 16px;
    border-radius: 6px;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
    width: 100%;
    text-align: center;
}

.card-btn:hover {
    background: #2563eb;
}
```

#### Key Features

- **Grid layout**: Responsive grid with minimum 380px cards
- **Small meta text**: 10px font size for dates
- **Status badges**: Color-coded rounded pills
- **Hover effects**: Subtle lift and shadow increase

### 5. Timeline Component

Vertical timeline displaying chronological events with connecting line and circular markers.

#### Structure

```html
<div class="timeline">
    <div class="timeline-item">
        <div class="timeline-date">Jan 15, 2025 2:30 PM</div>
        <div class="timeline-content">
            <span class="timeline-description">Application submitted</span>
            <span class="timeline-status tag tag-blue">Applied</span>
        </div>
    </div>
    <!-- More items -->
</div>
```

#### CSS

```css
.timeline {
    position: relative;
    padding-left: 40px;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #e5e7eb;
}

.timeline-item {
    position: relative;
    margin-bottom: 32px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -32px;
    top: 4px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #3b82f6;
    border: 3px solid #ffffff;
    box-shadow: 0 0 0 2px #e5e7eb;
    z-index: 1;
}

.timeline-date {
    font-size: 13px;
    color: #6b7280;
    min-width: 140px;
    flex-shrink: 0;
}

.timeline-content {
    flex: 1;
    font-size: 14px;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 12px;
}

.timeline-description {
    flex: 1;
}

.timeline-status {
    display: inline-block;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 16px;
    white-space: nowrap;
}
```

#### Status Tag Colors

```css
.tag-blue {
    background: #dbeafe;
    color: #1e40af;
}

.tag-green {
    background: #d1fae5;
    color: #065f46;
}

.tag-gray {
    background: #f3f4f6;
    color: #4b5563;
}

.tag-red {
    background: #fee2e2;
    color: #991b1b;
}
```

#### Key Features

- **Vertical line**: Gray line connecting all events
- **Circular markers**: Blue circles on the line
- **Three-column layout**: Date | Description | Status Tag
- **Color-coded tags**: Different colors for different status types
- **Clean spacing**: 32px between items

### 6. Footer with Action Buttons

Fixed footer at bottom of page with primary actions.

#### Structure

```html
<div class="page-footer">
    <div class="footer-buttons">
        <a href="/new-application" class="footer-btn footer-btn-primary">New Application</a>
        <a href="/new-application?resume=true" class="footer-btn">Manage Resume</a>
    </div>
</div>
```

#### CSS

```css
.page-footer {
    background: #ffffff;
    border-top: 1px solid #e5e7eb;
    padding: 20px 32px;
    width: calc(100% - 180px);
    margin-left: 180px;
    box-sizing: border-box;
    position: fixed;
    bottom: 0;
    z-index: 100;
}

.footer-buttons {
    display: flex;
    justify-content: center;
    gap: 16px;
}

.footer-btn {
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    border-radius: 6px;
    border: 1px solid #e5e7eb;
    background: #ffffff;
    color: #1f2937;
    text-decoration: none;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.footer-btn:hover {
    background: #f9fafb;
    border-color: #d1d5db;
}

.footer-btn-primary {
    background: #3b82f6;
    color: #ffffff;
    border-color: #3b82f6;
}

.footer-btn-primary:hover {
    background: #2563eb;
    border-color: #2563eb;
}
```

#### Key Features

- **Fixed position**: Stays at bottom when scrolling
- **Centered buttons**: Primary and secondary actions
- **Account for footer**: Add `padding-bottom: 100px` to containers

### 7. Collapsible Cards

Cards that can be expanded/collapsed to show/hide content.

#### Structure

```html
<div class="content-card">
    <div class="card-header collapsible" onclick="toggleCollapse(this)">
        <h3>Section Title</h3>
        <span class="collapse-icon">▼</span>
    </div>
    <div class="card-content collapsed">
        <!-- Content here -->
    </div>
</div>
```

#### CSS

```css
.content-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header.collapsible {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    cursor: pointer;
    border-bottom: 1px solid #e5e7eb;
}

.card-header.collapsible:hover {
    background: #f9fafb;
}

.card-content {
    padding: 20px;
    transition: all 0.3s ease;
}

.card-content.collapsed {
    display: none;
}
```

#### JavaScript

```javascript
function toggleCollapse(header) {
    const card = header.closest('.content-card');
    const content = card.querySelector('.card-content');
    const icon = header.querySelector('.collapse-icon');
    
    content.classList.toggle('collapsed');
    icon.textContent = content.classList.contains('collapsed') ? '▶' : '▼';
}
```

#### Key Features

- **Default collapsed**: Cards start collapsed
- **Smooth transitions**: CSS transitions for expand/collapse
- **Visual indicator**: Icon shows state (▼ expanded, ▶ collapsed)

## Page Layouts

### Standard Page Layout

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Poppins font import -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* CSS variables and component styles */
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">...</div>
    
    <!-- Hero Header -->
    <div class="hero-header">...</div>
    
    <!-- Main Content -->
    <div class="container">
        <!-- Page content -->
    </div>
    
    <!-- Footer -->
    <div class="page-footer">...</div>
</body>
</html>
```

### Container Spacing

```css
.container {
    width: calc(100vw - 180px);
    margin: 0;
    padding: 24px;
    margin-left: 180px;
    box-sizing: border-box;
    padding-bottom: 100px; /* Space for fixed footer */
}
```

## Implementation Guidelines

### 1. Font Import

Always include Poppins font at the top of your HTML:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### 2. CSS Variables

Use CSS variables for consistency:

```css
:root {
    /* Copy color palette and spacing from above */
}
```

### 3. Component Reuse

- Use existing component classes
- Maintain consistent spacing
- Follow the color palette
- Use the typography scale

### 4. Responsive Design

```css
@media (max-width: 1200px) {
    .stat-cards-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}

@media (max-width: 768px) {
    .stat-cards-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .sidebar {
        transform: translateX(-100%);
        /* Mobile sidebar behavior */
    }
}
```

## Status Label Mapping

The system automatically maps status values to display-friendly labels:

| Original Status | Display Label | Tag Color |
|----------------|---------------|-----------|
| `applied` | Applied | Blue |
| `company response` | Company Response | Blue |
| `scheduled interview` | Interview Scheduled | Green |
| `interview notes` | Interview Notes | Green |
| `thank you sent` | Thank You Sent | Gray |
| `rejected` | Rejected | Red |
| `offered` | Offered | Green |

## Best Practices

1. **Consistency**: Use the same components and styles across all pages
2. **Spacing**: Use the spacing scale (--space-xs through --space-2xl)
3. **Colors**: Always use CSS variables, never hardcode colors
4. **Typography**: Use the font size scale consistently
5. **Accessibility**: Ensure sufficient color contrast and semantic HTML
6. **Performance**: Minimize custom CSS, reuse component styles

## Migration Guide

When applying this design system to existing pages:

1. **Import Poppins font**
2. **Add CSS variables** to :root
3. **Replace old components** with new component classes
4. **Update colors** to use new palette
5. **Update spacing** to use spacing scale
6. **Add hero header** pattern
7. **Add footer** with action buttons
8. **Test responsive** behavior

## Examples

See the following files for reference implementations:

- `app/templates/web/analytics.html` - Analytics page
- `app/templates/web/reports.html` - Reports page
- `app/templates/web/daily_activities.html` - Daily activities page
- `app/templates/web/templates.html` - Templates page
- `app/services/dashboard_generator.py` - Dashboard generation
- `app/services/document_generator.py` - Application detail pages

## Conclusion

This design system provides a cohesive, professional appearance across all Hunter application pages. By following these guidelines and using the provided components, you can ensure consistency and maintainability across multiple applications.

For questions or customization needs, refer to the implementation files in the Hunter application codebase.





