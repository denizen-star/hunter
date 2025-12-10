# Hunter Installation Guide for Windows

Complete step-by-step guide to install and run Hunter on Windows 10/11.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: Install Git](#step-1-install-git)
- [Step 2: Install Python](#step-2-install-python)
- [Step 3: Install Ollama](#step-3-install-ollama)
- [Step 4: Clone Hunter Repository](#step-4-clone-hunter-repository)
- [Step 5: Set Up Python Environment](#step-5-set-up-python-environment)
- [Step 6: Start Ollama Service](#step-6-start-ollama-service)
- [Step 7: Run Hunter](#step-7-run-hunter)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Prerequisites

Before you begin, ensure your Windows PC meets these requirements:

- **Operating System**: Windows 10 (64-bit) or Windows 11
- **RAM**: 8GB minimum (16GB recommended for better performance)
- **Disk Space**: ~10GB free space (5GB for AI models + 5GB for application and dependencies)
- **Internet Connection**: Required for initial setup and downloads
- **Administrator Access**: Needed for software installation

---

## Step 1: Install Git

Git allows you to download and manage the Hunter source code.

### Download Git for Windows

1. Open your web browser and go to: **https://git-scm.com/download/win**
2. The download should start automatically. If not, click **"Click here to download manually"**
3. Run the downloaded installer (`Git-2.x.x-64-bit.exe`)

### Installation Steps

1. Click **"Next"** through the welcome screens
2. **Select Components**: Keep default selections (Git Bash, Git GUI, etc.)
3. **Choose Default Editor**: Select your preferred editor or keep "Vim"
4. **Adjust PATH Environment**: Select **"Git from the command line and also from 3rd-party software"**
5. **Choose HTTPS Backend**: Select **"Use the OpenSSL library"**
6. **Configure Line Ending**: Select **"Checkout Windows-style, commit Unix-style"**
7. **Terminal Emulator**: Select **"Use MinTTY"**
8. Click **"Install"**
9. Click **"Finish"** when installation completes

### Verify Git Installation

1. Press `Win + R` to open Run dialog
2. Type `cmd` and press Enter
3. In the Command Prompt, type:
   ```cmd
   git --version
   ```
4. You should see output like: `git version 2.43.0.windows.1`

---

## Step 2: Install Python

Hunter requires Python 3.11 or higher.

### Download Python

1. Go to: **https://www.python.org/downloads/windows/**
2. Click on **"Download Python 3.11.x"** (or latest 3.11+ version)
3. Run the downloaded installer (`python-3.11.x-amd64.exe`)

### Installation Steps

**IMPORTANT**: Follow these steps carefully!

1. **Check both boxes at the bottom**:
   - ✅ **"Add python.exe to PATH"** (CRITICAL - don't skip this!)
   - ✅ "Install launcher for all users"

2. Click **"Install Now"**

3. Wait for installation to complete

4. Click **"Close"** when finished

### Verify Python Installation

1. Open a **NEW** Command Prompt (close old ones first)
2. Type:
   ```cmd
   python --version
   ```
3. You should see: `Python 3.11.x`

4. Also verify pip (Python package manager):
   ```cmd
   pip --version
   ```
5. You should see: `pip 24.x.x from ...`

**Troubleshooting**: If you get `'python' is not recognized`, the PATH wasn't set correctly. See [Troubleshooting](#troubleshooting) section.

---

## Step 3: Install Ollama

Ollama is the local AI engine that powers Hunter's intelligent features.

### Download Ollama

1. Open your browser and go to: **https://ollama.com/download/windows**
2. Click **"Download for Windows"**
3. Run the downloaded installer (`OllamaSetup.exe`)

### Installation Steps

1. Click **"Install"**
2. Wait for installation to complete (may take 2-3 minutes)
3. Ollama will automatically start after installation
4. You'll see an Ollama icon in your system tray (bottom-right corner)

### Download the AI Model

Hunter needs an AI model to function. We'll use Llama 3 (recommended).

1. Open Command Prompt (`Win + R`, type `cmd`, press Enter)
2. Run the following command:
   ```cmd
   ollama pull llama3
   ```
3. **This will download approximately 4.7GB** - it may take 10-30 minutes depending on your internet speed
4. Wait for the download to complete

### Verify Ollama Installation

In Command Prompt, test the AI model:
```cmd
ollama run llama3 "Hello, what is 2+2?"
```

You should get an AI-generated response. Press `Ctrl+D` or type `/bye` to exit.

---

## Step 4: Clone Hunter Repository

Now we'll download the Hunter source code from GitHub.

### Choose Installation Location

Decide where to install Hunter. Common choices:
- `C:\Users\YourUsername\Documents\Projects\hunter`
- `C:\Projects\hunter`
- `C:\Dev\hunter`

For this guide, we'll use `C:\Projects\hunter`

### Clone the Repository

1. Open Command Prompt
2. Navigate to where you want to install Hunter:
   ```cmd
   cd C:\
   mkdir Projects
   cd Projects
   ```

3. Clone the Hunter repository:
   ```cmd
   git clone https://github.com/YOUR_USERNAME/hunter.git
   ```
   **Note**: Replace `YOUR_USERNAME/hunter` with the actual repository URL provided to you.

4. Navigate into the hunter directory:
   ```cmd
   cd hunter
   ```

5. Verify the files downloaded:
   ```cmd
   dir
   ```
   You should see folders like `app`, `config`, `data`, `docs`, etc.

---

## Step 5: Set Up Python Environment

### Create Virtual Environment

A virtual environment keeps Hunter's dependencies separate from other Python projects.

1. Make sure you're in the hunter directory:
   ```cmd
   cd C:\Projects\hunter
   ```

2. Create a virtual environment named `venv`:
   ```cmd
   python -m venv venv
   ```

3. Wait for creation to complete (30-60 seconds)

### Activate Virtual Environment

Every time you want to run Hunter, you'll need to activate this environment first.

```cmd
venv\Scripts\activate
```

Your prompt should change to show `(venv)` at the beginning:
```
(venv) C:\Projects\hunter>
```

### Install Required Python Packages

With the virtual environment activated, install Hunter's dependencies:

```cmd
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Ollama client library
- YAML, Jinja2, and other utilities

Installation takes 1-2 minutes. You should see "Successfully installed..." messages.

### Verify Installation

Check that packages installed correctly:
```cmd
pip list
```

You should see packages like: Flask, ollama, pyyaml, jinja2, etc.

---

## Step 6: Start Ollama Service

Ollama needs to be running for Hunter's AI features to work.

### Check if Ollama is Running

1. Look for the Ollama icon in your system tray (bottom-right of screen, near the clock)
2. If you see it, Ollama is already running!

### Start Ollama Manually (if needed)

If Ollama isn't running:

**Option 1: Start from Start Menu**
1. Press the Windows key
2. Type "Ollama"
3. Click on "Ollama" to start it

**Option 2: Start from Command Prompt**
1. Open a **NEW** Command Prompt window (don't close your existing one!)
2. Run:
   ```cmd
   ollama serve
   ```
3. Keep this window open - Ollama needs to keep running
4. You should see: `Listening on 127.0.0.1:11434`

---

## Step 7: Run Hunter

Now you're ready to launch Hunter!

### Start the Application

1. Go back to your Command Prompt with the virtual environment activated (shows `(venv)`)
2. Make sure you're in the hunter directory:
   ```cmd
   cd C:\Projects\hunter
   ```

3. Start Hunter:
   ```cmd
   python -m app.web
   ```

4. You should see output like:
   ```
   🚀 Starting Job Hunter Application...
   📱 Open http://localhost:51003 in your browser
   ✅ Ollama is connected
   📦 Available models: llama3:latest
   * Running on all addresses (0.0.0.0)
   * Running on http://127.0.0.1:51003
   * Running on http://192.168.1.x:51003
   ```

### Access Hunter in Your Browser

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to: **http://localhost:51003**
3. You should see the Hunter web interface!

### Main Features to Explore

- **Home Page**: Create new job applications
- **Dashboard**: View all your applications at `http://localhost:51003/dashboard`
- **Resume Manager**: Set up your resume
- **Analytics**: Track your job search progress

---

## Running Hunter in the Future

Every time you want to use Hunter, follow these quick steps:

### Quick Start Procedure

1. **Ensure Ollama is running** (check system tray icon)

2. **Open Command Prompt**

3. **Navigate to Hunter directory**:
   ```cmd
   cd C:\Projects\hunter
   ```

4. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```

5. **Start Hunter**:
   ```cmd
   python -m app.web
   ```

6. **Open browser**: http://localhost:51003

### Stopping Hunter

- In the Command Prompt window running Hunter, press `Ctrl + C`
- Type `deactivate` to exit the virtual environment
- Close the Command Prompt

---

## Troubleshooting

### Python Not Recognized

**Problem**: When you type `python`, you get: `'python' is not recognized as an internal or external command`

**Solution**:
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click **"Advanced"** tab → **"Environment Variables"**
3. Under **"System variables"**, find **"Path"**, click **"Edit"**
4. Click **"New"** and add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\`
5. Click **"New"** again and add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\Scripts\`
6. Click **"OK"** on all windows
7. **Close and reopen** Command Prompt
8. Try `python --version` again

### Ollama Not Connecting

**Problem**: Hunter says "Ollama is not running" or can't connect

**Solution 1: Check Ollama Status**
1. Look for Ollama icon in system tray
2. If missing, start Ollama from Start menu

**Solution 2: Restart Ollama**
1. Right-click Ollama icon in system tray
2. Click "Quit Ollama"
3. Start Ollama again from Start menu

**Solution 3: Test Ollama**
```cmd
ollama list
```
This should show installed models (llama3). If error occurs, reinstall Ollama.

### Port Already in Use

**Problem**: Error says port 51003 is already in use

**Solution 1: Find and Stop Process**
1. Open Command Prompt as Administrator
2. Run:
   ```cmd
   netstat -ano | findstr :51003
   ```
3. Note the PID (last number)
4. Run:
   ```cmd
   taskkill /PID [number] /F
   ```

**Solution 2: Use Different Port**
1. Set environment variable:
   ```cmd
   set PORT=51004
   ```
2. Start Hunter again:
   ```cmd
   python -m app.web
   ```
3. Use: http://localhost:51004

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

**Causes & Solutions**:
1. **Insufficient RAM**: Close other applications to free memory
2. **Wrong Model**: Try a smaller model:
   ```cmd
   ollama pull mistral
   ```
   Then edit `config/config.yaml` and change `model: "llama3"` to `model: "mistral"`
3. **Ollama Issues**: Restart Ollama service

### Git Clone Fails

**Problem**: Authentication error when cloning repository

**Solution 1: Using HTTPS**
- The repository might be private
- Contact the repository owner for access

**Solution 2: Using SSH**
1. Set up SSH key with GitHub
2. Use SSH clone URL instead:
   ```cmd
   git clone git@github.com:username/hunter.git
   ```

---

## Uninstallation

To completely remove Hunter from your system:

### 1. Stop Hunter
- Press `Ctrl + C` in the Command Prompt running Hunter
- Type `deactivate` and press Enter

### 2. Delete Hunter Directory
1. Open File Explorer
2. Navigate to `C:\Projects\hunter` (or wherever you installed it)
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

## System Requirements Summary

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
- **Disk**: 20GB free space (SSD preferred for faster AI model loading)
- **Internet**: Broadband for faster model downloads

---

## Additional Resources

- **User Guide**: See `docs/USER_GUIDE.md` for how to use Hunter
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md` for more solutions
- **Quick Start**: See `docs/QUICKSTART.md` for a faster setup overview
- **Technical Details**: See `docs/TECHNICAL_REFERENCE.md` for architecture info

---

## Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs**: The Command Prompt window shows error messages
2. **Review documentation**: Check the `docs/` folder
3. **Verify each step**: Make sure you completed all steps in order
4. **System requirements**: Ensure your PC meets minimum requirements
5. **Windows updates**: Make sure Windows is up to date

---

## Tips for Windows Users

### Using PowerShell Instead of Command Prompt

If you prefer PowerShell:

1. All `cmd` commands work the same
2. Virtual environment activation is:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

### Creating a Desktop Shortcut

To quickly launch Hunter:

1. Create a new text file called `start_hunter.bat`
2. Add these lines:
   ```batch
   @echo off
   cd C:\Projects\hunter
   call venv\Scripts\activate
   echo Starting Hunter...
   python -m app.web
   pause
   ```
3. Save and double-click to run Hunter

### Firewall Warning

First time running Hunter, Windows Firewall may ask for permission. Click **"Allow access"** to let Hunter run its web server.

---

**Installation complete!** You're now ready to use Hunter to manage your job applications with AI-powered assistance.

For next steps, see the [User Guide](USER_GUIDE.md) to learn how to:
- Set up your resume
- Create your first application
- Generate tailored cover letters
- Track application status
- View analytics

Happy job hunting!
