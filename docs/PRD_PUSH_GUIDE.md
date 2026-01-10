# PRD Push Guide - Static Search Page Deployment

The PRD Push functionality automatically generates a static search page from your application and networking contact data, then deploys it to production via GitHub and Netlify.

## What is PRD Push?

PRD Push ("Production Push") is a feature that:

1. **Generates a static HTML page** containing all your applications and networking contacts
2. **Copies the page** to the deployment directory (`hunterapp_demo/kpro/`)
3. **Commits and pushes** to GitHub automatically
4. **Triggers Netlify auto-deployment** to make the page live
5. **Sends email notifications** about the deployment status

The generated page is a fully static HTML file with embedded data, so it can be deployed without requiring a backend server.

## How It Works

1. **Data Collection**: Fetches all applications and networking contacts from the Flask API
2. **Page Generation**: Creates a static HTML file with embedded JSON data
3. **File Deployment**: Copies the generated file to `hunterapp_demo/kpro/index.html`
4. **Git Operations**: 
   - Stages the file
   - Commits with message "Update kpro search page with latest data"
   - Pushes to `origin/main`
5. **Email Notification**: Sends status email using the same configuration as daily digest
6. **Netlify Deployment**: Automatically deploys from GitHub (if configured)

## Prerequisites

### Required Setup

1. **Flask App Running**: The application must be running on `http://localhost:51003`
2. **Git Repository**: The project must be a git repository with a remote configured
3. **Git Authentication**: You must have push access to the `origin/main` branch
4. **Email Configuration**: (Optional but recommended) Configure email for notifications

### Optional: Netlify Deployment

If you want automatic deployment to a public URL:

1. Connect your GitHub repository to Netlify
2. Configure Netlify to build from the `hunterapp_demo` directory
3. Set the publish directory to `hunterapp_demo`
4. The page will be available at: `https://your-domain.com/kpro`

## Configuration

### Email Configuration (Optional but Recommended)

PRD Push uses the **same email configuration** as the daily digest. To enable email notifications:

1. **Follow the Email Setup Guide**: See **[EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)** for detailed email configuration instructions

2. **Configure `config/digest_config.yaml`**:
   ```yaml
   email:
     enabled: true  # Set to true to receive PRD Push notifications
     smtp_server: smtp.zoho.com
     smtp_port: 587
     sender_email: "your-email@zoho.com"
     sender_password: "your-app-specific-password"
     recipient_email: "your-email@zoho.com"
     subject: "Daily Job Hunt Digest"  # Subject is overridden for PRD Push emails
   ```

3. **Test Email Configuration**: Generate a daily digest to verify email works:
   ```bash
   python3 scripts/generate_daily_digest.py
   ```

**Note**: PRD Push will send emails with subject "Prd Push - Static Search Page Generation - [STATUS]" regardless of the subject configured in the digest config.

### Git Configuration

Ensure your git is properly configured:

```bash
# Check git remote is configured
git remote -v

# Should show something like:
# origin  https://github.com/your-username/hunter.git (fetch)
# origin  https://github.com/your-username/hunter.git (push)

# If not configured, add remote:
git remote add origin https://github.com/your-username/hunter.git

# Verify you can push (may require authentication)
git push origin main --dry-run
```

## How to Use PRD Push

### Via Web Interface (Recommended)

1. **Start the Flask Application**:
   ```bash
   python -m app.web
   ```

2. **Navigate to Search Page**: Go to `http://localhost:51003/search`

3. **Click "Prd Push" Button**: Located in the search interface

4. **Wait for Processing**: 
   - The button will show a loading state
   - Processing typically takes 30-60 seconds
   - You'll see success/error messages

5. **Check Email**: If email is configured, you'll receive a notification with deployment status

### Via API

```bash
curl -X POST http://localhost:51003/api/static-search/generate
```

Response:
```json
{
  "success": true,
  "message": "Static search page generated successfully. Email notification sent.",
  "email_sent": true,
  "output_path": "/path/to/static_search/kpro.html",
  "deploy_path": "/path/to/hunterapp_demo/kpro/index.html",
  "kpro_path": "/path/to/hunterapp_demo/kpro/index.html",
  "git_committed": true,
  "git_pushed": true,
  "git_error": null
}
```

### Via Script (Manual)

```bash
# Generate static search page manually
python3 scripts/generate_static_search.py kpro.html

# Then manually commit and push if needed
cd hunterapp_demo/kpro
git add index.html
git commit -m "Update kpro search page with latest data"
git push origin main
```

## Email Notifications

### Success Notification (Fully Successful)

You'll receive an email when:
- Static page is generated successfully
- File is copied to deployment directory
- Git commit is successful
- Git push to GitHub is successful

Subject: `Prd Push - Static Search Page Generation - SUCCESSFUL`

Content includes:
- Success confirmation
- Confirmation of commit and push
- Netlify auto-deployment note
- URL where page will be available
- Details message

### Partial Success Notification

You'll receive an email when:
- Static page is generated successfully
- File is copied
- Git commit succeeds
- Git push fails

Subject: `Prd Push - Static Search Page Generation - PARTIAL SUCCESS`

Content includes:
- Success confirmation
- Warning that push failed
- Manual push instructions
- Git error details

### Already Up to Date Notification

You'll receive an email when:
- Static page is generated
- File is copied
- No changes detected in git

Subject: `Prd Push - Static Search Page Generation - UP TO DATE`

Content indicates file is already current and should be live.

### Failure Notification

You'll receive an email when:
- Static page generation fails
- Script timeout occurs
- Exception occurs during processing

Subject: `Prd Push - Static Search Page Generation - FAILED`

Content includes:
- Error message
- Instructions to check server logs

## Generated Files

### Source File
- **Location**: `static_search/kpro.html`
- **Content**: Full static HTML with embedded JSON data
- **Git Tracking**: Changes are ignored via `git update-index --skip-worktree`

### Deployment File
- **Location**: `hunterapp_demo/kpro/index.html`
- **Content**: Copy of source file, deployed to production
- **Git Tracking**: Tracked, committed, and pushed

### Data Embedded
The static page includes:
- All job applications (company, title, status, match score, dates, etc.)
- All networking contacts (name, company, status, notes, etc.)
- Full search and filtering capabilities
- No backend required once deployed

## Troubleshooting

### "Generation script not found" Error

**Problem**: The generator script is missing or path is incorrect.

**Solution**:
```bash
# Verify script exists
ls -la scripts/generate_static_search.py

# If missing, ensure you're in the correct directory
cd /path/to/hunter
```

### "Could not connect to Flask app" Error

**Problem**: Flask app is not running.

**Solution**:
```bash
# Start Flask app in a terminal
python -m app.web

# Verify it's running
curl http://localhost:51003/api/check-ollama
```

### Git Push Fails

**Problem**: Authentication or permission issues with git.

**Solutions**:

1. **Check Git Remote Configuration**:
   ```bash
   git remote -v
   ```

2. **Verify Authentication**:
   ```bash
   # For HTTPS, you may need a personal access token
   git push origin main
   ```

3. **Check Branch Name**:
   ```bash
   # Ensure you're pushing to the correct branch
   git branch
   git push origin main  # or master, depending on your setup
   ```

4. **Manual Push** (if automatic fails):
   ```bash
   cd hunterapp_demo/kpro
   git add index.html
   git commit -m "Update kpro search page with latest data"
   git push origin main
   ```

### Email Notifications Not Sending

**Problem**: Email configuration is incorrect or disabled.

**Solution**:
1. Verify email is enabled in `config/digest_config.yaml`:
   ```yaml
   email:
     enabled: true
   ```

2. Follow **[EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)** to configure email properly

3. Test email configuration with daily digest:
   ```bash
   python3 scripts/generate_daily_digest.py
   ```

4. Check server logs for email errors:
   ```bash
   # Look for "Error sending Prd Push notification email" in terminal
   ```

### "No changes detected" Message

**Problem**: The generated file is identical to the version already in git.

**Solution**: This is normal! The data hasn't changed since the last generation. The page is already up to date. This is not an error.

### Generation Timeout

**Problem**: Process takes longer than 60 seconds.

**Solutions**:
1. Check if Flask app is responsive:
   ```bash
   curl http://localhost:51003/api/applications-and-contacts
   ```

2. Reduce data size (if you have many applications/contacts, generation may be slower)

3. Check system resources (RAM, CPU)

### Netlify Not Auto-Deploying

**Problem**: Netlify isn't deploying after git push.

**Solutions**:
1. **Verify Netlify Integration**:
   - Check Netlify dashboard for your site
   - Verify GitHub repository is connected
   - Check deployment logs

2. **Verify Build Settings**:
   - Publish directory: `hunterapp_demo`
   - Build command: (leave empty or use `echo "No build needed"`)
   - Base directory: (leave empty)

3. **Check File Path**:
   - Ensure `hunterapp_demo/kpro/index.html` exists
   - Verify file was committed and pushed

4. **Manual Deploy** (if needed):
   - Go to Netlify dashboard
   - Click "Trigger deploy" > "Deploy site"

## Best Practices

### When to Use PRD Push

✅ **Use PRD Push when:**
- You've added new applications or contacts
- Application statuses have changed significantly
- You want to update the public search page
- Weekly/monthly updates to keep data current

❌ **Don't use PRD Push:**
- After every single application creation (too frequent)
- If you're in active development (may cause conflicts)
- If git is in a conflicted state

### Frequency Recommendations

- **Daily**: If you're actively applying and want real-time public data
- **Weekly**: Good balance for most users
- **Monthly**: Sufficient for occasional updates

### Security Considerations

- The static page contains **all your application data** including company names, job titles, and statuses
- Ensure the deployed URL (e.g., `hunter.kervinapps.com/kpro`) is appropriate for public access
- Consider adding authentication to the Netlify deployment if data is sensitive
- Review what information is included in the embedded JSON data

## Advanced Usage

### Custom Output Filename

The default generates `kpro.html`, but you can customize:

```bash
# Generate with custom filename
python3 scripts/generate_static_search.py my-search.html
```

Then manually copy to deployment directory if needed.

### Skip Git Operations

If you want to generate the file without git operations:

1. Use the manual script approach
2. Or modify the API endpoint to skip git steps (development only)

### Custom Deployment Directory

To deploy to a different location, modify `app/web.py`:

```python
# Change this line (around line 510):
deploy_dir = get_project_root() / 'hunterapp_demo'
# To your custom directory
deploy_dir = get_project_root() / 'your_custom_directory'
```

## Related Documentation

- **[EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)** - Email configuration (required for notifications)
- **[USER_GUIDE.md](USER_GUIDE.md)** - General application usage
- **[API_REFERENCE.md](API_REFERENCE.md)** - API documentation

## Support

If you encounter issues not covered here:

1. Check server logs in the terminal running Flask
2. Review git status: `git status`
3. Verify Flask app is responsive: `curl http://localhost:51003/api/check-ollama`
4. Check email configuration separately using daily digest
5. Review Netlify deployment logs (if using Netlify)
