# Charts Reference Guide

## Overview

This document provides comprehensive documentation for all charts in the Hunter job application tracking system. Charts are displayed on two main pages:

- **Analytics Page** (`/analytics`): Contains three tabs with various analytics charts
- **Reports Page** (`/reports`): Contains summary charts for application status tracking

All charts use [Chart.js](https://www.chartjs.org/) version 4.4.0 for rendering and display a "Last updated" timestamp in the bottom right corner showing when the data was last refreshed (in EST timezone).

## How Charts Work

### Data Flow

1. **Backend Data Generation**: The `AnalyticsGenerator` class (`app/services/analytics_generator.py`) processes application data and generates analytics metrics
2. **API Endpoints**: 
   - `/api/analytics` - Returns comprehensive analytics data for the Analytics page
   - `/api/reports` - Returns reports data for the Reports page
3. **Frontend Rendering**: JavaScript in the HTML templates fetches data from APIs and uses Chart.js to render interactive charts
4. **Chart Updates**: Charts automatically update when:
   - Period selector changes (Today, 7 Days, 30 Days, All Time)
   - Tab is switched (Application Analytics, Trend Analysis, Skills Gap Analysis)
   - Page is refreshed

### Chart.js Configuration

All charts use Chart.js with the following common settings:
- **Responsive**: Charts automatically resize to fit their containers
- **Maintain Aspect Ratio**: Set to `false` to allow flexible sizing
- **Interactive**: Hover tooltips show detailed information
- **Clickable**: Some charts allow clicking to navigate to related applications

## How to Refresh Data

### Automatic Refresh

Charts automatically refresh when:
- Changing the period selector (Today, 7 Days, 30 Days, All Time)
- Switching between tabs on the Analytics page
- Reloading the page

### Manual Refresh

To manually refresh chart data:
1. Click any period selector button (Today, 7 Days, 30 Days, All Time)
2. Or refresh the browser page (F5 or Cmd+R)

### API Endpoints

- **Analytics**: `GET /api/analytics?period={period}&gap_period={gap_period}`
  - `period`: `today`, `7days`, `30days`, or `all`
  - `gap_period`: `daily`, `weekly`, `monthly`, or `all` (for skill gaps)
- **Reports**: `GET /api/reports?period={period}`
  - `period`: `today`, `7days`, `30days`, or `all`

## Chart Details

### Application Analytics Tab

#### Response Rate (Metric Card)

- **Purpose**: Shows the percentage of applications that received a response from companies
- **Data Source**: 
  - `Application.get_response_received_at()` method
  - `Application.status` field
  - `Application.created_at` timestamp
- **Collection Method**: `AnalyticsGenerator.compute_application_analytics()`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  ```
  Response Rate = (Applications with response_received checked) / (Total applications applied) × 100
  ```
  - Uses `get_response_received_at()` which checks:
    1. `response_received` checklist item being checked
    2. Status updates indicating company response (Company Response, Contacted Hiring Manager, etc.)
  - Denominator is all applications where status is not "pending"
  - Returns percentage (0-100%)

#### Average Time to Response (Metric Card)

- **Purpose**: Shows the average number of days between applying and receiving a response
- **Data Source**: 
  - `Application.get_response_received_at()` method
  - `Application.created_at` timestamp
  - `Application.status_updated_at` timestamp
- **Collection Method**: `AnalyticsGenerator.compute_application_analytics()`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  ```
  Average = Mean of (response_date - applied_date) for all applications with responses
  ```
  - `applied_date`: Application `created_at` OR `status_updated_at` when status changed to "applied"
  - `response_date`: When `response_received` checklist item was first checked
  - Calculated in days (can be fractional)
  - Also provides: median, min, max values

#### Interview Rate (Metric Card)

- **Purpose**: Shows the percentage of responses that led to interviews
- **Data Source**: 
  - `Application.status` field
  - `Application.get_response_received_at()` method
- **Collection Method**: `AnalyticsGenerator.compute_application_analytics()`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  ```
  Interview Rate = (Interviews / Phone Screens) × 100
  ```
  - Counts applications with status: `scheduled interview`, `interview notes`, `interview - follow up`
  - Denominator is applications that received responses

#### Offer Rate (Metric Card)

- **Purpose**: Shows the percentage of interviews that led to offers
- **Data Source**: 
  - `Application.status` field
- **Collection Method**: `AnalyticsGenerator.compute_application_analytics()`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  ```
  Offer Rate = (Offers / Interviews) × 100
  ```
  - Counts applications with status: `offered`
  - Denominator is applications that reached interview stage

#### Interview Conversion Funnel

- **Purpose**: Visualizes the progression of applications through the hiring pipeline
- **Data Source**: 
  - `Application.status` field
  - `Application.get_response_received_at()` method
- **Collection Method**: `AnalyticsGenerator.compute_application_analytics()` → `interview_conversion`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - **Applied**: Count of applications where status is not "pending"
  - **Responded**: Count of applications with `response_received` checked or status is "company response"
  - **Phone Screen**: Count of applications with status "company response", "scheduled interview", "interview notes", or "interview - follow up"
  - **Interview**: Count of applications with status "scheduled interview", "interview notes", or "interview - follow up"
  - **Offer**: Count of applications with status "offered"
- **Chart Type**: Bar chart showing counts at each stage

#### Time to Response Distribution

- **Purpose**: Shows how quickly companies respond, grouped into time buckets
- **Data Source**: 
  - `Application.get_response_received_at()` method
  - `Application.created_at` timestamp
  - `Application.status_updated_at` timestamp
- **Collection Method**: `AnalyticsGenerator.compute_application_analytics()` → `time_to_response.distribution`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  Groups all response times into buckets:
  - 0-1 days
  - 2-3 days
  - 4-7 days
  - 8-14 days
  - 15-30 days
  - 30+ days
  - Count of applications in each bucket
- **Chart Type**: Bar chart

#### Success by Match Score

- **Purpose**: Shows response and interview rates broken down by match score ranges
- **Data Source**: 
  - `Application.match_score` field
  - `Application.get_response_received_at()` method
  - `Application.status` field
- **Collection Method**: `AnalyticsGenerator.compute_application_analytics()` → `success_by_match_score`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  Groups applications by match score ranges:
  - 0-50%
  - 50-70%
  - 70-85%
  - 85-100%
  
  For each range:
  ```
  response_rate = (apps_with_response_in_range / total_apps_in_range) × 100
  interview_rate = (apps_interviewed_in_range / total_apps_in_range) × 100
  ```
- **Chart Type**: Grouped bar chart (Response Rate and Interview Rate)

#### Best Performing Day of Week

- **Purpose**: Shows which day of the week has the highest response rate
- **Data Source**: 
  - `Application.created_at` timestamp
  - `Application.get_response_received_at()` method
- **Collection Method**: `AnalyticsGenerator.compute_application_analytics()` → `best_performing_day`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Groups applications by day of week from `created_at` timestamp
  - For each day (Monday-Sunday):
    ```
    response_rate = (apps_with_response_on_day / total_apps_on_day) × 100
    ```
  - Shows both response rate % and total application count per day
- **Chart Type**: Grouped bar chart (Response Rate and Total Applications on dual y-axes)

### Trend Analysis Tab

#### Application Velocity (Daily)

- **Purpose**: Shows the number of applications submitted per day over time
- **Data Source**: 
  - `Application.created_at` timestamp
- **Collection Method**: `AnalyticsGenerator.compute_trend_analysis()` → `application_velocity.daily`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Groups applications by date (YYYY-MM-DD format)
  - Counts applications created per day
  - Returns time series: date → count
- **Chart Type**: Line chart with area fill

#### Application Velocity (Cumulative)

- **Purpose**: Shows the running total of applications over time
- **Data Source**: 
  - `Application.created_at` timestamp
- **Collection Method**: `AnalyticsGenerator.compute_trend_analysis()` → `application_velocity.daily_cumulative`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Same daily grouping as Daily Velocity
  - Cumulative sum: Day N = Sum of all previous days + Day N
  - Shows growth trend over time
- **Chart Type**: Line chart with area fill

#### Status Distribution

- **Purpose**: Shows the breakdown of applications by their current status
- **Data Source**: 
  - `Application.status` field
- **Collection Method**: `AnalyticsGenerator.compute_trend_analysis()` → `status_distribution`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Count of applications by current normalized status
  - Normalizes status labels (e.g., "contacted hiring manager" → "company response")
  - Counts applications in each status bucket
- **Chart Type**: Pie chart

#### Company Type Analysis

- **Purpose**: Shows response, interview, and offer rates broken down by company type
- **Data Source**: 
  - `Application.company_type` field (startup, enterprise, unknown)
  - `Application.get_response_received_at()` method
  - `Application.status` field
- **Collection Method**: `AnalyticsGenerator.compute_trend_analysis()` → `company_type_analysis`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  Groups by `application.company_type`:
  ```
  response_rate = (apps_with_response / total_apps) × 100
  interview_rate = (apps_interviewed / total_apps) × 100
  offer_rate = (apps_offered / total_apps) × 100
  ```
  - Shows top 20 company types
- **Chart Type**: Grouped bar chart (Response Rate and Interview Rate)

#### Work Type Distribution

- **Purpose**: Shows response and interview rates for Remote, Hybrid, and On-site positions
- **Data Source**: 
  - `Application.location` field
  - `Application.job_description_path` (for parsing work type)
  - `Application.get_response_received_at()` method
  - `Application.status` field
- **Collection Method**: `AnalyticsGenerator.compute_trend_analysis()` → `work_type_distribution`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Extracts work type from location and job description using `LocationNormalizer.extract_work_type()`
  - Groups into: Remote, Hybrid, On-site
  - For each type:
    ```
    response_rate = (apps_with_response / total_apps) × 100
    interview_rate = (apps_interviewed / total_apps) × 100
    ```
  - Shows total applications, response rate, and interview rate
- **Chart Type**: Grouped bar chart with dual y-axes (Total Applications on left, Rates on right)

#### Location Insights

- **Purpose**: Shows response and interview rates by geographic location
- **Data Source**: 
  - `Application.location` field
  - `Application.job_description_path` (for better location normalization)
  - `Application.get_response_received_at()` method
  - `Application.status` field
- **Collection Method**: `AnalyticsGenerator.compute_trend_analysis()` → `location_insights`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Normalizes locations using `LocationNormalizer.normalize()` with `group_by_region=True`
  - Removes work type from location (Remote locations are excluded)
  - For each unique location:
    ```
    response_rate = (apps_with_response / total_apps) × 100
    interview_rate = (apps_interviewed / total_apps) × 100
    ```
  - Sorted by response rate (highest first)
  - Shows top 20 locations
- **Chart Type**: Horizontal bar chart (Response Rate and Interview Rate)

#### Salary Range Distribution

- **Purpose**: Shows the distribution of salary ranges from job postings
- **Data Source**: 
  - `Application.salary_range` field (text format, e.g., "$120k - $150k")
- **Collection Method**: `AnalyticsGenerator.compute_trend_analysis()` → `salary_tracking.distribution`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  1. Parses `application.salary_range` text (e.g., "$120k - $150k")
  2. Extracts numeric values, handles "k" suffix
  3. If range: calculates average = (min + max) / 2
  4. Groups into buckets:
     - $0-50k
     - $50k-75k
     - $75k-100k
     - $100k-125k
     - $125k-150k
     - $150k-200k
     - $200k-220k
     - $220k-230k
     - $230k-250k
     - $250k-270k
     - $270k-300k
     - $300k+
  5. Counts applications in each bucket
- **Chart Type**: Bar chart (ordered ascending by salary range)

### Skills Gap Analysis Tab

#### Most Requested Skills (Top 20)

- **Purpose**: Shows the skills that appear most frequently in job descriptions
- **Data Source**: 
  - Qualification files (parsed from `Application.qualifications_path`)
  - `Application.match_score` field
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `most_requested_skills`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Extracts skills from qualification files using `_extract_skills_from_qualifications()`
  - Counts frequency of each skill appearing in job descriptions
  - Calculates percentage: `(frequency / total_applications) × 100`
  - Calculates average match score for applications containing each skill
  - Shows top 20 skills
- **Chart Type**: Horizontal bar chart

#### Skills Overlap: How Many Skills Are Common Between Jobs

- **Purpose**: Shows how many skills appear in multiple jobs vs. unique skills
- **Data Source**: 
  - Qualification files (parsed from `Application.qualifications_path`)
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `skills_overlap.distribution`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Tracks how many unique jobs each skill appears in
  - Groups skills by job count ranges:
    - 1 job (Unique)
    - 2 jobs
    - 3-5 jobs
    - 6-10 jobs
    - 11-20 jobs
    - 20+ jobs
  - Counts number of skills in each range
- **Chart Type**: Bar chart

#### Common Requested Skills Between Jobs

- **Purpose**: Shows specific skill names and how many jobs they appear in
- **Data Source**: 
  - Qualification files (parsed from `Application.qualifications_path`)
  - `Application.match_score` field
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `skills_overlap.common_requested_skills`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Identifies skills appearing in 2+ jobs
  - For each skill:
    - Job count: Number of unique applications containing the skill
    - Percentage: `(job_count / total_applications) × 100`
    - Average match score: Mean match score for applications with this skill
  - Sorted by job count (most common first)
  - Shows top 20 skills
- **Chart Type**: Horizontal bar chart

#### Common Unmatched Skills Between Jobs

- **Purpose**: Shows skills that are frequently missing from your resume across multiple jobs
- **Data Source**: 
  - Qualification files (parsed from `Application.qualifications_path`)
  - `Application.match_score` field
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `skills_overlap.common_unmatched_skills`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Identifies skills appearing in "Missing Skills" section of 2+ jobs
  - For each skill:
    - Job count: Number of unique applications missing this skill
    - Percentage: `(job_count / total_applications) × 100`
    - Average match score impact: Mean match score for applications missing this skill
  - Sorted by job count (most common first)
  - Shows top 20 skills
- **Chart Type**: Horizontal bar chart

#### Skill Gaps Table

- **Purpose**: Lists skills that appear in 3+ jobs but are missing from your resume
- **Data Source**: 
  - Qualification files (parsed from `Application.qualifications_path`)
  - `Application.match_score` field
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `skill_gaps`
- **Refresh**: Updates when period selector or gap period selector changes
- **Calculation**: 
  - Filters skills by gap period (daily, weekly, monthly, or all time)
  - Identifies skills appearing in 3+ jobs (for all time) or 1+ jobs (for filtered periods)
  - For each skill:
    - Frequency: Number of jobs requiring this skill
    - Percentage: `(frequency / total_applications) × 100`
    - Average match score impact: Mean match score for applications missing this skill
  - Sorted by frequency and match score impact
  - Shows top 20 gaps
- **Display**: Table with expandable rows showing related applications

#### Learning Priorities Table

- **Purpose**: Recommends which skills to learn next based on frequency and impact
- **Data Source**: 
  - Qualification files (parsed from `Application.qualifications_path`)
  - `Application.match_score` field
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `learning_priorities`
- **Refresh**: Updates when period selector or gap period selector changes
- **Calculation**: 
  - Takes top 20 skill gaps
  - For each gap:
    ```
    Priority Score = Frequency × (Average Match Score Impact / 100)
    ```
  - Sorted by priority score (highest first)
  - Shows top 20 priorities
- **Display**: Table with expandable rows showing related applications

#### Most Unmatched Skills (Top 20)

- **Purpose**: Visual representation of skills most frequently missing from your resume
- **Data Source**: 
  - Qualification files (parsed from `Application.qualifications_path`)
  - `Application.match_score` field
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `skill_gaps`
- **Refresh**: Updates when period selector or gap period selector changes
- **Calculation**: 
  - Same as Skill Gaps Table
  - Shows frequency count for each skill
  - Calculates average frequency across all shown skills
- **Chart Type**: Horizontal bar chart

#### Skill Match Trends Over Time

- **Purpose**: Tracks how match scores improve over time for the most frequently requested skills
- **Data Source**: 
  - `Application.match_score` field
  - `Application.created_at` timestamp
  - Qualification files (parsed from `Application.qualifications_path`)
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `skill_match_trends`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Groups applications by ISO week (YYYY-Www format)
  - Tracks top 10 most requested skills individually
  - Groups remaining skills as "Other"
  - For each skill/week combination:
    ```
    average_score = Mean of match scores for applications containing this skill in this week
    ```
  - Only includes weeks with actual data (filters null weeks)
  - Shows average match score per week for each skill
- **Chart Type**: Grouped bar chart (one bar per skill per week)
- **Note**: Chart is scrollable horizontally for long date ranges

#### Unique Skills List

- **Purpose**: Shows skills that appear in only one job posting
- **Data Source**: 
  - Qualification files (parsed from `Application.qualifications_path`)
- **Collection Method**: `AnalyticsGenerator.compute_skills_gap_analysis()` → `skills_overlap.unique_skills`
- **Refresh**: Updates when period selector changes or tab is switched
- **Calculation**: 
  - Identifies skills appearing in exactly 1 job
  - Links each skill to the application where it appears
  - Sorted alphabetically
  - Shows top 50 unique skills
- **Display**: Scrollable list with skill names and linked applications

### Reports Page

#### Applications by Status

- **Purpose**: Shows the current distribution of applications across all status categories
- **Data Source**: 
  - `Application.status` field
- **Collection Method**: `DashboardGenerator` or Reports API endpoint
- **Refresh**: Updates when period selector changes or page is refreshed
- **Calculation**: 
  - Counts applications by current normalized status
  - Normalizes status labels for consistency
  - Groups into status buckets
- **Chart Type**: Bar chart

#### Applications by Status Change

- **Purpose**: Shows how many applications have changed to each status during the selected period
- **Data Source**: 
  - `Application.status` field
  - Status change history (if tracked)
- **Collection Method**: Reports API endpoint
- **Refresh**: Updates when period selector changes or page is refreshed
- **Calculation**: 
  - Tracks status changes during the selected period
  - Counts applications that moved to each status
  - Normalizes status labels
- **Chart Type**: Bar chart

## Technical Implementation Details

### Backend

- **Service Class**: `AnalyticsGenerator` in `app/services/analytics_generator.py`
- **Main Methods**:
  - `generate_analytics(period, gap_period)`: Main entry point for analytics generation
  - `compute_application_analytics(applications)`: Application-level metrics
  - `compute_trend_analysis(applications)`: Trend and distribution analysis
  - `compute_skills_gap_analysis(applications, gap_period)`: Skills analysis
- **Data Models**: Uses `Application` model from `app/models/application.py`

### Frontend

- **Chart Library**: Chart.js 4.4.0 (loaded from CDN)
- **Templates**: 
  - `app/templates/web/analytics.html` - Analytics page
  - `app/templates/web/reports.html` - Reports page
- **Timestamp Formatting**: Uses `Intl.DateTimeFormat` with `America/New_York` timezone
- **Update Mechanism**: Charts update via `updateAllCharts()` function when data is loaded

### Data Refresh Flow

1. User changes period selector or switches tab
2. JavaScript calls API endpoint (`/api/analytics` or `/api/reports`)
3. Backend processes applications and generates analytics
4. Frontend receives JSON response
5. JavaScript updates all charts with new data
6. Timestamps are updated to current time in EST

## References

- [Analytics Metrics Explanation](./ANALYTICS_METRICS_EXPLANATION.md) - Detailed calculation formulas
- [Analytics Chart Improvements Plan](./ANALYTICS_CHART_IMPROVEMENTS_PLAN.md) - Chart structure and design decisions
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/) - Chart.js library reference
- Backend Code: `app/services/analytics_generator.py` - Implementation details

