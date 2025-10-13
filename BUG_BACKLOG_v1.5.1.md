# Bug Backlog - Version 1.5.1

**Target Release:** October 14, 2025  
**Priority:** High - Core functionality issues

## 🚨 Critical Issues

### 1. Summary Updates Not Auto-Updating
**Priority:** SUPER IMPORTANT  
**Issue:** Summaries are not updating automatically with updates text in the "Updates and Notes" section  
**Impact:** Users cannot track application progress - core tracking feature broken  
**Files Affected:** 
- `app/services/document_generator.py` - Summary generation
- `app/services/job_processor.py` - Update handling
- Summary HTML files

**Expected Behavior:** When status updates are added, the summary page should automatically refresh the "Updates & Notes" section

### 2. Missing Match Score in Dashboard
**Priority:** High  
**Issue:** Fundraise Down application does not display match score in dashboard cards  
**Impact:** Inconsistent UI, users can't see match score for this application  
**Files Affected:**
- `app/services/dashboard_generator.py` - Dashboard generation
- `data/output/index.html` - Dashboard display
- Application metadata handling

**Expected Behavior:** All application cards should display match score consistently

### 3. Summary Page Generation Failure
**Priority:** High  
**Issue:** Summary page generation is not working - core feature of the app  
**Impact:** Users cannot view comprehensive application summaries  
**Files Affected:**
- `app/services/document_generator.py` - `generate_summary_page()`
- `app/services/ai_analyzer.py` - `extract_job_details()`
- HTML template generation

**Expected Behavior:** Every application should have a working summary page with all sections

## 🔧 Enhancement Requests

### 4. Job Application Dashboard Button
**Priority:** Medium  
**Request:** Add a button to navigate to "Job Application Dashboard" from the main job hunter page  
**Files Affected:**
- `app/templates/web/ui.html` - Main UI
- Navigation/routing logic

### 5. Resume Features Documentation
**Priority:** Medium  
**Request:** Create comprehensive documentation outlining all features found in resume by category  
**Deliverable:** New documentation file categorizing:
- Technical Skills
- Tools & Platforms
- Programming Languages
- Frameworks & Libraries
- Databases
- Cloud Services
- Soft Skills
- Certifications
- Experience Areas

## 🐛 Technical Debt

### 6. Update Timeline Integration
**Issue:** Updates are created as individual HTML files but not integrated into main summary  
**Solution:** Modify summary generation to include update timeline in "Updates & Notes" section

### 7. Match Score Persistence
**Issue:** Match scores not being saved/loaded correctly from application metadata  
**Solution:** Ensure match scores are properly stored in `application.yaml` and displayed consistently

## 📋 Testing Checklist

- [ ] Verify summary pages update when status changes
- [ ] Confirm all applications show match scores in dashboard
- [ ] Test summary page generation for new applications
- [ ] Validate update timeline integration
- [ ] Check navigation between main page and dashboard
- [ ] Review resume feature extraction accuracy

## 🎯 Success Criteria

1. **Summary Auto-Update:** Status changes immediately reflect in summary pages
2. **Consistent UI:** All applications show match scores in dashboard
3. **Working Summaries:** Every application has a functional summary page
4. **Easy Navigation:** Clear path from main page to dashboard
5. **Complete Documentation:** Comprehensive resume features guide

## 📝 Notes

- Focus on core functionality first (issues 1-3)
- Summary page generation is critical for user experience
- Update tracking is essential for application management
- Dashboard consistency improves user confidence

---

**Assigned:** Development Team  
**Due Date:** October 14, 2025  
**Status:** Ready for Development
