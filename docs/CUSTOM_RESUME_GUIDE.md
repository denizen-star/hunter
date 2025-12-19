# Custom Resume Guide

## Overview

The Job Hunter application supports both a **base resume** (used by default for all applications) and **custom resumes** (for specific applications when needed).

## Base Resume (Default)

Your base resume is used for ALL applications by default. This is the resume you set up when you first use the application.

### How to Set/Update Your Base Resume

**Option 1: Via Web Interface**
1. Go to http://localhost:51003
2. Click "📄 Manage Resume"
3. Fill in your information
4. Paste your resume content (Markdown format)
5. Click "Save Resume"

**Option 2: Manually**
- Edit the file: `data/resumes/base_resume.md`
- Update metadata in: `data/resumes/base_resume.yaml`

## Custom Resume (Optional)

Use a custom resume when you want to use a different version of your resume for a specific job application. This is rare but useful when you have:
- Industry-specific resumes (e.g., Tech vs Finance)
- Role-specific resumes (e.g., Manager vs IC)
- Heavily customized versions for premium opportunities

### How to Set a Custom Resume for an Application

**Via API:**
```bash
curl -X POST http://localhost:51003/api/applications/<APP_ID>/custom-resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume_content": "Your custom resume in markdown format here..."
  }'
```

This will:
1. Save the custom resume to the application folder
2. Regenerate all documents (cover letter, tailored resume, qualifications) using the new resume
3. Update the dashboard

### When to Use Custom Resumes

✅ **Use a custom resume when:**
- You have a specialized resume for specific industries
- You want to emphasize completely different experience
- The job requires a significantly different approach

❌ **Don't use custom resumes when:**
- You just want to tweak a few bullet points (use the generated customized resume instead)
- The difference is minimal
- You're applying to similar roles

## How It Works

### Base Resume (Default Flow)
```
Create Application → Uses Base Resume → Generates:
  ├── Qualifications Analysis
  ├── Cover Letter
  └── Customized Resume (based on base resume)
```

### Custom Resume (Override Flow)
```
Create Application → Set Custom Resume → Regenerates:
  ├── Qualifications Analysis (with custom resume)
  ├── Cover Letter (with custom resume)
  └── Customized Resume (based on custom resume)
```

## File Structure

```
data/
├── resumes/
│   ├── base_resume.md          # Your default resume (used by all)
│   └── base_resume.yaml        # Metadata
└── applications/
    └── Company-JobTitle/
        ├── custom_resume_<app_id>.md  # Custom resume (if set)
        ├── <Name>-Company-Job-Resume.md  # Generated tailored resume
        └── ... (other generated files)
```

## Best Practice

**Recommendation:** Stick with your base resume for 95% of applications. The AI will automatically customize it for each job. Only use custom resumes when you have fundamentally different versions of your professional story.

The generated "Customized Resume" is already tailored for each job - you don't need a custom base resume unless you're targeting completely different career paths.

## API Reference

### Set Custom Resume
```
POST /api/applications/<app_id>/custom-resume
Content-Type: application/json

{
  "resume_content": "Your custom resume content in markdown"
}
```

### Regenerate Documents (after updating base resume)
```
POST /api/applications/<app_id>/regenerate
```

This will regenerate all documents for an application using whatever resume is set (base or custom).

---

**Remember:** The AI already does heavy customization of your resume for each job. Custom resumes are for the rare cases where you need a fundamentally different starting point!

