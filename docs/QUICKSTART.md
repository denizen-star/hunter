# Quick Start Guide - Job Hunter

Get Job Hunter running in 5 minutes!

## Prerequisites Check

Before starting, verify you have:
- [ ] macOS, Linux, or Windows
- [ ] Python 3.11 or higher
- [ ] 8GB+ RAM available
- [ ] Internet connection (for initial setup only)

## Step 1: Install Ollama (2 minutes)

### macOS
```bash
brew install ollama
```

### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

### Windows
Download from https://ollama.com/download/windows and run installer

**Need detailed Windows instructions?** See [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md)

## Step 2: Download AI Model (3 minutes)

```bash
# Start Ollama (keep this terminal open)
ollama serve

# In a NEW terminal, download the AI model (~4.7GB)
ollama pull llama3
```

## Step 3: Install Job Hunter (1 minute)

```bash
# Clone repository
git clone https://github.com/denizen-star/hunter.git
cd hunter

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Start Application (30 seconds)

```bash
# Make sure Ollama is still running in another terminal!

# Start Job Hunter
python -m app.web

# Or use the convenience script
./run.sh
```

## Step 5: Open Browser

Navigate to: **http://localhost:51002**

## Step 6: Set Up Your Resume (2 minutes)

1. Click "📄 Manage Resume"
2. Fill in your information:
   - Full name, email, phone
   - LinkedIn, location
   - Complete resume content (Markdown format)
3. Click "Save Resume"

## Step 7: Create Your First Application (1 minute)

1. Find a job posting you're interested in
2. Copy the complete job description
3. Back in Job Hunter:
   - Enter company name
   - Enter job title
   - Paste job description
   - (Optional) Add job URL
4. Click "🚀 Analyze & Create Application"
5. Wait 30-60 seconds for AI processing

## Step 8: View Results

1. See your match score (0-100%)
2. Click "View Summary" to see:
   - Qualifications analysis
   - Generated cover letter
   - Customized resume
   - Job details (salary, location, etc.)

## Step 9: Check Dashboard

Go to **http://localhost:51002/dashboard** to see all your applications!

---

## Quick Reference

### URLs
- **Main UI**: http://localhost:51002
- **Dashboard**: http://localhost:51002/dashboard

### Common Commands

```bash
# Start Ollama
ollama serve

# Start Job Hunter
cd /path/to/hunter
source venv/bin/activate
python -m app.web

# Check Ollama connection
curl http://localhost:11434/api/tags

# Check Job Hunter
curl http://localhost:51002/api/check-ollama
```

### Troubleshooting Quick Fixes

**Ollama not connected?**
```bash
ollama serve
```

**Resume not found?**
- Go to http://localhost:51002
- Click "📄 Manage Resume"
- Fill in and save

**Port already in use?**
- Edit `app/web.py` line 370
- Change port from 51002 to another number

---

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed usage
- Check [API Reference](API_REFERENCE.md) for automation
- See [Troubleshooting](TROUBLESHOOTING.md) if issues arise

---

**That's it! You're ready to supercharge your job search! 🎯**

Need help? Check the [full documentation](INDEX.md).

