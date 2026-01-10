# Troubleshooting Guide

Solutions to common issues you might encounter with Job Hunter.

## Quick Diagnostics

Run these commands to check system status:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if Job Hunter is running
curl http://localhost:51003/api/check-ollama

# Check if resume exists
ls -la data/resumes/base_resume.md
```

---

## Common Issues

### 1. Ollama Not Connected

**Symptoms:**
- ⚠️ "Ollama is not connected" warning
- Error: "Cannot connect to Ollama"
- Applications fail to create

**Solutions:**

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

If it fails, start Ollama:
```bash
ollama serve
```

**Check if model is downloaded:**
```bash
ollama list
```

If llama3 is not listed:
```bash
ollama pull llama3
```

**Kill and restart Ollama:**
```bash
pkill ollama
ollama serve
```

---

### 2. Application Won't Start

**Symptoms:**
- `python -m app.web` fails
- Import errors
- Module not found errors

**Solutions:**

**Verify virtual environment:**
```bash
# Check if activated (should see (venv) in prompt)
which python

# If not activated:
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

**Reinstall dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Check Python version:**
```bash
python3 --version
# Should be 3.11 or higher
```

**Check for port conflicts:**
```bash
lsof -i :51003  # macOS/Linux
netstat -ano | findstr :51003  # Windows

# If port is in use, kill the process or change port in app/web.py
```

---

### 3. Resume Not Found

**Symptoms:**
- Error: "Base resume not found"
- Can't create applications
- 404 when accessing `/api/resume`

**Solutions:**

**Create resume via web interface:**
1. Go to http://localhost:51003
2. Click "📄 Manage Resume"
3. Fill in your information
4. Click "Save Resume"

**Or create manually:**
```bash
# Create the file
touch data/resumes/base_resume.md

# Edit with your content
nano data/resumes/base_resume.md
```

**Check permissions:**
```bash
ls -la data/resumes/
# Should be readable/writable
chmod 755 data/resumes/
chmod 644 data/resumes/base_resume.md
```

---

### 4. Low Match Scores

**Symptoms:**
- Consistent match scores below 60%
- Missing many required skills
- Poor qualifications analysis

**Solutions:**

**Update your resume to be more comprehensive:**
- Include ALL technical skills (not just recent ones)
- List specific technologies, frameworks, tools
- Add years of experience per skill
- Include certifications and training
- Use industry-standard terminology

**Example - Bad:**
```markdown
- Experience with databases
- Worked on web applications
```

**Example - Good:**
```markdown
- PostgreSQL (5 years), MongoDB (3 years), Redis (2 years)
- React.js (4 years), Node.js (5 years), TypeScript (3 years)
- AWS Certified Solutions Architect
```

---

### 5. AI Processing Takes Too Long

**Symptoms:**
- Application creation takes 3+ minutes
- Timeout errors
- Slow responses from Ollama

**Solutions:**

**Use a faster model:**
```bash
ollama pull mistral
```

Then update `config/config.yaml`:
```yaml
ai:
  model: "mistral"
```

**Increase system resources:**
- Close other applications
- Ensure 8GB+ RAM available
- Check CPU usage

**Check Ollama logs:**
```bash
# Look for errors in Ollama terminal
```

**Shorten job descriptions:**
- Remove fluff and company marketing
- Keep only relevant sections
- Focus on requirements and responsibilities

---

### 6. Summary Page Not Opening

**Symptoms:**
- Click "View Summary" does nothing
- 404 error when accessing summary
- Blank page

**Solutions:**

**Check if file exists:**
```bash
ls -la data/applications/<Company>-<JobTitle>/
# Should see *-Summary-*.html file
```

**Regenerate documents:**
```bash
curl -X POST http://localhost:51003/api/applications/<APP_ID>/regenerate
```

**Check file permissions:**
```bash
chmod -R 755 data/applications/
```

**Access directly:**
```
http://localhost:51003/applications/<Company>-<JobTitle>/<Summary-File>.html
```

---

### 7. Documents Not Generated

**Symptoms:**
- Application created but no documents
- Missing cover letter or resume files
- Incomplete application folder

**Solutions:**

**Check disk space:**
```bash
df -h  # macOS/Linux
# Ensure at least 1GB free
```

**Check write permissions:**
```bash
ls -la data/applications/
chmod -R 755 data/applications/
```

**Review terminal output:**
Look for errors in the terminal where Job Hunter is running.

**Regenerate manually:**
```bash
curl -X POST http://localhost:51003/api/applications/<APP_ID>/regenerate
```

---

### 8. Dashboard Not Updating

**Symptoms:**
- New applications don't appear
- Old data showing
- Statistics are wrong

**Solutions:**

**Force dashboard regeneration:**
```bash
curl -X POST http://localhost:51003/api/dashboard/update
```

**Or from browser:**
```javascript
// In browser console
fetch('http://localhost:51003/api/dashboard/update', {method: 'POST'})
```

**Clear browser cache:**
- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Or clear cache in browser settings

**Check dashboard file:**
```bash
ls -la data/output/index.html
# Should exist and be recent
```

---

### 9. Import/Module Errors

**Symptoms:**
- `ModuleNotFoundError`
- `ImportError`
- Missing dependencies

**Solutions:**

**Ensure virtual environment is activated:**
```bash
source venv/bin/activate
which python  # Should show venv/bin/python
```

**Reinstall all dependencies:**
```bash
pip install --force-reinstall -r requirements.txt
```

**Check requirements.txt exists:**
```bash
cat requirements.txt
```

**Create fresh virtual environment:**
```bash
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 10. Unicode/Encoding Errors

**Symptoms:**
- Special characters display incorrectly
- Encoding errors in terminal
- Unicode decode errors

**Solutions:**

**Set UTF-8 encoding:**
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

**In job descriptions:**
- Copy from plain text, not PDF
- Remove smart quotes and special characters
- Use standard ASCII where possible

---

### 11. PRD Push / Static Search Page Generation Fails

**Symptoms:**
- "Prd Push" button doesn't work
- Error: "Generation script not found"
- Error: "Could not connect to Flask app"
- Git push fails
- Email notifications not sending

**Solutions:**

**Check Flask App is Running:**
```bash
# Verify Flask app is running
curl http://localhost:51003/api/check-ollama

# If not running, start it:
python -m app.web
```

**Verify Generator Script Exists:**
```bash
ls -la scripts/generate_static_search.py
# Should exist and be executable
```

**Check API Endpoint:**
```bash
# Test the endpoint directly
curl -X POST http://localhost:51003/api/static-search/generate
```

**Git Push Issues:**

If git push fails, verify:
```bash
# Check git remote is configured
git remote -v

# Check branch name
git branch

# Verify authentication (for HTTPS)
git push origin main --dry-run

# Manual push if automatic fails:
cd hunterapp_demo/kpro
git add index.html
git commit -m "Update kpro search page with latest data"
git push origin main
```

**Email Notifications Not Sending:**

1. Verify email is enabled in `config/digest_config.yaml`:
   ```yaml
   email:
     enabled: true
   ```

2. Follow **[EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)** to configure email properly

3. Test email configuration with daily digest:
   ```bash
   python3 scripts/generate_daily_digest.py
   ```

4. Check server logs for email errors in terminal

**"No changes detected" Message:**

This is normal! The generated file is identical to the version already in git. The page is already up to date. This is not an error.

**Generation Timeout:**

If process takes longer than 60 seconds:
```bash
# Check Flask app is responsive
curl http://localhost:51003/api/applications-and-contacts

# Check system resources (RAM, CPU)
# Large datasets may take longer to process
```

For detailed PRD Push troubleshooting, see **[PRD_PUSH_GUIDE.md](PRD_PUSH_GUIDE.md)**.

---

### 12. Email Notifications Not Working (Daily Digest / PRD Push)

**Symptoms:**
- Daily digest emails not sending
- PRD Push email notifications not received
- "Authentication failed" errors
- "Connection refused" errors

**Solutions:**

**Verify Email Configuration:**
```bash
# Check config file exists and is properly formatted
cat config/digest_config.yaml

# Should have:
# email:
#   enabled: true
#   smtp_server: smtp.zoho.com  # or your provider
#   smtp_port: 587
#   sender_email: "your-email@example.com"
#   sender_password: "your-password"
#   recipient_email: "your-email@example.com"
```

**For Zoho Mail:**
- Ensure IMAP Access is enabled in Zoho Mail settings
- If 2FA is enabled, use app-specific password (not regular password)
- Verify SMTP server: `smtp.zoho.com` (personal) or `smtppro.zoho.com` (organization)

**For Gmail:**
- Must use app-specific password (not regular password)
- Generate app password at: https://myaccount.google.com/apppasswords

**Test Email Configuration:**
```bash
# Test with daily digest
python3 scripts/generate_daily_digest.py

# Check server logs for errors
# Look for "Error sending email" messages
```

**Common Errors:**

**"Authentication failed":**
- Check username/password are correct
- For Zoho/Gmail with 2FA: Use app-specific password
- Verify email address is correct (case-sensitive for some providers)

**"Connection refused":**
- Check internet connection
- Verify SMTP server and port are correct
- Some networks block SMTP ports (try different network)
- Check firewall settings

**Email enabled but not sending:**
- Verify `enabled: true` in config
- Check spam/junk folder
- Verify all email fields are filled in
- Check server logs for detailed error messages

For detailed email setup, see **[EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)**.

---

## Platform-Specific Issues

### macOS

**SSL Certificate Issues:**
```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

**Homebrew Ollama not starting:**
```bash
brew services restart ollama
```

### Linux

**Permission denied errors:**
```bash
sudo chown -R $USER:$USER /path/to/hunter
chmod -R 755 /path/to/hunter
```

**Ollama not in PATH:**
```bash
export PATH=$PATH:/usr/local/bin
```

### Windows

**Virtual environment activation fails:**
```powershell
# Run as Administrator
Set-ExecutionPolicy RemoteSigned
```

**Path issues:**
- Use forward slashes: `/` instead of `\`
- Or use raw strings: `r"C:\path\to\hunter"`

---

## Performance Optimization

### Slow AI Processing

1. **Use Mistral model** (faster than Llama 3)
2. **Increase RAM allocation** (16GB recommended)
3. **Close unnecessary applications**
4. **Use SSD instead of HDD**

### Large Resumes

- Keep resume under 1000 lines
- Remove unnecessary details
- Focus on recent experience (last 10 years)

### Many Applications

- Archive old applications periodically
- Keep active applications under 100
- Clean up rejected applications

---

## Debug Mode

Enable detailed logging:

```python
# Edit app/web.py
app.run(debug=True, port=51003, host='0.0.0.0')
```

Check logs in terminal for detailed error messages.

---

## Getting Help

If none of these solutions work:

1. **Check terminal output** for detailed error messages
2. **Review the logs** in the terminal where Ollama is running
3. **Verify system requirements** meet minimum specifications
4. **Try a fresh installation** in a new directory
5. **Check GitHub Issues** for similar problems

### Collect Debug Information

```bash
# System info
python3 --version
ollama --version

# Check Ollama
ollama list
curl http://localhost:11434/api/tags

# Check Job Hunter
curl http://localhost:51003/api/check-ollama

# List files
ls -la data/resumes/
ls -la data/applications/

# Disk space
df -h
```

---

## Still Having Issues?

Create an issue on GitHub with:
- Your operating system and version
- Python version (`python3 --version`)
- Ollama version (`ollama --version`)
- Complete error message from terminal
- Steps to reproduce the issue

---

**Related Documentation:**
- [Installation Guide](INSTALLATION.md)
- [User Guide](USER_GUIDE.md)
- [Email Setup Guide](EMAIL_SETUP_GUIDE.md)
- [PRD Push Guide](PRD_PUSH_GUIDE.md)

