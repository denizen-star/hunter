# 🎯 Job Hunter - AI-Powered Application Manager

An intelligent job application management system that uses local AI (Ollama) to match your resume with job descriptions, generate customized cover letters and resumes, and track your applications.

## 📚 Documentation

**All documentation is now organized in the `docs/` folder:**

- **[📖 Start Here](docs/README.md)** - Main documentation overview
- **[🚀 Quick Start](docs/QUICKSTART.md)** - Get running in 5 minutes
- **[👤 User Guide](docs/USER_GUIDE.md)** - Complete usage guide
- **[🔧 Technical Docs](docs/TECHNICAL_SPECIFICATION.md)** - Architecture and API

## ✨ Key Features

- **AI-Powered Matching**: Local AI analyzes job descriptions and resumes
- **Automated Documents**: Generates cover letters, tailored resumes, and analyses
- **Application Tracking**: Dashboard with status management and notes
- **Privacy-First**: 100% local processing, no cloud services
- **Modern Interface**: Clean web UI with tabbed dashboard

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

---

**Version**: 2.0.0  
**Last Updated**: October 21, 2025
