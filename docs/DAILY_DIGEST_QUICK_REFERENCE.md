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

## Email Setup (Zoho Mail)

1. **Enable IMAP Access** in Zoho Mail: Settings > Mail Accounts > IMAP Access
2. **If 2FA enabled**: Generate app-specific password in Settings > Account Security
3. **Update `config/digest_config.yaml`**:
   ```yaml
   email:
     enabled: true
     smtp_server: smtp.zoho.com  # Use smtppro.zoho.com for organization accounts
     smtp_port: 587  # Port 587 (TLS) or 465 (SSL)
     sender_email: "your-email@zoho.com"
     sender_password: "your-app-password"  # App password if 2FA, or regular password
     recipient_email: "recipient@example.com"
   ```
   
   **For Canadian Data Center** (mail.zohocloud.ca):
   ```yaml
   email:
     enabled: true
     smtp_server: smtp.zoho.com
     smtp_port: 587
     sender_email: "your-email@yourdomain.ca"
     sender_password: "your-app-password"
     recipient_email: "your-email@yourdomain.ca"
   ```

**Reference:** [Zoho Mail SMTP Setup](https://www.zoho.com/mail/help/zoho-smtp.html)

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
- Check SMTP credentials (server, port, email, password)
- **Zoho Mail**: Ensure IMAP Access is enabled in settings
- **Zoho Mail with 2FA**: Use app-specific password (not regular password)
- Verify SMTP server: `smtp.zoho.com` (personal) or `smtppro.zoho.com` (organization)
- Try port 587 (TLS) or 465 (SSL)

