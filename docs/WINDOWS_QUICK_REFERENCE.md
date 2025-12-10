# Hunter Windows Quick Reference

Quick reference card for running Hunter on Windows.

## Daily Startup Commands

```cmd
# 1. Open Command Prompt
Win + R → type "cmd" → Enter

# 2. Navigate to Hunter
cd C:\Projects\hunter

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Start Hunter
python -m app.web

# 5. Open browser
http://localhost:51003
```

## Stop Hunter

```cmd
# In Command Prompt window running Hunter
Ctrl + C

# Deactivate virtual environment
deactivate
```

## Check Ollama Status

```cmd
# List installed models
ollama list

# Test Ollama
ollama run llama3 "test"

# Check if Ollama is running
# Look for Ollama icon in system tray (bottom-right)
```

## Common Issues & Quick Fixes

### Ollama Not Running
```cmd
# Start Ollama
Start Menu → type "Ollama" → click Ollama

# Or from Command Prompt
ollama serve
```

### Port Already in Use
```cmd
# Use different port
set PORT=51004
python -m app.web
# Then use: http://localhost:51004
```

### Virtual Environment Won't Activate
```powershell
# Open PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found
```cmd
# Add Python to PATH (one-time fix):
# Win + R → sysdm.cpl → Advanced → Environment Variables
# Edit "Path" → Add:
#   C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\
#   C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\Scripts\
```

### Reinstall Dependencies
```cmd
cd C:\Projects\hunter
venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

## Update Hunter

```cmd
cd C:\Projects\hunter
git pull origin main
venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

## Useful URLs

- **Main App**: http://localhost:51003
- **Dashboard**: http://localhost:51003/dashboard
- **Analytics**: http://localhost:51003/analytics

## File Locations

```
C:\Projects\hunter\              # Main directory
├── data\
│   ├── applications\            # Your applications
│   ├── resumes\                 # Resume files
│   └── covers\                  # Generated cover letters
├── config\
│   └── config.yaml              # Settings
└── docs\                        # Documentation
```

## Backup Your Data

```cmd
# Create backup folder
mkdir C:\Hunter-Backup-%date%

# Copy data folder
xcopy C:\Projects\hunter\data C:\Hunter-Backup-%date%\data /E /I /H
```

## Environment Variables (Optional)

Set these to customize Hunter:

```cmd
# Change port
set PORT=51004

# Set timezone
set TZ=America/New_York
```

## Desktop Shortcut Script

Create `start_hunter.bat` on your desktop:

```batch
@echo off
echo Starting Hunter...
cd C:\Projects\hunter
call venv\Scripts\activate
start http://localhost:51003
python -m app.web
pause
```

## Keyboard Shortcuts

While Hunter is running:
- `Ctrl + C` - Stop the server
- `Ctrl + Shift + R` - Hard refresh browser (clear cache)
- `F12` - Open browser developer tools (for debugging)

## Model Management

```cmd
# List installed models
ollama list

# Pull new model
ollama pull mistral

# Remove model
ollama rm llama3

# Switch model in config/config.yaml:
# Change line: model: "llama3" to model: "mistral"
```

## Performance Tips

1. **Close unused applications** to free RAM
2. **Use SSD** for faster model loading
3. **Restart Ollama** if responses are slow
4. **Use smaller model** (mistral instead of llama3) if low on RAM

## Getting Help

- **Documentation**: `C:\Projects\hunter\docs\`
- **Full Installation Guide**: `docs\INSTALLATION_WINDOWS.md`
- **User Guide**: `docs\USER_GUIDE.md`
- **Troubleshooting**: `docs\TROUBLESHOOTING.md`

---

**Print this page and keep it handy for quick reference!**
