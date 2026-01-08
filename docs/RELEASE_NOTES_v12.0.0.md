# Release Notes - Version 12.0.0

**Release Date:** January 8, 2026  
**Version:** 12.0.0  
**Type:** Major Release

## 🎉 Overview

Version 12.0.0 introduces a powerful new **Unified Search** feature that allows users to search and filter all job applications and networking contacts from a single, comprehensive interface. This release significantly improves discoverability and organization of your job search pipeline.

## ✨ New Features

### 🔍 Unified Search Page

A new dedicated Search page provides a centralized location to search and filter all applications and contacts:

- **Accessible from Main Menu**: New "Search" menu item located after "Progress Dash"
- **Hero Header**: Matches the design language of other dashboards with Search icon
- **Full-width Layout**: Hero header extends full width, touching the left sidebar
- **Clean Interface**: Modern, table-based layout with clear visual hierarchy

### 📊 Combined List View

View all applications and contacts in a single, unified list:

- **Type Badges**: Visual distinction between Applications (APP - blue badge) and Contacts (CONTACT - green badge)
- **Comprehensive Data**: Shows name, match score, status, and last updated date
- **Clickable Rows**: Entire row is clickable, navigating to detail pages
- **Hover Effects**: Visual feedback on row hover

### 🎯 Smart Sorting

Intelligent sorting algorithm ensures logical organization:

1. **Applications First**: All applications appear before contacts
2. **Company Grouping**: Items grouped by company name (alphabetically, case-insensitive)
3. **Time-based Ordering**: Within each company, items sorted by last updated date (newest to oldest)
4. **Consistent Logic**: Same sorting applied to both applications and contacts

### 🔎 Real-time Search

Powerful search functionality with instant results:

- **Multi-field Search**: Searches across company name, person name, job title, and status
- **Case-insensitive**: Search works regardless of capitalization
- **Instant Filtering**: Results update as you type
- **Results Counter**: Shows number of matching results

### 📦 Comprehensive Coverage

The search includes all relevant items:

- **Active Applications**: All non-rejected applications
- **Rejected Applications**: Previously excluded applications now included
- **Archived Applications**: Applications from the archived directory
- **All Contacts**: All networking contacts

## 🔧 Technical Details

### New API Endpoint

**`GET /api/applications-and-contacts`**

Returns a combined list of all applications and contacts with unified sorting.

**Response Format:**
```json
{
  "success": true,
  "items": [
    {
      "type": "application",
      "id": "20250108120000-Company-JobTitle",
      "name": "Company - Job Title",
      "company": "Company",
      "match_score": 85.5,
      "status": "applied",
      "last_updated": "2026-01-08T12:00:00",
      "detail_url": "/applications/Company-JobTitle/summary.html"
    },
    {
      "type": "contact",
      "id": "20250108120000-Person-Company",
      "name": "Person Name - Company",
      "company": "Company",
      "match_score": 90.0,
      "status": "In Conversation",
      "last_updated": "2026-01-08T10:00:00",
      "detail_url": "/networking/Person-Company/summary.html"
    }
  ],
  "count": 2
}
```

**Sorting Logic:**
1. Separates applications and contacts
2. Sorts applications by: company name (ascending), then last updated (descending)
3. Sorts contacts by: company name (ascending), then last updated (descending)
4. Combines: applications first, then contacts

### New Route

**`GET /search`**

Renders the unified search page template.

### Menu Integration

- Added "Search" menu item to `static/js/shared-menu.js`
- Positioned after "Progress Dash" in main navigation
- Uses `search11.png` icon

## 📁 Files Changed

### New Files
- `app/templates/web/search.html` - Search page template

### Modified Files
- `app/web.py`
  - Added `/search` route
  - Added `/api/applications-and-contacts` endpoint
  - Enhanced sorting logic with timezone handling
- `static/js/shared-menu.js`
  - Added Search menu item
- `app/services/dashboard_generator.py`
  - Removed list view section (moved to dedicated page)

## 🎨 UI/UX Improvements

### Hero Header
- Matches Progress Dash design language
- Full-width layout touching left sidebar
- Sticky positioning for easy access
- Search icon (80px × 80px)

### Search Interface
- Large, prominent search input
- Real-time results counter
- Clean table layout with clear column headers
- Responsive design with scrollable results area

### Visual Design
- Type badges for quick identification
- Status badges with consistent styling
- Hover effects for better interactivity
- Consistent spacing and typography

## 🔄 Migration Notes

No migration required. The new Search page is immediately available from the main navigation menu.

## 🐛 Bug Fixes

- Fixed hero header positioning to touch left sidebar
- Improved timezone handling in sorting logic
- Enhanced datetime parsing for consistent sorting

## 📈 Performance

- Efficient sorting algorithm with O(n log n) complexity
- Single API call for all data
- Client-side filtering for instant search results
- Optimized timestamp extraction

## 🚀 Future Enhancements

Potential future improvements:
- Advanced filtering options (by status, match score range, date range)
- Export functionality
- Bulk actions
- Saved search filters

## 📝 Notes

- The Search page includes all applications (active, rejected, archived) and all contacts
- Sorting is consistent across both applications and contacts
- Search is case-insensitive and searches across multiple fields
- Results update in real-time as you type

---

**For questions or issues, please refer to the main documentation or contact support.**
