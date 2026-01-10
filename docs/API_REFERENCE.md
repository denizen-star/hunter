# API Reference

Complete REST API documentation for Job Hunter.

## Base URL

```
http://localhost:51003
```

## Authentication

No authentication required (local application).

## Endpoints

### System

#### Check Ollama Status
```
GET /api/check-ollama
```

Check if Ollama AI service is connected and list available models.

**Response:**
```json
{
  "success": true,
  "connected": true,
  "base_url": "http://localhost:11434",
  "current_model": "llama3",
  "available_models": ["llama3:latest", "mistral:latest"]
}
```

---

### Resume Management

#### Get Base Resume
```
GET /api/resume
```

Retrieve the base resume.

**Response:**
```json
{
  "success": true,
  "resume": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-234-567-8900",
    "linkedin": "linkedin.com/in/johndoe",
    "location": "Toronto, ON",
    "content": "# Resume content in markdown...",
    "version": "1.0",
    "is_active": true
  }
}
```

#### Update Base Resume
```
PUT /api/resume
Content-Type: application/json
```

Update the base resume used for all applications.

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-234-567-8900",
  "linkedin": "linkedin.com/in/johndoe",
  "location": "Toronto, ON",
  "content": "# Full resume content in markdown..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Resume updated successfully"
}
```

#### Initialize Resume Template
```
POST /api/resume/init
```

Create a base resume template to get started.

**Response:**
```json
{
  "success": true,
  "message": "Base resume template created successfully",
  "path": "/path/to/data/resumes"
}
```

---

### Applications

#### Create Application
```
POST /api/applications
Content-Type: application/json
```

Create a new job application with AI analysis.

**Request Body:**
```json
{
  "company": "Google",
  "job_title": "Senior Software Engineer",
  "job_description": "Full job posting text here...",
  "job_url": "https://careers.google.com/job123" 
}
```

**Response:**
```json
{
  "success": true,
  "message": "Application created successfully",
  "application_id": "20251013153548-Google-SeniorSoftwareEngineer",
  "folder_path": "/path/to/data/applications/Google-SeniorSoftwareEngineer",
  "summary_path": "/path/to/summary.html",
  "summary_url": "/applications/Google-SeniorSoftwareEngineer/20251013153548-Summary-Google-SeniorSoftwareEngineer.html",
  "match_score": 85.5
}
```

**Processing Time:** 30-90 seconds depending on document length

#### List All Applications
```
GET /api/applications
```

Get a list of all job applications.

**Response:**
```json
{
  "success": true,
  "count": 5,
  "applications": [
    {
      "id": "20251013153548-Google-SeniorSoftwareEngineer",
      "company": "Google",
      "job_title": "Senior Software Engineer",
      "status": "pending",
      "created_at": "Oct 13, 2025 3:35 PM",
      "updated_at": "Oct 13, 2025 3:35 PM",
      "folder_path": "/path/to/folder",
      "summary_path": "/path/to/summary.html",
      "match_score": 85.5
    }
  ]
}
```

#### Get Applications and Contacts (Unified Search)
```
GET /api/applications-and-contacts
```

Get a combined list of all applications and contacts for unified search. Includes active applications, rejected applications, archived applications, and all networking contacts. Results are sorted with applications first (by company name, then newest to oldest), followed by contacts (by company name, then newest to oldest).

**Response:**
```json
{
  "success": true,
  "items": [
    {
      "type": "application",
      "id": "20250108120000-Company-JobTitle",
      "name": "Company - Job Title",
      "company": "Company",
      "match_score": 85.5,
      "status": "applied",
      "last_updated": "2026-01-08T12:00:00",
      "detail_url": "/applications/Company-JobTitle/summary.html"
    },
    {
      "type": "contact",
      "id": "20250108120000-Person-Company",
      "name": "Person Name - Company",
      "company": "Company",
      "match_score": 90.0,
      "status": "In Conversation",
      "last_updated": "2026-01-08T10:00:00",
      "detail_url": "/networking/Person-Company/summary.html"
    }
  ],
  "count": 2
}
```

**Sorting Logic:**
- Applications appear first, then contacts
- Within each type, items are sorted by company name (alphabetically, case-insensitive)
- Within each company, items are sorted by last updated date (newest to oldest)

#### Get Application Details
```
GET /api/applications/<application_id>
```

Get detailed information about a specific application.

**Response:**
```json
{
  "success": true,
  "application": {
    "id": "20251013153548-Google-SeniorSoftwareEngineer",
    "company": "Google",
    "job_title": "Senior Software Engineer",
    "status": "applied",
    "created_at": "Oct 13, 2025 3:35 PM",
    "updated_at": "Oct 14, 2025 10:00 AM",
    "match_score": 85.5,
    "job_url": "https://careers.google.com/job123",
    "folder_path": "/path/to/folder",
    "summary_path": "/path/to/summary.html",
    "updates": [
      {
        "timestamp": "20251014100000",
        "status": "applied",
        "content": "Submitted via company website"
      }
    ]
  }
}
```

#### Update Application Status
```
PUT /api/applications/<application_id>/status
Content-Type: application/json
```

Update the status of an application with optional notes.

**Request Body:**
```json
{
  "status": "interviewed",
  "notes": "Phone screen went well. Technical interview scheduled for next week."
}
```

**Statuses:** `pending`, `applied`, `interviewed`, `offered`, `rejected`, `accepted`

**Response:**
```json
{
  "success": true,
  "message": "Status updated to interviewed",
  "application_id": "20251013153548-Google-SeniorSoftwareEngineer"
}
```

#### Set Custom Resume
```
POST /api/applications/<application_id>/custom-resume
Content-Type: application/json
```

Set a custom resume for a specific application and regenerate all documents.

**Request Body:**
```json
{
  "resume_content": "# Custom resume content in markdown..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Custom resume set and documents regenerated",
  "resume_path": "/path/to/custom_resume.md"
}
```

**Note:** This regenerates all documents (qualifications, cover letter, resume) using the new resume.

#### Regenerate Documents
```
POST /api/applications/<application_id>/regenerate
```

Regenerate all documents for an application (useful after updating base resume).

**Response:**
```json
{
  "success": true,
  "message": "Documents regenerated successfully",
  "application_id": "20251013153548-Google-SeniorSoftwareEngineer"
}
```

---

### Dashboard

#### Update Dashboard
```
POST /api/dashboard/update
```

Manually trigger dashboard regeneration.

**Response:**
```json
{
  "success": true,
  "message": "Dashboard updated successfully"
}
```

**Note:** Dashboard auto-updates after application creation/modification.

#### View Dashboard
```
GET /dashboard
```

View the generated HTML dashboard (opens in browser).

---

### Static Search / PRD Push

#### Generate Static Search Page
```
POST /api/static-search/generate
```

Generate a static HTML search page containing all applications and networking contacts, then deploy it to production.

**What This Endpoint Does:**
1. Fetches all applications and contacts from the API
2. Generates static HTML file with embedded JSON data
3. Copies file to `hunterapp_demo/kpro/index.html`
4. Commits and pushes to GitHub (if git is configured)
5. Sends email notification (if email is configured)

**Response (Success):**
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

**Response (Partial Success - Git Push Failed):**
```json
{
  "success": true,
  "message": "Static search page generated and committed. Push to GitHub failed - you may need to push manually.",
  "email_sent": true,
  "output_path": "/path/to/static_search/kpro.html",
  "deploy_path": "/path/to/hunterapp_demo/kpro/index.html",
  "kpro_path": "/path/to/hunterapp_demo/kpro/index.html",
  "git_committed": true,
  "git_pushed": false,
  "git_error": "Git push failed: authentication required"
}
```

**Response (Failure):**
```json
{
  "success": false,
  "error": "Generation script not found",
  "email_sent": false,
  "output": ""
}
```

**Prerequisites:**
- Flask app must be running on `http://localhost:51003`
- Generator script must exist at `scripts/generate_static_search.py`
- Git repository must be initialized (for automatic deployment)
- Email configuration optional (see **[EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)**)

**Timeout:** 60 seconds maximum

**Email Notifications:**
- If email is configured in `config/digest_config.yaml`, notifications are sent for:
  - Successful generation and deployment
  - Partial success (generated but push failed)
  - Already up to date (no changes detected)
  - Generation failures
- See **[PRD_PUSH_GUIDE.md](PRD_PUSH_GUIDE.md)** for detailed setup instructions

**Example cURL:**
```bash
curl -X POST http://localhost:51003/api/static-search/generate
```

**Example JavaScript:**
```javascript
const response = await fetch('http://localhost:51003/api/static-search/generate', {
  method: 'POST'
});

const data = await response.json();
if (data.success) {
  console.log(`Generated: ${data.output_path}`);
  console.log(`Deployed: ${data.deploy_path}`);
  if (data.git_pushed) {
    console.log('Successfully pushed to GitHub!');
  }
}
```

---

### File Serving

#### Serve Application Files
```
GET /applications/<company>-<jobtitle>/<filename>
```

Serve application files (summaries, documents, etc.).

**Example:**
```
GET /applications/Google-SeniorSoftwareEngineer/20251013153548-Summary-Google-SeniorSoftwareEngineer.html
```

---

## Error Responses

### Common Error Format
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (missing required fields)
- `404` - Not Found (application or file not found)
- `500` - Internal Server Error
- `503` - Service Unavailable (Ollama not connected)

### Example Errors

**Missing Required Field:**
```json
{
  "success": false,
  "error": "Missing required fields: company, job_title, job_description"
}
```

**Resume Not Found:**
```json
{
  "success": false,
  "error": "Base resume not found. Please create a resume first."
}
```

**Ollama Not Connected:**
```json
{
  "success": false,
  "error": "Cannot connect to Ollama. Please ensure Ollama is running."
}
```

---

## Code Examples

### Python

```python
import requests

# Create application
response = requests.post('http://localhost:51003/api/applications', json={
    'company': 'Google',
    'job_title': 'Senior Software Engineer',
    'job_description': 'Full job description...',
    'job_url': 'https://careers.google.com/job123'
})

data = response.json()
if data['success']:
    print(f"Match Score: {data['match_score']}%")
    print(f"Summary: {data['summary_url']}")
```

### cURL

```bash
# Create application
curl -X POST http://localhost:51003/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Google",
    "job_title": "Senior Software Engineer",
    "job_description": "Full job description...",
    "job_url": "https://careers.google.com/job123"
  }'

# Update status
curl -X PUT http://localhost:51003/api/applications/<APP_ID>/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "applied",
    "notes": "Submitted application"
  }'

# List applications
curl http://localhost:51003/api/applications

# Generate static search page (PRD Push)
curl -X POST http://localhost:51003/api/static-search/generate
```

### JavaScript (fetch)

```javascript
// Create application
const response = await fetch('http://localhost:51003/api/applications', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    company: 'Google',
    job_title: 'Senior Software Engineer',
    job_description: 'Full job description...',
    job_url: 'https://careers.google.com/job123'
  })
});

const data = await response.json();
if (data.success) {
  console.log(`Match Score: ${data.match_score}%`);
}
```

---

## Rate Limiting

No rate limiting (local application).

## Webhooks

Not supported in v1.0.0. Coming in future version.

---

## API Versioning

Current version: `v1.0.0`

API version is not included in URL paths. Breaking changes will be announced in release notes.

---

**Need Help?** 
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [User Guide](USER_GUIDE.md)
- [PRD Push Guide](PRD_PUSH_GUIDE.md)
- [Email Setup Guide](EMAIL_SETUP_GUIDE.md)

