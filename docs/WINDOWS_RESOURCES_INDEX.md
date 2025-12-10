# Windows Resources Index

Complete guide to all Windows-specific documentation for Hunter.

---

## Quick Navigation

### 📥 **Installation**
| Document | Purpose | When to Use |
|----------|---------|-------------|
| [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md) | Complete step-by-step installation guide | First-time setup on Windows |
| [WINDOWS_INSTALLATION_CHECKLIST.md](WINDOWS_INSTALLATION_CHECKLIST.md) | Printable checklist to track progress | During installation to stay organized |

### 🚀 **Daily Use**
| Document | Purpose | When to Use |
|----------|---------|-------------|
| [WINDOWS_QUICK_REFERENCE.md](WINDOWS_QUICK_REFERENCE.md) | Quick command reference card | Daily startup and common tasks |

### 🔧 **Troubleshooting**
| Document | Purpose | When to Use |
|----------|---------|-------------|
| [WINDOWS_TROUBLESHOOTING_FLOWCHART.md](WINDOWS_TROUBLESHOOTING_FLOWCHART.md) | Decision tree for diagnosing problems | When encountering errors or issues |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | General troubleshooting guide | Additional problem-solving |

---

## Documentation by User Type

### 🆕 **First-Time Windows Users**

Start here and follow in order:

1. **Read the Overview**
   - [WHAT_IS_HUNTER.md](WHAT_IS_HUNTER.md) - Understand what Hunter does

2. **Install Hunter**
   - [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md) - Follow step-by-step
   - [WINDOWS_INSTALLATION_CHECKLIST.md](WINDOWS_INSTALLATION_CHECKLIST.md) - Track your progress

3. **Learn to Use Hunter**
   - [USER_GUIDE.md](USER_GUIDE.md) - Complete usage guide
   - [QUICKSTART.md](QUICKSTART.md) - Quick overview

4. **Keep for Reference**
   - [WINDOWS_QUICK_REFERENCE.md](WINDOWS_QUICK_REFERENCE.md) - Bookmark or print this

### 👨‍💻 **Experienced Windows Developers**

Quick path to get running:

1. **Quick Install** - [QUICKSTART.md](QUICKSTART.md)
2. **Windows Commands** - [WINDOWS_QUICK_REFERENCE.md](WINDOWS_QUICK_REFERENCE.md)
3. **Technical Details** - [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)

### 🐛 **Troubleshooting Issues**

When something goes wrong:

1. **Identify the Problem**
   - [WINDOWS_TROUBLESHOOTING_FLOWCHART.md](WINDOWS_TROUBLESHOOTING_FLOWCHART.md) - Diagnose the issue

2. **Find the Solution**
   - [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md) - See Troubleshooting section
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - General fixes

3. **Verify Setup**
   - [WINDOWS_INSTALLATION_CHECKLIST.md](WINDOWS_INSTALLATION_CHECKLIST.md) - Ensure all steps completed

---

## Document Details

### INSTALLATION_WINDOWS.md
**Size**: Comprehensive (50+ pages)  
**Time to Read**: 20-30 minutes  
**Time to Complete**: 1-2 hours (including downloads)

**Contents**:
- Step 1: Install Git
- Step 2: Install Python
- Step 3: Install Ollama
- Step 4: Clone Repository
- Step 5: Set Up Virtual Environment
- Step 6: Start Ollama
- Step 7: Run Hunter
- Troubleshooting section
- Uninstallation guide

**Best For**: First-time installation, complete setup

---

### WINDOWS_QUICK_REFERENCE.md
**Size**: Quick (2-3 pages)  
**Time to Read**: 5 minutes  

**Contents**:
- Daily startup commands
- Common issues quick fixes
- Useful URLs
- File locations
- Backup commands
- Model management

**Best For**: Daily use, quick command lookup

---

### WINDOWS_INSTALLATION_CHECKLIST.md
**Size**: Checklist (3-4 pages)  
**Time to Complete**: During installation  

**Contents**:
- Pre-installation checklist
- Step-by-step checkboxes
- Space for notes
- Quick reference section
- Issue tracking

**Best For**: Staying organized during installation, printing out

---

### WINDOWS_TROUBLESHOOTING_FLOWCHART.md
**Size**: Decision tree (15+ pages)  
**Time to Read**: As needed  

**Contents**:
- Installation problems
- Runtime issues
- Browser access problems
- Performance issues
- Error message reference
- Advanced diagnostics

**Best For**: Diagnosing specific problems, systematic troubleshooting

---

## Common Workflows

### Fresh Installation on New Windows PC

```
1. Read: WHAT_IS_HUNTER.md (understand the app)
2. Follow: INSTALLATION_WINDOWS.md (complete setup)
3. Use: WINDOWS_INSTALLATION_CHECKLIST.md (track progress)
4. If issues: WINDOWS_TROUBLESHOOTING_FLOWCHART.md
5. Bookmark: WINDOWS_QUICK_REFERENCE.md (daily use)
```

### Hunter Stopped Working

```
1. Check: WINDOWS_QUICK_REFERENCE.md (quick fixes)
2. Diagnose: WINDOWS_TROUBLESHOOTING_FLOWCHART.md
3. Deep dive: INSTALLATION_WINDOWS.md (troubleshooting section)
4. Last resort: Clean reinstall (INSTALLATION_WINDOWS.md)
```

### Setting Up on Multiple Windows PCs

```
1. First PC: Follow INSTALLATION_WINDOWS.md completely
2. Document issues: Use WINDOWS_INSTALLATION_CHECKLIST.md
3. Other PCs: Use your notes + WINDOWS_QUICK_REFERENCE.md
4. Streamline: Create custom batch file (see WINDOWS_QUICK_REFERENCE.md)
```

### Daily Hunter Usage

```
1. Quick start: WINDOWS_QUICK_REFERENCE.md
2. Usage guide: USER_GUIDE.md
3. If issues: WINDOWS_TROUBLESHOOTING_FLOWCHART.md
```

---

## Printable Resources

Recommended documents to print and keep at your desk:

1. **WINDOWS_QUICK_REFERENCE.md** (1-2 pages)
   - Daily commands
   - Common issues
   - Quick fixes

2. **WINDOWS_INSTALLATION_CHECKLIST.md** (3-4 pages)
   - For first-time installation
   - Track your progress
   - Note custom settings

---

## Windows-Specific Topics Covered

### Prerequisites
- ✅ Git installation for Windows
- ✅ Python installation with PATH setup
- ✅ Ollama installation and setup
- ✅ System requirements verification

### Installation
- ✅ Repository cloning with Windows paths
- ✅ Virtual environment creation and activation
- ✅ Dependency installation
- ✅ Configuration file setup

### Running Hunter
- ✅ Starting Ollama service
- ✅ Activating virtual environment
- ✅ Launching Hunter application
- ✅ Accessing in browser

### Common Issues
- ✅ Python not recognized errors
- ✅ Virtual environment activation issues
- ✅ PowerShell execution policy
- ✅ Port conflicts
- ✅ Ollama connection problems
- ✅ SSL certificate errors
- ✅ Module not found errors
- ✅ Firewall permissions

### Advanced Topics
- ✅ Desktop shortcuts for Windows
- ✅ Batch file creation
- ✅ Using PowerShell vs Command Prompt
- ✅ Windows Firewall configuration
- ✅ Environment variable setup
- ✅ Multiple Hunter installations

---

## Quick Command Reference

### Installation Commands (One-Time)
```cmd
# Navigate to installation location
cd C:\
mkdir Projects
cd Projects

# Clone repository
git clone [repository-url]
cd hunter

# Set up Python environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Download AI model
ollama pull llama3
```

### Daily Usage Commands
```cmd
# Start Hunter
cd C:\Projects\hunter
venv\Scripts\activate
python -m app.web

# Access Hunter
# Open browser to: http://localhost:51003

# Stop Hunter
# Press Ctrl+C in Command Prompt
# Type: deactivate
```

### Troubleshooting Commands
```cmd
# Check installations
python --version
git --version
ollama --version

# Check Ollama
ollama list
ollama run llama3 "test"

# Check dependencies
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Getting Help

### For Installation Issues
1. Check [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md) troubleshooting section
2. Use [WINDOWS_TROUBLESHOOTING_FLOWCHART.md](WINDOWS_TROUBLESHOOTING_FLOWCHART.md)
3. Verify [WINDOWS_INSTALLATION_CHECKLIST.md](WINDOWS_INSTALLATION_CHECKLIST.md)

### For Runtime Issues
1. Check [WINDOWS_QUICK_REFERENCE.md](WINDOWS_QUICK_REFERENCE.md) quick fixes
2. Use [WINDOWS_TROUBLESHOOTING_FLOWCHART.md](WINDOWS_TROUBLESHOOTING_FLOWCHART.md)
3. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### For Usage Questions
1. Read [USER_GUIDE.md](USER_GUIDE.md)
2. Check [QUICKSTART.md](QUICKSTART.md)
3. Review [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)

---

## Windows Version Compatibility

### Supported Windows Versions
- ✅ Windows 11 (all versions) - **Recommended**
- ✅ Windows 10 (64-bit, version 1809 or later) - **Supported**

### Unsupported Windows Versions
- ❌ Windows 10 (32-bit)
- ❌ Windows 8.1 or earlier
- ❌ Windows Server (not tested)

---

## Additional Resources

### General Documentation
- [README.md](README.md) - Main documentation index
- [WHAT_IS_HUNTER.md](WHAT_IS_HUNTER.md) - What Hunter does
- [USER_GUIDE.md](USER_GUIDE.md) - How to use Hunter
- [QUICKSTART.md](QUICKSTART.md) - 5-minute quick start

### Technical Documentation
- [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md) - Architecture details
- [API_REFERENCE.md](API_REFERENCE.md) - REST API documentation

---

## Windows Tips & Best Practices

### Installation Tips
- Install in short path (e.g., `C:\Projects\hunter`) to avoid path length issues
- Check "Add Python to PATH" during Python installation
- Use Command Prompt instead of PowerShell for fewer permission issues
- Disable antivirus temporarily during installation if needed

### Daily Usage Tips
- Create desktop shortcut using batch file
- Keep Command Prompt window open while using Hunter
- Bookmark http://localhost:51003 in browser
- Check system tray for Ollama icon before starting

### Performance Tips
- Close unnecessary applications to free RAM
- Use SSD for faster model loading
- Consider smaller model (mistral) if RAM limited
- Restart Ollama if responses slow

### Backup Tips
- Regularly backup `data/` folder
- Keep copy of `config/config.yaml`
- Document any custom configurations
- Note which AI model you're using

---

**Last Updated**: December 10, 2025  
**Hunter Version**: 2.0.0+  
**Maintained By**: Hunter Documentation Team

---

## Document Change Log

| Date | Change | Documents Affected |
|------|--------|-------------------|
| 2025-12-10 | Created Windows resources | All Windows docs |
| 2025-12-10 | Added troubleshooting flowchart | WINDOWS_TROUBLESHOOTING_FLOWCHART.md |
| 2025-12-10 | Created installation checklist | WINDOWS_INSTALLATION_CHECKLIST.md |
| 2025-12-10 | Created quick reference | WINDOWS_QUICK_REFERENCE.md |

---

**Bookmark this page for easy access to all Windows documentation!**
