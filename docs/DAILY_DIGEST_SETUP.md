# Daily Digest Setup Guide

This guide explains how to set up the daily digest generator to automatically create summaries of your job hunting activities.

## Overview

The daily digest automatically generates a Markdown file containing:
- Today's activities (new applications, status changes, networking contacts)
- Key metrics from the last 30 days (response rates, interview conversion, etc.)
- Status distribution
- Best performing days
- Optional: Skills analysis

## Quick Start

### 1. Test the Script Manually

First, test that the script works:

```bash
cd /path/to/hunter
python3 scripts/generate_daily_digest.py
```

This will generate a digest file at: `data/output/digests/YYYY-MM-DD-digest.md`

### 2. Configure Email (Optional)

Edit `config/digest_config.yaml`:

```yaml
email:
  enabled: true
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender_email: "your-email@gmail.com"
  sender_password: "your-app-password"  # Use app-specific password for Gmail
  recipient_email: "recipient@gmail.com"
  subject: "Daily Job Hunt Digest"
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an app-specific password: https://myaccount.google.com/apppasswords
3. Use that password in the config

### 3. Set Up Scheduling

#### macOS / Linux (Cron)

1. Open your crontab:
```bash
crontab -e
```

2. Add this line to run daily at 8:00 AM:
```bash
0 8 * * * cd /path/to/hunter && /usr/bin/python3 scripts/generate_daily_digest.py >> /path/to/hunter/data/output/digests/cron.log 2>&1
```

**Important:** Replace `/path/to/hunter` with your actual project path.

**To find your Python path:**
```bash
which python3
```

**Example crontab entry:**
```bash
0 8 * * * cd /Users/kervinleacock/Documents/Development/hunter && /usr/local/bin/python3 scripts/generate_daily_digest.py >> /Users/kervinleacock/Documents/Development/hunter/data/output/digests/cron.log 2>&1
```

3. Save and exit (in vim: press `Esc`, type `:wq`, press Enter)

4. Verify it's scheduled:
```bash
crontab -l
```

#### Windows (Task Scheduler)

1. Open Task Scheduler (search for it in Start menu)

2. Click "Create Basic Task"

3. Name it: "Daily Job Hunt Digest"

4. Set trigger: Daily, at 8:00 AM

5. Action: Start a program
   - Program: `C:\Python3\python.exe` (or your Python path)
   - Arguments: `scripts\generate_daily_digest.py`
   - Start in: `C:\path\to\hunter` (your project path)

6. Finish the wizard

## Command Line Options

```bash
# Generate digest for today
python3 scripts/generate_daily_digest.py

# Generate digest for specific date
python3 scripts/generate_daily_digest.py --date 2025-01-15

# Generate but skip email
python3 scripts/generate_daily_digest.py --no-email

# Use custom config file
python3 scripts/generate_daily_digest.py --config /path/to/custom_config.yaml
```

## Output Location

Digests are saved to: `data/output/digests/YYYY-MM-DD-digest.md`

Example: `data/output/digests/2025-01-15-digest.md`

## Customizing the Template

Edit `scripts/digest_template.md` to customize the digest format. The template uses Jinja2 syntax.

Available variables:
- `date` - Formatted date (e.g., "January 15, 2025")
- `daily_activities` - List of today's activities
- `metrics` - Analytics metrics
- `pipeline` - Pipeline conversion data
- `status_distribution` - Status counts
- `best_days` - Best performing days
- `skills_analysis` - Skills data (if enabled)

## Troubleshooting

### Script doesn't run from cron

1. **Check Python path**: Cron may use a different Python. Use full path:
```bash
which python3
```

2. **Check file permissions**: Make script executable:
```bash
chmod +x scripts/generate_daily_digest.py
```

3. **Check cron logs**: Look at the log file specified in crontab

4. **Test manually**: Run the script manually first to ensure it works

### Email not sending

1. **Check config**: Verify `email.enabled: true` in config file
2. **Check credentials**: Ensure email/password are correct
3. **Gmail users**: Use app-specific password, not regular password
4. **Check SMTP settings**: Verify server and port are correct

### No activities showing

- Activities are logged when you create applications or change statuses
- If you haven't done anything today, the digest will show "No activities recorded today"
- Historical data will still show in metrics sections

## Advanced: Custom Schedule

To run at different times, modify the cron schedule:

```bash
# Every day at 8 AM
0 8 * * *

# Every day at 6 PM
0 18 * * *

# Every Monday at 9 AM
0 9 * * 1

# Twice daily (8 AM and 6 PM)
0 8,18 * * *
```

Cron format: `minute hour day month weekday`

## Next Steps

- Option 2: Flask CLI Command (if you want to run within Flask app context)
- Option 3: GitHub Actions (if you want cloud-based scheduling)

