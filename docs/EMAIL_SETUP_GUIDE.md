# Email Setup Guide for Daily Digest

The daily digest can be automatically emailed to you. Here's how to set it up:

## Quick Setup (Gmail)

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not already enabled

### Step 2: Generate App-Specific Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Enter "Hunter Daily Digest" as the name
4. Click "Generate"
5. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)

### Step 3: Update Config File
Edit `config/digest_config.yaml`:

```yaml
email:
  enabled: true  # Change to true
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender_email: "your-email@gmail.com"  # Your Gmail address
  sender_password: "abcd efgh ijkl mnop"  # The app password from Step 2
  recipient_email: "your-email@gmail.com"  # Where to send (can be same or different)
  subject: "Daily Job Hunt Digest"
```

**Important:** Use the app-specific password, NOT your regular Gmail password!

### Step 4: Test It
```bash
python3 scripts/generate_daily_digest.py
```

You should see:
```
✅ Digest generated: /path/to/digest.md
✅ Email sent to your-email@gmail.com
```

## Other Email Providers

### Outlook/Hotmail
```yaml
email:
  enabled: true
  smtp_server: smtp-mail.outlook.com
  smtp_port: 587
  sender_email: "your-email@outlook.com"
  sender_password: "your-password"
  recipient_email: "recipient@example.com"
```

### Yahoo Mail
```yaml
email:
  enabled: true
  smtp_server: smtp.mail.yahoo.com
  smtp_port: 587
  sender_email: "your-email@yahoo.com"
  sender_password: "your-app-password"  # Yahoo also requires app password
  recipient_email: "recipient@example.com"
```

### Custom SMTP Server
```yaml
email:
  enabled: true
  smtp_server: mail.yourdomain.com
  smtp_port: 587  # or 465 for SSL
  sender_email: "your-email@yourdomain.com"
  sender_password: "your-password"
  recipient_email: "recipient@example.com"
```

## Email Format

The email includes:
- **HTML body**: Formatted digest with styling
- **Markdown attachment**: The original `.md` file for easy reference

## Troubleshooting

### "Authentication failed" error
- **Gmail**: Make sure you're using an app-specific password, not your regular password
- **Other providers**: Check if they require app passwords or special authentication

### "Connection refused" error
- Check your internet connection
- Verify SMTP server and port are correct
- Some networks block SMTP ports - try a different network

### Email not sending but no error
- Check that `enabled: true` in config
- Verify all email fields are filled in
- Check spam/junk folder

### Test email sending separately
You can test just the email part:
```bash
python3 scripts/generate_daily_digest.py --no-email  # Generate but don't send
# Then manually test email in Python:
python3 -c "
from scripts.generate_daily_digest import DailyDigestGenerator
from pathlib import Path
gen = DailyDigestGenerator()
gen.send_email(Path('data/output/digests/2025-12-28-digest.md'))
"
```

## Security Notes

- **Never commit passwords to git**: The config file should be in `.gitignore` or use environment variables
- **Use app-specific passwords**: More secure than regular passwords
- **Consider using environment variables** for sensitive data (future enhancement)

## Disable Email

To stop sending emails, just set:
```yaml
email:
  enabled: false
```

Or use the `--no-email` flag:
```bash
python3 scripts/generate_daily_digest.py --no-email
```

