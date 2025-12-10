# Windows Troubleshooting Flowchart

Use this decision tree to diagnose and fix common Windows installation and runtime issues.

---

## Problem: "I can't install/run Hunter"

### START HERE: What stage are you at?

```
┌─────────────────────────────────────────────┐
│ What problem are you experiencing?          │
└─────────────────────────────────────────────┘
          │
          ├─→ [A] Installing prerequisites
          ├─→ [B] Cloning repository
          ├─→ [C] Setting up virtual environment
          ├─→ [D] Installing dependencies
          ├─→ [E] Running Hunter
          └─→ [F] Accessing Hunter in browser
```

---

## [A] Installing Prerequisites

### Python not recognized

```
ERROR: 'python' is not recognized as an internal or external command
│
├─→ Did you check "Add python.exe to PATH" during installation?
│   │
│   ├─→ NO: Reinstall Python, check the box this time
│   │
│   └─→ YES: Add to PATH manually
│       │
│       └─→ Win + R → sysdm.cpl → Advanced → Environment Variables
│           Edit "Path" → Add:
│           C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python311\
│           C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python311\Scripts\
│           Close and reopen Command Prompt
```

### Git not recognized

```
ERROR: 'git' is not recognized as an internal or external command
│
└─→ Reinstall Git from https://git-scm.com/download/win
    Select "Git from the command line and also from 3rd-party software"
```

### Ollama not installing

```
ERROR: Ollama installer fails or won't run
│
├─→ Windows version too old?
│   └─→ Requires Windows 10 64-bit or Windows 11
│
├─→ Antivirus blocking?
│   └─→ Temporarily disable antivirus, run installer
│
└─→ Downloaded incomplete file?
    └─→ Re-download from https://ollama.com/download/windows
```

---

## [B] Cloning Repository

### Git clone fails - Authentication error

```
ERROR: Authentication failed
│
├─→ Repository is private
│   └─→ Contact repository owner for access
│
├─→ Using wrong URL?
│   └─→ Verify URL with repository owner
│
└─→ Need credentials?
    └─→ Use: git config --global credential.helper wincred
```

### Git clone fails - Network error

```
ERROR: Failed to connect to github.com
│
├─→ Behind corporate firewall?
│   └─→ Configure proxy: git config --global http.proxy http://proxy.company.com:8080
│
├─→ No internet connection?
│   └─→ Check network connection
│
└─→ GitHub down?
    └─→ Check https://www.githubstatus.com/
```

---

## [C] Setting Up Virtual Environment

### Virtual environment creation fails

```
ERROR: Error creating virtual environment
│
├─→ Insufficient disk space?
│   └─→ Free up at least 2GB disk space
│
├─→ Python not installed correctly?
│   └─→ Verify: python --version
│       If fails, reinstall Python
│
└─→ Path too long?
    └─→ Install in shorter path: C:\Projects\hunter
```

### Virtual environment won't activate

```
ERROR: venv\Scripts\activate cannot be loaded because running scripts is disabled
│
└─→ Execution policy issue
    │
    ├─→ Solution 1: Use PowerShell as Administrator
    │   │
    │   └─→ Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    │
    └─→ Solution 2: Use Command Prompt instead
        │
        └─→ venv\Scripts\activate.bat
```

---

## [D] Installing Dependencies

### pip install fails - General error

```
ERROR: Could not install packages due to an EnvironmentError
│
├─→ Virtual environment not activated?
│   └─→ Look for (venv) in prompt
│       If missing: venv\Scripts\activate
│
├─→ Insufficient permissions?
│   └─→ Run Command Prompt as Administrator
│
└─→ Corrupted download?
    └─→ Clear pip cache:
        pip cache purge
        pip install -r requirements.txt --force-reinstall
```

### pip install fails - Specific package

```
ERROR: Could not find a version that satisfies the requirement
│
├─→ Python version too old?
│   └─→ Check: python --version
│       Requires Python 3.11+
│
├─→ Typo in requirements.txt?
│   └─→ Verify requirements.txt is unmodified
│
└─→ Network issue?
    └─→ Try: pip install --upgrade pip
        Then: pip install -r requirements.txt
```

### SSL certificate error

```
ERROR: SSL: CERTIFICATE_VERIFY_FAILED
│
├─→ Corporate SSL inspection?
│   └─→ pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
│
└─→ Antivirus interference?
    └─→ Temporarily disable SSL inspection in antivirus
```

---

## [E] Running Hunter

### Ollama not running

```
ERROR: Could not connect to Ollama at http://localhost:11434
│
├─→ Check system tray for Ollama icon
│   │
│   ├─→ Icon present?
│   │   └─→ Restart Ollama:
│   │       Right-click icon → Quit
│   │       Start Menu → Ollama
│   │
│   └─→ Icon missing?
│       └─→ Start Menu → Ollama
│           If not found: Reinstall Ollama
│
└─→ Test Ollama:
    ollama list
    If error: Reinstall Ollama
```

### Ollama model not found

```
ERROR: Model 'llama3' not found
│
└─→ Pull model:
    ollama pull llama3
    
    Wait for download (~4.7GB, 10-30 minutes)
```

### Port already in use

```
ERROR: Address already in use - Port 51003
│
├─→ Find process using port:
│   netstat -ano | findstr :51003
│   │
│   └─→ Kill process:
│       taskkill /PID [number] /F
│
└─→ Or use different port:
    set PORT=51004
    python -m app.web
```

### Module not found error

```
ERROR: ModuleNotFoundError: No module named 'flask' (or other module)
│
├─→ Virtual environment not activated?
│   └─→ Activate: venv\Scripts\activate
│       Look for (venv) in prompt
│
└─→ Dependencies not installed?
    └─→ pip install -r requirements.txt
```

### Python path issues

```
ERROR: No module named 'app'
│
└─→ Wrong directory?
    │
    ├─→ Check current directory:
    │   cd
    │   Should be in: C:\Projects\hunter (or your path)
    │
    └─→ Navigate to hunter directory:
        cd C:\Projects\hunter
```

---

## [F] Accessing Hunter in Browser

### Page won't load - Connection refused

```
ERROR: This site can't be reached / Connection refused
│
├─→ Hunter not running?
│   └─→ Check Command Prompt window
│       Should show "Running on http://127.0.0.1:51003"
│       If not: python -m app.web
│
├─→ Wrong URL?
│   └─→ Use: http://localhost:51003
│       NOT: https://localhost:51003
│
└─→ Firewall blocking?
    └─→ Windows Firewall popup?
        Click "Allow access"
```

### Page loads but shows errors

```
ERROR: Page shows "500 Internal Server Error" or errors
│
├─→ Check Command Prompt for error messages
│   │
│   ├─→ Ollama connection error?
│   │   └─→ Start Ollama service
│   │
│   ├─→ File not found error?
│   │   └─→ Create missing directories:
│   │       mkdir data\applications
│   │       mkdir data\resumes
│   │       mkdir data\covers
│   │
│   └─→ Configuration error?
│       └─→ Check config\config.yaml exists
│           If missing, restore from backup or git
│
└─→ Browser cache issue?
    └─→ Hard refresh: Ctrl + Shift + R
```

### Slow performance

```
ISSUE: Hunter is extremely slow
│
├─→ Insufficient RAM?
│   └─→ Close other applications
│       Check Task Manager (Ctrl+Shift+Esc)
│       Ollama needs 4-8GB RAM
│
├─→ Large model running?
│   └─→ Switch to smaller model:
│       ollama pull mistral
│       Edit config\config.yaml:
│       model: "mistral"
│
└─→ Ollama not responding?
    └─→ Restart Ollama service:
        System tray → Right-click Ollama → Quit
        Start Menu → Ollama
```

---

## Common Error Messages Reference

### "SSL: CERTIFICATE_VERIFY_FAILED"
**Cause**: Corporate proxy or antivirus SSL inspection  
**Fix**: Use `--trusted-host` flag with pip

### "Script execution disabled"
**Cause**: PowerShell execution policy  
**Fix**: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

### "python is not recognized"
**Cause**: Python not in PATH  
**Fix**: Add Python to PATH or reinstall with PATH checkbox

### "Port 51003 is in use"
**Cause**: Hunter or another app using the port  
**Fix**: Kill process or use different port

### "Could not connect to Ollama"
**Cause**: Ollama service not running  
**Fix**: Start Ollama from Start Menu

### "Model not found"
**Cause**: AI model not downloaded  
**Fix**: `ollama pull llama3`

### "No module named"
**Cause**: Dependencies not installed or venv not activated  
**Fix**: Activate venv and run `pip install -r requirements.txt`

---

## Still Having Issues?

### Checklist
- [ ] Windows 10 64-bit or Windows 11?
- [ ] At least 8GB RAM free?
- [ ] At least 10GB disk space free?
- [ ] Python 3.11+ installed with PATH?
- [ ] Git installed?
- [ ] Ollama installed and running (icon in system tray)?
- [ ] Model downloaded (`ollama list` shows llama3)?
- [ ] Virtual environment activated (shows `(venv)`)?
- [ ] Dependencies installed (`pip list` shows flask, ollama, etc.)?
- [ ] In correct directory (`cd` shows hunter path)?

### Advanced Diagnostics

1. **Verify each component individually**:
   ```cmd
   python --version          # Should show 3.11+
   git --version            # Should show git version
   ollama --version         # Should show ollama version
   ollama list              # Should show llama3
   pip list                 # Should show flask, ollama, etc.
   ```

2. **Test Ollama separately**:
   ```cmd
   ollama run llama3 "test"
   # Should get AI response
   ```

3. **Check all paths**:
   ```cmd
   where python             # Find Python location
   where git                # Find Git location
   where ollama             # Find Ollama location
   ```

4. **Review logs**:
   - Command Prompt output shows error messages
   - Browser console (F12) shows JavaScript errors
   - Check Windows Event Viewer for system errors

### Clean Reinstall

If all else fails, perform a clean reinstall:

1. Stop Hunter (`Ctrl+C`)
2. Deactivate virtual environment (`deactivate`)
3. Delete hunter directory
4. Uninstall Ollama (remove `C:\Users\[YourUsername]\.ollama`)
5. Uninstall Python
6. Restart computer
7. Follow installation guide from the beginning

---

## Quick Fix Summary

| Problem | Quick Fix |
|---------|-----------|
| Python not found | Add to PATH or reinstall |
| Script execution disabled | `Set-ExecutionPolicy RemoteSigned` |
| Ollama not connecting | Check system tray, restart Ollama |
| Port in use | `taskkill /PID [number] /F` |
| Module not found | Activate venv, `pip install -r requirements.txt` |
| Page won't load | Check Hunter is running, use http:// not https:// |
| Slow performance | Close apps, use smaller model (mistral) |
| SSL errors | Use `pip install --trusted-host` |

---

**Remember**: Most issues are solved by:
1. Making sure Ollama is running (system tray icon)
2. Activating the virtual environment (look for `(venv)`)
3. Being in the correct directory (`cd C:\Projects\hunter`)
4. Reading error messages carefully

**Still stuck?** Check the full [Windows Installation Guide](INSTALLATION_WINDOWS.md) for detailed explanations.
