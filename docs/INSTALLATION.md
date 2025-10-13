# Installation Guide

Complete guide to installing and setting up Job Hunter.

## Prerequisites

Before you begin, ensure you have:

- **Operating System**: macOS, Linux, or Windows
- **Python**: Version 3.11 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: ~5GB for Ollama models
- **Internet**: For initial setup only

## Step 1: Install Ollama

Ollama is the local AI engine that powers Job Hunter.

### macOS

```bash
# Option 1: Using Homebrew (recommended)
brew install ollama

# Option 2: Direct download
# Download from https://ollama.ai and run installer
```

### Linux

```bash
curl https://ollama.ai/install.sh | sh
```

### Windows

1. Download installer from https://ollama.ai/download
2. Run the installer
3. Follow installation prompts

### Verify Installation

```bash
# Check Ollama is installed
ollama --version
```

## Step 2: Download AI Model

Download the Llama 3 model (recommended):

```bash
# This will download ~4.7GB
ollama pull llama3
```

**Alternative models:**

```bash
# Faster, smaller (4.1GB)
ollama pull mistral

# Higher quality, larger (26GB, requires 16GB+ RAM)
ollama pull mixtral
```

## Step 3: Install Python Dependencies

### Clone/Download the Project

```bash
cd /path/to/your/projects
# If using git:
git clone https://github.com/denizen-star/hunter.git
cd hunter

# Or navigate to existing directory:
cd /Users/kervinleacock/Documents/Development/hunter
```

### Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

### Install Requirements

```bash
pip install -r requirements.txt
```

## Step 4: Start Ollama Service

Ollama needs to be running for the AI features to work.

```bash
# Start Ollama (keep this terminal open)
ollama serve
```

You should see output like:
```
Listening on 127.0.0.1:11434
```

## Step 5: Verify Installation

### Test Ollama

```bash
# In a NEW terminal
ollama run llama3 "Hello, world!"
```

You should get a response from the AI.

### Test Job Hunter

```bash
# Navigate to project
cd /Users/kervinleacock/Documents/Development/hunter

# Activate virtual environment
source venv/bin/activate

# Start Job Hunter
python -m app.web
```

You should see:
```
🚀 Starting Job Hunter Application...
📱 Open http://localhost:51002 in your browser
✅ Ollama is connected
📦 Available models: llama3:latest
```

## Step 6: Access the Application

Open your browser and go to:
- **Main UI**: http://localhost:51002
- **Dashboard**: http://localhost:51002/dashboard

## Next Steps

1. **Set up your resume**: Click "📄 Manage Resume" and add your information
2. **Create your first application**: Click "+ New Application"
3. **Explore the dashboard**: See all your applications at http://localhost:51002/dashboard

## Troubleshooting Installation

### Ollama Not Starting

```bash
# Check if something is using port 11434
lsof -i :11434

# Try restarting Ollama
pkill ollama
ollama serve
```

### Python Version Issues

```bash
# Check Python version
python3 --version

# Should be 3.11 or higher
# If not, install Python 3.11+
```

### Port 51002 Already in Use

Edit `app/web.py` and change the port:

```python
app.run(debug=True, port=51003, host='0.0.0.0')  # Use different port
```

### Virtual Environment Issues

```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Model Download Fails

```bash
# Clear Ollama cache and retry
rm -rf ~/.ollama/models
ollama pull llama3
```

## Uninstallation

To remove Job Hunter:

```bash
# 1. Stop the application (Ctrl+C)

# 2. Deactivate virtual environment
deactivate

# 3. Remove the project directory
rm -rf /path/to/hunter

# 4. (Optional) Remove Ollama
brew uninstall ollama  # macOS
# or follow OS-specific uninstall steps
```

## System Requirements

### Minimum Requirements
- CPU: Modern x86_64 or ARM processor
- RAM: 8GB
- Disk: 10GB free space
- OS: macOS 10.15+, Ubuntu 20.04+, Windows 10+

### Recommended Requirements
- CPU: Multi-core processor (4+ cores)
- RAM: 16GB
- Disk: 20GB free space (for multiple models)
- OS: Latest version

## Docker Installation (Optional)

Coming in future version - Docker support for easier deployment.

---

**Need Help?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md) or [FAQ](FAQ.md)

