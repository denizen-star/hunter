# 🎯 Job Hunter - AI-Powered Application Manager

An intelligent job application management system that uses local AI (Ollama) to match your resume with job descriptions, generate customized cover letters and resumes, and track your applications.

## 📚 Documentation

**All documentation is now organized in the `docs/` folder:**

- **[📖 Start Here](docs/README.md)** - Main documentation overview
- **[🚀 Quick Start](docs/QUICKSTART.md)** - Get running in 5 minutes
- **[👤 User Guide](docs/USER_GUIDE.md)** - Complete usage guide
- **[🔧 Technical Docs](docs/TECHNICAL_SPECIFICATION.md)** - Architecture and API

## ✨ Key Features

- **AI-Powered Matching**: Local AI analyzes job descriptions and resumes for match scoring
- **Automated Documents**: Generates cover letters, tailored resumes, and detailed analyses
- **Application Tracking**: Comprehensive dashboard with status management, notes, and progress tracking
- **Daily Digest**: Automated daily summaries with status changes, activities, and analytics (MD/PDF/Email)
- **Unified Search**: Search and filter all applications and contacts from a single interface (v12.0.0)
- **Networking Contacts**: Track professional networking contacts with AI-generated research and messages
- **Privacy-First**: 100% local processing, no cloud services required
- **Modern Interface**: Clean web UI with icon-driven navigation and responsive design

## 🚀 Quick Start

### macOS/Linux

```bash
# 1. Install Ollama
brew install ollama
ollama pull llama3
ollama serve

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
python -m app.web
```

### Windows

**See [Windows Installation Guide](docs/INSTALLATION_WINDOWS.md)** for detailed step-by-step instructions.

Quick Windows steps:
1. Install Git, Python 3.11+, and Ollama
2. Clone repository: `git clone [repository-url]`
3. Create virtual environment: `python -m venv venv`
4. Activate: `venv\Scripts\activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run: `python -m app.web`

Open **http://localhost:51003** in your browser.

## 📖 Full Documentation

For complete documentation, installation guides, troubleshooting, and API reference, see the **[docs/](docs/)** folder.

## 🎯 Main Dashboards

- **App Dash**: Job applications dashboard with status cards and filtering
- **Network Dash**: Networking contacts dashboard for relationship management
- **Daily Activities**: Track all activities with status changes and timeline
- **Search**: Unified search across all applications and contacts (v12.0.0)
- **Reports**: Analytics and reporting on your job search activity
- **Analytics**: Detailed insights and metrics
- **Daily Digest**: Automated daily summaries (configure in `config/digest_config.yaml`)

---

**Version**: 12.0.0  
**Last Updated**: January 8, 2026
