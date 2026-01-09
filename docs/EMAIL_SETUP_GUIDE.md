# Email Setup Guide for Daily Digest

The daily digest can be automatically emailed to you. Here's how to set it up:

## Quick Setup (Zoho Mail) - Recommended

### Step 1: Enable IMAP Access in Zoho Mail
1. Log in to your Zoho Mail account at [https://mail.zohocloud.ca](https://mail.zohocloud.ca) (or your Zoho Mail URL)
2. Click on the **Settings** (gear icon) in the top-right corner
3. Navigate to **Mail Accounts** > **IMAP Access**
4. Ensure that **IMAP Access** is enabled
5. Click **Save** to apply the changes

**Reference:** [Zoho IMAP Access Guide](https://www.zoho.com/mail/help/imap-access.html)

### Step 2: Generate App-Specific Password (If 2FA is Enabled)
If you have Two-Factor Authentication (2FA) enabled on your Zoho account:

1. Log in to your Zoho Mail account
2. Go to **Settings** > **Account Security**
3. Under **Application-Specific Passwords**, click **Generate New Password**
4. Enter a name for the app (e.g., "Daily Digest Script") and click **Generate**
5. Copy the generated password (you'll only see it once!) 1XCt30Ruzgpx


**Note:** If 2FA is not enabled, you can use your regular Zoho Mail password.

**Reference:** [Zoho SMTP Setup Guide](https://www.zoho.com/mail/help/zoho-smtp.html)

### Step 3: Update Config File
Edit `config/digest_config.yaml`:

For **Personal Zoho Mail** (e.g., username@zoho.com or username@zoho.ca):
```yaml
email:
  enabled: true  # Change to true
  smtp_server: smtp.zoho.com
  smtp_port: 587
  sender_email: "your-email@zoho.com"  # Your Zoho Mail address
  sender_password: "your-app-specific-password"  # App password if 2FA enabled, or regular password
  recipient_email: "your-email@zoho.com"  # Where to send (can be same or different)
  subject: "Daily Job Hunt Digest"
```

For **Organization/Enterprise Zoho Mail** (e.g., you@yourdomain.com):
```yaml
email:
  enabled: true  # Change to true
  smtp_server: smtp.zohocloud.ca
  smtp_port: 465
  sender_email: "your-email@yourdomain.com"  # Your domain-based Zoho Mail address
  sender_password: "your-app-specific-password"  # App password if 2FA enabled
  recipient_email: "your-email@yourdomain.com"
  subject: "Daily Job Hunt Digest"
```

For **Canadian Data Center** (mail.zohocloud.ca):
```yaml
email:
  enabled: true
  smtp_server: smtp.zoho.com  # Use standard Zoho SMTP server (works for all regions)
  smtp_port: 587  # Port 587 (TLS) recommended, or 465 (SSL)
  sender_email: "your-email@yourdomain.ca"  # Your Zoho Mail address
  sender_password: "your-app-specific-password"  # App password if 2FA enabled
  recipient_email: "your-email@yourdomain.ca"  # Where to send
  subject: "Daily Job Hunt Digest"
```

**Important Notes:** 
- Port **587 with TLS** is recommended (better compatibility)
- Port **465 with SSL** is also supported
- If 2FA is enabled, you **must** generate and use an app-specific password
- If 2FA is not enabled, you can use your regular Zoho Mail password
- Ensure **IMAP Access** is enabled in Zoho Mail settings
- The standard `smtp.zoho.com` server works for all Zoho Mail regions, including Canadian data center

### Step 4: Test It
```bash
python3 scripts/generate_daily_digest.py
```

You should see:
```
✅ Digest generated: /path/to/digest.md
✅ Email sent to your-email@zoho.com
```

## Alternative Setup (Gmail)

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

## Zoho Mail SMTP Server Options

Depending on your Zoho Mail account type:

**Personal Accounts** (username@zoho.com, username@zoho.ca, username@zohomail.com):
- Server: `smtp.zoho.com`
- Port: `587` (TLS) or `465` (SSL)

**Organization/Enterprise Accounts** (you@yourdomain.com):
- Server: `smtppro.zoho.com`
- Port: `587` (TLS) or `465` (SSL)

**Canadian Data Center** (mail.zohocloud.ca):
- Server: `smtp.zoho.com` (standard Zoho SMTP works for all regions)
- Port: `587` (TLS) or `465` (SSL)

**Reference:** [Zoho Mail SMTP Settings](https://www.zoho.com/mail/help/zoho-smtp.html)

## Other Email Providers

### Gmail (Alternative)
```yaml
email:
  enabled: true
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender_email: "your-email@gmail.com"
  sender_password: "your-app-password"  # Required: app-specific password
  recipient_email: "recipient@example.com"
```

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
- **Zoho Mail**: 
  - Make sure IMAP Access is enabled in Zoho Mail settings
  - If 2FA is enabled, use an app-specific password, not your regular password
  - Verify your email address is correct (case-sensitive for some domains)
  - Check that you're using the correct SMTP server (smtp.zoho.com for personal, smtppro.zoho.com for organization)
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

