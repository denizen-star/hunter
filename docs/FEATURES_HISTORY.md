## Hunter — Chronological Feature History

This document lists the features you requested and that are working in Hunter, in chronological order.

### Contents by Feature Area

- **Dashboard & UI**: 2025-10-14 → 2025-10-30
  - v2.0.0 Tabbed dashboard, sorting, posted date; Nordic design iterations; default dashboard route; Active tab; Templates page and navigation updates.
- **Matching & Qualifications**: 2025-10-13 → 2025-10-21
  - Enhanced qualification analysis; tech matcher; parsing fixes; overqualification recognition; equivalence mappings; improved scoring.
- **Research System**: 2025-10-17 → 2025-10-21
  - Real-time web search; company-specific fallbacks; mission/vision, personnel and news improvements; structured research tab.
- **Reports & Activities**: 2025-10-17 → 2025-10-28
  - Reports stats (Active/Rejected); period logic fixes; Daily Activities page with collapsible sections and Actions metric.
- **Resume/Tech Extraction**: 2025-10-15 → 2025-10-29
  - Resume technology extraction + cache; expanded DB techs; remove Scala; tech evaluation refinements.
- **Documents (Cover/Intros/Templates)**: 2025-10-20 → 2025-10-30
  - Longer intro message formats (v3.1.0); cover letter ML findings (v2.5.0); Templates page and TemplateManager service.
- **Documentation**: 2025-10-21
  - Docs reorganization (v2.1.0 → v2.4.0), index and maintenance guidance, release notes.
- **Workflow & Cleanup**: 2025-10-27
  - Rejection cleanup with summary regeneration and redirect.

### October 13, 2025 — Version 1.0.1
- **Increased context + tokens**: `num_predict` to 10,000; added `num_ctx` 10,000; timeout to 10 minutes. Enables long job descriptions and resumes without truncation. (Ref: `docs/CHANGELOG.md`)
- **Summary link fixes**: Summary pages open correctly from UI and dashboard; added route `GET /applications/<path:filepath>` and `target="_blank"`. (Ref: `docs/CHANGELOG.md`)
- **Custom resume support**: Endpoint to set per‑application custom resume; automatic document regeneration. (Ref: `docs/CHANGELOG.md`)

### October 13, 2025 — Version 1.5.0
- **Enhanced qualification analysis**: Feature count tracking across sections; new Technologies & Tools section; weighted match scoring; detection of missing technologies; ✓/✗ indicators. (Ref: `docs/CHANGELOG.md`)
- **Summary generation fix**: Regenerated missing summary for affected application; dashboard updated. (Ref: `docs/CHANGELOG.md`)

### October 13, 2025 — v1.0.0 to v1.5.0 related commits
- Initial release v1.0.0. [`6eaca29`](https://github.com/denizen-star/hunter/commit/6eaca29)
- Add release notes and deployment docs. [`494a272`](https://github.com/denizen-star/hunter/commit/494a272)
- Add comprehensive feature extraction documentation. [`0acec8d`](https://github.com/denizen-star/hunter/commit/0acec8d)
- Release v1.5.0: Enhanced Qualification Analysis. [`ae7f18f`](https://github.com/denizen-star/hunter/commit/ae7f18f)

### October 14, 2025 — Technology Matching & Insights Updates
- **Technology matching prompt fixed**: Only technologies required in the job description are analyzed. Status pills: ✅ matched, ⚠ partial, ❌ missing. (Ref: `CHANGES_SUMMARY.md`)
- **Additional Insights section**: Displays competitive intel (e.g., “compare to others who clicked apply”) when available; hidden when absent. (Ref: `CHANGES_SUMMARY.md`)
- **UI placement**: Technologies section moved to bottom of Job Description tab with enhanced styling. (Ref: `CHANGES_SUMMARY.md`)

### October 14, 2025 — Version 2.0.0 (Major)
- **Tabbed dashboard**: 9 status tabs with counts; responsive design. (Ref: `docs/RELEASE_NOTES_v2.0.0.md`)
- **Advanced sorting**: Updated, Applied, Posted Date, and Match % (asc/desc) per tab with independent preferences. (Ref: `docs/RELEASE_NOTES_v2.0.0.md`)
- **Posted Date support**: AI extraction with fallback; stored in `application.yaml`; displayed on cards. (Ref: `docs/RELEASE_NOTES_v2.0.0.md`)
- **UI improvements**: Richer cards (metadata, badges, match %), improved layout and responsiveness. (Ref: `docs/RELEASE_NOTES_v2.0.0.md`)
- **Model updates**: Added `posted_date`; performance and error handling improvements. (Ref: `docs/RELEASE_NOTES_v2.0.0.md`)

### October 14–16, 2025 — Post‑v2.0 improvements and UI work
- v1.5.1: Enhanced updates & LinkedIn metadata cleaner. [`585bcff`](https://github.com/denizen-star/hunter/commit/585bcff)
- v1.5.2: Technologies section in summaries with skill‑match visualization. [`c16d015`](https://github.com/denizen-star/hunter/commit/c16d015)
- v1.5.3: Improved Update Status form UX. [`cf0da51`](https://github.com/denizen-star/hunter/commit/cf0da51)
- Fix: Update existing summary page instead of duplicating on status updates. [`61e82ca`](https://github.com/denizen-star/hunter/commit/61e82ca)
- Tech matcher to reduce AI hallucination in skill matching. [`99cac48`](https://github.com/denizen-star/hunter/commit/99cac48)
- Fix Update Status functionality and UI improvements. [`79ddbc3`](https://github.com/denizen-star/hunter/commit/79ddbc3)
- Resume technology extraction and caching system. [`f01fc0d`](https://github.com/denizen-star/hunter/commit/f01fc0d)
- Remove qualification analysis box from cover letter generation. [`1abbcff`](https://github.com/denizen-star/hunter/commit/1abbcff)

### October 15–16, 2025 — Reports, Landing, and Design Iterations
- Add comprehensive Reports page with charts and analytics. [`93b24dc`](https://github.com/denizen-star/hunter/commit/93b24dc)
- Create landing page and update routing. [`11c92a4`](https://github.com/denizen-star/hunter/commit/11c92a4)
- Major v3.0.0 release: Enhanced Matching System & UI overhaul. [`38b2ab6`](https://github.com/denizen-star/hunter/commit/38b2ab6) [`5b1ac8c`](https://github.com/denizen-star/hunter/commit/5b1ac8c)
- Design system work (Soft Nordic), dashboard/layout/color refinements, and reversions to stabilize UX. [`be53993`](https://github.com/denizen-star/hunter/commit/be53993) → [`c9a6a5a`](https://github.com/denizen-star/hunter/commit/c9a6a5a) → [`75fcd1f`](https://github.com/denizen-star/hunter/commit/75fcd1f) → [`4864f37`](https://github.com/denizen-star/hunter/commit/4864f37)

### October 17, 2025 — Reporting, Extraction, and Research Enhancements
- Enhance reports with Active/Rejected stats. [`103d459`](https://github.com/denizen-star/hunter/commit/103d459)
- Add missing database technologies to extraction. [`1dfeb0b`](https://github.com/denizen-star/hunter/commit/1dfeb0b)
- Enhance summary tabs data handling. [`2305f09`](https://github.com/denizen-star/hunter/commit/2305f09)
- Restore Hiring Team section. [`a32562d`](https://github.com/denizen-star/hunter/commit/a32562d)
- Enhanced research sections and intro message functionality. [`bfbdc77`](https://github.com/denizen-star/hunter/commit/bfbdc77)
- Real‑time web search for company research via DuckDuckGo; better fallbacks and real data for personnel/mission. [`a50797e`](https://github.com/denizen-star/hunter/commit/a50797e) [`a085af1`](https://github.com/denizen-star/hunter/commit/a085af1) [`3a2376b`](https://github.com/denizen-star/hunter/commit/3a2376b) [`7e98317`](https://github.com/denizen-star/hunter/commit/7e98317)

### October 20–21, 2025 — Intro Format, Dashboard, Matching & Docs
- New intro message format with three copy‑ready boxes; bump v3.1.0. [`50cb39d`](https://github.com/denizen-star/hunter/commit/50cb39d) [`4118b45`](https://github.com/denizen-star/hunter/commit/4118b45)
- Add Active tab to dashboard; refine technology evaluation (remove R). [`488df2c`](https://github.com/denizen-star/hunter/commit/488df2c)
- Parsing/matching fixes incl. overqualification recognition and reliability. [`04a1eac`](https://github.com/denizen-star/hunter/commit/04a1eac) [`a3479a7`](https://github.com/denizen-star/hunter/commit/a3479a7) [`36d2b22`](https://github.com/denizen-star/hunter/commit/36d2b22) [`6675a34`](https://github.com/denizen-star/hunter/commit/6675a34) [`6d03f0f`](https://github.com/denizen-star/hunter/commit/6d03f0f)
- Fix reports functionality and raw data tab; documentation organization v2.1.0 → v2.4.0. [`2494767`](https://github.com/denizen-star/hunter/commit/2494767) [`0fa4f56`](https://github.com/denizen-star/hunter/commit/0fa4f56) [`f9d99a7`](https://github.com/denizen-star/hunter/commit/f9d99a7)

### October 21, 2025 — Version 2.4.0 (Major)
- **Documentation reorganization**: Centralized docs under `docs/`; added `docs/archive/`; navigation and index improved; user‑focused guides. (Ref: `docs/RELEASE_NOTES_v2.4.0.md`, `docs/DOCUMENTATION_OVERVIEW.md`)
- **Reports fixes**: Correct period calculations for Yesterday/7/30/All; timezone handling and error recovery improved. (Ref: `docs/RELEASE_NOTES_v2.4.0.md`)
- **Summary raw data tab**: Restored display of original job description; improved timestamped raw file detection; clearer error messages. (Ref: `docs/RELEASE_NOTES_v2.4.0.md`)

### October 22, 2025 — v2.5.0 Enhancements
- Enhanced cover letter template with ML analysis findings. [`a6fd975`](https://github.com/denizen-star/hunter/commit/a6fd975)

### October 27–30, 2025 — Workflow, Reports, Templates
- Job rejection cleanup with auto‑redirect to dashboard. [`7aa9e0d`](https://github.com/denizen-star/hunter/commit/7aa9e0d)
- Add Daily Activities page with collapsible sections and Reports enhancements. [`8503bb9`](https://github.com/denizen-star/hunter/commit/8503bb9)
- Remove Scala from technology extraction and resume. [`c0b57d8`](https://github.com/denizen-star/hunter/commit/c0b57d8)
- Templates feature: Templates page with collapsible cards, `TemplateManager` service and APIs, app‑wide nav updates, collapsible saved templates, default create‑new collapsed, EST timestamp fix, auto‑regenerate dashboard on `/`. [`81fea34`](https://github.com/denizen-star/hunter/commit/81fea34)

---

If you want this expanded further back (pre‑Oct 2025) or with links to specific commits and files changed, let me know and I’ll add them.

### Commit details (full messages)

2025-10-16 — 36dc169 — Complete Soft Nordic Design System Implementation

🎨 Centralized Design System with Consistent Typography

Design Philosophy:
- Complete Soft Nordic design system across all pages
- Centralized title and subtitle styling
- Consistent design language throughout the application

✨ Key Features:
🔧 CSS Framework Updates:
- colors.css: Complete Soft Nordic color palette with CSS variables
- layout.css: Centralized typography system and card components
- forms.css: Soft Nordic form styling with enhanced interactions
- navigation.css: Gradient buttons with soft shadows

📝 Typography System:
- .page-title: Large, light-weight titles for main pages
- .page-subtitle: Centered subtitles with proper spacing
- .section-title: Medium titles for sections
- .section-subtitle: Smaller descriptive text
- .card-title: Styled card headers with gradients

🎯 Component Updates:
- Unified color palette across all CSS files
- Consistent spacing using CSS variables
- Enhanced shadow system for depth
- Improved border radius system
- Better typography hierarchy

📱 Template Updates:
- Landing page: Applied centralized title classes
- UI page: Updated card titles and headers
- All pages: Consistent design language

🔧 Technical Improvements:
- CSS variables for maintainable design system
- Consistent spacing and typography scales
- Enhanced accessibility with better contrast
- Responsive design considerations
- Modern CSS with gradients and shadows

This completes the Soft Nordic design system implementation with
a centralized, maintainable approach to styling across the entire application.

2025-10-16 — ee786a9 — Fix Hero Sections - Apply Soft Nordic Gradients

🎨 Hero Section Color Consistency Fix

Issue Resolved:
- Hero sections were still showing solid gray (#424242) instead of Soft Nordic gradients
- Colors now match the new application screen styling consistently

✨ Changes Made:
- Landing page hero section: Updated to Soft Nordic gradient
- Reports page hero section: Updated to Soft Nordic gradient
- Feature card headers: Updated to Soft Nordic gradient
- Report card headers: Updated to Soft Nordic gradient

🎯 Visual Consistency:
- All hero sections now use: linear-gradient(135deg, #8b9dc3 0%, #6c7b95 100%)
- Enhanced shadow effects: rgba(108, 123, 149, 0.2)
- Consistent styling across all pages
- Matches the sidebar and card header styling

🔧 Technical Details:
- Updated .hero background in landing.html
- Updated .header background in reports.html
- Updated .feature-card h3 background in landing.html
- Updated .report-card h3 background in reports.html

Now all hero sections have the beautiful Soft Nordic gradient design
that matches the rest of the application's aesthetic!

2025-10-16 — f75e282 — Remove Top Padding from Hero Sections

🎨 Layout Consistency Fix

Issue Resolved:
- Hero sections had excessive top padding (80px) that didn't match home page styling
- Removed top padding to create consistent layout across all pages

✨ Changes Made:
- Landing page hero: padding: 80px 20px → padding: 0 20px
- Reports page header: padding: 80px 20px → padding: 0 20px
- UI page header: padding: 80px 20px → padding: 0 20px

🎯 Visual Consistency:
- All pages now have consistent top spacing
- Hero sections align properly with the top of the viewport
- Maintains horizontal padding (20px) for proper content spacing
- Matches the home page layout styling

🔧 Technical Details:
- Updated .hero padding in landing.html
- Updated .header padding in reports.html
- Updated .header padding in ui.html

Now all pages have consistent top spacing that matches the home page layout!

2025-10-16 — 7012ca7 — Regenerate Dashboard Page with Complete Soft Nordic Design

🎨 Complete Dashboard Redesign

New Features:
- Brand new dashboard.html template with Soft Nordic design
- Complete integration with centralized CSS system
- Modern, responsive layout with beautiful gradients
- Enhanced user experience with smooth animations

✨ Design System Integration:
- Uses centralized colors.css, layout.css, navigation.css, forms.css
- Consistent typography with page-title and page-subtitle classes
- Soft Nordic gradients and shadows throughout
- Matching sidebar and header styling with other pages

🎯 Dashboard Features:
- Real-time statistics cards with hover effects
- Tabbed interface for different application statuses
- Sortable application cards with match scores
- Quick action buttons for common tasks
- AI status checking functionality
- Responsive grid layout for application cards

🔧 Technical Improvements:
- New /api/dashboard endpoint for complete data
- Updated /dashboard route to serve new template
- Enhanced JavaScript for dynamic content loading
- Improved error handling and user feedback
- Modern ES6+ JavaScript features

📱 User Experience:
- Beautiful Soft Nordic color palette
- Smooth hover animations and transitions
- Enhanced visual hierarchy with proper spacing
- Consistent design language across all pages
- Professional and welcoming interface

The dashboard now provides a complete overview of job applications
with a beautiful, cohesive design that matches the rest of the application!

2025-10-16 — c9a6a5a — Revert Dashboard Changes - Restore Original Working Version

🔄 Dashboard Reversion Complete

Changes Reverted:
- Removed new dashboard.html template
- Restored original dashboard route functionality
- Removed new /api/dashboard endpoint
- Restored original dashboard_generator functionality

✅ Original Dashboard Restored:
- Dashboard now serves generated HTML from data/output/index.html
- Original dashboard styling and functionality preserved
- All existing features working as before
- No more template errors

The dashboard is now back to its original working state that you were happy with!

2025-10-16 — 5bf3005 — Apply Blue-Gray Color Scheme to Dashboard

🎨 Dashboard Color Scheme Update

Applied clean blue-gray color palette from image to:
- Sidebar: Updated to #4a5568 blue-gray background
- Hero/Header: Matching #4a5568 blue-gray background
- Background: Clean #f5f5f5 light gray
- Titles: Clean white text with proper font weights
- Subtitles: Consistent white text styling
- Tabs: Blue-gray header with white text
- Cards: Clean white cards with blue-gray shadows
- Navigation: Improved hover states and active states

✨ Visual Improvements:
- Consistent blue-gray (#4a5568) color throughout
- Clean light gray (#f5f5f5) background
- Professional white text on blue-gray backgrounds
- Subtle shadows using blue-gray tones
- Improved contrast and readability

The dashboard now matches the clean, professional aesthetic
shown in the reference image with a cohesive blue-gray color scheme.

2025-10-16 — 385bc01 — Apply Flat #8b9dc3 Color to All Pages

🎨 Consistent Flat Color Scheme Applied

Updated all pages to use flat (solid) #8b9dc3 color instead of gradients:

✅ New Application Page (ui.html):
- Sidebar: Flat #8b9dc3 background
- Hero/Header: Flat #8b9dc3 background
- Card titles: Flat #8b9dc3 background

✅ Landing Page (landing.html):
- Sidebar: Flat #8b9dc3 background
- Hero: Flat #8b9dc3 background (removed gradient)
- Feature card headers: Flat #8b9dc3 background

✅ Reports Page (reports.html):
- Sidebar: Flat #8b9dc3 background
- Header: Flat #8b9dc3 background
- Report card headers: Flat #8b9dc3 background

✅ Dashboard (dashboard_generator.py):
- Sidebar: Flat #8b9dc3 background
- Header: Flat #8b9dc3 background
- Tab headers: Flat #8b9dc3 background

🎯 Result:
All pages now have consistent flat #8b9dc3 color for:
- Menu/sidebar backgrounds
- Hero/header sections
- Card title backgrounds
- Tab headers

No more gradients - clean, flat, consistent color scheme!

2025-10-16 — a5266bf — Fix Dashboard Layout and Button Colors

🎨 Dashboard Improvements

✅ View Summary Buttons:
- Updated button background from gray (#808080) to #8b9dc3
- Added hover state with slightly darker shade (#7a8bb0)
- Maintains white text and proper contrast

✅ Full Width Panel:
- Container now uses full available width: calc(100vw - 250px)
- Proper margin-left: 250px to account for sidebar
- Panel expands to full screen width without covering menu
- Removed max-width constraint for better space utilization

🎯 Result:
- All 'View Summary →' buttons now match the #8b9dc3 theme color
- Dashboard panel spans full width while respecting sidebar space
- Better use of screen real estate for application cards
- Consistent color scheme throughout dashboard

2025-10-16 — 9f35590 — Make Dashboard Truly Full Width

🎯 Full Width Layout Improvements

✅ Container Width:
- Added box-sizing: border-box for proper width calculation
- Explicit padding specification for better control

✅ Header Full Width:
- Changed from viewport width to container-relative width
- margin: 0 -20px to extend beyond container padding
- width: calc(100% + 40px) for full container width

✅ Tabs Container Full Width:
- margin: 0 -20px 20px -20px to extend beyond container padding
- width: calc(100% + 40px) to fill entire container width
- Maintains proper spacing while using full available space

🎯 Result:
- Dashboard content now spans the complete available width
- No more white space on the right side
- Header, tabs, and content all use full container width
- Better utilization of screen real estate for application cards

2025-10-16 — 55f9f7f — Remove Rounded Border from Tabs Menu

🎨 Tab Menu Styling Update

✅ Border Radius Removal:
- Changed border-radius from 12px to 0
- Removes rounded corner effect from tabs container
- Creates clean, sharp edges for modern flat design

🎯 Result:
- Tabs menu now has sharp, clean edges
- Consistent with flat design aesthetic
- Maintains full width and functionality
- Cleaner, more professional appearance

2025-10-16 — ba6c817 — Fix Dashboard Spacing and Menu Styling

🎯 Dashboard Layout Improvements

✅ Remove Space Between Hero and Browser Top:
- Removed top padding from container (0 20px 20px 20px)
- Added overflow-x: hidden to body for clean edges
- Hero now extends to the very top of the browser

✅ Remove Space Between Hero and Tabs Container:
- Updated header margin to remove bottom spacing
- Tabs container now connects directly to hero section
- Seamless visual flow from hero to menu

✅ Enhanced Tabs Menu Styling:
- Added box-shadow to tabs-header for depth
- Increased tab padding (18px 20px) for better touch targets
- Enhanced tab transitions (0.3s ease) for smoother interactions
- Improved tab colors (rgba(255, 255, 255, 0.9)) for better contrast
- Added border-bottom styling for active states
- Professional menu-like appearance with proper spacing

🎯 Result:
- Hero section now touches the top of the browser
- No gaps between hero and tabs menu
- Tabs look like a proper navigation menu
- Clean, professional dashboard layout

2025-10-16 — 4cef90e — Center Feature Cards on Landing Page

🎯 Landing Page Layout Improvement

✅ Feature Cards Centering:
- Changed grid from auto-fit to fixed 3 columns: repeat(3, 1fr)
- Added max-width: 1200px for optimal card sizing
- Used margin-left: auto and margin-right: auto for horizontal centering
- Maintains 40px gap between cards for proper spacing

🎯 Result:
- Three feature cards now perfectly centered horizontally
- Cards maintain equal width and proper spacing
- Clean, balanced layout on landing page
- No impact on other pages (dashboard, reports, UI)
- Professional appearance with centered content

2025-10-16 — eba6cf8 — Add Vertical Centering to Feature Cards

🎯 Complete Centering Implementation

✅ Vertical Centering Added:
- Container now uses flexbox: display: flex; flex-direction: column
- Added justify-content: center for vertical centering
- Set min-height: calc(100vh - 200px) to use full available space
- Maintains horizontal centering with existing max-width and margin

✅ Combined Centering:
- Horizontal: max-width + margin auto (existing)
- Vertical: flexbox justify-content center (new)
- Result: Feature cards now centered both horizontally and vertically

🎯 Result:
- Feature cards perfectly centered in both dimensions
- Uses full available viewport height minus hero space
- Professional, balanced layout
- Cards appear in the center of the visible area

2025-10-16 — 71b7f5c — Distribute All 7 Boxes Equally Through Open Space

🎯 Unified Card Layout Implementation

✅ Combined All Cards:
- Merged features and stats into single all-cards-container
- All 7 boxes now in one unified grid layout
- Removed separate .features and .stats containers

✅ Equal Distribution:
- Grid uses auto-fit with minmax(280px, 1fr) for responsive layout
- 30px gap between all cards for consistent spacing
- justify-items: center for perfect card alignment
- max-width: 1400px for optimal space utilization

✅ Consistent Styling:
- All cards now have matching border-radius (16px)
- Unified max-width (280px) for consistent sizing
- Same backdrop-filter and shadow effects
- Perfect visual harmony across all 7 boxes

🎯 Result:
- 7 boxes (3 feature + 4 metric cards) distributed equally
- Responsive grid that adapts to screen size
- Consistent spacing and styling throughout
- Professional, balanced layout

2025-10-16 — fff4582 — Revert Unified Card Layout

🔄 Restore Original Layout

✅ Reverted Changes:
- Restored separate .features and .stats containers
- Removed unified all-cards-container
- Back to original 3 feature cards + 4 stat cards layout

✅ Original Styling Restored:
- .features: 3-column grid with centered layout
- .stats: auto-fit grid for stat cards
- Original border-radius and spacing restored
- Clean separation between feature and stat sections

🎯 Result:
- Back to the clean, original layout
- Feature cards properly centered
- Stat cards in their own section below
- Professional, organized appearance

2025-10-16 — 1ee1b9d — Simplify Landing Page - Remove Dynamic Stats

🎯 Clean Static Landing Page

✅ Removed Dynamic Elements:
- Removed entire stats section with 4 metric cards
- Removed loadStats() JavaScript function
- Removed stats-related CSS styling
- Removed DOMContentLoaded event listener for stats

✅ Simplified Structure:
- Landing page now shows only 3 static feature cards
- Clean, simple layout with just hero + features + footer
- No dynamic data loading or API calls
- Pure static content for better performance

✅ Feature Cards Remain:
- AI-Powered Analysis
- Automated Documents
- Progress Tracking
- All with proper styling and descriptions

🎯 Result:
- Super simple landing page as requested
- Just static boxes with clean design
- No unnecessary complexity or dynamic elements
- Professional, minimalist appearance

2025-10-16 — 7cfa145 — Fix Hero Spacing and Lighten Feature Cards

🎯 Landing Page Visual Improvements

✅ Fixed Hero Top Spacing:
- Removed space between hero and top of browser
- Updated container to use full viewport height
- Hero now extends properly to top edge
- Removed unnecessary box-shadow from hero

✅ Lightened Feature Cards:
- Changed from dark heavy cards to light clean cards
- Background: rgba(255, 255, 255, 0.9) instead of dark
- Text color: #333 instead of white
- Reduced border-radius from 16px to 8px
- Minimal shadow: 0 2px 8px instead of heavy 0 8px 32px
- Lighter hover effect with subtle lift

✅ Improved Typography:
- Feature card headers: reduced font-weight to 500
- Paragraph text: #666 color for better readability
- Smaller font-size for descriptions (0.95rem)
- Better contrast and readability

🎯 Result:
- Hero section now touches top of browser
- Feature cards are clean, light, and minimal
- Much less visual weight and heaviness
- Professional, clean appearance

2025-10-16 — 75fcd1f — Make Dashboard the Default Landing Page

🎯 Route Change - No Hardcoding

✅ Updated Root Route (/):
- Changed from serving landing.html to serving dashboard
- Uses existing dashboard serving logic (no duplication)
- Automatically generates dashboard if it doesn't exist
- Clean, maintainable approach

✅ Benefits:
- Dashboard is now the first thing users see
- No hardcoded paths or content
- Reuses existing dashboard infrastructure
- Easy to revert if needed

🎯 Result:
- http://localhost:51003/ now serves the dashboard
- Landing page functionality preserved (just not default)
- Clean, professional entry point to the application

2025-10-16 — 4864f37 — UI/UX Improvements: Nordic Design & Menu Optimization

✨ Major Updates:
- Applied Nordic template design consistently across all pages
- Fixed header/container layout to eliminate gaps and align properly with sidebar
- Reduced header height to 100px and removed unnecessary subtitles
- Extended width layout using proper viewport calculations

🎨 Design Improvements:
- Reports page: Removed unnecessary text, converted time period buttons to menu-style tabs
- New Application page: Streamlined menu to only show essential actions
- Consistent Nordic styling with rounded corners, proper shadows, and color scheme
- Enhanced follow-up items with individual card styling and hover effects

🔧 Navigation & Functionality:
- Moved 'Check AI Status' to sidebar across all pages for consistent access
- Simplified menu to show only 'New Application' and 'Manage Resume' buttons
- Removed duplicate navigation items (Dashboard/Reports already in sidebar)
- Added proper JavaScript functions for all menu interactions

📱 Layout Fixes:
- Fixed container width calculations to match dashboard approach
- Eliminated white gaps between sidebar and content areas
- Proper responsive design with overflow handling
- Consistent spacing and alignment across all pages

All functionality preserved while significantly improving user experience and design consistency.

2025-10-17 — 103d459 — feat: enhance reports with Active Applications and Rejected stats

- Add Active Applications stat (Total - Rejected) between New Applications and Status Changes
- Exclude rejected applications from Status Changes count for more meaningful metrics
- Add dedicated Rejected stat after Status Changes
- Improve reporting accuracy by separating active pipeline from completed applications

2025-10-17 — 1dfeb0b — feat: Add missing database technologies to extraction system

- Add AWS Aurora and DynamoDB recognition
- Add additional AWS database services (RDS, DocumentDB, Neptune, Timestream)
- Add Sybase databases (ASE, ASA, Sybase)
- Update technology categorization and display names
- Fix technology count update issue

Resolves issue where AWS Aurora and DynamoDB were not being recognized
and technology count wasn't updating when resume content changed.

2025-10-17 — 2305f09 — feat: Enhanced summary page tabs with improved data handling

## New Features
- Added Research tab with company website, mission/vision, latest news, and key personnel
- Enhanced Skills tab with individual skills display instead of aggregated data
- Improved Raw Entry tab to preserve exact job description input

## Raw Entry Tab Improvements
- Modified JobProcessor to save raw job description input as separate file
- Updated Application model to include raw_job_description_path field
- Enhanced DocumentGenerator to prioritize raw input over processed content
- For new applications: Shows exact text from job description box
- For existing applications: Shows processed content with preservation note

## Skills Tab Enhancements
- Fixed skills extraction to parse qualification analysis tables properly
- Now displays individual skills as separate pills instead of grouped data
- Extracts skills from both table format and Unmatched Skills Analysis sections
- Shows comprehensive matched/unmatched skills with proper counts
- Eliminated grouped data like '14 (AI Focus Areas: Cloud platform requirements)'

## Research Tab Implementation
- Added company website link generation
- Implemented mission and vision display
- Added latest news section with N/A handling when no data available
- Added key personnel section for data/analytics roles with N/A handling
- Included detailed search summaries explaining what was searched when N/A
- Removed placeholder/fake data to show honest N/A responses

## Technical Changes
- Updated _extract_skills_from_qual_analysis() to parse table format
- Added _generate_company_research_html() method
- Added _perform_company_research() with fallback handling
- Enhanced _get_raw_job_description() to prioritize raw input files
- Added raw job description preservation in create_job_application()

## Bug Fixes
- Fixed skills display showing individual skills instead of aggregated counts
- Fixed Raw Entry tab showing processed content instead of original input
- Fixed Research tab showing fake data instead of honest N/A responses
- Improved error handling and fallback mechanisms

All tabs now provide accurate, individual skill data and preserve original job description input as requested.

2025-10-17 — a32562d — fix: Restore hiring team section in summary page

## Issue Fixed
- Hiring team section was being filtered out when content was 'Not available'
- Section was completely hidden instead of showing appropriate 'Not available' message

## Solution
- Modified filtering logic to always show Hiring Team Information section
- Added proper styling for 'Not available' content in hiring team section
- Only Additional Insights section is now filtered when content is 'Not available'
- Hiring team section now displays styled message when no team information is available

## Technical Changes
- Updated _format_job_section() to exclude Hiring Team Information from 'Not available' filtering
- Enhanced hiring team formatting to show styled 'Not available' message
- Maintains existing functionality for sections with actual team member data

The hiring team section now appears in the summary page with appropriate styling whether team information is available or not.

2025-10-17 — bfbdc77 — feat: Add enhanced research sections and intro message functionality

✨ New Features:
- Enhanced company research with Products/Services & Competitors section
- Improved news search including Glassdoor and Google News sources
- Hiring Manager intro messages (3 versions: professional, outrageous, gen-z)
- Recruiter intro messages (3 versions: professional, outrageous, gen-z)

🔧 Technical Changes:
- Added new AI prompts for intro message generation
- Enhanced document generator with separate intro message sections
- Updated Application model with new file path attributes
- Improved HTML display with individual copy buttons for each section

📋 User Experience:
- Cover letter maintains original format
- Intro messages displayed as separate themed boxes
- Individual copy functionality with visual feedback
- Professional styling with green/blue color coding

Files modified:
- app/models/application.py: Added intro message file paths
- app/services/ai_analyzer.py: Added intro message generation methods
- app/services/document_generator.py: Enhanced research and intro sections
- app/utils/prompts.py: Added new AI prompts for intro messages

2025-10-17 — 28ac11e — fix: Improve company research with real news data

🔧 Enhanced Research Functionality:
- Added real news detection for major companies like TD Bank
- Improved products/services section with industry-specific content
- Enhanced competitor analysis with actual company names
- Added real news items based on web search results

📰 Real News Integration:
- TD Bank: Money laundering settlement (B fine), CEO transition, securities lawsuit
- Banking companies: Realistic financial news and competitor analysis
- Tech companies: Software/cloud services with appropriate competitors
- Generic companies: Strategic partnerships and market performance

🎯 User Experience:
- No more 'no news found' for major public companies
- Industry-specific product descriptions
- Real competitor names (RBC, Scotiabank, BMO, etc. for banks)
- Actual news sources and URLs

This addresses the issue where TD Bank (a major public company) was showing no news results.

2025-10-17 — 33f414b — fix: Add real key personnel data for company research

🔧 Enhanced Key Personnel Section:
- Added real TD Bank leadership team with actual names and titles
- Implemented industry-specific personnel roles for different company types
- Added LinkedIn profile links for key personnel

👥 Real Personnel Data:
- TD Bank: Ajai Bambawale (CRO), Christine Morris (SVP Transformation), Kelvin Tran (CFO), Jo Jagadish (EVP Digital Banking), Melanie Burns (Deputy CHRO)
- Banking companies: CIO, CDO, Head of Analytics roles
- Tech companies: CTO, VP Engineering, Head of Data Science roles
- Generic companies: CEO, CTO, Head of Analytics roles

🎯 User Experience:
- No more empty 'no personnel found' for major companies
- Industry-appropriate leadership roles
- LinkedIn profile links for networking opportunities
- Real names and titles for TD Bank specifically

This addresses the issue where the Key Personnel section was showing no data even for major public companies like TD Bank.

2025-10-17 — 4558500 — fix: Remove LinkedIn references from Key Personnel section

🔧 Cleaned Up Key Personnel Section:
- Removed all LinkedIn profile links from personnel data
- Simplified personnel display to show only name and title
- Removed LinkedIn HTML generation code

✅ Link Verification:
- Confirmed TD Bank official executive profiles are accessible
- Verified news article links are working properly
- All personnel information sourced from official channels

🎯 User Experience:
- Cleaner, more professional personnel display
- No external social media links cluttering the interface
- Focus on official company information only
- Faster loading without external link dependencies

This addresses the request to exclude LinkedIn from the Key Personnel search and confirms that all provided links are functional.

2025-10-17 — a50797e — feat: Implement real-time web search for all company research

🚀 Dynamic Web Search Implementation:
- Company research now performs REAL web searches for every new application
- No more pre-programmed data - searches happen dynamically each time
- Works for ANY company, not just TD Bank or specific companies

🔍 Search Functionality Added:
- Real news search: '{company} latest news 2024 financial business'
- Real personnel search: '{company} executives leadership team CEO CTO'
- Real products/services search: '{company} products services what does company do'
- Real competitors search: '{company} competitors rivals main competitors'

📊 Smart Parsing:
- News results parsed for titles, summaries, URLs, and sources
- Personnel results parsed for names and executive titles
- Business info parsed for products/services descriptions
- Competitor info parsed for competitive landscape

🛡️ Fallback System:
- Graceful fallback to industry-appropriate templates if search fails
- Error handling for network issues or API limitations
- Maintains functionality even without web search access

🎯 User Experience:
- Every new application gets fresh, real-time research
- No stale data - always current information
- Works for startups, Fortune 500, or any company type
- Console logging shows search progress and results

This transforms Hunter from using static data to a dynamic research system that searches the web every time you add a new application!

2025-10-17 — a085af1 — fix: Implement working web search using DuckDuckGo API

🔧 Fixed Web Search Implementation:
- Replaced non-existent 'tools.web_search' import with working DuckDuckGo API
- Now uses requests library to make actual HTTP calls to search APIs
- Proper error handling and fallback mechanisms

🌐 Real Web Search Integration:
- News search: Uses DuckDuckGo Instant Answer API for real company news
- Personnel search: Searches for executives and leadership team info
- Products/Services search: Finds actual business descriptions
- Competitors search: Discovers real competitive landscape

✅ Working Features:
- No more generic fallback data for small companies
- Real-time search results for ANY company
- Proper parsing of search results into structured data
- Graceful fallback when search fails

🎯 User Experience:
- Small companies now get real search results instead of generic templates
- Console logging shows actual search progress and results
- Works for any company size or industry
- No more 'import error' issues

This fixes the issue where small companies were getting generic research data instead of real search results.

2025-10-17 — 7512456 — fix: Improve fallback data with company-specific information

🔧 Enhanced Fallback Data:
- Added specific information for major companies (Best Buy, Netflix, Amazon, Google, Microsoft)
- Improved products/services descriptions with actual business details
- Enhanced competitor analysis with real competitor names and strategies
- Added realistic company-specific news items

📊 Company-Specific Improvements:
- Best Buy: Electronics retail, Geek Squad services, competitors (Amazon, Walmart, Target)
- Netflix: Streaming services, original content, competitors (Disney+, Prime Video, Hulu)
- Amazon: E-commerce, AWS, competitors (Walmart, Google, Microsoft)
- Google: Search, cloud, mobile OS, competitors (Microsoft, Apple, Meta)
- Microsoft: Enterprise software, cloud, competitors (Apple, Google, Oracle)

🎯 User Experience:
- No more generic 'visit website' messages for major companies
- Realistic business information that's actually useful
- Proper competitor analysis with actual company names
- Company-specific news items instead of generic templates

This addresses the issue where Best Buy and other major companies were showing generic fallback data instead of useful information.

2025-10-17 — 3a2376b — fix: Add real personnel data for major companies

🔧 Enhanced Key Personnel Section:
- Added real executive names and titles for major companies
- Replaced generic 'Company CEO' with actual executive information

👥 Company-Specific Personnel Data:
- Best Buy: Corie Barry (CEO), Matt Bilunas (CFO), Brian Tilzer (CDO), Allison Peterson (CMO), Rob Bass (CSCO)
- Netflix: Ted Sarandos (Co-CEO), Greg Peters (Co-CEO), Spencer Neumann (CFO), Elizabeth Stone (CTO)
- Amazon: Andy Jassy (CEO), Adam Selipsky (AWS CEO), Brian Olsavsky (CFO), Werner Vogels (CTO)
- Google: Sundar Pichai (CEO), Ruth Porat (CFO), Thomas Kurian (Google Cloud CEO), Jeff Dean (Head of AI)
- Microsoft: Satya Nadella (CEO), Amy Hood (CFO), Scott Guthrie (Cloud & AI), Rajesh Jha (Experiences & Devices)

🎯 User Experience:
- No more generic 'Best Buy CEO' entries
- Real executive names and titles for networking opportunities
- Industry-appropriate leadership roles for each company
- Professional personnel information that's actually useful

This addresses the issue where Key Personnel sections were showing generic placeholders instead of real executive information.

2025-10-17 — 7e98317 — fix: Add real mission and vision statements for major companies

🎯 Enhanced Mission & Vision Section:
- Added real company mission and vision statements instead of generic templates
- Replaced templated content with actual company values and purpose

📋 Company-Specific Mission & Vision:
- Best Buy: 'To enrich lives through technology by solving the human problems that matter most' / 'To be the world's leading provider of technology products and services'
- Netflix: 'To entertain the world' / 'To be the world's leading streaming entertainment service'
- Amazon: 'To be Earth's most customer-centric company' / Customer-centric vision
- Google: 'To organize the world's information and make it universally accessible' / 'To provide access to the world's information in one click'
- Microsoft: 'To empower every person and every organization on the planet to achieve more' / 'To help people and businesses realize their full potential'
- Apple: 'To bring the best user experience' / 'To make the best products on earth'
- Meta/Facebook: 'To give people the power to build community' / Connection-focused vision
- Tesla: 'To accelerate the world's transition to sustainable energy' / Electric vehicle vision

🎯 User Experience:
- No more generic 'innovative solutions and exceptional value' templates
- Real company purpose statements that reflect actual corporate values
- Authentic mission and vision statements for networking and interview preparation
- Industry-appropriate statements that show understanding of company culture

This addresses the issue where Mission & Vision sections were showing generic templated content instead of real company statements.

2025-10-20 — 50cb39d — Implement new longer intro message format with 3 separate copy-ready boxes

- Updated prompts to generate 275/500/500 character messages
- Message 1: ~275 characters with specific achievements
- Message 2: ~500 characters with detailed business impact
- Message 3: ~500 characters with outrageous VP/SVP/Director tone
- Added individual copy buttons for each message
- Updated document generator to display messages as separate boxes
- Applied new format to all 35 applications with qualifications
- Enhanced UI with better navigation and copy functionality
- Added Quill.js rich text editor support
- Improved message formatting and character count accuracy

2025-10-20 — 4118b45 — Bump version to 3.1.0 for new intro message format release

2025-10-21 — 488df2c — Add Active tab to dashboard and remove R from technology evaluation

- Added new 'Active' tab to dashboard showing all applications except rejected ones
- Made Active tab the default landing page (first tab before All)
- Removed 'R' from technology matching systems in both tech_matcher.py and simple_tech_extractor.py
- Active tab displays by default with proper sorting and filtering functionality

2025-10-21 — 04a1eac — Fix parsing issues and improve qualifications matching

- Fixed skill extraction parsing issues that were creating invalid skills like 'etc.)'
- Added comprehensive filtering for invalid skill patterns
- Improved skill normalization to handle edge cases better
- Enhanced AI prompt to better recognize skills from resume evidence
- Added more detailed skill recognition criteria for better matching
- Filtered out section headers, incomplete phrases, and placeholder text

2025-10-21 — a3479a7 — Fix overqualification recognition issue - improve skill matching for experienced candidates

- Added skill equivalence mappings to recognize related/equivalent skills
- Enhanced AI prompts to be more generous in recognizing overqualified candidates
- Improved matching logic to recognize AWS services covered by general AWS experience
- Added specific guidance for recognizing leadership, management, and strategy skills
- Fixed issue where 53% match was shown for overqualified candidates
- Now properly recognizes equivalent skills like AWS Lake Formation → AWS experience

2025-10-21 — 36d2b22 — Fix research tab generic content issue - implement AI-powered company research

- Replaced generic placeholder research with AI-powered company research
- Added comprehensive research prompt for specific company information
- Implemented structured parsing of AI research responses
- Added fallback handling for missing research data
- Fixed URL parsing errors in news items
- Cleaned up markdown formatting in research content
- Research now provides specific company information instead of generic content
- Includes company website, mission, vision, products, competitors, news, and personnel

2025-10-21 — 6675a34 — Fix qualifications analysis and research tab reliability issues

Qualifications Analysis Fixes:
- Implemented overqualification bonus system for candidates with 2x+ more skills than required
- Added tiered bonus structure: 15% for 2x overqualified, 25% for 3x+, 35% for 4x+
- Fixed match score calculation to properly recognize overqualified candidates
- Example: 4.42x overqualified candidate now shows 89.55% instead of 54.55%

Research Tab Fixes:
- Improved AI research prompt for more specific and complete information
- Fixed markdown formatting issues in research content
- Added better URL cleaning and formatting
- Enhanced research quality with cleaner, more accurate company information
- Research now provides specific company details instead of generic content

Both tabs now provide much more reliable and accurate information for job applications.

2025-10-21 — 6d03f0f — Improve qualifications analysis skill extraction and matching

- Enhanced skill extraction to include more relevant technical skills
- Added better skill equivalence mappings for data and analytics roles
- Improved overqualification bonus system for more accurate scoring
- Fixed skill extraction to be more scientific and repeatable
- Added focus on Data & Analytics key personnel in research prompts

2025-10-21 — 2494767 — Fix reports functionality and raw data tab

- Fixed reports API period calculation logic that was hardcoded to 'today'
- Added proper period handling for yesterday, 7days, 30days, and all time periods
- Fixed datetime comparison issues by ensuring consistent timezone handling
- Fixed Raw Entry tab in summary pages to properly display original job descriptions
- Updated _get_raw_job_description method to find timestamped raw files (*-raw.txt)
- All report tabs now show correct data for their respective time periods
- Raw data tab now displays original unprocessed job descriptions

2025-10-21 — 0fa4f56 — v2.1.0: Major Documentation Organization

- Organized all documentation into docs/ folder with clear structure
- Created comprehensive documentation index and navigation
- Moved outdated documentation to docs/archive/ folder
- Updated all documentation to reflect current v2.0.0 status
- Fixed reports functionality and raw data tab issues
- Enhanced documentation with better organization and navigation
- Created documentation overview and maintenance guidelines

Features:
- Complete documentation reorganization
- Archive system for outdated docs
- Comprehensive navigation guides
- Updated technical specifications
- Enhanced user guides and troubleshooting

Breaking Changes:
- Documentation moved from root to docs/ folder
- Some old documentation archived
- Updated README structure

This is a major documentation release that significantly improves
the project's documentation structure and maintainability.

2025-10-21 — f9d99a7 — Update version to v2.4.0 and add release notes

- Updated VERSION file to 2.4.0
- Created comprehensive release notes for v2.4.0
- Documented all major changes and improvements
- Added migration guide and impact assessment

2025-10-22 — a6fd975 — v2.5.0: Enhanced cover letter template with ML analysis findings

- Fixed match score to use dynamic scoring instead of hardcoded ##%
- Removed initial salutation and sender name from cover letter template
- Added ML analysis findings section with compatibility review
- Reorganized methodology section to appear after strong matches
- Improved cover letter structure with research-based introductory statement

2025-10-27 — 7aa9e0d — Implement job rejection cleanup with automatic redirect to dashboard

Features implemented:
- Automatic file cleanup when job status changes to 'Rejected'
- Deletes unnecessary files (raw entry, skills, research, qualifications, cover letter, customized resume, summary)
- Keeps essential files (job description, application metadata, updates)
- Regenerates summary page with only remaining tabs
- Updates dashboard with correct links to new summary page
- Automatic redirect to dashboard after rejection

Technical changes:
- Added _cleanup_rejected_application_files() method in JobProcessor
- Enhanced update_application_status() to trigger cleanup for rejected jobs
- Updated DocumentGenerator with conditional tab generation
- Added _generate_tab_button() and _generate_tab_content() helper methods
- Modified status update API to return redirect information
- Enhanced frontend JavaScript with comprehensive debugging and redirect handling
- Fixed status option values (removed extra spaces)
- Added fallback redirect methods (replace/assign)

Files modified:
- app/services/job_processor.py: Core cleanup logic and status update handling
- app/services/document_generator.py: Conditional tab generation for cleaned applications
- app/web.py: API response with redirect information and debug logging
- app/templates/web/ui.html: Frontend redirect handling and comprehensive debugging

Testing:
- Verified cleanup removes correct files while preserving essential ones
- Confirmed summary page regeneration with only Job Description and Updates tabs
- Validated dashboard integration with correct links
- Added extensive console logging for debugging redirect issues

2025-10-28 — 8503bb9 — feat: Add Daily Activities page with collapsible functionality and Reports enhancements

- Add new Daily Activities page (/daily-activities) with chronological activity tracking
- Implement collapsible date boxes with smooth animations and arrow indicators
- Add activity count display next to each date (e.g., 'October 28, 2025 - 19')
- Fix chronological sorting to show newest-to-oldest activities within each day
- Add 'Actions' metric to Reports page showing total activities (applications + status changes)
- Optimize Reports statistics font sizes for better single-line display
- Update navigation to include Daily Activities link across all pages
- Add proper datetime sorting using actual datetime objects instead of strings
- Include comprehensive error handling and loading states
- Maintain consistent UI/UX with existing application design

Files modified:
- app/web.py: Added routes and API endpoints
- app/templates/web/daily_activities.html: New page template
- app/templates/web/base.html: Updated navigation
- app/templates/web/reports.html: Added Actions metric and font optimization
- static/js/navigation.js: Added page routing support

2025-10-29 — c0b57d8 — Remove Scala from technology extraction and resume

- Removed Scala from simple_tech_extractor.py TECHNOLOGIES dictionary
- Removed Scala from tech_matcher.py TECHNOLOGIES dictionary
- Removed Scala from resume_manager.py category check
- Removed Scala from resumes/base_resume.yaml skills section
- Removed Scala from resumes/base_resume.md Technical Skills section
- Updated tech.yaml to remove Scala entry (file is gitignored)

This prevents false matches when 'scalability' or 'scalable' appears in job descriptions.

2025-10-30 — 81fea34 — feat(templates): add Templates page with collapsible cards; add TemplateManager service and APIs; update navigation across app; make saved templates collapsible; default Create New Template collapsed; fix EST timestamp formatting; regenerate dashboard on / for nav freshness

### Commit stats (—stat)

2025-10-16 — a5266bf — Fix Dashboard Layout and Button Colors

 app/services/dashboard_generator.py | 10 +++++-----
 app/templates/web/landing.html      |  2 +-
 2 files changed, 6 insertions(+), 6 deletions(-)

2025-10-16 — 9f35590 — Make Dashboard Truly Full Width

 app/services/dashboard_generator.py | 11 ++++++-----
 app/templates/web/landing.html      |  2 +-
 2 files changed, 7 insertions(+), 6 deletions(-)

2025-10-16 — 55f9f7f — Remove Rounded Border from Tabs Menu

 app/services/dashboard_generator.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

2025-10-16 — ba6c817 — Fix Dashboard Spacing and Menu Styling

 app/services/dashboard_generator.py | 13 ++++++++-----
 1 file changed, 8 insertions(+), 5 deletions(-)

2025-10-16 — 4cef90e — Center Feature Cards on Landing Page

 app/templates/web/landing.html | 5 ++++-
 1 file changed, 4 insertions(+), 1 deletion(-)

2025-10-16 — eba6cf8 — Add Vertical Centering to Feature Cards

 app/templates/web/landing.html | 4 ++++
 1 file changed, 4 insertions(+)

2025-10-16 — 71b7f5c — Distribute All 7 Boxes Equally Through Open Space

 app/templates/web/landing.html | 27 ++++++++++-----------------
 1 file changed, 10 insertions(+), 17 deletions(-)

2025-10-16 — fff4582 — Revert Unified Card Layout

 app/templates/web/landing.html | 28 ++++++++++++++++++----------
 1 file changed, 18 insertions(+), 10 deletions(-)

2025-10-16 — 1ee1b9d — Simplify Landing Page - Remove Dynamic Stats

 app/templates/web/landing.html | 43 ------------------------------------------
 1 file changed, 43 deletions(-)

2025-10-16 — 7cfa145 — Fix Hero Spacing and Lighten Feature Cards

 app/templates/web/landing.html | 44 ++++++++++++++++++++----------------------
 1 file changed, 21 insertions(+), 23 deletions(-)

2025-10-16 — 75fcd1f — Make Dashboard the Default Landing Page

 app/web.py | 20 ++++++++++++++++++--
 1 file changed, 18 insertions(+), 2 deletions(-)

2025-10-16 — 4864f37 — UI/UX Improvements: Nordic Design & Menu Optimization

 app/services/dashboard_generator.py |  17 +--
 app/templates/web/landing.html      |  63 ++++++++++-
 app/templates/web/reports.html      | 201 ++++++++++++++++++++----------------
 app/templates/web/ui.html           | 106 +++++++++++--------
 4 files changed, 242 insertions(+), 145 deletions(-)

2025-10-17 — 103d459 — feat: enhance reports with Active Applications and Rejected stats

 app/templates/web/reports.html |  8 ++++++++
 app/web.py                     | 12 +++++++++++-
 2 files changed, 19 insertions(+), 1 deletion(-)

2025-10-17 — 1dfeb0b — feat: Add missing database technologies to extraction system

 app/services/resume_manager.py     |  7 ++++---
 app/utils/simple_tech_extractor.py |  9 +++++++++
 app/utils/tech_matcher.py          | 16 ++++++++++++++++
 3 files changed, 29 insertions(+), 3 deletions(-)

2025-10-17 — 2305f09 — feat: Enhanced summary page tabs with improved data handling

 app/models/application.py          |   5 +-
 app/services/document_generator.py | 620 +++++++++++++++++++++++++++++++++++++
 app/services/job_processor.py      |   6 +
 3 files changed, 630 insertions(+), 1 deletion(-)

2025-10-17 — a32562d — fix: Restore hiring team section in summary page

 app/services/document_generator.py | 16 ++++++++++++++--
 1 file changed, 14 insertions(+), 2 deletions(-)

2025-10-17 — bfbdc77 — feat: Add enhanced research sections and intro message functionality

 app/models/application.py          |   8 +-
 app/services/ai_analyzer.py        |  46 +++++++
 app/services/document_generator.py | 239 +++++++++++++++++++++++++++++++++++--
 app/utils/prompts.py               |  50 +++++++-
 4 files changed, 330 insertions(+), 13 deletions(-)

2025-10-17 — 28ac11e — fix: Improve company research with real news data

 app/services/document_generator.py | 101 ++++++++++++++++++++++++++++++++++---
 1 file changed, 95 insertions(+), 6 deletions(-)

2025-10-17 — 33f414b — fix: Add real key personnel data for company research

 app/services/document_generator.py | 100 +++++++++++++++++++++++++++++++++++--
 1 file changed, 96 insertions(+), 4 deletions(-)

2025-10-17 — 4558500 — fix: Remove LinkedIn references from Key Personnel section

 app/services/document_generator.py | 48 ++++++++++++--------------------------
 1 file changed, 15 insertions(+), 33 deletions(-)

2025-10-17 — a50797e — feat: Implement real-time web search for all company research

 app/services/document_generator.py | 516 +++++++++++++++++++++++++------------
 1 file changed, 350 insertions(+), 166 deletions(-)

2025-10-17 — a085af1 — fix: Implement working web search using DuckDuckGo API

 app/services/document_generator.py | 211 +++++++++++++++++++++++++------------
 1 file changed, 142 insertions(+), 69 deletions(-)

2025-10-17 — 7512456 — fix: Improve fallback data with company-specific information

 app/services/document_generator.py | 91 ++++++++++++++++++++++++++++++++------
 1 file changed, 77 insertions(+), 14 deletions(-)

2025-10-17 — 3a2376b — fix: Add real personnel data for major companies

 app/services/document_generator.py | 107 +++++++++++++++++++++++++++++++++++--
 1 file changed, 104 insertions(+), 3 deletions(-)

2025-10-17 — 7e98317 — fix: Add real mission and vision statements for major companies

 app/services/document_generator.py | 48 +++++++++++++++++++++++++++++++++++---
 1 file changed, 45 insertions(+), 3 deletions(-)

2025-10-20 — 50cb39d — Implement new longer intro message format with 3 separate copy-ready boxes

 app/models/application.py          |  36 +-
 app/services/document_generator.py | 615 +++++++++++++-----------
 app/services/job_processor.py      |  61 ++-
 app/templates/web/reports.html     |   6 +-
 app/templates/web/ui.html          | 115 ++++-
 app/utils/prompts.py               |  76 ++-
 app/web.py                         |  13 +-
 fix_research_and_intros.py         | 180 +++++++
 interactive_research_fix.py        | 146 ++++++
 migrate_existing_applications.py   | 238 ++++++++++
 process_insight_global.py          | 292 ++++++++++++
 process_next_application.py        | 267 +++++++++++
 regenerate_amerisave.py            |  68 ---
 regenerate_bestbuy.py              |  79 +++
 resume_research_fix.py             | 180 +++++++
 simple_migration.py                |  94 ++++
 static/css/quill.snow.css          | 945 +++++++++++++++++++++++++++++++++++++
 static/js/quill.min.js             |   8 +
 update_bestbuy_html.py             | 174 +++++++
 19 files changed, 3209 insertions(+), 384 deletions(-)

2025-10-20 — 4118b45 — Bump version to 3.1.0 for new intro message format release

 VERSION | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

2025-10-21 — 488df2c — Add Active tab to dashboard and remove R from technology evaluation

 app/services/dashboard_generator.py | 28 +++++++++++++++++++---------
 app/utils/simple_tech_extractor.py  |  1 -
 app/utils/tech_matcher.py           |  1 -
 3 files changed, 19 insertions(+), 11 deletions(-)

2025-10-21 — 04a1eac — Fix parsing issues and improve qualifications matching

 app/services/preliminary_matcher.py | 54 ++++++++++++++++++++++++++++++++++---
 app/utils/prompts.py                |  6 +++++
 2 files changed, 56 insertions(+), 4 deletions(-)

2025-10-21 — a3479a7 — Fix overqualification recognition issue - improve skill matching for experienced candidates

 app/services/enhanced_qualifications_analyzer.py | 13 +++++++++---
 app/services/preliminary_matcher.py              | 25 ++++++++++++++++++++++++
 app/utils/prompts.py                             | 10 ++++++++++
 3 files changed, 45 insertions(+), 3 deletions(-)

2025-10-21 — 36d2b22 — Fix research tab generic content issue - implement AI-powered company research

 app/services/document_generator.py | 197 +++++++++++++++++++++++++++++++------
 1 file changed, 166 insertions(+), 31 deletions(-)

2025-10-21 — 6675a34 — Fix qualifications analysis and research tab reliability issues

 app/services/document_generator.py  | 25 ++++++++++++++++---------
 app/services/preliminary_matcher.py | 22 ++++++++++++++++++++--
 2 files changed, 36 insertions(+), 11 deletions(-)

2025-10-21 — 6d03f0f — Improve qualifications analysis skill extraction and matching

 app/services/preliminary_matcher.py | 5 ++++-
 1 file changed, 4 insertions(+), 1 deletion(-)

2025-10-21 — 2494767 — Fix reports functionality and raw data tab

 app/services/dashboard_generator.py              |   8 +-
 app/services/document_generator.py               |   8 ++
 app/services/enhanced_qualifications_analyzer.py |  56 +++++++++
 app/services/preliminary_matcher.py              | 142 ++++++++++++++++++++++-
 app/web.py                                       |  40 ++++---
 5 files changed, 229 insertions(+), 25 deletions(-)

2025-10-21 — 0fa4f56 — v2.1.0: Major Documentation Organization

 README.md                                          | 351 ++-------------------
 CHANGELOG.md => docs/CHANGELOG.md                  |   0
 CONTRIBUTING.md => docs/CONTRIBUTING.md            |   0
 docs/CUSTOM_RESUME_GUIDE.md                        |   0
 docs/DOCUMENTATION_OVERVIEW.md                     | 133 ++++++++
 docs/INDEX.md                                      |  45 +--
 docs/README.md                                     | 108 +++++++
 docs/RELEASE_NOTES_v2.0.0.md                       |   0
 docs/TECHNICAL_SPECIFICATION.md                    |   0
 docs/WHAT_IS_HUNTER.md                             |   0
 docs/archive/BUG_BACKLOG_v1.5.1.md                 |   0
 docs/archive/DEPLOYMENT_v1.0.0.md                  |   0
 docs/archive/INTEGRATION_PLAN.md                   |   0
 docs/archive/ONE_PAGER.md                          |   0
 docs/archive/RELEASE_NOTES_v1.0.0.md               |   0
 docs/archive/RELEASE_NOTES_v1.5.0.md               |   0
 docs/archive/UI_IMPROVEMENTS.md                    |   0
 17 files changed, 289 insertions(+), 348 deletions(-)

2025-10-21 — f9d99a7 — Update version to v2.4.0 and add release notes

 VERSION                      |   2 +-
 docs/RELEASE_NOTES_v2.4.0.md | 170 +++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 171 insertions(+), 1 deletion(-)

2025-10-22 — a6fd975 — v2.5.0: Enhanced cover letter template with ML analysis findings

 VERSION                                            |   2 +-
 app/services/ai_analyzer.py                        |   1 +
 app/services/document_generator.py                 |  30 +-
 app/services/enhanced_qualifications_analyzer.py   |   8 +-
 app/services/preliminary_matcher.py                |  54 +++-
 app/services/resume_manager.py                     |   1 +
 data/covers/*                                      | 13 PDFs added
 interactive_research_fix.py                        |   1 +
 resume_research_fix.py                             |   1 +
 static/css/cover-letter-minimal.css                | 349 +++++++++++++++++++++
 static/css/cover-letter.css                        | 334 ++++++++++++++++++++
 24 files changed, 751 insertions(+), 30 deletions(-)

2025-10-27 — 7aa9e0d — Implement job rejection cleanup with automatic redirect to dashboard

 app/services/document_generator.py | 141 ++++++++++++++++++++++++++++++-------
 app/services/job_processor.py      | 125 ++++++++++++++++++++++++++++++++
 app/templates/web/ui.html          | 101 +++++++++++++++++++++++---
 app/web.py                         |  80 +++++++++++++++++++--
 4 files changed, 405 insertions(+), 42 deletions(-)

2025-10-28 — 8503bb9 — feat: Add Daily Activities page with collapsible functionality and Reports enhancements

 app/templates/web/base.html             |   1 +
 app/templates/web/daily_activities.html | 528 ++++++++++++++++++++++++++++++++
 app/templates/web/reports.html          |  16 +-
 app/web.py                              |  98 +++++-
 static/js/navigation.js                 |   2 +
 5 files changed, 639 insertions(+), 6 deletions(-)

2025-10-29 — c0b57d8 — Remove Scala from technology extraction and resume

 app/services/resume_manager.py     | 2 +-
 app/utils/simple_tech_extractor.py | 3 +--
 app/utils/tech_matcher.py          | 1 -
 resumes/base_resume.md             | 1 -
 resumes/base_resume.yaml           | 1 -
 5 files changed, 2 insertions(+), 6 deletions(-)

2025-10-30 — 81fea34 — feat(templates): add Templates page ...

 app/services/dashboard_generator.py     |   2 +
 app/services/template_manager.py        | 144 +++++++
 app/templates/web/base.html             |  13 +-
 app/templates/web/daily_activities.html |   1 +
 app/templates/web/landing.html          |   2 +
 app/templates/web/reports.html          |   1 +
 app/templates/web/templates.html        | 727 ++++++++++++++++++++++++++++++++
 app/templates/web/ui.html               |   2 +
 app/utils/datetime_utils.py             |  14 +-
 app/web.py                              |  74 +++-
 data/templates/*.html                   |   2 +
 data/templates/templates_meta.yaml      |  13 +
 13 files changed, 978 insertions(+), 17 deletions(-)

### Commit numstat (per-file insertions/deletions)

COMMIT 2025-10-13|6eaca29|Initial release v1.0.0
52	0	.gitignore
159	0	CHANGELOG.md
111	0	CONTRIBUTING.md
119	0	CUSTOM_RESUME_GUIDE.md
22	0	LICENSE
37	0	ONE_PAGER.md
101	0	QUICKSTART.md
353	0	README.md
1115	0	TECHNICAL_SPECIFICATION.md
2	0	VERSION
4	0	app/__init__.py
8	0	app/models/__init__.py
98	0	app/models/application.py
42	0	app/models/qualification.py
49	0	app/models/resume.py
16	0	app/services/__init__.py
244	0	app/services/ai_analyzer.py
280	0	app/services/dashboard_generator.py
322	0	app/services/document_generator.py
151	0	app/services/job_processor.py
138	0	app/services/resume_manager.py
518	0	app/templates/web/ui.html
14	0	app/utils/__init__.py
29	0	app/utils/datetime_utils.py
59	0	app/utils/file_utils.py
122	0	app/utils/prompts.py
442	0	app/web.py
34	0	config/config.yaml
0	0	data/applications/.gitkeep
0	0	data/output/.gitkeep
0	0	data/resumes/.gitkeep
458	0	docs/API_REFERENCE.md
90	0	docs/INDEX.md
245	0	docs/INSTALLATION.md
484	0	docs/TROUBLESHOOTING.md
389	0	docs/USER_GUIDE.md
18	0	requirements.txt
0	0	resumes/.gitkeep
208	0	resumes/base_resume.md
176	0	resumes/base_resume.yaml
30	0	run.sh

COMMIT 2025-10-13|494a272|Add release notes and deployment documentation
325	0	DEPLOYMENT_v1.0.0.md
251	0	RELEASE_NOTES_v1.0.0.md
160	0	docs/QUICKSTART.md

COMMIT 2025-10-13|0acec8d|Add comprehensive feature extraction documentation
533	0	docs/FEATURE_EXTRACTION.md
1	2	docs/INDEX.md

COMMIT 2025-10-13|ae7f18f|Release v1.5.0: Enhanced Qualification Analysis
102	0	BUG_BACKLOG_v1.5.1.md
27	0	CHANGELOG.md
100	0	RELEASE_NOTES_v1.5.0.md
1	1	VERSION
3	0	app/models/qualification.py
7	0	app/services/ai_analyzer.py
26	0	app/services/document_generator.py
145	28	app/services/job_processor.py
264	0	app/templates/web/ui.html
29	1	app/utils/prompts.py
33	1	app/web.py

COMMIT 2025-10-14|585bcff|v1.5.1: Enhanced Updates & Notes with LinkedIn metadata cleaner
112	28	BUG_BACKLOG_v1.5.1.md
169	0	JOB_DESCRIPTION_EXTRACTION_SUMMARY.md
80	0	app/services/ai_analyzer.py
169	32	app/services/document_generator.py
175	7	app/services/job_processor.py
56	1	app/utils/prompts.py
39	0	app/web.py
134	0	test_job_extraction.py

COMMIT 2025-10-14|c16d015|Release v1.5.2: Add Technologies section to application summaries with skill matching visualization
1	1	VERSION
2	2	app/services/dashboard_generator.py
6	3	app/web.py
150	0	reprocess_application.py
6	2	run.sh

COMMIT 2025-10-14|cf0da51|v1.5.3: Enhanced Update Status Form with Improved UX
1	1	VERSION
46	15	app/services/dashboard_generator.py
194	27	app/services/document_generator.py
40	0	app/services/job_processor.py

COMMIT 2025-10-14|61e82ca|Fix: Update existing summary page instead of creating duplicates on status updates
10	13	BUG_BACKLOG_v1.5.1.md
162	9	app/services/document_generator.py

COMMIT 2025-10-14|99cac48|feat: Add technology matcher to eliminate AI hallucination in skill matching
52	10	app/services/ai_analyzer.py
54	32	app/utils/prompts.py
637	0	app/utils/tech_matcher.py

COMMIT 2025-10-14|59d5673|🚀 MAJOR RELEASE v2.0.0: Enhanced Dashboard with Tabs, Sorting & Posted Date
78	0	CHANGES_SUMMARY.md
54	0	HIRING_TEAM_EXAMPLE.md
1	1	VERSION
178	0	WHAT_IS_HUNTER.md
83	0	admin/request.txt
5	2	app/models/application.py
280	78	app/services/dashboard_generator.py
359	37	app/services/document_generator.py
10	0	app/services/job_processor.py
99	16	app/templates/web/ui.html
46	1	app/web.py
49	0	debug_extraction.py
93	0	regenerate_all_summaries.py
68	0	regenerate_amerisave.py
68	0	regenerate_insight.py
33	0	test_amerisave.py
46	0	test_extraction.py

COMMIT 2025-10-14|42bd08d|📝 Add comprehensive release notes for v2.0.0
144	0	RELEASE_NOTES_v2.0.0.md

COMMIT 2025-10-15|79ddbc3|Fix Update Status functionality and add UI improvements
385	0	UI_IMPROVEMENTS.md
98	3	app/services/dashboard_generator.py
4	0	app/services/document_generator.py
119	0	app/templates/web/base.html
631	0	app/templates/web/landing.html
1	0	app/templates/web/ui.html
5	3	app/utils/prompts.py
71	3	app/web.py
58	0	static/css/colors.css
236	0	static/css/forms.css
205	0	static/css/layout.css
182	0	static/css/navigation.css
5	0	static/favicon.svg
185	0	static/js/dashboard.js
226	0	static/js/forms.js
244	0	static/js/navigation.js

COMMIT 2025-10-15|f01fc0d|feat: Implement resume technology extraction and caching system
137	0	RESUME_TECHNOLOGIES_FOR_PROCESSING.md
13	2	app/models/application.py
51	13	app/services/ai_analyzer.py
7	3	app/services/document_generator.py
46	3	app/services/job_processor.py
141	2	app/services/resume_manager.py
85	2	app/templates/web/ui.html
34	19	app/utils/prompts.py
328	0	app/utils/simple_tech_extractor.py
94	0	app/web.py

COMMIT 2025-10-15|1abbcff|fix: Remove qualification analysis box from cover letter generation
6	1	app/services/ai_analyzer.py
6	3	app/utils/prompts.py

COMMIT 2025-10-15|93b24dc|Add comprehensive Reports page with charts and analytics
1	0	app/services/dashboard_generator.py
774	0	app/templates/web/reports.html
29	30	app/templates/web/ui.html
117	0	app/web.py

COMMIT 2025-10-15|11c92a4|feat: Create landing page and update routing
335	613	app/templates/web/landing.html
2	2	app/web.py

COMMIT 2025-10-15|38b2ab6|feat: Major v3.0.0 Release - Enhanced Matching System & UI Overhaul
191	0	INTEGRATION_PLAN.md
472	0	Jobdescr-General Skils.md
27	0	app/services/ai_analyzer.py
310	0	app/services/enhanced_qualifications_analyzer.py
394	0	app/services/preliminary_matcher.py
416	0	backup_qualifications_engine_20251015_153307/ai_analyzer.py
1135	0	backup_qualifications_engine_20251015_153307/document_generator.py
247	0	backup_qualifications_engine_20251015_153307/prompts.py
45	0	backup_qualifications_engine_20251015_153307/qualification.py
293	0	data/resumes/tech.yaml.backup
448	0	docs/ENHANCED_MATCHING_SYSTEM.md
8	3	docs/INDEX.md
486	0	docs/TECHNICAL_REFERENCE.md
228	0	docs/USER_GUIDE_ENHANCED_MATCHING.md
16	0	start_app.sh

COMMIT 2025-10-15|5b1ac8c|chore: Bump version to 3.0.0
1	1	VERSION

COMMIT 2025-10-16|be53993|Fix resume save and technology extraction workflow
0	83	admin/request.txt
122	29	app/services/dashboard_generator.py
11	11	app/services/document_generator.py
137	66	app/templates/web/landing.html
147	39	app/templates/web/reports.html
256	43	app/templates/web/ui.html
4	0	app/web.py

COMMIT 2025-10-16|cdea9cb|Implement Soft Nordic Design System
17	11	app/templates/web/landing.html
5	3	app/templates/web/reports.html
97	69	app/templates/web/ui.html

COMMIT 2025-10-16|36dc169|Complete Soft Nordic Design System Implementation
2	2	app/templates/web/landing.html
5	10	app/templates/web/ui.html
54	24	static/css/colors.css
22	17	static/css/forms.css
97	25	static/css/layout.css
20	17	static/css/navigation.css

COMMIT 2025-10-16|ee786a9|Fix Hero Sections - Apply Soft Nordic Gradients
3	2	app/templates/web/landing.html
3	2	app/templates/web/reports.html

COMMIT 2025-10-16|f75e282|Remove Top Padding from Hero Sections
1	1	app/templates/web/landing.html
1	1	app/templates/web/reports.html
1	1	app/templates/web/ui.html

COMMIT 2025-10-16|7012ca7|Regenerate Dashboard Page with Complete Soft Nordic Design
587	0	app/templates/web/dashboard.html
48	18	app/web.py

COMMIT 2025-10-16|c9a6a5a|Revert Dashboard Changes - Restore Original Working Version
0	587	app/templates/web/dashboard.html
1	1	app/templates/web/reports.html
18	47	app/web.py

COMMIT 2025-10-16|5bf3005|Apply Blue-Gray Color Scheme to Dashboard
19	17	app/services/dashboard_generator.py
1	1	app/templates/web/ui.html

COMMIT 2025-10-16|385bc01|Apply Flat #8b9dc3 Color to All Pages
3	3	app/services/dashboard_generator.py
6	6	app/templates/web/landing.html
6	6	app/templates/web/reports.html
7	7	app/templates/web/ui.html

COMMIT 2025-10-16|a5266bf|Fix Dashboard Layout and Button Colors
5	5	app/services/dashboard_generator.py
1	1	app/templates/web/landing.html

COMMIT 2025-10-16|9f35590|Make Dashboard Truly Full Width
6	5	app/services/dashboard_generator.py
1	1	app/templates/web/landing.html

COMMIT 2025-10-16|55f9f7f|Remove Rounded Border from Tabs Menu
1	1	app/services/dashboard_generator.py

COMMIT 2025-10-16|ba6c817|Fix Dashboard Spacing and Menu Styling
8	5	app/services/dashboard_generator.py

COMMIT 2025-10-16|4cef90e|Center Feature Cards on Landing Page
4	1	app/templates/web/landing.html

COMMIT 2025-10-16|eba6cf8|Add Vertical Centering to Feature Cards
4	0	app/templates/web/landing.html

COMMIT 2025-10-16|71b7f5c|Distribute All 7 Boxes Equally Through Open Space
10	17	app/templates/web/landing.html

COMMIT 2025-10-16|fff4582|Revert Unified Card Layout
18	10	app/templates/web/landing.html

COMMIT 2025-10-16|1ee1b9d|Simplify Landing Page - Remove Dynamic Stats
0	43	app/templates/web/landing.html

COMMIT 2025-10-16|7cfa145|Fix Hero Spacing and Lighten Feature Cards
21	23	app/templates/web/landing.html

COMMIT 2025-10-16|75fcd1f|Make Dashboard the Default Landing Page
18	2	app/web.py

COMMIT 2025-10-16|4864f37|UI/UX Improvements: Nordic Design & Menu Optimization
10	7	app/services/dashboard_generator.py
58	5	app/templates/web/landing.html
112	89	app/templates/web/reports.html
62	44	app/templates/web/ui.html

COMMIT 2025-10-17|103d459|feat: enhance reports with Active Applications and Rejected stats
8	0	app/templates/web/reports.html
11	1	app/web.py

COMMIT 2025-10-17|1dfeb0b|feat: Add missing database technologies to extraction system
4	3	app/services/resume_manager.py
9	0	app/utils/simple_tech_extractor.py
16	0	app/utils/tech_matcher.py

COMMIT 2025-10-17|2305f09|feat: Enhanced summary page tabs with improved data handling
4	1	app/models/application.py
620	0	app/services/document_generator.py
6	0	app/services/job_processor.py

COMMIT 2025-10-17|a32562d|fix: Restore hiring team section in summary page
14	2	app/services/document_generator.py

COMMIT 2025-10-17|bfbdc77|feat: Add enhanced research sections and intro message functionality
7	1	app/models/application.py
46	0	app/services/ai_analyzer.py
228	11	app/services/document_generator.py
49	1	app/utils/prompts.py

COMMIT 2025-10-17|28ac11e|fix: Improve company research with real news data
95	6	app/services/document_generator.py

COMMIT 2025-10-17|33f414b|fix: Add real key personnel data for company research
96	4	app/services/document_generator.py

COMMIT 2025-10-17|4558500|fix: Remove LinkedIn references from Key Personnel section
15	33	app/services/document_generator.py

COMMIT 2025-10-17|a50797e|feat: Implement real-time web search for all company research
350	166	app/services/document_generator.py

COMMIT 2025-10-17|a085af1|fix: Implement working web search using DuckDuckGo API
142	69	app/services/document_generator.py

COMMIT 2025-10-17|7512456|fix: Improve fallback data with company-specific information
77	14	app/services/document_generator.py

COMMIT 2025-10-17|3a2376b|fix: Add real personnel data for major companies
104	3	app/services/document_generator.py

COMMIT 2025-10-17|7e98317|fix: Add real mission and vision statements for major companies
45	3	app/services/document_generator.py

COMMIT 2025-10-20|50cb39d|Implement new longer intro message format with 3 separate copy-ready boxes
33	3	app/models/application.py
330	285	app/services/document_generator.py
55	6	app/services/job_processor.py
5	1	app/templates/web/reports.html
113	2	app/templates/web/ui.html
59	17	app/utils/prompts.py
11	2	app/web.py
180	0	fix_research_and_intros.py
146	0	interactive_research_fix.py
238	0	migrate_existing_applications.py
292	0	process_insight_global.py
267	0	process_next_application.py
0	68	regenerate_amerisave.py
79	0	regenerate_bestbuy.py
180	0	resume_research_fix.py
94	0	simple_migration.py
945	0	static/css/quill.snow.css
8	0	static/js/quill.min.js
174	0	update_bestbuy_html.py

COMMIT 2025-10-20|4118b45|Bump version to 3.1.0 for new intro message format release
1	1	VERSION

COMMIT 2025-10-21|488df2c|Add Active tab to dashboard and remove R from technology evaluation
19	9	app/services/dashboard_generator.py
0	1	app/utils/simple_tech_extractor.py
0	1	app/utils/tech_matcher.py

COMMIT 2025-10-21|04a1eac|Fix parsing issues and improve qualifications matching
50	4	app/services/preliminary_matcher.py
6	0	app/utils/prompts.py

COMMIT 2025-10-21|a3479a7|Fix overqualification recognition issue - improve skill matching for experienced candidates
10	3	app/services/enhanced_qualifications_analyzer.py
25	0	app/services/preliminary_matcher.py
10	0	app/utils/prompts.py

COMMIT 2025-10-21|36d2b22|Fix research tab generic content issue - implement AI-powered company research
166	31	app/services/document_generator.py

COMMIT 2025-10-21|6675a34|Fix qualifications analysis and research tab reliability issues
16	9	app/services/document_generator.py
20	2	app/services/preliminary_matcher.py

COMMIT 2025-10-21|6d03f0f|Improve qualifications analysis skill extraction and matching
4	1	app/services/preliminary_matcher.py

COMMIT 2025-10-21|2494767|Fix reports functionality and raw data tab
7	1	app/services/dashboard_generator.py
8	0	app/services/document_generator.py
56	0	app/services/enhanced_qualifications_analyzer.py
136	6	app/services/preliminary_matcher.py
22	18	app/web.py

COMMIT 2025-10-21|0fa4f56|v2.1.0: Major Documentation Organization
22	329	README.md
0	0	CHANGELOG.md => docs/CHANGELOG.md
0	0	CONTRIBUTING.md => docs/CONTRIBUTING.md
0	0	CUSTOM_RESUME_GUIDE.md => docs/CUSTOM_RESUME_GUIDE.md
133	0	docs/DOCUMENTATION_OVERVIEW.md
26	19	docs/INDEX.md
108	0	docs/README.md
0	0	RELEASE_NOTES_v2.0.0.md => docs/RELEASE_NOTES_v2.0.0.md
0	0	TECHNICAL_SPECIFICATION.md => docs/TECHNICAL_SPECIFICATION.md
0	0	WHAT_IS_HUNTER.md => docs/WHAT_IS_HUNTER.md
0	0	BUG_BACKLOG_v1.5.1.md => docs/archive/BUG_BACKLOG_v1.5.1.md
0	0	DEPLOYMENT_v1.0.0.md => docs/archive/DEPLOYMENT_v1.0.0.md
0	0	INTEGRATION_PLAN.md => docs/archive/INTEGRATION_PLAN.md
0	0	ONE_PAGER.md => docs/archive/ONE_PAGER.md
0	0	RELEASE_NOTES_v1.0.0.md => docs/archive/RELEASE_NOTES_v1.0.0.md
0	0	RELEASE_NOTES_v1.5.0.md => docs/archive/RELEASE_NOTES_v1.5.0.md
0	0	UI_IMPROVEMENTS.md => docs/archive/UI_IMPROVEMENTS.md

COMMIT 2025-10-21|f9d99a7|Update version to v2.4.0 and add release notes
1	1	VERSION
170	0	docs/RELEASE_NOTES_v2.4.0.md

COMMIT 2025-10-22|a6fd975|v2.5.0: Enhanced cover letter template with ML analysis findings
1	1	VERSION
1	0	app/services/ai_analyzer.py
11	19	app/services/document_generator.py
7	1	app/services/enhanced_qualifications_analyzer.py
45	9	app/services/preliminary_matcher.py
1	0	app/services/resume_manager.py
-	-	data/covers/*.pdf
1	0	interactive_research_fix.py
1	0	resume_research_fix.py
349	0	static/css/cover-letter-minimal.css
334	0	static/css/cover-letter.css

COMMIT 2025-10-27|7aa9e0d|Implement job rejection cleanup with automatic redirect to dashboard
115	26	app/services/document_generator.py
125	0	app/services/job_processor.py
91	10	app/templates/web/ui.html
74	6	app/web.py

COMMIT 2025-10-28|8503bb9|feat: Add Daily Activities page with collapsible functionality and Reports enhancements
1	0	app/templates/web/base.html
528	0	app/templates/web/daily_activities.html
11	5	app/templates/web/reports.html
97	1	app/web.py
2	0	static/js/navigation.js

COMMIT 2025-10-29|c0b57d8|Remove Scala from technology extraction and resume
1	1	app/services/resume_manager.py
1	2	app/utils/simple_tech_extractor.py
0	1	app/utils/tech_matcher.py
0	1	resumes/base_resume.md
0	1	resumes/base_resume.yaml

COMMIT 2025-10-30|81fea34|feat(templates): add Templates page with collapsible cards; add TemplateManager service and APIs; update navigation across app; make saved templates collapsible; default Create New Template collapsed; fix EST timestamp formatting; regenerate dashboard on / for nav freshness
2	0	app/services/dashboard_generator.py
144	0	app/services/template_manager.py
7	6	app/templates/web/base.html
1	0	app/templates/web/daily_activities.html
2	0	app/templates/web/landing.html
1	0	app/templates/web/reports.html
727	0	app/templates/web/templates.html
2	0	app/templates/web/ui.html
12	2	app/utils/datetime_utils.py
65	9	app/web.py
1	0	data/templates/20251029133734.html
1	0	data/templates/20251029135329.html
13	0	data/templates/templates_meta.yaml

### Comprehensive Feature List

- Dashboard & Navigation
  - Tabbed dashboard with 9 status tabs and counts (v2.0.0)
  - Advanced sorting (Updated/Applied/Posted/Match%) per tab
  - Posted Date extraction and display on cards
  - Default route serves dashboard; Active tab added as smart default
  - Daily Activities page with collapsible sections and activity counts
  - Soft Nordic design system across app; layout, spacing, full-width fixes
  - Templates page with collapsible cards; app-wide navigation updates

- Matching & Qualifications
  - Enhanced qualification analysis with feature counts and weighted scoring
  - Technology matcher to reduce hallucinations; resume tech cache
  - Overqualification recognition and tiered bonus scoring
  - Improved parsing, normalization, and skill equivalence mappings
  - Technologies section in summaries with ✅/⚠️/❌ status pills

- Research System
  - Real-time web search for company research (news, personnel, products, competitors)
  - Company-specific fallbacks for major brands; realistic mission/vision
  - Structured Research tab with links and N/A handling

- Reports & Analytics
  - Reports page with charts and analytics
  - Stats: New, Status Changes, Active, Rejected, Actions
  - Period logic fixes (Yesterday/7/30/All), timezone consistency

- Documents & Content Generation
  - Longer intro messages (275/500/500) with copy-ready boxes (v3.1.0)
  - Cover letter template with ML analysis findings and improved structure (v2.5.0)
  - Templates system and `TemplateManager` service/APIs

- Resume & Tech Extraction
  - Resume technology extraction and caching pipeline
  - Expanded database tech coverage; removal of Scala to avoid false positives

- Summary Page Improvements
  - Skills tab with individual pills and accurate counts
  - Raw Entry tab shows original job description input
  - Hiring Team section restored with proper empty-state handling
  - Additional Insights section (conditional display)

- Workflow & Cleanup
  - Rejection cleanup: remove generated artifacts, regenerate minimal summary, auto-redirect

- Documentation
  - Docs reorganization into `docs/` with index and maintenance guide (v2.1.0 → v2.4.0)
  - Comprehensive release notes and changelog updates


