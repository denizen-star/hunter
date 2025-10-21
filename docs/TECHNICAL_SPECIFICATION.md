# Job Hunting Follow-Ups — Technical Specification

## 1. Overview

### 1.1 Purpose
An automated job application management system that analyzes job descriptions, customizes resumes, generates cover letters, and tracks application progress through AI-powered document generation and analysis.

### 1.2 Core Functionality
- Resume management and customization
- Job description parsing and storage
- AI-powered skill matching and gap analysis
- Automated cover letter generation
- Tailored resume generation
- Comprehensive application summary generation
- Web-based dashboard for application tracking

### 1.3 Quick Start Prerequisites

**Before starting development, ensure you have:**

1. **Ollama installed and running** (FREE)
   ```bash
   # macOS
   brew install ollama
   
   # Download Llama 3 model
   ollama pull llama3
   
   # Start Ollama service
   ollama serve
   ```

2. **Python 3.11+** installed
3. **8GB+ RAM** available for Ollama

**Total Cost: $0** - Everything runs locally!

---

## 2. System Architecture

### 2.1 Architecture Pattern
**Modular Monolith with Service Layer**
```
┌─────────────────────────────────────────┐
│         Web Interface (HTML)            │
│    (Application List & Navigation)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Application Service Layer          │
│  (Node.js/Python Backend)              │
│  - Job Processing                       │
│  - Document Generation                  │
│  - File Management                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         AI/LLM Service                  │
│  (OpenAI, Anthropic, or Local LLM)     │
│  - Resume Analysis                      │
│  - Cover Letter Writing                 │
│  - Job Description Parsing              │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      File Storage System                │
│  - Base Resume Storage                  │
│  - Job Folders (<company>-<jobtitle>)  │
│  - Generated Documents                  │
└─────────────────────────────────────────┘
```

### 2.2 Tech Stack Recommendation

#### Backend
- **Primary Language**: Python 3.11+
  - Rationale: Excellent for text processing, AI integration, file operations
  - Alternative: Node.js with TypeScript

#### AI/LLM Integration
- **Primary**: Ollama (Local LLM) - FREE & PRIVATE
  - Models: Llama 3, Mistral, or Mixtral
  - Runs entirely on your computer
  - Zero API costs, complete privacy
- **Alternative Options** (Paid, for premium quality):
  - OpenAI API (GPT-4)
  - Anthropic Claude API

#### Frontend
- **Static HTML/CSS/JavaScript**
  - Simple, fast, no build process required
  - Progressive enhancement possible later

#### File Storage
- **Local Filesystem**
  - Organized directory structure
  - Markdown for documents
  - PDF support for original resumes

#### Dependencies
```python
# requirements.txt
ollama>=0.1.0              # Primary - Local LLM client
requests>=2.31.0           # For HTTP requests to Ollama
python-dotenv>=1.0.0       # Environment configuration
python-dateutil>=2.8.0     # Datetime utilities
markdown>=3.4.0            # Markdown processing
jinja2>=3.1.0              # Template rendering
pyyaml>=6.0                # YAML configuration

# Optional (only if using cloud APIs)
# openai>=1.0.0
# anthropic>=0.18.0
```

---

## 3. Data Models

### 3.1 Base Resume
```yaml
# base_resume.yaml
metadata:
  full_name: "John Doe"
  email: "john@example.com"
  phone: "+1-234-567-8900"
  linkedin: "linkedin.com/in/johndoe"
  location: "Toronto, ON"
  
content_path: "resumes/base_resume.md"
version: "1.0"
created_at: "2025-10-13T10:00:00-05:00"
is_active: true
```

### 3.2 Job Application
```yaml
# <company>-<jobtitle>/application.yaml
application:
  id: "20251013100000-TechCorp-SeniorDeveloper"
  company: "TechCorp"
  job_title: "Senior Developer"
  created_at: "2025-10-13T10:00:00-05:00"
  status: "pending" # pending, applied, interviewed, offered, rejected, accepted
  
files:
  job_description: "20251013100000-TechCorp-SeniorDeveloper.md"
  qualifications: "SeniorDeveloper-Qualifications.md"
  cover_letter: "JohnDoe-TechCorp-SeniorDeveloper-intro.md"
  custom_resume: "JohnDoe-TechCorp-SeniorDeveloper-Resume.md"
  summary: "20251013100000-Summary-TechCorp-SeniorDeveloper.md"
  
resume_used: "base_resume.md" # or path to custom resume
```

### 3.3 Qualification Analysis
```markdown
# <JobTitle>-Qualifications.md

## Skills Match Summary
- **Match Score**: 85%
- **Missing Skills**: Docker, Kubernetes
- **Strong Matches**: Python, React, PostgreSQL

## Detailed Analysis

### Matching Skills
1. **Python Development** (10 years experience)
   - Job Requirement: "5+ years Python"
   - Resume Evidence: "Led Python development team for 10 years"

### Skills Gaps
1. **Container Orchestration**
   - Job Requirement: "Experience with Kubernetes"
   - Resume Status: Not mentioned
   - Recommendation: Emphasize Docker experience, mention willingness to learn K8s

### Soft Skills Alignment
- Leadership: ✓ Strong match
- Communication: ✓ Strong match
- Problem Solving: ✓ Strong match
```

---

## 4. System Components

### 4.1 Core Services

#### 4.1.1 Resume Manager
```python
class ResumeManager:
    """Manages base and custom resumes"""
    
    def load_base_resume() -> Resume
    def save_custom_resume(job_id: str, content: str) -> None
    def get_resume_for_job(job_id: str) -> Resume
    def parse_resume_content(content: str) -> dict
```

#### 4.1.2 Job Processor
```python
class JobProcessor:
    """Processes job descriptions and creates application folders"""
    
    def create_job_application(job_description: str, company: str, title: str) -> str
    def save_job_description(job_id: str, content: str) -> None
    def get_job_folder_path(job_id: str) -> Path
```

#### 4.1.3 AI Analyzer
```python
class AIAnalyzer:
    """AI-powered analysis and generation using Ollama"""
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def analyze_qualifications(job_desc: str, resume: str) -> QualificationAnalysis
    def generate_cover_letter(qualifications: QualificationAnalysis, soft_skills: list) -> str
    def rewrite_resume_bullets(resume: str, qualifications: QualificationAnalysis) -> str
    def create_summary(job_id: str, all_documents: dict) -> str
    
    # Internal method for Ollama API calls
    def _call_ollama(prompt: str, system_prompt: str = None) -> str
```

#### 4.1.4 Document Generator
```python
class DocumentGenerator:
    """Generates and saves all required documents"""
    
    def generate_qualifications_doc(job_id: str) -> None
    def generate_cover_letter(job_id: str) -> None
    def generate_custom_resume(job_id: str) -> None
    def generate_summary(job_id: str) -> None
```

#### 4.1.5 Dashboard Generator
```python
class DashboardGenerator:
    """Generates HTML dashboard"""
    
    def generate_index_page() -> None
    def list_all_applications() -> list[Application]
    def create_application_card(application: Application) -> str
```

---

## 5. File Structure

```
job-hunting-follow-ups/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resume_manager.py
│   │   ├── job_processor.py
│   │   ├── ai_analyzer.py
│   │   ├── document_generator.py
│   │   └── dashboard_generator.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── resume.py
│   │   ├── application.py
│   │   └── qualification.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── datetime_utils.py
│   │   └── prompts.py         # AI prompt templates
│   └── templates/
│       ├── index.html          # Dashboard template
│       ├── application_card.html
│       └── summary_template.md
├── data/
│   ├── resumes/
│   │   ├── base_resume.md
│   │   └── base_resume.yaml
│   ├── applications/
│   │   └── <company>-<jobtitle>/
│   │       ├── application.yaml
│   │       ├── <datetime>-<company>-<jobtitle>.md
│   │       ├── <JobTitle>-Qualifications.md
│   │       ├── <Name>-<company>-<jobtitle>-intro.md
│   │       ├── <Name>-<company>-<jobtitle>-Resume.md
│   │       └── <datetime>-Summary-<company>-<jobtitle>.md
│   └── output/
│       └── index.html          # Generated dashboard
├── config/
│   ├── config.yaml
│   └── prompts.yaml           # AI prompt configurations
├── requirements.txt
├── .env.example
├── .env                       # API keys (gitignored)
├── README.md
└── ONE_PAGER.md
```

---

## 6. Workflow Process

### 6.1 Job Application Creation Flow

```
1. User Input
   ├─► Job Description (text)
   ├─► Company Name
   ├─► Job Title
   └─► [Optional] Custom Resume

2. Create Job Folder
   └─► Format: <company>-<jobtitle>
   
3. Save Job Description
   └─► <datetimeEST>-<company>-<jobtitle>.md

4. Load Resume
   └─► Base or Custom Resume

5. AI Analysis (Qualifications)
   ├─► Compare job description vs resume
   ├─► Identify matching skills
   ├─► Identify skill gaps
   └─► Save: <JobTitle>-Qualifications.md

6. Generate Cover Letter
   ├─► Use qualifications analysis
   ├─► Integrate 50% of required soft skills
   └─► Save: <Name>-<company>-<jobtitle>-intro.md

7. Generate Custom Resume
   ├─► Rewrite job descriptions based on qualifications
   ├─► Make bullets short, direct, professional
   └─► Save: <Name>-<company>-<jobtitle>-Resume.md

8. Create Summary Document
   ├─► Action items and next steps
   ├─► Include qualifications
   ├─► Include cover letter
   ├─► Include custom resume
   └─► Save: <datetimeEST>-Summary-<company>-<jobtitle>.md

9. Update Dashboard
   └─► Regenerate index.html with new application
```

### 6.2 Dashboard Update Flow

```
1. Scan Applications Folder
   └─► List all <company>-<jobtitle> directories

2. Read Application Metadata
   └─► application.yaml from each folder

3. Generate Application Cards
   ├─► Company & Job Title
   ├─► Creation Date
   ├─► Status
   └─► Links to Summary and Folder

4. Render HTML Dashboard
   └─► Save to data/output/index.html
```

---

## 7. AI Prompt Templates

### 7.1 Qualification Analysis Prompt
```python
QUALIFICATION_ANALYSIS_PROMPT = """
You are a career advisor analyzing how well a candidate's resume matches a job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_content}

Please provide a detailed analysis in the following format:

## Skills Match Summary
- Match Score: [percentage]
- Strong Matches: [list top 5 matching skills]
- Missing Skills: [list skills mentioned in job but not in resume]

## Detailed Skill Analysis
For each major skill/requirement in the job description:
1. Skill Name
2. Job Requirement (quote from description)
3. Resume Evidence (quote from resume if match exists)
4. Match Level: Strong Match / Partial Match / No Match

## Soft Skills Alignment
List relevant soft skills from job description and indicate if demonstrated in resume.

## Recommendations
Suggest 3-5 ways to emphasize relevant experience or address gaps.
"""
```

### 7.2 Cover Letter Generation Prompt
```python
COVER_LETTER_PROMPT = """
You are a professional cover letter writer.

Write an eloquent, professional cover letter based on:

QUALIFICATIONS ANALYSIS:
{qualifications}

SOFT SKILLS TO EMPHASIZE (use 50%):
{soft_skills}

REQUIREMENTS:
- Opening paragraph: Express interest and briefly state why you're a great fit
- 2-3 body paragraphs: Integrate the provided soft skills naturally
- Emphasize strengths from the qualifications analysis
- Closing: Call to action
- Tone: Professional yet personable
- Length: 300-400 words

Format as markdown with proper structure.
"""
```

### 7.3 Resume Bullet Rewriting Prompt
```python
RESUME_REWRITE_PROMPT = """
You are a professional resume writer specializing in ATS optimization.

ORIGINAL RESUME:
{original_resume}

QUALIFICATIONS ANALYSIS:
{qualifications}

Rewrite each job description bullet point to:
1. Align with keywords and requirements from the qualifications analysis
2. Keep bullets short (1-2 lines maximum)
3. Use strong action verbs
4. Quantify achievements where possible
5. Maintain professional tone
6. Ensure relevance to target job

Return the complete resume with rewritten bullets, maintaining the original structure and format.
"""
```

---

## 8. API Design

### 8.1 CLI Interface (v1)

```bash
# Create new job application
python app/main.py create-application \
  --company "TechCorp" \
  --title "Senior Developer" \
  --job-description "path/to/description.txt"

# Use custom resume for application
python app/main.py set-custom-resume \
  --job-id "20251013100000-TechCorp-SeniorDeveloper" \
  --resume "path/to/custom_resume.md"

# Regenerate specific document
python app/main.py regenerate \
  --job-id "20251013100000-TechCorp-SeniorDeveloper" \
  --document "cover-letter"

# Update dashboard
python app/main.py update-dashboard

# Update application status
python app/main.py update-status \
  --job-id "20251013100000-TechCorp-SeniorDeveloper" \
  --status "interviewed"
```

### 8.2 Future Web API (v2)

```
POST   /api/applications              # Create new application
GET    /api/applications              # List all applications
GET    /api/applications/:id          # Get application details
PUT    /api/applications/:id          # Update application
DELETE /api/applications/:id          # Delete application
POST   /api/applications/:id/regenerate  # Regenerate documents
PUT    /api/resumes/base              # Update base resume
POST   /api/resumes/custom            # Upload custom resume
GET    /api/dashboard                 # Get dashboard data
```

---

## 9. Configuration

### 9.1 config.yaml
```yaml
app:
  name: "Job Hunting Follow-Ups"
  version: "1.0.0"
  timezone: "America/Toronto"

paths:
  data_root: "./data"
  resumes: "./data/resumes"
  applications: "./data/applications"
  output: "./data/output"
  templates: "./app/templates"

ai:
  provider: "ollama"  # ollama (free, local), openai (paid), anthropic (paid)
  model: "llama3"     # llama3, mistral, mixtral for Ollama
  base_url: "http://localhost:11434"  # Ollama default endpoint
  temperature: 0.7
  max_tokens: 2000

resume:
  default_name: "base_resume.md"
  supported_formats: ["md", "txt", "pdf"]

document_naming:
  datetime_format: "%Y%m%d%H%M%S"
  timezone: "EST"

dashboard:
  title: "Job Application Dashboard"
  items_per_page: 20
  sort_by: "created_at"
  sort_order: "desc"
```

### 9.2 .env
```bash
# AI Provider Settings
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Optional: Only needed if using paid APIs
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Application Settings
TIMEZONE=America/Toronto
DEBUG=false
```

---

## 10. User Interface Design

### 10.1 Dashboard (index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Application Dashboard</title>
    <style>
        /* Modern, clean design */
        /* Grid layout for application cards */
        /* Status badges with color coding */
        /* Responsive design */
    </style>
</head>
<body>
    <header>
        <h1>Job Application Dashboard</h1>
        <div class="stats">
            <span>Total: 12</span>
            <span>Pending: 5</span>
            <span>Interviewed: 3</span>
        </div>
    </header>
    
    <main>
        <div class="application-grid">
            <!-- Application cards generated dynamically -->
            <div class="card">
                <div class="card-header">
                    <h2>Senior Developer</h2>
                    <span class="company">TechCorp</span>
                </div>
                <div class="card-meta">
                    <span class="date">Oct 13, 2025</span>
                    <span class="status status-pending">Pending</span>
                </div>
                <div class="card-actions">
                    <a href="applications/TechCorp-SeniorDeveloper/">📁 Folder</a>
                    <a href="applications/TechCorp-SeniorDeveloper/20251013100000-Summary-TechCorp-SeniorDeveloper.md">📄 Summary</a>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
```

---

## 11. Ollama Setup & Installation

### 11.1 Installing Ollama

**macOS:**
```bash
# Using Homebrew
brew install ollama

# Or download from ollama.ai
curl https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
- Download installer from https://ollama.ai/download

### 11.2 Downloading Models

```bash
# Recommended: Llama 3 (best balance of quality and speed)
ollama pull llama3

# Alternative: Mistral (faster, slightly lower quality)
ollama pull mistral

# Alternative: Mixtral (higher quality, slower)
ollama pull mixtral
```

### 11.3 Starting Ollama Server

```bash
# Start Ollama service (runs on http://localhost:11434)
ollama serve
```

### 11.4 Testing Ollama

```bash
# Test in terminal
ollama run llama3 "Write a professional greeting for a cover letter"

# Or test via Python
python -c "import ollama; print(ollama.chat(model='llama3', messages=[{'role': 'user', 'content': 'Hello!'}]))"
```

### 11.5 System Requirements

**Minimum:**
- 8GB RAM
- 4GB disk space (per model)
- Modern CPU (Intel/AMD/Apple Silicon)

**Recommended:**
- 16GB+ RAM
- 8GB disk space
- Apple Silicon Mac or GPU-enabled PC (for faster inference)

---

## 12. Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Project setup and dependencies
- [ ] File structure creation
- [ ] Configuration system
- [ ] Base resume management
- [ ] Job folder creation
- [ ] File naming utilities

### Phase 2: AI Integration (Week 2)
- [ ] Ollama setup and installation
- [ ] Ollama API integration
- [ ] Prompt template system
- [ ] Qualification analysis
- [ ] Cover letter generation
- [ ] Resume rewriting
- [ ] Error handling and retries

### Phase 3: Document Generation (Week 3)
- [ ] All document generators
- [ ] Summary compilation
- [ ] File organization
- [ ] Application metadata tracking

### Phase 4: Dashboard (Week 4)
- [ ] HTML template design
- [ ] Application listing
- [ ] Status visualization
- [ ] Link generation
- [ ] Responsive design

### Phase 5: CLI & Testing (Week 5)
- [ ] Command-line interface
- [ ] User input validation
- [ ] Error messages
- [ ] Basic testing
- [ ] Documentation

---

## 13. Security & Privacy Considerations

### 13.1 Data Privacy
- **100% Local Processing**: Using Ollama means all AI processing happens on your computer
- **No Cloud Transmission**: Your resume and job data never leave your machine
- **No API Keys Required**: No need to share sensitive data with third parties
- All application data stored locally in organized folders

### 13.2 File Security
- Restricted file permissions on resume folder
- No cloud sync by default
- Gitignore for sensitive data
- Encrypted storage option (future)

### 13.3 API Key Management (Optional - Only for Cloud Providers)
- If using OpenAI/Claude: Never commit .env to version control
- Use environment variables for API keys
- Rotate keys periodically
- Monitor API usage and set budget limits

---

## 14. Error Handling

### 14.1 Common Error Scenarios
```python
class ApplicationError(Exception):
    """Base exception for application errors"""
    
class ResumeNotFoundError(ApplicationError):
    """Raised when base resume is missing"""
    
class OllamaNotAvailableError(ApplicationError):
    """Raised when Ollama service is not running"""
    
class AIServiceError(ApplicationError):
    """Raised when AI service fails (Ollama or cloud API)"""
    
class InvalidJobDescriptionError(ApplicationError):
    """Raised when job description is invalid"""
    
class DuplicateApplicationError(ApplicationError):
    """Raised when application already exists"""
```

### 14.2 Retry Logic
- Ollama API calls: 3 retries with exponential backoff
- File operations: 2 retries
- Network errors: Graceful degradation
- Check Ollama service health before processing

---

## 15. Testing Strategy

### 15.1 Unit Tests
- Resume parsing
- File naming utilities
- Configuration loading
- Document generation logic

### 15.2 Integration Tests
- End-to-end application creation
- Ollama service mocking
- File system operations
- Dashboard generation

### 15.3 Manual Testing Checklist
- [ ] Create application with base resume
- [ ] Create application with custom resume
- [ ] Verify all documents generated
- [ ] Check dashboard displays correctly
- [ ] Test with various job descriptions
- [ ] Verify file naming conventions

---

## 16. Future Enhancements (Out of Scope v1)

### v2 Features
- Web-based UI with form inputs
- Email integration for follow-ups
- Calendar integration for interview scheduling
- Analytics and insights
- Export to PDF
- Browser extension for job posting capture

### v3 Features
- Full ATS integration
- Team collaboration
- Application templates library
- A/B testing for cover letters
- Success rate tracking
- Interview preparation guides

---

## 17. Documentation Requirements

### 17.1 User Documentation
- Installation guide
- Quick start tutorial
- CLI command reference
- Configuration guide
- Troubleshooting

### 17.2 Developer Documentation
- Architecture overview
- API documentation
- Prompt engineering guide
- Testing guide
- Contribution guidelines

---

## 18. Success Criteria

### 18.1 Functional Requirements
✅ System can process job description  
✅ System generates all required documents  
✅ Documents follow naming conventions  
✅ Dashboard displays all applications  
✅ Links work correctly  

### 18.2 Quality Requirements
✅ Documents are well-formatted markdown  
✅ Cover letters are eloquent and professional  
✅ Resume bullets are concise and relevant  
✅ Analysis is accurate and helpful  
✅ Dashboard is clean and usable  

### 18.3 Performance Requirements
✅ Application creation < 60 seconds (may vary with Ollama model)
✅ Dashboard generation < 5 seconds  
✅ Handle 100+ applications  

---

## 19. Appendix

### A. Datetime Format
```python
# EST timezone
datetime_format = "%Y%m%d%H%M%S"
# Example: 20251013143000 (Oct 13, 2025 2:30:00 PM EST)
```

### B. Folder Naming Convention
```
Format: <company>-<jobtitle>
Rules:
- Remove special characters
- Replace spaces with hyphens
- Use PascalCase for multi-word titles
Examples:
- Google-SoftwareEngineer
- Microsoft-SeniorProductManager
- Meta-DataScientistII
```

### C. Document Templates
See `app/templates/` directory for all markdown and HTML templates.

### D. Ollama Model Recommendations

**Llama 3 (Recommended)**
- Best balance of quality and speed
- Excellent for professional writing
- Size: ~4.7GB
- RAM: 8GB minimum, 16GB recommended

**Mistral**
- Faster than Llama 3
- Good for quick iterations
- Size: ~4.1GB
- RAM: 8GB minimum

**Mixtral**
- Highest quality output
- Best for critical applications
- Size: ~26GB
- RAM: 16GB minimum, 32GB recommended

**Command to download:**
```bash
ollama pull llama3    # Recommended
ollama pull mistral   # Faster alternative
ollama pull mixtral   # Premium quality
```

---

## 20. Confirmed Implementation Specification (Final)

### 20.1 Core Feature: Feature Extraction & Matching Engine

#### Feature Extraction from Resume
The system will extract and categorize the following from the user's resume:

**Technical Skills**
- Programming languages (Python, JavaScript, Java, etc.)
- Frameworks and libraries (React, Django, TensorFlow, etc.)
- Tools and platforms (AWS, Docker, Kubernetes, Git, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)

**Soft Skills**
- Leadership
- Communication
- Problem-solving
- Team collaboration
- Project management

**Years of Experience**
- Per skill/technology when mentioned
- Overall years of professional experience
- Years in specific roles or industries

**Certifications**
- Professional certifications (AWS Certified, PMP, CPA, etc.)
- Academic credentials
- Special training or courses

#### Feature Extraction from Job Description
The system will extract and categorize the following from each job posting:

**Required Skills**
- Technical skills required
- Soft skills required
- Experience level requirements
- Certifications required or preferred

**Job Details**
- **Salary Range**: AI extracts if available, defaults to "$0" if not found
- **Location**: AI extracts if available, defaults to "N/A" if not found
- **Hiring Manager**: Extract name if mentioned in posting
- **Company Name**: Provided by user
- **Job Title**: Provided by user

#### Matching Algorithm
- **Overall Match Percentage**: Calculate 0-100% match score
- Compare extracted resume features against job requirements
- Weight technical skills, experience, and certifications appropriately
- Factor in soft skills alignment

### 20.2 User Interface Specification

#### Dashboard (Main Page)
The main dashboard will display all job applications in a card/grid layout:

```
Component Structure:
┌─────────────────────────────────────────────────────┐
│  [+ New Application Button]                         │
│                                                      │
│  Application Cards Grid:                            │
│  ┌──────────────────────────────────────┐          │
│  │ Company Name (Large, Bold)           │          │
│  │ Job Title (Medium)                   │          │
│  │ [Status Pill with Color]             │          │
│  │ Applied: Oct 13, 2025 2:30 PM EST    │          │
│  │ Updated: Oct 13, 2025 2:30 PM EST    │          │
│  │              [View Summary →]         │          │
│  └──────────────────────────────────────┘          │
└─────────────────────────────────────────────────────┘
```

**Card Information:**
- Company Name
- Job Title
- Status Pill (color-coded: pending, applied, interviewed, offered, rejected, accepted)
- Application Timestamp (EST format)
- Last Updated Timestamp (EST format)
- Button linking to Summary Page

#### Application Summary Page (Individual Application)

**Summary Section (Top):**
- AI-generated Job Description Summary (2-3 sentences)
- Salary Range: $120,000 - $180,000 (or "$0" if not found)
- Location: Remote / City, State (or "N/A" if not found)
- Hiring Manager: Name (if found in posting)
- Current Status: [Dropdown to update]
- Job URL: [Clickable link] (if provided)
- Application Timestamp: Oct 13, 2025 2:30 PM EST
- Last Updated: Oct 13, 2025 2:30 PM EST
- **Match Score: 85%** (prominently displayed)

**Details Section (Tabs or Sections):**

1. **Full Job Description Tab**
   - Complete original job posting text
   - Extracted features highlighted

2. **Cover Letter Tab**
   - AI-generated cover letter
   - Based on feature matching
   - Integrates 50% of required soft skills

3. **Customized Resume Tab**
   - AI-rewritten resume
   - Optimized for this specific job
   - Bullets aligned with job requirements

4. **Qualifications Analysis Tab**
   - Detailed feature matching breakdown
   - Strong matches listed
   - Missing skills identified
   - Recommendations provided

5. **Updates & Notes Tab**
   - Timeline of status changes
   - User-added notes per update
   - Timestamped entries (EST)

### 20.3 Application Creation Flow

**New Application Form:**
```
Fields:
- Company Name (text input, required)
- Job Title (text input, required)
- Job Description (large textarea, required)
- Job URL (text input, optional)
[Submit Button]
```

**Backend Processing:**
1. Create application folder: `<company>-<jobtitle>/`
2. Extract features from job description
3. Extract features from base resume
4. Calculate match percentage
5. Generate qualifications analysis
6. Generate customized cover letter
7. Generate customized resume
8. Create summary HTML page
9. Update dashboard

### 20.4 File Organization Per Application

```
data/applications/<company>-<jobtitle>/
├── application.yaml                    # Metadata
├── <datetime>-<company>-<jobtitle>.md # Original job description
├── <JobTitle>-Qualifications.md       # Feature matching analysis
├── <Name>-<company>-<jobtitle>-intro.md   # Cover letter
├── <Name>-<company>-<jobtitle>-Resume.md  # Customized resume
├── <datetime>-Summary-<company>-<jobtitle>.html  # Summary page
└── updates/                           # Status update notes
    ├── <datetime>-applied.md
    ├── <datetime>-interviewed.md
    └── ...
```

### 20.5 API Endpoints (REST)

```
POST   /api/applications              # Create new application
GET    /api/applications              # List all applications
GET    /api/applications/:id          # Get application details
PUT    /api/applications/:id/status   # Update status with notes
POST   /api/applications/:id/regenerate  # Regenerate documents
GET    /api/resume                    # Get base resume
PUT    /api/resume                    # Update base resume
GET    /api/check-ollama              # Check AI service health
```

### 20.6 Success Criteria

✅ **Feature Extraction**: System accurately extracts technical skills, soft skills, experience, and certifications from both resume and job descriptions

✅ **Matching**: System calculates meaningful match percentage (0-100%)

✅ **Salary & Location**: AI extracts salary range and location from job postings when available

✅ **Organized Storage**: Each application has its own folder with all required documents

✅ **Summary Page**: Individual HTML page per application with all required information sections

✅ **Dashboard**: Clean interface showing all applications with key info and quick access

✅ **Status Tracking**: Ability to update application status with timestamped notes

✅ **Timestamps**: All dates/times displayed in EST timezone

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-13 | Initial | Technical specification created |
| 1.1 | 2025-10-13 | Update | Updated to use Ollama as primary AI provider (free, local) |
| 1.2 | 2025-10-13 | Update | Added confirmed implementation specification with feature extraction and matching engine |


