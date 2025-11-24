# Analytics Calculations Documentation

This document explains how each metric in the Advanced Analytics & Reports feature is calculated.

## Application Analytics

### Response Rate
**Formula**: `(Applications with response_received checked) / (Total applications applied) * 100`

**How it works**:
- Counts applications where `response_received` checklist item is checked OR status is "Company Response"
- Denominator is all applications with status other than "pending"
- Returns percentage

### Average Time to Response
**Formula**: `Average of (response_received_at - applied_date) for all applications with responses`

**How it works**:
- For each application with a response:
  - `applied_date` = `created_at` OR `status_updated_at` when moved to "applied" status
  - `response_date` = `get_response_received_at()` (from checklist or status updates)
- Calculates days difference, then averages all response times
- Also provides: median, min, max, and distribution buckets

### Time to Response Distribution
**Formula**: Groups response times into buckets

**Buckets**:
- 0-1 days
- 2-3 days  
- 4-7 days
- 8-14 days
- 15-30 days
- 30+ days

### Success by Match Score
**Formula**: Groups applications by match score ranges and calculates response/interview rates for each range

**Score Ranges**:
- 0-50%
- 50-70%
- 70-85%
- 85-100%

**For each range**:
- `response_rate` = (applications with response in range) / (total applications in range) * 100
- `interview_rate` = (applications interviewed in range) / (total applications in range) * 100

### Best Performing Day of Week
**Formula**: Groups applications by day of week created and calculates response rate

**How it works**:
- Extracts day of week from `created_at` timestamp
- Groups all applications by day (Monday, Tuesday, etc.)
- For each day: `response_rate` = (applications with response) / (total applications) * 100
- Shows both response rate and total application count per day

## Trend Analysis

### Application Velocity (Daily)
**Formula**: Count of applications created per day

**How it works**:
- Groups applications by date (`created_at` formatted as YYYY-MM-DD)
- Counts applications per day
- Returns time series of daily counts

### Application Velocity (Cumulative)
**Formula**: Running total of applications over time

**How it works**:
- Same daily grouping as above
- Calculates cumulative sum: Day N cumulative = Sum of all days from first day to Day N
- Shows overall growth trend

### Status Distribution
**Formula**: Count of applications by current status

**How it works**:
- Normalizes all status labels to consistent format
- Counts applications in each status bucket
- Returns counts as pie chart data

### Company Type Analysis
**Formula**: Response/interview/offer rates grouped by company type

**How it works**:
- Uses `application.company_type` field (startup, enterprise, or unknown)
- For each type:
  - `response_rate` = (apps with response) / (total apps) * 100
  - `interview_rate` = (apps interviewed) / (total apps) * 100
  - `offer_rate` = (apps offered) / (total apps) * 100

### Location Insights
**Formula**: Response/interview rates grouped by job location

**How it works**:
- Uses `application.location` field
- Groups applications by location (e.g., "New York, NY", "Remote")
- For each location:
  - `response_rate` = (apps with response) / (total apps) * 100
  - `interview_rate` = (apps interviewed) / (total apps) * 100
- Sorted by response rate (highest first)

### Salary Range Distribution
**Formula**: Extracts and buckets salary data from applications

**How it works**:
- Parses `application.salary_range` field (e.g., "$120k - $150k")
- Extracts numeric values, converts "k" to thousands
- If range provided, calculates average: (min + max) / 2
- Groups into buckets:
  - $0-50k
  - $50k-75k
  - $75k-100k
  - $100k-125k
  - $125k-150k
  - $150k-200k
  - $200k+

## Skills Gap Analysis

### Most Requested Skills
**Formula**: Frequency count of skills appearing in job descriptions

**How it works**:
- Extracts skills from qualification files for each application
- Counts how many times each skill appears across all job descriptions
- Ranks by frequency (most common first)
- Also tracks average match score when skill appears

### Your Skill Gaps
**Formula**: Skills appearing in 3+ jobs that you don't have

**How it works**:
- Extracts "missing skills" from qualification analysis files
- Counts frequency of each missing skill across all applications
- Filters to skills appearing in at least 3 jobs
- Includes average match score impact (match score when this skill was missing)

### Learning Priorities
**Formula**: `Priority Score = Frequency * (Average Match Score Impact / 100)`

**How it works**:
- Takes top 20 skill gaps
- Calculates priority score: frequency × match score impact
- Sorts by priority score (highest first)
- Returns top 10 priorities with reason explanation

### Skill Match Trends Over Time
**Formula**: Average match score over time, grouped by top 10 skills

**How it works**:
- Groups applications by month
- For each month, tracks:
  - Overall average match score
  - Average match score for applications containing each of the top 10 most requested skills
  - Average match score for "other" skills (not in top 10)
- Shows trends as separate lines, color-coded by skill
- Helps identify which skills improve your match scores over time

## Data Sources

All analytics use data from:
- `Application` model fields (status, match_score, created_at, location, salary_range, company_type)
- Checklist items (response_received)
- Status update files in `updates/` folder
- Qualification analysis files (for skill extraction)

## Notes

- All percentages are rounded to 2 decimal places
- Empty/missing data is handled gracefully (returns 0, empty lists, or "Unknown")
- Date calculations assume EST timezone (-5 hours)
- Skill matching uses fuzzy matching and normalization from existing skill taxonomy

