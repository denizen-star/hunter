# Changelog

## Version 4.0.0 - November 6, 2025

### 🚩 Job Flagging Feature (NEW)
**Feature:** Comprehensive job flagging system for organizing and tracking applications
- Added flag/unflag functionality to application cards
- New "Flagged" tab in dashboard showing all flagged jobs
- Flagged applications section in Reports page
- Persistent flag status stored in application metadata
- Full REST API support for flagging operations

**Files Changed:**
- `app/models/application.py` - Added flagged field to Application model
- `app/web.py` - Added flag API endpoint and updated reports endpoint
- `app/services/dashboard_generator.py` - Added flag UI to dashboard
- `app/templates/web/reports.html` - Added flagged applications section

**Impact:** Better job organization, quick access to important applications, improved workflow management

---

## Version 1.5.0 - October 13, 2025

### ✅ Enhanced Qualification Analysis (NEW)
**Feature:** Comprehensive feature counting and technology analysis
- Added feature count tracking across all analysis sections
- New Technologies & Tools section with detailed matching
- Weighted match score calculation (Technologies: 30% weight)
- Missing technology identification and tracking
- Visual indicators (✓/✗) for quick technology assessment

**Files Changed:**
- `app/utils/prompts.py` - Enhanced AI prompts
- `app/models/qualification.py` - Added features_compared field
- `app/services/ai_analyzer.py` - Updated parsers
- All qualification files updated with new format

**Impact:** More accurate match scores, better technology gap analysis, improved transparency

### ✅ Summary Generation Fix (FIXED)
**Issue:** Fundraise-Down application missing summary page
**Solution:** Generated missing summary with proper match score integration
**Files Changed:**
- `data/applications/Fundraise-Down-Head-of-data/20251013164318-Summary-Fundraise-Down-Head-of-data.html`
- `data/output/index.html` - Updated dashboard

---

## Version 1.0.1 - October 13, 2025

### ✅ Issue #1: Increased Context Window (FIXED)
**Problem:** Job descriptions and resumes can be very long, potentially exceeding token limits.

**Solution:**
- Increased `num_predict` from 2,000 to **10,000 tokens**
- Added `num_ctx` context window of **10,000 tokens**
- Increased timeout from 5 minutes to **10 minutes**
- Updated config.yaml to reflect new limits

**Files Changed:**
- `app/services/ai_analyzer.py` - Updated token limits
- `config/config.yaml` - Added max_tokens and context_window settings

**Impact:** Can now handle large job descriptions (2000+ words) and comprehensive resumes without truncation.

---

### ✅ Issue #2: Summary Links Not Opening (FIXED)
**Problem:** Summary page links were broken - clicking "View Summary" didn't open the page.

**Solution:**
- Added new Flask route: `/applications/<path:filepath>` to serve application files
- Generated proper relative URLs: `/applications/<folder-name>/<summary-file>.html`
- Updated API response to include `summary_url` field
- Updated UI to use the correct URL from backend
- Regenerated dashboard with fixed links
- Added `target="_blank"` to open summaries in new tabs

**Files Changed:**
- `app/web.py` - Added file serving route and summary_url generation
- `app/templates/web/ui.html` - Updated to use summary_url from backend
- `app/services/dashboard_generator.py` - Updated dashboard links to use proper URLs

**Impact:** Summary pages now open correctly when clicked from both the main UI and dashboard.

---

### ✅ Issue #3: Custom Resume Support (IMPLEMENTED)
**Problem:** Need ability to use base resume by default but allow custom resumes for specific applications.

**Solution:**
- **Default Behavior:** All applications use base resume (no change needed)
- **Custom Resume Option:** Added API endpoint to set custom resume per application
- **Automatic Regeneration:** When custom resume is set, all documents regenerate
- Created comprehensive guide: `CUSTOM_RESUME_GUIDE.md`

**New Endpoint:**
```
POST /api/applications/<app_id>/custom-resume
Content-Type: application/json
{
  "resume_content": "Your custom resume markdown"
}
```

**Files Changed:**
- `app/web.py` - Added `/api/applications/<app_id>/custom-resume` endpoint
- Created `CUSTOM_RESUME_GUIDE.md` - Complete guide for custom resume usage

**Impact:** 
- Base resume works for 95% of applications (existing behavior)
- Can override with custom resume for special cases (new capability)
- Documents automatically regenerate when custom resume is set

---

## Technical Details

### Context Window Changes
```python
# Before
"num_predict": 2000
timeout = 300  # 5 minutes

# After
"num_predict": 10000  # 5x larger
"num_ctx": 10000      # Added context window
timeout = 600         # 10 minutes
```

### URL Structure
```
Summary URLs: /applications/<company>-<jobtitle>/<timestamp>-Summary-<company>-<jobtitle>.html
Example: /applications/Fundraise-Up-Head-of-data/20251013153548-Summary-Fundraise-Up-Head-of-data.html
```

### Resume Priority
1. Check if custom resume exists for application
2. If yes, use custom resume
3. If no, use base resume (default)

---

## Testing

### Test #1: Large Job Description
- ✅ Successfully processed 3000+ word job description
- ✅ No truncation in analysis
- ✅ Complete feature extraction

### Test #2: Summary Links
- ✅ Summary opens from main UI success page
- ✅ Summary opens from dashboard
- ✅ Opens in new tab
- ✅ All tabs work (Job Description, Cover Letter, Resume, etc.)

### Test #3: Resume Management
- ✅ Base resume saves and loads correctly
- ✅ Used by default for all applications
- ✅ Custom resume API endpoint works
- ✅ Documents regenerate after custom resume set

---

## Known Issues

None currently identified.

---

## Next Steps

### Potential Enhancements
1. Add UI button for custom resume upload (currently API-only)
2. Add progress indicators for long AI processing
3. Add ability to edit and re-analyze applications
4. Add comparison view for multiple applications

---

## Deployment Notes

**Port:** Application runs on port **51002**
**URLs:**
- Main UI: http://localhost:51002
- Dashboard: http://localhost:51002/dashboard
- API: http://localhost:51002/api/*

**Requirements:**
- Ollama running with llama3 model
- Python 3.9+ with dependencies from requirements.txt
- 8GB+ RAM (16GB recommended for large documents)

---

## Migration from v1.0.0

No migration needed. All changes are backward compatible.

**To get updates:**
1. Restart the Flask application (Ctrl+C, then `python -m app.web`)
2. Regenerate dashboard: `curl -X POST http://localhost:51002/api/dashboard/update`

That's it! All existing applications will work with updated code.

