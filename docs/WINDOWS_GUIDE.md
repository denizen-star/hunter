# Hunter Windows Guide

Complete guide for installing, running, and troubleshooting Hunter on Windows 10/11.

---

## Table of Contents

1. [Installation](#installation)
2. [Daily Usage](#daily-usage)
3. [Quick Reference](#quick-reference)
4. [Troubleshooting](#troubleshooting)
5. [Installation Checklist](#installation-checklist)
6. [Uninstallation](#uninstallation)

---

## Installation

### Prerequisites

Before you begin, ensure your Windows PC meets these requirements:

- **Operating System**: Windows 10 (64-bit) or Windows 11
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: ~10GB free space (5GB for AI models + 5GB for application)
- **Internet Connection**: Required for initial setup
- **Administrator Access**: Needed for software installation

### Step 1: Install Git

Git allows you to download and manage the Hunter source code.

1. Go to: **https://git-scm.com/download/win**
2. Download and run the installer (`Git-2.x.x-64-bit.exe`)
3. During installation, select **"Git from the command line and also from 3rd-party software"**
4. Complete the installation wizard

**Verify Installation:**
```cmd
git --version
```
Should show: `git version 2.x.x.windows.1`

### Step 2: Install Python

Hunter requires Python 3.11 or higher.

1. Go to: **https://www.python.org/downloads/windows/**
2. Download Python 3.11+ (latest 3.11+ version)
3. Run the installer (`python-3.11.x-amd64.exe`)
4. **CRITICAL**: Check **"Add python.exe to PATH"** checkbox at the bottom
5. Click **"Install Now"**

**Verify Installation:**
```cmd
python --version
```
Should show: `Python 3.11.x`

```cmd
pip --version
```
Should show pip version number

**Troubleshooting**: If `python` is not recognized, see [Troubleshooting](#python-not-recognized) section.

### Step 3: Install Ollama

Ollama is the local AI engine that powers Hunter's intelligent features.

1. Go to: **https://ollama.com/download/windows**
2. Click **"Download for Windows"**
3. Run the installer (`OllamaSetup.exe`)
4. Ollama will automatically start after installation
5. Look for Ollama icon in system tray (bottom-right)

**Download the AI Model:**
```cmd
ollama pull llama3
```
This downloads ~4.7GB and may take 10-30 minutes.

**Verify Installation:**
```cmd
ollama run llama3 "Hello, what is 2+2?"
```
You should get an AI response. Press `Ctrl+D` to exit.

### Step 4: Clone Hunter Repository

1. Choose installation location (e.g., `C:\Projects\hunter`)
2. Open Command Prompt
3. Navigate to installation location:
   ```cmd
   cd C:\
   mkdir Projects
   cd Projects
   ```
4. Clone the repository:
   ```cmd
   git clone https://github.com/YOUR_USERNAME/hunter.git
   ```
   Replace `YOUR_USERNAME/hunter` with actual repository URL.
5. Navigate into hunter directory:
   ```cmd
   cd hunter
   ```
6. Verify files:
   ```cmd
   dir
   ```
   Should see folders: `app`, `config`, `data`, `docs`, etc.

### Step 5: Set Up Python Environment

**Create Virtual Environment:**
```cmd
python -m venv venv
```

**Activate Virtual Environment:**
```cmd
venv\Scripts\activate
```
Your prompt should show `(venv)` at the beginning.

**Install Dependencies:**
```cmd
pip install -r requirements.txt
```
Installation takes 1-2 minutes.

**Verify Installation:**
```cmd
pip list
```
Should show: Flask, ollama, pyyaml, jinja2, etc.

### Step 6: Start Ollama Service

**Check if Running:**
- Look for Ollama icon in system tray (bottom-right)

**Start Manually (if needed):**
- Start Menu → type "Ollama" → click Ollama
- OR from Command Prompt: `ollama serve` (keep window open)

### Step 7: Run Hunter

1. Ensure Ollama is running (system tray icon)
2. Navigate to hunter directory:
   ```cmd
   cd C:\Projects\hunter
   ```
3. Activate virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
4. Start Hunter:
   ```cmd
   python -m app.web
   ```
5. You should see:
   ```
   🚀 Starting Job Hunter Application...
   📱 Open http://localhost:51003 in your browser
   ✅ Ollama is connected
   ```
6. Open browser: **http://localhost:51003**

**Installation Complete!** 🎉

---

## Daily Usage

### Quick Start Procedure

Every time you want to use Hunter:

```cmd
# 1. Navigate to Hunter directory
cd C:\Projects\hunter

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Ensure Ollama is running (check system tray icon)

# 4. Start Hunter
python -m app.web

# 5. Open browser
http://localhost:51003
```

### Stopping Hunter

- In Command Prompt: Press `Ctrl + C`
- Type `deactivate` to exit virtual environment
- Close Command Prompt

### Creating a Desktop Shortcut

Create `start_hunter.bat` on your desktop:

```batch
@echo off
cd C:\Projects\hunter
call venv\Scripts\activate
start http://localhost:51003
python -m app.web
pause
```

Double-click to run Hunter.

---

## Quick Reference

### Daily Commands

```cmd
# Start Hunter
cd C:\Projects\hunter
venv\Scripts\activate
python -m app.web

# Stop Hunter
Ctrl + C
deactivate

# Check Ollama
ollama list
ollama run llama3 "test"
```

### Useful URLs

- **Main App**: http://localhost:51003
- **Dashboard**: http://localhost:51003/dashboard
- **Analytics**: http://localhost:51003/analytics
- **Reports**: http://localhost:51003/reports

### File Locations

```
C:\Projects\hunter\
├── data\
│   ├── applications\      # Your applications
│   ├── resumes\           # Resume files
│   └── covers\            # Generated cover letters
├── config\
│   └── config.yaml        # Settings
└── docs\                  # Documentation
```

### Update Hunter

```cmd
cd C:\Projects\hunter
git pull origin main
venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

### Model Management

```cmd
# List installed models
ollama list

# Pull new model
ollama pull mistral

# Remove model
ollama rm llama3

# Switch model: Edit config/config.yaml
# Change: model: "llama3" to model: "mistral"
```

---

## Troubleshooting

### Python Not Recognized

**Problem**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click **"Advanced"** tab → **"Environment Variables"**
3. Under **"System variables"**, find **"Path"**, click **"Edit"**
4. Click **"New"** and add:
   - `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\`
   - `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\Scripts\`
5. Click **"OK"** on all windows
6. **Close and reopen** Command Prompt
7. Try `python --version` again

**Alternative**: Reinstall Python and make sure to check **"Add python.exe to PATH"**

### Ollama Not Connecting

**Problem**: Hunter says "Ollama is not running" or can't connect

**Solutions**:

1. **Check Ollama Status**:
   - Look for Ollama icon in system tray
   - If missing, start Ollama from Start menu

2. **Restart Ollama**:
   - Right-click Ollama icon in system tray → "Quit Ollama"
   - Start Ollama again from Start menu

3. **Test Ollama**:
   ```cmd
   ollama list
   ```
   Should show installed models. If error, reinstall Ollama.

### Port Already in Use

**Problem**: Error says port 51003 is already in use

**Solution 1: Find and Stop Process**
```cmd
# Find process using port
netstat -ano | findstr :51003

# Note the PID (last number), then kill it
taskkill /PID [number] /F
```

**Solution 2: Use Different Port**
```cmd
set PORT=51004
python -m app.web
```
Then use: http://localhost:51004

### Virtual Environment Activation Fails

**Problem**: Script execution is disabled on this system

**Solution**:
1. Open PowerShell as Administrator
2. Run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Type `Y` and press Enter
4. Close PowerShell
5. Try activating virtual environment again

**Alternative**: Use Command Prompt instead of PowerShell

### Missing Dependencies

**Problem**: Import errors when running Hunter

**Solution**:
```cmd
cd C:\Projects\hunter
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Slow AI Responses

**Problem**: Hunter is very slow when generating content

**Solutions**:
1. **Insufficient RAM**: Close other applications to free memory
2. **Wrong Model**: Try a smaller model:
   ```cmd
   ollama pull mistral
   ```
   Then edit `config/config.yaml`: change `model: "llama3"` to `model: "mistral"`
3. **Ollama Issues**: Restart Ollama service

### Git Clone Fails

**Problem**: Authentication error when cloning repository

**Solutions**:
1. Repository might be private - contact repository owner for access
2. Use SSH instead of HTTPS (set up SSH key with GitHub first)
3. Configure credentials:
   ```cmd
   git config --global credential.helper wincred
   ```

### Page Won't Load in Browser

**Problem**: "This site can't be reached" or "Connection refused"

**Solutions**:
1. **Hunter not running**: Check Command Prompt - should show "Running on http://127.0.0.1:51003"
2. **Wrong URL**: Use `http://localhost:51003` (not `https://`)
3. **Firewall**: Windows Firewall may ask permission - click "Allow access"

### SSL Certificate Error

**Problem**: `SSL: CERTIFICATE_VERIFY_FAILED` when installing packages

**Solution** (if behind corporate proxy):
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `'python' is not recognized` | Python not in PATH | Add to PATH or reinstall with PATH checkbox |
| `Script execution disabled` | PowerShell execution policy | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `Port 51003 is in use` | Another process using port | Kill process or use different port |
| `Could not connect to Ollama` | Ollama not running | Start Ollama from Start menu |
| `Model not found` | AI model not downloaded | `ollama pull llama3` |
| `No module named 'X'` | Dependencies not installed | Activate venv, run `pip install -r requirements.txt` |

---

## Installation Checklist

Print this checklist and check off each step as you complete it.

### Pre-Installation
- [ ] Windows 10 (64-bit) or Windows 11
- [ ] At least 8GB RAM (16GB recommended)
- [ ] At least 10GB free disk space
- [ ] Internet connection active
- [ ] Administrator access to PC

### Step 1: Install Git
- [ ] Downloaded Git from https://git-scm.com/download/win
- [ ] Ran installer
- [ ] Verified: `git --version` shows version number

### Step 2: Install Python
- [ ] Downloaded Python 3.11+ from https://www.python.org/downloads/windows/
- [ ] Ran installer
- [ ] **CRITICAL**: Checked box "Add python.exe to PATH"
- [ ] Verified: `python --version` shows 3.11.x or higher
- [ ] Verified: `pip --version` shows version number

### Step 3: Install Ollama
- [ ] Downloaded Ollama from https://ollama.com/download/windows
- [ ] Ran installer
- [ ] Confirmed: Saw Ollama icon in system tray
- [ ] Downloaded AI model: `ollama pull llama3`
- [ ] Waited for download to complete (~4.7GB, 10-30 minutes)
- [ ] Verified: `ollama run llama3 "Hello"` receives AI response

### Step 4: Clone Hunter Repository
- [ ] Decided installation location: `____________________________`
- [ ] Opened Command Prompt
- [ ] Navigated to installation location
- [ ] Cloned repository: `git clone [REPOSITORY_URL]`
- [ ] Navigated into hunter directory: `cd hunter`
- [ ] Verified files: `dir` shows folders like `app`, `config`, `data`, `docs`

### Step 5: Set Up Python Environment
- [ ] In hunter directory
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Activated virtual environment: `venv\Scripts\activate`
- [ ] Confirmed: Saw `(venv)` in command prompt
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Verified: `pip list` shows Flask, ollama, pyyaml, jinja2

### Step 6: Start Ollama Service
- [ ] Checked system tray for Ollama icon
- [ ] If not running: Started Ollama from Start menu
- [ ] Confirmed: Ollama is running

### Step 7: Run Hunter
- [ ] In Command Prompt with `(venv)` active
- [ ] In hunter directory
- [ ] Started Hunter: `python -m app.web`
- [ ] Confirmed: Saw "🚀 Starting Job Hunter Application..."
- [ ] Confirmed: Saw "✅ Ollama is connected"
- [ ] Confirmed: Saw "Running on http://127.0.0.1:51003"
- [ ] Opened web browser
- [ ] Navigated to: http://localhost:51003
- [ ] Confirmed: Hunter web interface loaded successfully

### Post-Installation
- [ ] Explored Hunter dashboard
- [ ] Read User Guide at `docs\USER_GUIDE.md`
- [ ] Bookmarked: http://localhost:51003
- [ ] Created desktop shortcut (optional)

### Important Information

**Installation Date**: `____________________________`  
**Installation Path**: `____________________________`  
**Ollama Model Used**: `llama3`  
**Python Version**: `____________________________`  
**Git Repository URL**: `____________________________`

---

## Uninstallation

To completely remove Hunter from your system:

### 1. Stop Hunter
- Press `Ctrl + C` in Command Prompt running Hunter
- Type `deactivate` and press Enter

### 2. Delete Hunter Directory
1. Open File Explorer
2. Navigate to `C:\Projects\hunter` (or your installation location)
3. Delete the `hunter` folder

### 3. Uninstall Ollama (Optional)
1. Press `Win + R`, type `appwiz.cpl`, press Enter
2. Find "Ollama" in the list
3. Right-click → Uninstall
4. Delete folder: `C:\Users\YourUsername\.ollama` (contains downloaded models)

### 4. Uninstall Python (Optional)
1. Press `Win + R`, type `appwiz.cpl`, press Enter
2. Find "Python 3.11.x" in the list
3. Right-click → Uninstall

### 5. Uninstall Git (Optional)
1. Press `Win + R`, type `appwiz.cpl`, press Enter
2. Find "Git" in the list
3. Right-click → Uninstall

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 (64-bit) or Windows 11
- **CPU**: Intel Core i5 or AMD Ryzen 5 (or equivalent)
- **RAM**: 8GB
- **Disk**: 10GB free space
- **Internet**: For initial setup only

### Recommended Requirements
- **OS**: Windows 11 (latest version)
- **CPU**: Intel Core i7 or AMD Ryzen 7 (or equivalent)
- **RAM**: 16GB or more
- **Disk**: 20GB free space (SSD preferred)
- **Internet**: Broadband for faster model downloads

---

## Additional Resources

- **User Guide**: See `docs/USER_GUIDE.md` for how to use Hunter
- **General Troubleshooting**: See `docs/TROUBLESHOOTING.md` for more solutions
- **Quick Start**: See `docs/QUICKSTART.md` for a faster setup overview
- **Technical Details**: See `docs/TECHNICAL_REFERENCE.md` for architecture info
- **API Reference**: See `docs/API_REFERENCE.md` for API documentation

---

## Tips for Windows Users

### Using PowerShell Instead of Command Prompt
All `cmd` commands work the same. Virtual environment activation:
```powershell
.\venv\Scripts\Activate.ps1
```

### Performance Tips
1. Close unused applications to free RAM
2. Use SSD for faster model loading
3. Restart Ollama if responses are slow
4. Use smaller model (mistral) if low on RAM

### Firewall Warning
First time running Hunter, Windows Firewall may ask for permission. Click **"Allow access"** to let Hunter run its web server.

---

**Last Updated**: January 2026  
**Hunter Version**: 12.2.0  
**Windows Compatibility**: Windows 10 (64-bit), Windows 11

---

Happy job hunting! 🎯
