# 🎯 Job Hunter - AI-Powered Application Manager

An intelligent job application management system that uses local AI (Ollama) to match your resume with job descriptions, generate customized cover letters and resumes, and track your applications.

## ✨ Key Features

- **Feature Extraction & Matching Engine**: AI extracts skills, experience, and certifications from both your resume and job descriptions
- **Intelligent Match Scoring**: Get a 0-100% match score for each job application
- **Automated Document Generation**:
  - Customized cover letters
  - Tailored resumes optimized for each job
  - Detailed qualifications analysis
  - Comprehensive summary pages
- **Application Tracking**: Track status, add notes, and manage your job search pipeline
- **100% Local & Private**: All AI processing happens on your computer using Ollama (free!)
- **Modern Web Interface**: Clean, intuitive UI for managing applications
- **Beautiful Dashboard**: Visual overview of all your applications

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **Ollama** (free, local AI)
3. **8GB+ RAM** available

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Or download from https://ollama.ai

# Start Ollama service
ollama serve

# Pull the AI model (in a new terminal)
ollama pull llama3
```

### 2. Install Job Hunter

```bash
# Clone or navigate to the project directory
cd /Users/kervinleacock/Documents/Development/hunter

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Your Resume

Create your base resume at `data/resumes/base_resume.md` or use the web interface to create one.

**Option A: Use Web Interface**
1. Start the application (see step 4)
2. Click "📄 Manage Resume"
3. Fill in your information and save

**Option B: Create Manually**

Create a file at `data/resumes/base_resume.md` with your resume in Markdown format:

```markdown
# Your Name

## Contact Information
- Email: your.email@example.com
- Phone: +1-XXX-XXX-XXXX
- LinkedIn: linkedin.com/in/yourprofile
- Location: City, State

## Professional Summary
Your professional summary here...

## Experience
### Job Title | Company Name
*Month Year - Present*
- Achievement or responsibility with quantifiable results
- Another key accomplishment

... (rest of your resume)
```

### 4. Start the Application

```bash
# Make sure Ollama is running in another terminal:
ollama serve

# Start Job Hunter
python -m app.web

# Or use the run script
chmod +x run.sh
./run.sh
```

Open your browser to **http://localhost:3000**

## 📖 Usage

### Creating a New Application

1. Click "**+ New Application**" on the main page
2. Fill in:
   - **Company Name** (required)
   - **Job Title** (required)
   - **Job URL** (optional - link to posting)
   - **Job Description** (required - paste the full job posting)
3. Click "**🚀 Analyze & Create Application**"
4. Wait 30-60 seconds while AI processes
5. View your match score and generated documents!

### What Gets Generated

For each application, the system creates:

```
data/applications/<company>-<jobtitle>/
├── application.yaml                    # Metadata
├── <timestamp>-<company>-<jobtitle>.md # Job description
├── <JobTitle>-Qualifications.md        # Feature matching analysis
├── <YourName>-<company>-<jobtitle>-intro.md   # Cover letter
├── <YourName>-<company>-<jobtitle>-Resume.md  # Customized resume
├── <timestamp>-Summary-<company>-<jobtitle>.html  # Summary page
└── updates/                            # Status updates & notes
```

### Viewing Applications

- **Dashboard**: http://localhost:3000/dashboard - See all applications at a glance
- **Summary Page**: Click "View Summary" on any application card for detailed information

### Updating Application Status

Use the API or update manually:

```bash
curl -X PUT http://localhost:3000/api/applications/<app-id>/status \
  -H "Content-Type: application/json" \
  -d '{"status": "interviewed", "notes": "Phone screen went well!"}'
```

Available statuses: `pending`, `applied`, `interviewed`, `offered`, `rejected`, `accepted`

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python 3.11+ with Flask
- **AI**: Ollama (local LLM) with Llama 3
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Storage**: File-based (YAML, Markdown, HTML)

### Directory Structure

```
job-hunter/
├── app/
│   ├── models/          # Data models (Application, Resume, Qualification)
│   ├── services/        # Business logic services
│   ├── utils/           # Utility functions
│   ├── templates/       # HTML templates
│   └── web.py          # Flask web application
├── config/
│   └── config.yaml     # Configuration
├── data/
│   ├── resumes/        # Your base resume
│   ├── applications/   # Generated applications
│   └── output/         # Dashboard HTML
├── requirements.txt
└── README.md
```

## 🔧 Configuration

Edit `config/config.yaml` to customize:

```yaml
ai:
  provider: "ollama"
  model: "llama3"  # Options: llama3, mistral, mixtral
  base_url: "http://localhost:11434"
  temperature: 0.7
  max_tokens: 2000
```

### Using Different Ollama Models

```bash
# Faster, smaller model
ollama pull mistral

# Higher quality, larger model (requires 16GB+ RAM)
ollama pull mixtral

# Update config.yaml to use the new model
```

## 📊 API Endpoints

### Applications

- `POST /api/applications` - Create new application
- `GET /api/applications` - List all applications
- `GET /api/applications/:id` - Get application details
- `PUT /api/applications/:id/status` - Update status with notes
- `POST /api/applications/:id/regenerate` - Regenerate documents

### Resume

- `GET /api/resume` - Get base resume
- `PUT /api/resume` - Update base resume
- `POST /api/resume/init` - Create resume template

### System

- `GET /api/check-ollama` - Check AI connection status
- `POST /api/dashboard/update` - Regenerate dashboard

## 🎨 Features in Detail

### Feature Extraction

The AI automatically extracts and categorizes:

**From Your Resume:**
- Technical skills (Python, React, AWS, etc.)
- Soft skills (Leadership, Communication, etc.)
- Years of experience per technology
- Certifications

**From Job Descriptions:**
- Required technical skills
- Required soft skills
- Experience requirements
- Certifications needed
- Salary range (if mentioned, defaults to "$0")
- Location (defaults to "N/A" if not found)
- Hiring manager (if mentioned)

### Match Scoring

The AI compares extracted features and provides:
- Overall match percentage (0-100%)
- List of strong matches
- Missing skills identified
- Recommendations for highlighting relevant experience

### Document Generation

1. **Qualifications Analysis**: Detailed breakdown of how you match the job
2. **Cover Letter**: Professional letter integrating 50% of required soft skills
3. **Customized Resume**: Rewritten bullets optimized for the specific job
4. **Summary Page**: Beautiful HTML page with all information and tabs

## 🐛 Troubleshooting

### Ollama Not Connected

```bash
# Make sure Ollama is running
ollama serve

# Check if model is downloaded
ollama list

# Pull the model if needed
ollama pull llama3

# Test Ollama
ollama run llama3 "Hello"
```

### Port Already in Use

```bash
# Change port in app/web.py:
app.run(debug=True, port=3001)  # Use different port
```

### Resume Not Found

1. Go to http://localhost:3000
2. Click "📄 Manage Resume"
3. Fill in your information and save

Or create manually at `data/resumes/base_resume.md`

### Slow AI Processing

- Use a faster model: `ollama pull mistral`
- Update `config/config.yaml` to use `mistral`
- Or allocate more RAM to your system

## 🔒 Privacy & Security

- **100% Local**: All AI processing happens on your computer
- **No Cloud**: Your resume and job data never leave your machine
- **No API Keys**: No need to share data with third parties
- **File-Based Storage**: All data stored locally in organized folders

## 🚧 Roadmap

### v1.1 (Planned)
- [ ] Email integration for follow-ups
- [ ] Calendar integration for interviews
- [ ] Export to PDF
- [ ] Browser extension for job capture

### v2.0 (Future)
- [ ] Analytics and insights
- [ ] A/B testing for cover letters
- [ ] Success rate tracking
- [ ] Interview preparation guides

## 📝 License

MIT License - Feel free to use and modify for personal use

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📧 Support

For issues or questions, please check:
1. Ollama is running: `ollama serve`
2. Model is downloaded: `ollama list`
3. Resume exists at `data/resumes/base_resume.md`
4. Check browser console for errors

## 🌟 Credits

Built with:
- [Ollama](https://ollama.ai) - Local LLM runtime
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Llama 3](https://ai.meta.com/llama/) - AI model

---

**Happy Job Hunting! 🎯**

