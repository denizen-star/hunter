# Daily Digest Quick Reference

## Quick Commands

```bash
# Generate today's digest
python3 scripts/generate_daily_digest.py

# Generate for specific date
python3 scripts/generate_daily_digest.py --date 2025-01-15

# Generate without email
python3 scripts/generate_daily_digest.py --no-email
```

## File Locations

- **Script**: `scripts/generate_daily_digest.py`
- **Template**: `scripts/digest_template.md`
- **Config**: `config/digest_config.yaml`
- **Output**: `data/output/digests/YYYY-MM-DD-digest.md`

## Cron Examples

### Daily at 8 AM
```bash
0 8 * * * cd /path/to/hunter && python3 scripts/generate_daily_digest.py
```

### Daily at 6 PM
```bash
0 18 * * * cd /path/to/hunter && python3 scripts/generate_daily_digest.py
```

### Every Monday at 9 AM
```bash
0 9 * * 1 cd /path/to/hunter && python3 scripts/generate_daily_digest.py
```

## Email Setup (Gmail)

1. Enable 2FA on Gmail
2. Generate app password: https://myaccount.google.com/apppasswords
3. Update `config/digest_config.yaml`:
   ```yaml
   email:
     enabled: true
     sender_email: "your-email@gmail.com"
     sender_password: "your-app-password"
     recipient_email: "recipient@gmail.com"
   ```

## Troubleshooting

**Script fails to run:**
- Check Python path: `which python3`
- Make script executable: `chmod +x scripts/generate_daily_digest.py`
- Run manually first to see errors

**No activities in digest:**
- Activities are logged when you create/update applications
- Historical metrics still show even if no activities today

**Email not sending:**
- Verify `email.enabled: true` in config
- Check SMTP credentials
- Gmail requires app-specific password (not regular password)

