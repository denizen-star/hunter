# API Reference

Complete REST API documentation for Job Hunter.

## Base URL

```
http://localhost:51002
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
response = requests.post('http://localhost:51002/api/applications', json={
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
curl -X POST http://localhost:51002/api/applications \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Google",
    "job_title": "Senior Software Engineer",
    "job_description": "Full job description...",
    "job_url": "https://careers.google.com/job123"
  }'

# Update status
curl -X PUT http://localhost:51002/api/applications/<APP_ID>/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "applied",
    "notes": "Submitted application"
  }'

# List applications
curl http://localhost:51002/api/applications
```

### JavaScript (fetch)

```javascript
// Create application
const response = await fetch('http://localhost:51002/api/applications', {
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

**Need Help?** See [Troubleshooting Guide](TROUBLESHOOTING.md) or [User Guide](USER_GUIDE.md)

