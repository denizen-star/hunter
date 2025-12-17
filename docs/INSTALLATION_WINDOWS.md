# Hunter Installation Guide for Windows

Complete step-by-step guide to install and run Hunter on Windows 10/11.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: Install Python](#step-1-install-python)
- [Step 2: Install Git](#step-2-install-git)
- [Step 3: Install Ollama](#step-3-install-ollama)
- [Step 4: Clone Hunter Repository](#step-4-clone-hunter-repository)
- [Step 5: Fix Hardcoded Paths](#step-5-fix-hardcoded-paths)
- [Step 6: Set Up Python Environment](#step-6-set-up-python-environment)
- [Step 7: Initialize Data Structure](#step-7-initialize-data-structure)
- [Step 8: Run Hunter](#step-8-run-hunter)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **OS**: Windows 10 (64-bit) or Windows 11
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: ~10GB free
- **Internet**: Required for setup
- **Administrator Access**: Required

---

## Step 1: Install Python

Hunter requires Python 3.11 or higher.

### Download and Install

1. Go to: **https://www.python.org/downloads/windows/**
2. Download Python 3.11+ installer
3. Run the installer

**CRITICAL**: Check both boxes:
- ✅ **"Add python.exe to PATH"**
- ✅ **"Install launcher for all users"**

4. Click **"Install Now"**
5. Wait for completion, click **"Close"**

### Disable Windows Python Aliases

Windows 11 includes Python shortcuts that interfere with the real installation:

1. Press `Win + I` → **Apps** → **Advanced app settings** → **App execution aliases**
2. Find **python.exe** and **python3.exe**
3. Turn **both OFF**

### Verify Installation

Open a **new** Command Prompt:
```cmd
python --version
pip --version
```

Expected output:
```
Python 3.11.x
pip 24.x.x from ...
```

**If "python is not recognized"**: See [Troubleshooting](#python-not-recognized).

---

## Step 2: Install Git

1. Go to: **https://git-scm.com/download/win**
2. Download and run installer
3. Accept defaults, click **"Install"**

Verify:
```cmd
git --version
```

---

## Step 3: Install Ollama

1. Go to: **https://ollama.com/download/windows**
2. Download and run **OllamaSetup.exe**
3. Click **"Install"**
4. Verify Ollama icon appears in system tray

### Download AI Model

```cmd
ollama pull llama3
```

This downloads ~4.7GB (10-30 minutes depending on connection).

Test:
```cmd
ollama run llama3 "Hello"
```

Press `Ctrl+D` or type `/bye` to exit.

---

## Step 4: Clone Hunter Repository

Choose installation location. Example: `C:\Projects\hunter`

```cmd
cd C:\
mkdir Projects
cd Projects
git clone https://github.com/YOUR_USERNAME/hunter.git
cd hunter
```

Replace `YOUR_USERNAME/hunter` with actual repository URL.

---

## Step 5: Fix Hardcoded Paths

**CRITICAL STEP**: Hunter source code contains hardcoded paths that must be fixed.

Create file `fix_all_paths.py` in Hunter directory with this content:

```python
"""Fix all hardcoded paths in Hunter"""
import re
from pathlib import Path

files_to_fix = [
    'app/services/preliminary_matcher.py',
    'fix_research_and_intros.py',
    'interactive_research_fix.py',
    'regenerate_research.py',
    'migrate_existing_applications.py',
    'process_insight_global.py',
    'process_next_application.py',
    'regenerate_bestbuy.py',
    'resume_research_fix.py',
    'simple_migration.py',
    'update_bestbuy_html.py'
]

for file_path in files_to_fix:
    file_path = Path(file_path)
    if not file_path.exists():
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace absolute paths with relative paths
    content = re.sub(r'/Users/[^/]+/Documents/Development/hunter/', '', content)
    content = re.sub(r'Path\(["\']\/Users\/[^/]+\/Documents\/Development\/hunter\/', 'Path("', content)
    content = re.sub(r"sys\.path\.(append|insert)\([^,]*,\s*['\"]\/Users\/[^/]+\/Documents\/Development\/hunter['\"]", 
                     r"# sys.path.\1 not needed", content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Fixed {file_path}")

print("\n✅ All paths fixed")
```

Run:
```cmd
python fix_all_paths.py
```

Since these file path clean up scripts are only needed once at set up
Optional cleanup: You can delete fix_all_paths.py and fix_paths.py from the repository since they're just one-time fix scripts:
``` 
powershellgit rm fix_all_paths.py fix_paths.py
git commit -m "Remove temporary fix scripts"
git push

```

---

## Step 6: Set Up Python Environment

### Create Virtual Environment

```cmd
cd C:\Projects\hunter
python -m venv venv
```

### Activate Virtual Environment

```cmd
venv\Scripts\activate
```

Your prompt should show `(venv)`.

### Install Dependencies

Run as **Administrator** if you get permission errors:

```cmd
pip install -r requirements.txt
```

Verify:
```cmd
pip list
```

Should show Flask, ollama, pyyaml, jinja2, etc.

---

## Step 7: Initialize Data Structure

**CRITICAL STEP**: Create required data files populated with your CV information.

Create file `setup_data.py` in Hunter directory:

```python
"""Initialize Hunter data structure with your CV information"""
import os
import yaml
from pathlib import Path

# Create directories
for directory in ['data', 'data/resumes', 'data/applications', 'data/templates', 'data/analytics']:
    Path(directory).mkdir(parents=True, exist_ok=True)

# Create skills.yaml - CUSTOMIZE WITH YOUR SKILLS
skills_data = {
    'technical_skills': [
        # Add your technical skills here
        'Python', 'R', 'SQL', 'Machine Learning', 'Data Visualization'
    ],
    'soft_skills': [
        # Add your soft skills here
        'Leadership', 'Communication', 'Problem Solving'
    ],
    'tools_and_platforms': [
        # Add your tools here
        'Git', 'Docker', 'AWS', 'Power BI'
    ],
    'certifications': [
        # Add your certifications here
    ]
}

with open('data/resumes/skills.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(skills_data, f, default_flow_style=False, allow_unicode=True)

# Create resume.yaml - CUSTOMIZE WITH YOUR INFO
resume_data = {
    'personal_info': {
        'name': 'Your Name',  # CHANGE THIS
        'email': 'your.email@example.com',  # CHANGE THIS
        'phone': '',
        'location': '',
        'linkedin': '',
        'github': ''
    },
    'summary': 'Your professional summary here',  # CHANGE THIS
    'experience': [],
    'education': [],
    'projects': []
}

with open('data/resumes/resume.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(resume_data, f, default_flow_style=False, allow_unicode=True)

print("✓ Created data/resumes/skills.yaml")
print("✓ Created data/resumes/resume.yaml")
print("\n⚠️  IMPORTANT: Edit these files with your actual CV information before running Hunter")
print("   - data/resumes/skills.yaml")
print("   - data/resumes/resume.yaml")
```

Run:
```cmd
python setup_data.py
```

**REQUIRED**: Edit the created files with your actual CV information:
- `data/resumes/skills.yaml`
- `data/resumes/resume.yaml`

---

## Step 8: Run Hunter

### Start Ollama

Check system tray for Ollama icon. If not running:
```cmd
ollama serve
```
Keep this window open.

### Start Hunter

In a **new** Command Prompt:
```cmd
cd C:\Projects\hunter
venv\Scripts\activate
python -m app.web
```

Expected output:
```
🚀 Starting Job Hunter Application...
✅ Ollama is connected
* Running on http://127.0.0.1:51003
```

### Access Application

Open browser: **http://localhost:51003**

---

## Troubleshooting

### Python Not Recognized

**Problem**: `'python' is not recognized`

**Solution**:
1. Press `Win + X` → **System** → **Advanced system settings** → **Environment Variables**
2. Under "User variables", select **Path** → **Edit**
3. Add (replace `YourUsername`):
   - `C:\Users\YourUsername\AppData\Local\Programs\Python\Python314\`
   - `C:\Users\YourUsername\AppData\Local\Programs\Python\Python314\Scripts\`
4. Click **OK** on all windows
5. Open **new** Command Prompt
6. Test: `python --version`

### FileNotFoundError: skills.yaml

**Problem**: `FileNotFoundError: data/resumes/skills.yaml`

**Solution**:
1. Run the setup script: `python setup_data.py`
2. Edit `data/resumes/skills.yaml` with your skills
3. Edit `data/resumes/resume.yaml` with your information

### Pip Install Permission Denied

**Problem**: `Access is denied` during pip install

**Solution**:
1. Close Command Prompt
2. Right-click Command Prompt → **Run as administrator**
3. Navigate to Hunter directory
4. Activate venv: `venv\Scripts\activate`
5. Run: `pip install -r requirements.txt`

### Ollama Already Running Error

**Problem**: `bind: Only one usage of each socket address`

**Solution**: Ollama is already running (this is good). Skip `ollama serve` and proceed to run Hunter.

### Port 51003 Already in Use

**Solution**: Find and stop the process:
```cmd
netstat -ano | findstr :51003
taskkill /PID [number] /F
```

---

## Quick Start (After Initial Setup)

1. Open Command Prompt
2. Check Ollama is running (system tray icon)
3. Run:
   ```cmd
   cd C:\Projects\hunter
   venv\Scripts\activate
   python -m app.web
   ```
4. Open browser: http://localhost:51003

### Stop Hunter

Press `Ctrl + C` in Command Prompt
Type `deactivate` to exit virtual environment

---

## Important Notes

1. **Paths**: Never use absolute paths. All paths in code must be relative to Hunter directory.
2. **Data Files**: Always customize `skills.yaml` and `resume.yaml` with actual CV data before first run.
3. **Administrator**: Run Command Prompt as administrator if you encounter permission issues.
4. **Python Aliases**: Disable Windows app execution aliases for Python to avoid conflicts.
5. **New Terminal**: Always open a new Command Prompt after modifying PATH or environment variables.

---

**Installation complete!** Hunter is now ready to use for managing job applications with AI-powered assistance.
