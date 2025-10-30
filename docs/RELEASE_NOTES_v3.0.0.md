# Hunter v3.0.0 - 2025-10-30

Major release focused on performance, UX improvements, and robust summary pages.

Highlights
- Parallelized intro generation: Hiring Manager and Recruiter intros are generated concurrently.
- Deferred resume generation: Customized resume is now on-demand from the Summary → Customized Resume tab.
- Summary UX:
  - Clean intro message titles and copy content (removed metadata and helper lines).
  - Titles used as dropdown templates; added Cover Letter to templates.
  - Dropdown labels now include Delivery Method (e.g., "… - Intro").
  - Tabs made robust across browsers (explicit display toggling and safer handlers).
  - Fixed JS newline escaping to preserve formatting when inserting into Notes.
- New endpoint: POST /api/applications/<id>/generate-resume to generate customized resume on demand.

Fixes
- Prevented broken script execution due to regex/newline emission in generated pages.
- Resolved tab switching issues caused by inline handler mismatches and display styles.
- Preserved formatting when inserting Cover Letter/Intros into Notes (HTML conversion).

Developer Notes
- Version bumped to 3.0.0 in VERSION.
- Changed files include app/services/document_generator.py, app/web.py, and related helpers.

Upgrade Guide
- No migration steps required.
- Existing summary pages will benefit after regeneration; newly generated pages include all fixes.
