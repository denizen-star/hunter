# User Guide

Complete guide to using Job Hunter for managing your job applications.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Setting Up Your Resume](#setting-up-your-resume)
3. [Creating Applications](#creating-applications)
4. [Understanding the Results](#understanding-the-results)
5. [Managing Applications](#managing-applications)
6. [Dashboard Overview](#dashboard-overview)
7. [Daily Digest](#daily-digest)
8. [PRD Push - Static Search Page Deployment](#prd-push---static-search-page-deployment)
9. [Best Practices](#best-practices)

## Getting Started

### First Time Setup

1. **Start Ollama** (in a terminal):
   ```bash
   ollama serve
   ```

2. **Start Job Hunter** (in another terminal):
   ```bash
   cd /path/to/hunter
   source venv/bin/activate
   python -m app.web
   ```

3. **Open your browser**: http://localhost:51003

### Main Interface

The main page has three sections:
- **Quick Links**: Access dashboard, check AI status, manage resume
- **Status Banner**: Shows connection status and notifications
- **Application Form**: Create new job applications

## Setting Up Your Resume

Your resume is the foundation for all applications. Set it up once, use it everywhere.

### Via Web Interface (Recommended)

1. Click "📄 Manage Resume" on the main page
2. Fill in your information:
   - **Full Name**: Your complete name
   - **Email**: Professional email address
   - **Phone**: Contact number
   - **LinkedIn**: Your LinkedIn profile URL
   - **Location**: City, State/Country
   - **Resume Content**: Your full resume in Markdown format

3. Click "Save Resume"

### Resume Content Format

Use Markdown format for your resume:

```markdown
# Your Name

## Professional Summary
Brief summary of your experience and skills.

## Experience

### Job Title | Company Name
*Month Year - Present*

- Key accomplishment with quantifiable results
- Technical skills demonstrated
- Leadership or impact examples

### Previous Job Title | Previous Company
*Month Year - Month Year*

- Achievement showing growth
- Project contributions
- Technologies used

## Education

### Degree Name | University
*Year*

## Skills

**Technical**: Python, React, AWS, Docker, PostgreSQL
**Soft Skills**: Leadership, Communication, Problem-solving
```

### Tips for a Great Resume

✅ **Do:**
- Use clear, concise bullet points
- Include quantifiable achievements (numbers, percentages, dollar amounts)
- List specific technologies and tools
- Mention years of experience with key skills
- Include certifications

❌ **Don't:**
- Use vague language ("responsible for...")
- Forget to update regularly
- Include personal information (SSN, photo, age)
- Make it too long (2-3 pages max)

## Creating Applications

### Basic Workflow

1. Find a job posting you're interested in
2. Copy the complete job description
3. Go to http://localhost:51003
4. Fill in the application form:
   - **Company Name** (required)
   - **Job Title** (required)
   - **Job URL** (optional but recommended)
   - **Job Description** (paste the entire posting)
5. Click "🚀 Analyze & Create Application"
6. Wait 30-90 seconds for AI processing

### What to Include in Job Description

Copy the ENTIRE job posting, including:
- Company description
- Job responsibilities
- Required qualifications
- Preferred qualifications
- Benefits and perks
- Salary range (if mentioned)
- Location information
- Hiring manager name (if mentioned)

**More information = Better analysis!**

### During Processing

You'll see:
- Loading spinner
- "AI is working its magic..." message
- Estimated time remaining

The AI is:
1. Extracting features from the job description
2. Extracting features from your resume
3. Calculating match score
4. Generating qualifications analysis
5. Writing customized cover letter
6. Creating tailored resume
7. Building summary page

## Understanding the Results

### Match Score

After processing completes, you'll see your **Match Score** (0-100%):

- **80-100%**: Excellent match! Apply with confidence
- **60-79%**: Good match, highlight relevant experience
- **40-59%**: Moderate match, consider if you can bridge gaps
- **Below 40%**: Significant gaps, may not be the best fit

### Generated Documents

Click "View Summary" to see:

#### 1. Summary Section
- **Match Score**: Your overall match percentage
- **Salary Range**: Extracted from job posting
- **Location**: Job location
- **Hiring Manager**: If mentioned in posting
- **Status**: Current application status
- **Job URL**: Link to original posting
- **Timestamps**: When created and last updated

#### 2. Job Description Tab
- Complete job posting
- Extracted features highlighted

#### 3. Qualifications Analysis Tab
Shows:
- **Skills Match Summary**: Overall assessment
- **Strong Matches**: Skills you have that match requirements
- **Missing Skills**: Skills mentioned in job but not in your resume
- **Detailed Analysis**: Skill-by-skill breakdown
- **Soft Skills Alignment**: Leadership, communication, etc.
- **Recommendations**: How to address gaps

#### 4. Cover Letter Tab
AI-generated cover letter that:
- Addresses the specific company and role
- Integrates 50% of required soft skills
- Highlights your strongest matches
- Uses professional, engaging tone
- Includes call to action

#### 5. Customized Resume Tab
Your resume rewritten to:
- Align with job keywords
- Emphasize relevant experience
- Optimize for ATS (Applicant Tracking Systems)
- Keep bullets short and impactful

#### 6. Updates & Notes Tab
Timeline of:
- Application creation
- Status changes
- Your notes and follow-ups

## Managing Applications

### Viewing All Applications

Go to **http://localhost:51003/dashboard**

You'll see:
- Total applications count
- Breakdown by status (Pending, Applied, Interviewed)
- Grid of application cards

Each card shows:
- Company name and job title
- Match score
- Status (color-coded pill)
- Creation date
- Last update date
- "View Summary" button

### Updating Application Status

Use the API to update status:

```bash
curl -X PUT http://localhost:51003/api/applications/<APP_ID>/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "applied",
    "notes": "Submitted application via company website"
  }'
```

**Available Statuses:**
- `pending` - Created but not yet submitted
- `applied` - Application submitted
- `interviewed` - Interview scheduled or completed
- `offered` - Received job offer
- `rejected` - Application rejected
- `accepted` - Accepted job offer

### Application Files

Each application creates a folder:
```
data/applications/<Company>-<JobTitle>/
├── application.yaml
├── <timestamp>-<Company>-<JobTitle>.md (job description)
├── <JobTitle>-Qualifications.md
├── <Name>-<Company>-<JobTitle>-intro.md (cover letter)
├── <Name>-<Company>-<JobTitle>-Resume.md (customized resume)
├── <timestamp>-Summary-<Company>-<JobTitle>.html
└── updates/ (status notes)
```

## Dashboard Overview

### Stats at a Glance
- **Total**: All applications
- **Pending**: Not yet submitted
- **Applied**: Submitted, awaiting response
- **Interviewed**: In interview process

### Application Cards
- Click "View Summary" to see full details
- Cards show match score for quick assessment
- Color-coded status badges

### Creating New Application from Dashboard
Click "+ New Application" to return to main form

## Daily Digest

Job Hunter can automatically generate daily digest reports that summarize your job hunting activity, including status changes, new applications, and analytics.

### Generating a Daily Digest

The daily digest can be generated manually or automated:

```bash
# Generate daily digest manually
python3 scripts/generate_daily_digest.py
```

This creates a markdown file in `data/output/digests/` with today's date, containing:
- Summary of activity since last digest
- Status changes (new applications, status updates)
- Analytics and metrics
- List of all current applications
- Networking contacts updates (if applicable)

### Email Configuration

To receive daily digests via email, you need to configure email settings. See the **[Email Setup Guide](EMAIL_SETUP_GUIDE.md)** for detailed instructions on setting up:

- Zoho Mail (recommended)
- Gmail
- Outlook/Hotmail
- Yahoo Mail
- Custom SMTP servers

**Quick Setup Steps:**

1. Copy the sample configuration file:
   ```bash
   cp config/digest_config.yaml.example config/digest_config.yaml
   ```

2. Edit `config/digest_config.yaml` with your email settings

3. Follow the detailed instructions in **[EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)** to:
   - Enable IMAP access in your email provider
   - Generate app-specific passwords (if 2FA enabled)
   - Configure SMTP server settings
   - Test email delivery

4. Generate and test:
   ```bash
   python3 scripts/generate_daily_digest.py
   ```

### Digest Contents

The daily digest includes:
- **Activity Summary**: New applications created, status updates, notes added
- **Status Changes**: All applications that changed status since last digest
- **Analytics**: Match score distribution, application counts by status
- **Application List**: Quick reference of all active applications
- **Networking Updates**: New contacts added, research completed (if applicable)

### Automating Daily Digest

You can set up a cron job (macOS/Linux) or Task Scheduler (Windows) to automatically generate and email the digest daily. See **[DAILY_DIGEST_SETUP.md](DAILY_DIGEST_SETUP.md)** for automation instructions.

## PRD Push - Static Search Page Deployment

PRD Push ("Production Push") allows you to generate a static HTML search page containing all your applications and networking contacts, then automatically deploy it to production via GitHub and Netlify.

### What is PRD Push?

PRD Push generates a fully static HTML page with embedded data that can be deployed without a backend server. This is useful for:
- Creating a public searchable view of your applications and contacts
- Sharing your job search progress
- Deploying to static hosting services like Netlify

### How to Use PRD Push

**Via Web Interface:**
1. Navigate to the search page: `http://localhost:51003/search`
2. Click the "Prd Push" button
3. Wait 30-60 seconds for processing
4. Check email for deployment status (if email is configured)

**Via API:**
```bash
curl -X POST http://localhost:51003/api/static-search/generate
```

### Configuration Requirements

PRD Push uses the **same email configuration** as the daily digest:

1. **Configure Email** (optional but recommended for notifications):
   - Follow the **[Email Setup Guide](EMAIL_SETUP_GUIDE.md)** to configure email
   - PRD Push will send status notifications using the same email settings

2. **Git Setup** (required for automatic deployment):
   - Ensure your repository is a git repository
   - Configure remote: `git remote add origin https://github.com/your-username/hunter.git`
   - Ensure you have push access to the `main` branch

3. **Netlify Setup** (optional, for public deployment):
   - Connect your GitHub repository to Netlify
   - Configure build directory as `hunterapp_demo`
   - Page will be available at: `https://your-domain.com/kpro`

### What Gets Generated

The PRD Push process:
1. Fetches all applications and networking contacts from the API
2. Generates static HTML file with embedded JSON data
3. Copies to `hunterapp_demo/kpro/index.html`
4. Commits and pushes to GitHub automatically
5. Triggers Netlify auto-deployment (if configured)
6. Sends email notification with status

### Email Notifications

You'll receive email notifications about:
- **Success**: Page generated, committed, and pushed successfully
- **Partial Success**: Generated and committed, but push failed (manual push needed)
- **Up to Date**: No changes detected, page already current
- **Failure**: Generation or deployment failed with error details

### Detailed Documentation

For complete setup instructions, troubleshooting, and advanced usage, see the **[PRD Push Guide](PRD_PUSH_GUIDE.md)**.

## Best Practices

### Resume Management
- ✅ Keep your base resume updated regularly
- ✅ Include all relevant skills and experiences
- ✅ Use specific technologies and tools
- ✅ Quantify achievements with numbers
- ❌ Don't use generic descriptions

### Application Process
- ✅ Copy the complete job posting
- ✅ Add the job URL for future reference
- ✅ Review the qualifications analysis carefully
- ✅ Customize the generated cover letter slightly
- ✅ Use the tailored resume for applications
- ❌ Don't apply to jobs with very low match scores
- ❌ Don't submit without reviewing generated documents

### Organization
- ✅ Update application status promptly
- ✅ Add notes after interviews
- ✅ Track follow-up dates
- ✅ Review dashboard weekly
- ❌ Don't let applications pile up without updates

### Follow-Up Strategy
1. **Applied**: Note submission date, set 1-week follow-up
2. **Interviewed**: Add interview notes, prepare for next round
3. **Offered**: Record offer details, deadline to respond
4. **Rejected**: Note reason if known, learn for next time

## Advanced Features

### Custom Resume (Rarely Needed)
If you have industry-specific resumes, you can set a custom resume per application:

```bash
curl -X POST http://localhost:51003/api/applications/<APP_ID>/custom-resume \
  -H "Content-Type: application/json" \
  -d '{"resume_content": "Your custom resume..."}'
```

See [CUSTOM_RESUME_GUIDE.md](../CUSTOM_RESUME_GUIDE.md) for details.

### Regenerating Documents
If you update your base resume and want to refresh an application:

```bash
curl -X POST http://localhost:51003/api/applications/<APP_ID>/regenerate
```

## Tips for Success

### Maximize Match Scores
- Include all relevant skills in your base resume
- Use industry-standard terminology
- Mention certifications and training
- Quantify your experience (years with each technology)

### Use Generated Documents Effectively
- **Cover Letter**: Light edit for personal touch, then copy to application
- **Resume**: Export as PDF, use for application submission
- **Qualifications**: Study before interviews, prepare talking points

### Track Everything
- Update status immediately after each action
- Add detailed notes after interviews
- Track recruiter names and contacts
- Note any special instructions

## Keyboard Shortcuts & Tips

### Quick Navigation
- Main UI: http://localhost:51003
- Dashboard: http://localhost:51003/dashboard
- Check AI: Click "🔍 Check AI Status"

### Efficiency Tips
- Keep Ollama running in background
- Have job posting URLs ready
- Update resume in batches (once a week)
- Review dashboard before applying

## Troubleshooting

### Application Not Processing
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Verify resume exists: Click "📄 Manage Resume"
- Look at terminal for error messages

### Low Match Scores
- Ensure your resume includes all your skills
- Use specific technology names, not generic terms
- Add years of experience per skill
- Include relevant certifications

### Documents Not Generated
- Check disk space is available
- Verify write permissions in data/ folder
- Review terminal logs for errors

---

**Need More Help?** 
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [FAQ](FAQ.md)
- [API Reference](API_REFERENCE.md)

