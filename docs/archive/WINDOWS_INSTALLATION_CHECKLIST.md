# Hunter Windows Installation Checklist

Print this page and check off each step as you complete it.

---

## Pre-Installation

- [ ] Windows 10 (64-bit) or Windows 11
- [ ] At least 8GB RAM (16GB recommended)
- [ ] At least 10GB free disk space
- [ ] Internet connection active
- [ ] Administrator access to PC

---

## Step 1: Install Git

- [ ] Downloaded Git from https://git-scm.com/download/win
- [ ] Ran installer (`Git-2.x.x-64-bit.exe`)
- [ ] Completed installation wizard
- [ ] Verified: Opened Command Prompt and typed `git --version`
- [ ] Confirmed: Saw Git version number displayed

---

## Step 2: Install Python

- [ ] Downloaded Python 3.11+ from https://www.python.org/downloads/windows/
- [ ] Ran installer (`python-3.11.x-amd64.exe`)
- [ ] **CRITICAL**: Checked box "Add python.exe to PATH"
- [ ] Clicked "Install Now"
- [ ] Completed installation
- [ ] Verified: Opened **NEW** Command Prompt and typed `python --version`
- [ ] Confirmed: Saw Python 3.11.x or higher
- [ ] Verified: Typed `pip --version`
- [ ] Confirmed: Saw pip version number

**If Python not recognized**: Added to PATH manually (see Troubleshooting section)

---

## Step 3: Install Ollama

- [ ] Downloaded Ollama from https://ollama.com/download/windows
- [ ] Ran installer (`OllamaSetup.exe`)
- [ ] Completed installation
- [ ] Confirmed: Saw Ollama icon in system tray
- [ ] Downloaded AI model: Typed `ollama pull llama3` in Command Prompt
- [ ] Waited for download to complete (~4.7GB, 10-30 minutes)
- [ ] Verified: Typed `ollama run llama3 "Hello"`
- [ ] Confirmed: Received AI response

---

## Step 4: Clone Hunter Repository

- [ ] Decided installation location: `____________________________`
- [ ] Opened Command Prompt
- [ ] Navigated to installation location
- [ ] Cloned repository: `git clone [REPOSITORY_URL]`
  - Repository URL: `____________________________`
- [ ] Navigated into hunter directory: `cd hunter`
- [ ] Verified files: Typed `dir`
- [ ] Confirmed: Saw folders like `app`, `config`, `data`, `docs`

---

## Step 5: Set Up Python Environment

- [ ] In hunter directory: `cd C:\Projects\hunter` (or your location)
- [ ] Created virtual environment: `python -m venv venv`
- [ ] Waited for creation to complete (~30-60 seconds)
- [ ] Activated virtual environment: `venv\Scripts\activate`
- [ ] Confirmed: Saw `(venv)` in command prompt
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Waited for installation to complete (~1-2 minutes)
- [ ] Verified: Typed `pip list`
- [ ] Confirmed: Saw Flask, ollama, pyyaml, jinja2 in list

**If activation failed**: Fixed execution policy (see Troubleshooting section)

---

## Step 6: Start Ollama Service

- [ ] Checked system tray for Ollama icon
- [ ] If not running: Started Ollama from Start menu
- [ ] Confirmed: Ollama is running

---

## Step 7: Run Hunter

- [ ] In Command Prompt with `(venv)` active
- [ ] In hunter directory
- [ ] Started Hunter: `python -m app.web`
- [ ] Confirmed: Saw "🚀 Starting Job Hunter Application..."
- [ ] Confirmed: Saw "✅ Ollama is connected"
- [ ] Confirmed: Saw "Running on http://127.0.0.1:51003"
- [ ] Opened web browser
- [ ] Navigated to: http://localhost:51003
- [ ] Confirmed: Hunter web interface loaded successfully

---

## Post-Installation

- [ ] Explored Hunter dashboard
- [ ] Read User Guide at `docs\USER_GUIDE.md`
- [ ] Bookmarked: http://localhost:51003
- [ ] Created desktop shortcut (optional)
- [ ] Backed up data folder (optional)

---

## Quick Start for Future Use

Write down your quick start commands:

```cmd
1. cd _______________________  (your hunter directory)
2. venv\Scripts\activate
3. python -m app.web
4. Open: http://localhost:51003
```

---

## Common Issues Encountered

Document any issues you faced and solutions:

**Issue 1**: `____________________________`
**Solution**: `____________________________`

**Issue 2**: `____________________________`
**Solution**: `____________________________`

---

## Important Information

**Installation Date**: `____________________________`

**Installation Path**: `____________________________`

**Ollama Model Used**: `____________________________`

**Python Version**: `____________________________`

**Git Repository URL**: `____________________________`

---

## Next Steps After Installation

1. [ ] Set up your resume in Hunter
2. [ ] Create first test application
3. [ ] Explore dashboard features
4. [ ] Review analytics page
5. [ ] Read full documentation in `docs\` folder

---

## Quick Reference

**Stop Hunter**: Press `Ctrl + C` in Command Prompt

**Restart Hunter**: 
```cmd
cd C:\Projects\hunter
venv\Scripts\activate
python -m app.web
```

**Check Ollama**: Look for icon in system tray

**Update Hunter**:
```cmd
cd C:\Projects\hunter
git pull origin main
venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

---

## Resources

- [ ] Saved bookmark: Full Windows Installation Guide (`docs\INSTALLATION_WINDOWS.md`)
- [ ] Saved bookmark: Quick Reference Card (`docs\WINDOWS_QUICK_REFERENCE.md`)
- [ ] Saved bookmark: User Guide (`docs\USER_GUIDE.md`)
- [ ] Saved bookmark: Troubleshooting Guide (`docs\TROUBLESHOOTING.md`)

---

**Installation Complete!** 🎉

Date Completed: `____________________________`

Total Time Taken: `____________________________`

---

**Keep this checklist for reference and future troubleshooting.**
