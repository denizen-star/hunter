# Analytics Chart Improvements - Implementation Plan

## Overview
This document outlines a comprehensive plan to improve the analytics charts, making them scrollable, showing all skills, filtering null days, and switching to **daily bar chart trends**.

**Key Change**: "Skill Match Trends Over Time" will be converted from a monthly line chart to a **daily grouped bar chart**, where each day on the x-axis shows grouped bars for each skill, allowing users to compare skill match scores across skills and over time.

### Visual Design of Daily Bar Chart
- **X-Axis**: Dates (daily, e.g., "Jan 15", "Jan 16", "Jan 17")
- **Y-Axis**: Match Score (0-100%)
- **Bars**: Each day has multiple grouped bars, one for each skill
- **Colors**: Each skill has a unique color (extended palette for all skills)
- **Grouping**: Bars are grouped by day (all skills visible for each day)
- **Legend**: Shows all skills with their colors
- **Null Handling**: Days with no data are excluded entirely

Example structure for a single day:
```
Jan 15: [Python bar] [SQL bar] [Tableau bar] [AWS bar] ... (all skills)
Jan 16: [Python bar] [SQL bar] [Tableau bar] [AWS bar] ... (all skills)
```

## Requirements Summary
1. **Scrollable Charts**: Make "Most Requested Skills" and "Skill Match Trends Over Time" charts scrollable
2. **Show All Skills**: Display all skills (not just top 20) in both charts
3. **Remove Null Days**: Filter out days with no data from all analysis
4. **Daily Trends with Bar Chart**: Change "Skill Match Trends Over Time" from monthly line chart to **daily bar chart** showing trends over time
5. **Skill Parsing**: Ensure skills come from parsed qualification files, not AI-generated descriptions

---

## Phase 1: Backend Changes - Daily Aggregation & Null Day Filtering

### 1.1 Update Skill Match Trends to Daily Bar Chart Data (Backend)
**File**: `app/services/analytics_generator.py`
**Method**: `compute_skills_gap_analysis()` → Skill Match Trends section

**Changes**:
- Change from `month_key = created.strftime('%Y-%m')` to `day_key = created.strftime('%Y-%m-%d')`
- Update all dictionary keys from `month_key` to `day_key`
- Update variable names: `monthly_scores` → `daily_scores`, etc.
- Filter out days with no applications: Check `if scores and len(scores) > 0` before adding to trends
- Only return days that have actual data (avoid empty/null entries)
- **Prepare data structure suitable for grouped bar chart** (daily aggregation with skill breakdowns)

**Data Structure for Bar Chart**:
- Each day should have average match scores per skill
- Structure: `by_skill[skill_name][day] = { average_score, count }`
- Overall daily scores in `overall[day] = { average_score, count }`

**Testing**:
- Verify daily aggregation produces correct results
- Ensure days without applications are excluded
- Test with different date ranges
- Verify data structure supports bar chart rendering

### 1.2 Return All Skills (Not Just Top 20)
**File**: `app/services/analytics_generator.py`
**Method**: `compute_skills_gap_analysis()`

**Changes**:
- Remove `.most_common(20)` limit → use `.most_common()` to get all skills
- Return all skills in `most_requested_skills` (remove `[:20]` slice)
- For skill trends, track ALL skills, not just top 20
- Update color palette generation to support unlimited skills

**Considerations**:
- Performance: With many skills, ensure efficient data structures
- Memory: Monitor if returning all skills causes memory issues

---

## Phase 2: Frontend Changes - Scrollable Charts & All Skills Display

### 2.1 Add Scrollable Container CSS
**File**: `app/templates/web/analytics.html`
**Section**: `<style>` block

**CSS Additions**:
```css
.scrollable-chart-wrapper {
    position: relative;
    height: 500px;
    width: 100%;
    overflow-x: auto;
    overflow-y: auto;
    padding: 10px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    background: #f8f9fa;
}

/* Specific sizing for each chart type */
.chart-container.scrollable {
    height: auto;
    min-height: 500px;
}

#mostRequestedChart {
    min-height: auto;
    min-width: 100%;
}

#skillTrendsChart {
    min-width: max-content;
    min-height: 400px;
}
```

**Design Decisions**:
- Use fixed height container with scrollbars
- Horizontal scroll for date ranges (skill trends)
- Vertical scroll for long skill lists (most requested)
- Maintain responsive design for smaller screens

### 2.2 Update HTML Structure for Scrollable Charts
**File**: `app/templates/web/analytics.html`
**Sections**: Chart container divs

**Changes**:
1. Wrap "Most Requested Skills" chart:
```html
<div class="chart-container scrollable">
    <div class="chart-title">Most Requested Skills</div>
    <div class="scrollable-chart-wrapper">
        <canvas id="mostRequestedChart"></canvas>
    </div>
</div>
```

2. Wrap "Skill Match Trends Over Time" chart:
```html
<div class="chart-container scrollable">
    <div class="chart-title">Skill Match Trends Over Time</div>
    <div class="scrollable-chart-wrapper">
        <canvas id="skillTrendsChart"></canvas>
    </div>
</div>
```

### 2.3 Update Chart.js Configuration for All Skills
**File**: `app/templates/web/analytics.html`
**Function**: `updateSkillsCharts()`

**Changes**:

1. **Most Requested Skills Chart**:
   - Remove `.slice(0, 20)` to show all skills
   - Calculate dynamic height based on number of skills
   - Add pagination or virtual scrolling if too many skills (>100)
   - Improve tooltip with frequency and percentage

2. **Skill Match Trends Chart** (Daily Bar Chart):
   - **Change chart type from `line` to `bar`**
   - Change from `allMonths` to `allDays`
   - Filter null days: `allDays.filter(day => trendsData.overall[day]?.count > 0)`
   - Show ALL skills (not just top 20) as grouped bars per day
   - Use grouped bar chart format: each day has bars for each skill
   - Generate extended color palette dynamically for skills
   - Format dates: "Jan 15" instead of "2025-01-15"
   - Rotate x-axis labels 45° for readability (dates on x-axis)
   - Add horizontal scroll for many dates
   - Stack or group bars based on readability (grouped recommended)
   - Each bar represents the average match score for that skill on that day

**Code Structure for Bar Chart**:
```javascript
// Filter null days
const allDays = Object.keys(trendsData.overall || {})
    .filter(day => {
        const data = trendsData.overall[day];
        return data && data.average_score != null && data.count > 0;
    })
    .sort();

// Show all skills as datasets (one dataset per skill)
const allSkills = skills.most_requested_skills || [];
const skillColors = generateExtendedColorPalette(allSkills.length);

// Build grouped bar chart datasets
const datasets = allSkills.map((skill, index) => ({
    label: skill.skill,
    data: allDays.map(day => {
        const dayData = trendsData.by_skill[skill.skill]?.[day];
        return dayData?.average_score || null;
    }),
    backgroundColor: skillColors[index],
    borderColor: skillColors[index],
    borderWidth: 1
}));

// Chart configuration for grouped bar chart
charts.skillTrends = new Chart(trendsCtx, {
    type: 'bar',
    data: {
        labels: allDays.map(formatDate), // Dates on x-axis
        datasets: datasets
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                stacked: false, // Grouped bars (set to true for stacked)
                ticks: { maxRotation: 45, minRotation: 45 }
            },
            y: {
                beginAtZero: true,
                max: 100,
                title: { display: true, text: 'Match Score (%)' }
            }
        },
        plugins: {
            legend: { display: true, position: 'right' },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        }
    }
});
```

---

## Phase 3: Skill Parsing Improvements

### 3.1 Verify Skill Extraction from Qualification Files
**File**: `app/services/analytics_generator.py`
**Method**: `_extract_skills_from_qualifications()`

**Current State**: 
- Already extracts from comma-separated lists
- Filters out table headers
- Skips placeholder text

**Improvements Needed**:
1. **Normalize Skill Variations**: 
   - "Insights", "Insights)", "insights" → "Insights" (case-insensitive, strip punctuation)
   - Use a normalization function before counting frequencies

2. **Better Pattern Matching**:
   - Extract from both comma-separated lists AND first column of tables
   - Handle various formats (bullet points, numbered lists, etc.)

3. **Validation**:
   - Skip skills that are too long (likely sentences)
   - Skip skills with special characters that indicate formatting
   - Minimum length: 2 characters
   - Maximum length: 50 characters (reasonable skill name length)

**Implementation**:
```python
def _normalize_skill_name(self, skill: str) -> str:
    """Normalize skill name for consistent matching"""
    # Remove trailing punctuation
    skill = skill.rstrip('.,;:!?)')
    # Remove parentheses
    skill = skill.replace('(', '').replace(')', '')
    # Title case for consistency
    return skill.strip().title()

def _is_valid_skill(self, skill: str) -> bool:
    """Check if a string is a valid skill name"""
    if not skill or len(skill) < 2 or len(skill) > 50:
        return False
    # Skip if looks like a sentence (too many words)
    if len(skill.split()) > 5:
        return False
    # Skip if contains quotes (likely a quote from job description)
    if '"' in skill or "'" in skill:
        return False
    return True
```

---

## Phase 4: Performance Optimization

### 4.1 Handle Large Datasets
**Considerations**:
- If >100 skills, consider:
  - Lazy loading/pagination
  - Virtual scrolling
  - Progressive disclosure (show top 20, expand to show all)
  - Grouping less frequent skills

### 4.2 Chart Rendering Performance
- Limit number of visible data points (for very long date ranges)
- Use Chart.js `skipNull: true` to skip null values
- Debounce chart updates if period changes frequently
- Consider using Chart.js plugins for better performance with large datasets

---

## Phase 5: User Experience Enhancements

### 5.1 Chart Controls
- Add "Show All" / "Show Top 20" toggle for Most Requested Skills
- Add date range selector for Skill Trends
- Add legend toggle for Skill Trends (hide/show specific skills)
- **Add "Grouped" / "Stacked" toggle for Skill Trends bar chart** (grouped by default)
- Add export functionality (CSV, PNG)

### 5.2 Visual Improvements
- Add loading states while data loads
- Add empty states with helpful messages
- Improve tooltip formatting
- Add chart titles with data summary (e.g., "Showing 45 skills from 120 applications")

### 5.3 Accessibility
- Ensure keyboard navigation works with scrollable areas
- Add ARIA labels for screen readers
- Ensure color contrast meets WCAG standards
- Add chart descriptions for screen readers

---

## Implementation Order

1. **Phase 1**: Backend changes (daily aggregation, null filtering, all skills)
   - ✅ Foundation for all other changes
   - ✅ Tested independently
   
2. **Phase 2**: Frontend structure (scrollable containers, CSS)
   - ✅ Visual foundation
   - ✅ Can test with existing data
   
3. **Phase 3**: Skill parsing improvements
   - ✅ Fixes data quality issues
   - ✅ Improves accuracy of all charts
   
4. **Phase 4**: Performance optimization
   - ✅ Only needed if performance issues arise
   - ✅ Can be done incrementally
   
5. **Phase 5**: UX enhancements
   - ✅ Nice-to-have improvements
   - ✅ Can be added after core functionality works

---

## Testing Checklist

### Backend Testing
- [ ] Daily aggregation produces correct daily data points
- [ ] Null/empty days are filtered out
- [ ] All skills are returned (not limited to 20)
- [ ] Skill normalization works correctly
- [ ] Performance is acceptable with large datasets (100+ applications)

### Frontend Testing
- [ ] Charts are scrollable (horizontal and vertical)
- [ ] All skills are visible and readable
- [ ] **Skill Match Trends is a bar chart (not line chart)**
- [ ] **Bar chart shows grouped bars per day with skills**
- [ ] Dates are formatted correctly (daily) on x-axis
- [ ] Null days don't appear in charts
- [ ] Tooltips work correctly for bar chart (showing skill and score)
- [ ] Charts render correctly on different screen sizes
- [ ] Performance is acceptable with many skills/dates
- [ ] Bar chart legend is readable and toggleable

### Integration Testing
- [ ] Data flows correctly from backend to frontend
- [ ] Charts update correctly when period changes
- [ ] Skill names are consistent (no duplicates from variations)
- [ ] Daily trends match expected results

---

## Risks & Mitigation

### Risk 1: Performance with Many Skills
**Mitigation**: 
- Implement progressive disclosure (show top 20 by default, expand to all)
- Use virtual scrolling if >100 skills
- Cache chart configurations

### Risk 2: Chart.js Limitations with Large Datasets
**Mitigation**:
- Limit visible data points
- Use data sampling for very long date ranges
- Consider alternative charting libraries if needed
- **For bar charts with many skills**: Consider grouping less frequent skills or using a "top N + others" approach
- **Bar chart readability**: Limit visible skills in legend or make it scrollable

### Risk 3: Skill Name Variations
**Mitigation**:
- Implement robust normalization
- Group similar skills before counting
- Test with real qualification files

### Risk 4: Browser Compatibility
**Mitigation**:
- Test on multiple browsers
- Use CSS fallbacks for older browsers
- Ensure scrollable containers work everywhere

---

## Success Criteria

✅ Charts are fully scrollable (horizontal and vertical)
✅ All skills are displayed (not limited to top 20)
✅ Daily trends show correctly with null days filtered
✅ **Skill Match Trends is a daily bar chart (grouped bars by skill per day)**
✅ Skill names are normalized (no duplicate variations)
✅ Performance is acceptable (<2s load time)
✅ Charts are readable and accessible

---

## Next Steps

1. Review this plan with stakeholders
2. Prioritize phases based on business needs
3. Begin with Phase 1 (backend changes)
4. Test incrementally after each phase
5. Iterate based on feedback

