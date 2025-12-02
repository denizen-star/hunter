# Timeline Component Design Guide

## Overview

This document provides a comprehensive guide to the timeline component design used in the Hunter application. The timeline displays chronological events with a clean, minimal vertical line design that connects circular markers.

## Design Principles

### Visual Structure

The timeline component follows these key design principles:

1. **Vertical Line**: A thin gray line (`#e5e7eb`) connects all timeline events vertically
2. **Circular Markers**: Blue circular markers (`#3b82f6`) indicate each event point
3. **Three-Column Layout**: Date/Time | Description | Status Tag
4. **Clean Spacing**: Generous spacing between items (32px) for readability
5. **Color-Coded Status Tags**: Different colors for different status types

## HTML Structure

```html
<div class="timeline">
    <div class="timeline-item">
        <div class="timeline-date">Jan 15, 2025 2:30 PM</div>
        <div class="timeline-content">
            <span class="timeline-description">Application submitted</span>
            <span class="timeline-status tag tag-blue">Applied</span>
        </div>
    </div>
    <!-- More timeline items... -->
</div>
```

## CSS Implementation

### Container

```css
.timeline {
    position: relative;
    padding-left: 40px;
}
```

The container uses relative positioning and left padding to make room for the vertical line and markers.

### Vertical Line

```css
.timeline::before {
    content: '';
    position: absolute;
    left: 8px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #e5e7eb;
}
```

The vertical line is created using a `::before` pseudo-element that spans the full height of the timeline container.

### Timeline Item

```css
.timeline-item {
    position: relative;
    margin-bottom: 32px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
}
```

Each timeline item uses flexbox for horizontal layout with:
- Relative positioning for marker placement
- 32px bottom margin for spacing
- 16px gap between date and content sections

### Circular Marker

```css
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
```

The circular marker is created using a `::before` pseudo-element with:
- 16px diameter circle
- Blue background (`#3b82f6`)
- White border (3px) for contrast
- Gray shadow (2px) to match the vertical line
- Positioned absolutely to align with the vertical line

### Date/Time Display

```css
.timeline-date {
    font-size: 13px;
    color: #6b7280;
    min-width: 140px;
    flex-shrink: 0;
}
```

The date/time section:
- Uses light gray color (`#6b7280`) for subtlety
- Fixed minimum width for alignment
- Does not shrink in flex layout

### Content Section

```css
.timeline-content {
    flex: 1;
    font-size: 14px;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 12px;
}
```

The content section uses flexbox to align description and status tag horizontally.

### Description

```css
.timeline-description {
    flex: 1;
}
```

The description takes up available space and wraps if needed.

### Status Tags

```css
.timeline-status {
    display: inline-block;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 16px;
    white-space: nowrap;
}
```

Status tags are rounded pills with:
- Compact padding
- Rounded corners (16px border-radius)
- No text wrapping

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

## Status Label Mapping

The timeline automatically maps status values to display-friendly labels:

| Original Status | Display Label | Tag Color |
|----------------|---------------|-----------|
| `applied` | Applied | Blue |
| `company response` | Company Response | Blue |
| `scheduled interview` | Interview Scheduled | Green |
| `interview notes` | Interview Notes | Green |
| `thank you sent` | Thank You Sent | Gray |
| `rejected` | Rejected | Red |
| `offered` | Offered | Green |

## Description Text

Descriptions are automatically generated based on status:

- **Applied**: "Application submitted"
- **Company Response**: "Company viewed profile"
- **Interview Scheduled**: "Phone screen scheduled"
- **Interview Notes**: "Phone screen completed"
- **Thank You Sent**: "Thank you email sent"

## Implementation in Python

### Timeline Generation Function

```python
def _generate_timeline_html_for_summary(self, application: Application) -> str:
    """Generate Application Timeline HTML for two-column layout"""
    # Get application updates
    updates = job_processor.get_application_updates(application)
    
    # Build timeline items
    timeline_items = []
    timeline_items.append({
        'date': format_for_display(application.created_at),
        'status': 'Applied',
        'description': 'Application submitted'
    })
    
    # Add status updates
    for update in reversed(updates[:9]):
        timeline_items.append({
            'date': update['display_timestamp'],
            'status': update['status'],
            'description': update['status']
        })
    
    # Generate HTML
    timeline_html = '<div class="timeline">'
    for item in timeline_items:
        # Determine tag class and description
        tag_class = "tag-blue"
        description = item['description']
        
        # Map status to appropriate tag and description
        if "interview" in item['status'].lower():
            tag_class = "tag-green"
            if "scheduled" in item['status'].lower():
                description = "Phone screen scheduled"
            elif "notes" in item['status'].lower():
                description = "Phone screen completed"
        # ... more mappings ...
        
        # Format status label
        status_label = self._format_status_label(item['status'])
        
        # Generate HTML
        timeline_html += f'''
            <div class="timeline-item">
                <div class="timeline-date">{item['date']}</div>
                <div class="timeline-content">
                    <span class="timeline-description">{description}</span>
                    <span class="timeline-status tag {tag_class}">{status_label}</span>
                </div>
            </div>
        '''
    
    timeline_html += '</div>'
    return timeline_html
```

## Usage in Other Applications

### Step 1: Copy CSS

Copy the timeline CSS styles to your application's stylesheet:

```css
.timeline { /* ... */ }
.timeline::before { /* ... */ }
.timeline-item { /* ... */ }
.timeline-item::before { /* ... */ }
.timeline-date { /* ... */ }
.timeline-content { /* ... */ }
.timeline-description { /* ... */ }
.timeline-status { /* ... */ }
.tag-blue { /* ... */ }
.tag-green { /* ... */ }
.tag-gray { /* ... */ }
.tag-red { /* ... */ }
```

### Step 2: Implement HTML Structure

Use the HTML structure shown above, ensuring:
- Timeline container with `timeline` class
- Each item wrapped in `timeline-item` div
- Date in `timeline-date` div
- Content in `timeline-content` div with description and status tag

### Step 3: Generate Timeline Data

Create a function that:
1. Collects chronological events
2. Formats dates/times consistently
3. Maps status values to display labels
4. Generates appropriate descriptions
5. Assigns color classes based on status type

### Step 4: Customize for Your Use Case

Adapt the design for your specific needs:

- **Different Colors**: Modify the tag color classes
- **Different Markers**: Change the `::before` pseudo-element styles
- **Different Layout**: Adjust flex properties
- **Additional Information**: Add more elements to timeline items

## Responsive Design

For mobile devices, consider:

```css
@media (max-width: 768px) {
    .timeline {
        padding-left: 32px;
    }
    
    .timeline-item {
        flex-direction: column;
        gap: 8px;
    }
    
    .timeline-date {
        min-width: auto;
        font-size: 12px;
    }
    
    .timeline-content {
        flex-direction: column;
        align-items: flex-start;
    }
}
```

## Accessibility

Ensure accessibility by:

1. **Semantic HTML**: Use proper heading hierarchy
2. **ARIA Labels**: Add `aria-label` to timeline container
3. **Color Contrast**: Ensure sufficient contrast for all text
4. **Keyboard Navigation**: Ensure timeline is keyboard accessible
5. **Screen Readers**: Provide descriptive text for status tags

Example:

```html
<div class="timeline" role="list" aria-label="Application timeline">
    <div class="timeline-item" role="listitem">
        <!-- ... -->
    </div>
</div>
```

## Best Practices

1. **Consistent Date Format**: Use a consistent date/time format across all items
2. **Limit Items**: Consider pagination or limiting visible items (e.g., last 10)
3. **Empty State**: Provide a message when no timeline items exist
4. **Loading State**: Show a loading indicator while fetching timeline data
5. **Error Handling**: Display error messages if timeline data fails to load

## Examples

### Basic Timeline

```html
<div class="timeline">
    <div class="timeline-item">
        <div class="timeline-date">Jan 15, 2025 2:30 PM</div>
        <div class="timeline-content">
            <span class="timeline-description">Application submitted</span>
            <span class="timeline-status tag tag-blue">Applied</span>
        </div>
    </div>
</div>
```

### Timeline with Multiple Events

```html
<div class="timeline">
    <div class="timeline-item">
        <div class="timeline-date">Jan 15, 2025 2:30 PM</div>
        <div class="timeline-content">
            <span class="timeline-description">Application submitted</span>
            <span class="timeline-status tag tag-blue">Applied</span>
        </div>
    </div>
    <div class="timeline-item">
        <div class="timeline-date">Jan 16, 2025 10:15 AM</div>
        <div class="timeline-content">
            <span class="timeline-description">Company viewed profile</span>
            <span class="timeline-status tag tag-blue">Company Response</span>
        </div>
    </div>
    <div class="timeline-item">
        <div class="timeline-date">Jan 17, 2025 3:45 PM</div>
        <div class="timeline-content">
            <span class="timeline-description">Phone screen scheduled</span>
            <span class="timeline-status tag tag-green">Interview Scheduled</span>
        </div>
    </div>
</div>
```

## Color Palette Reference

- **Vertical Line**: `#e5e7eb` (Light Gray)
- **Marker Background**: `#3b82f6` (Blue)
- **Marker Border**: `#ffffff` (White)
- **Date Text**: `#6b7280` (Medium Gray)
- **Description Text**: `#1f2937` (Dark Gray)
- **Blue Tag**: Background `#dbeafe`, Text `#1e40af`
- **Green Tag**: Background `#d1fae5`, Text `#065f46`
- **Gray Tag**: Background `#f3f4f6`, Text `#4b5563`
- **Red Tag**: Background `#fee2e2`, Text `#991b1b`

## Conclusion

This timeline design provides a clean, professional way to display chronological events. The vertical line and circular markers create a visual connection between events, while the three-column layout ensures information is easy to scan and understand.

For questions or customization needs, refer to the implementation in `app/services/document_generator.py` in the Hunter application codebase.





