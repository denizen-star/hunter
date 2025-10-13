# 🚀 Quick Start Guide

Get Job Hunter running in 5 minutes!

## Step 1: Install Ollama (2 minutes)

```bash
# Install Ollama
brew install ollama

# Start Ollama (keep this terminal open)
ollama serve

# In a NEW terminal, download the AI model (4-5GB)
ollama pull llama3
```

## Step 2: Install Job Hunter (1 minute)

```bash
# Navigate to project
cd /Users/kervinleacock/Documents/Development/hunter

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Create Your Resume (1 minute)

**Option A: Via Web Interface (Recommended)**
1. Start the app: `./run.sh`
2. Open http://localhost:3000
3. Click "📄 Manage Resume"
4. Paste your resume content
5. Click "Save Resume"

**Option B: Manually**
```bash
# Copy your resume to:
cp your_resume.md data/resumes/base_resume.md
```

## Step 4: Start the Application (30 seconds)

```bash
# Easy way:
./run.sh

# Or manually:
source venv/bin/activate
python -m app.web
```

Open **http://localhost:3000** in your browser!

## Step 5: Create Your First Application

1. Click "**+ New Application**"
2. Enter company name and job title
3. Paste the job description
4. Click "**🚀 Analyze & Create Application**"
5. Wait 30-60 seconds
6. View your match score and generated documents!

## View Your Dashboard

Go to **http://localhost:3000/dashboard** to see all your applications!

---

## Troubleshooting

### "Ollama is not connected"
```bash
# Make sure Ollama is running in a separate terminal:
ollama serve
```

### "Resume not found"
1. Go to http://localhost:3000
2. Click "📄 Manage Resume"
3. Fill in your info and save

### "Model not found"
```bash
# Download the AI model:
ollama pull llama3
```

---

**That's it! You're ready to supercharge your job search! 🎯**

For detailed documentation, see [README.md](README.md)

