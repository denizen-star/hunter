# Analytics Metrics - How They Are Calculated

## Response Rate

**Calculation**:
```
Response Rate = (Applications with response_received checked) / (Total applications applied) × 100
```

**Details**:
- Uses `get_response_received_at()` method which checks:
  1. `response_received` checklist item being checked
  2. Status updates indicating company response (Company Response, Contacted Hiring Manager, etc.)
- Denominator is all applications where status is not "pending"
- Returns percentage (0-100%)

## Average Time to Response

**Calculation**:
```
Average = Mean of (response_date - applied_date) for all applications with responses
```

**Details**:
- `applied_date`: Application `created_at` OR `status_updated_at` when status changed to "applied"
- `response_date`: When `response_received` checklist item was first checked (from `get_response_received_at()`)
- Calculated in days (can be fractional)
- Also provides: median, min, max values

## Time to Response Distribution

**Calculation**:
Groups all response times into buckets:
- 0-1 days
- 2-3 days
- 4-7 days
- 8-14 days
- 15-30 days
- 30+ days

Count of applications in each bucket.

## Success by Match Score

**Calculation**:
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

## Best Performing Day of Week

**Calculation**:
- Groups applications by day of week from `created_at` timestamp
- For each day (Monday-Sunday):
```
response_rate = (apps_with_response_on_day / total_apps_on_day) × 100
```

Shows both response rate % and total application count per day.

## Application Velocity (Daily)

**Calculation**:
Counts applications created per day:
- Groups by date (YYYY-MM-DD format)
- Returns time series: date → count

## Application Velocity (Cumulative)

**Calculation**:
Running total of applications:
- Same daily grouping
- Cumulative sum: Day N = Sum of all previous days + Day N
- Shows growth trend over time

## Status Distribution

**Calculation**:
Count of applications by current normalized status:
- Normalizes status labels (e.g., "contacted hiring manager" → "company response")
- Counts applications in each status bucket
- Pie chart data

## Company Type Analysis

**Calculation**:
Groups by `application.company_type` (startup, enterprise, unknown):
```
response_rate = (apps_with_response / total_apps) × 100
interview_rate = (apps_interviewed / total_apps) × 100
offer_rate = (apps_offered / total_apps) × 100
```

## Location Insights

**Calculation**:
Groups by `application.location`:
- For each unique location:
  - Response rate
  - Interview rate
- Sorted by response rate (highest first)
- Shows top locations

## Salary Range Distribution

**Calculation**:
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
   - $200k+

## Skills Gap Analysis

### Most Requested Skills
Counts frequency of each skill appearing in job descriptions across all applications.

### Skill Gaps
Skills appearing in 3+ jobs that are missing from your resume (from qualification analysis).

### Learning Priorities
Priority Score = Frequency × (Average Match Score Impact / 100)
- Sorted by priority score
- Top 10 recommendations

### Skill Match Trends Over Time
**NEW STRUCTURE**:
- Tracks match scores by month
- **Top 10 Skills**: Individual lines for each of the 10 most requested skills
- **Other Skills**: Grouped together as "Other" line
- Each line shows average match score over time for applications containing that skill
- Color-coded for easy identification





