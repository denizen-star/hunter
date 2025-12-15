# Performance Optimization for Reports, Analytics, and Daily Activities

## Overview

This document describes the performance optimizations implemented to improve the speed of the Reports, Analytics, and Daily Activities pages after adding the Networking module.

## Problem

After adding the Networking module, the following pages became slow:
- **Reports** (`/reports`) - Loading all applications and networking contacts, then scanning all update files
- **Analytics** (`/analytics`) - Complex calculations on all applications
- **Daily Activities** (`/daily-activities`) - Scanning all applications and contacts for activities

## Solution: Activity Log System

We've implemented a centralized **Activity Log** system that maintains a single JSON file tracking all activities. This eliminates the need to scan all files on every request.

### Key Components

1. **ActivityLogService** (`app/services/activity_log_service.py`)
   - Maintains a single JSON log file (`data/output/activity_log.json`)
   - Logs all activities in real-time:
     - Job application creation
     - Application status changes
     - Networking contact creation
     - Networking status changes
   - Provides fast querying methods for reports

2. **Automatic Logging**
   - `JobProcessor` automatically logs when applications are created or status changes
   - `NetworkingProcessor` automatically logs when contacts are created or status changes
   - No manual intervention required

3. **Optimized Endpoints**
   - **Daily Activities**: Now uses activity log directly (5-minute cache)
   - **Analytics**: Uses 24-hour cache (refreshes once per day)
   - **Reports**: Uses activity log for bulk data, only loads applications/contacts for follow-up/flagged items

## Performance Improvements

### Before
- Reports: ~5-10 seconds (scanning all files)
- Daily Activities: ~3-5 seconds (scanning all files)
- Analytics: ~5-8 seconds (processing all applications)

### After
- Reports: ~0.5-1 second (using activity log + 5-minute cache)
- Daily Activities: ~0.2-0.5 seconds (using activity log + 5-minute cache)
- Analytics: ~0.5-1 second (using 24-hour cache)

## Migration

To backfill the activity log with existing data, run:

```bash
python backfill_activity_log.py
```

This script will:
- Scan all existing applications and log their creation
- Scan all status update files and log status changes
- Scan all networking contacts and log their creation
- Scan all networking status updates and log status changes

**Note**: The script is idempotent - it won't create duplicate entries if run multiple times.

## Cache Strategy

### Daily Activities
- **Cache Duration**: 5 minutes (300 seconds)
- **Rationale**: Activities are logged in real-time, so cache can be short
- **Cache File**: `data/output/daily_activities_cache.json`

### Analytics
- **Cache Duration**: 24 hours (86400 seconds)
- **Rationale**: Analytics are computationally expensive and don't need real-time updates
- **Cache File**: `data/output/analytics_cache_{period}_{gap_period}.json`

### Reports
- **Cache Duration**: 5 minutes (300 seconds)
- **Rationale**: Uses activity log for bulk data, cache provides additional speed
- **Cache File**: `data/output/reports_cache_{period}_{type}_{gap_period}.json`

## Activity Log Structure

The activity log is stored as JSON with the following structure:

```json
{
  "version": "1.0",
  "created_at": "2025-01-15T10:00:00-04:00",
  "last_updated": "2025-01-15T15:30:00-04:00",
  "activities": [
    {
      "id": "20250115100000-Company-JobTitle_20250115100000",
      "type": "job_application_created",
      "application_id": "20250115100000-Company-JobTitle",
      "company": "Company",
      "job_title": "Job Title",
      "status": "pending",
      "match_score": 85.5,
      "timestamp": "2025-01-15T10:00:00-04:00",
      "date": "2025-01-15"
    },
    {
      "id": "20250115100000-Company-JobTitle_status_20250115120000",
      "type": "job_application_status_changed",
      "application_id": "20250115100000-Company-JobTitle",
      "company": "Company",
      "job_title": "Job Title",
      "old_status": "pending",
      "new_status": "applied",
      "timestamp": "2025-01-15T12:00:00-04:00",
      "date": "2025-01-15"
    }
  ]
}
```

## Maintenance

The activity log automatically maintains itself:
- New activities are appended in real-time
- The log is limited to the last 10,000 activities to prevent file growth
- Old activities are automatically removed when the limit is reached

## Future Enhancements

Potential improvements:
1. **Database Migration**: Move from JSON file to SQLite/PostgreSQL for better querying
2. **Incremental Updates**: Only process new activities since last cache update
3. **Background Processing**: Pre-compute reports in background jobs
4. **Activity Log Archiving**: Archive old activities to separate files

## Troubleshooting

### Activity Log Not Updating
- Check that `JobProcessor` and `NetworkingProcessor` are initialized with `ActivityLogService`
- Verify file permissions on `data/output/activity_log.json`
- Check for errors in application logs

### Cache Not Refreshing
- Delete cache files in `data/output/` to force refresh
- Check cache TTL settings in `app/web.py`

### Missing Historical Data
- Run `backfill_activity_log.py` to populate historical activities
- Note: Status change history may be approximate (old status inferred from current status)

