# Terminal Messages Reference Guide

This document lists all terminal messages that appear during application processing, organized by priority level. Use this guide to understand what each message means and when it appears.

## Priority Levels

- **High Priority**: Critical messages you should always pay attention to (errors, warnings, completion status)
- **Medium Priority**: Progress updates that show what's happening (document generation steps, AI analysis status)
- **Low Priority**: Debug details for troubleshooting (phase activations, match score details, verbose progress)

---

## High Priority Messages

### Error Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 1 | Active | `❌ Error generating research file: {error}` | When research file generation fails | Research generation encountered an error | `document_generator.py` |
| 2 | Active | `❌ Error in _get_company_news: {error}` | When company news search fails | Failed to fetch company news | `document_generator.py` |
| 3 | Active | `❌ Error in _get_company_personnel: {error}` | When personnel search fails | Failed to fetch company personnel info | `document_generator.py` |
| 4 | Active | `✗ Error generating summary page: {error}` | When summary page generation fails | Summary page creation encountered an error | `document_generator.py` |
| 5 | Active | `❌ Application with ID {app_id} not found.` | When application ID doesn't exist | The requested application doesn't exist | `process_next_application.py` |
| 6 | Active | `❌ Job description file not found!` | When job description file is missing | Required job description file is missing | `reprocess_audubon_qualifications.py` |
| 7 | Active | `❌ Error during reprocessing: {error}` | When reprocessing fails | Application reprocessing encountered an error | `reprocess_audubon_qualifications.py` |

### Warning Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 8 | Active | `⚠️  Warning: Could not load Job Engine V2 config: {error}` | When Job Engine V2 config file can't be loaded | Config file missing or invalid, using defaults | `preliminary_matcher.py` |
| 9 | Active | `⚠️  Warning: Could not load skills taxonomy: {error}` | When skills taxonomy file can't be loaded | Taxonomy file missing or invalid | `preliminary_matcher.py` |
| 10 | Active | `⚠️ Warning: Could not load research file: {error}` | When research file can't be read | Research file exists but can't be loaded | `document_generator.py` |
| 11 | Active | `⚠️ Warning: Could not load qualifications from JSON: {error}` | When qualifications JSON can't be loaded | Qualifications file exists but can't be parsed | `document_generator.py` |
| 12 | Active | `⚠️ No search results found for {company_name}` | When web search returns no results | No news found, using fallback data | `document_generator.py` |
| 13 | Active | `⚠️ No personnel results found for {company_name}` | When personnel search returns no results | No personnel found, using fallback data | `document_generator.py` |
| 14 | Active | `⚠️ Web search failed: {error}, using fallback data` | When web search fails | Web search unavailable, using fallback | `document_generator.py` |
| 15 | Active | `⚠️ Personnel search failed: {error}, using fallback data` | When personnel search fails | Personnel search unavailable, using fallback | `document_generator.py` |
| 16 | Active | `⚠️ Enhanced Qualifications Analyzer not available - using standard AI analysis` | When enhanced analyzer can't be loaded | Enhanced analyzer unavailable, using standard | `ai_analyzer.py` |
| 17 | Active | `⚠️ Using Standard AI Analysis (Enhanced analyzer not available)` | When enhanced analyzer isn't available | Falling back to standard analysis | `ai_analyzer.py` |
| 18 | Active | `⚠️  Warning: Cover letter scan failed: {error}. Using original version.` | When cover letter scanning fails | Cover letter improvement failed, using original | `ai_analyzer.py` |
| 19 | Active | `⚠️  WARNING: Score mismatch detected! Preliminary={prelim}%, AI={ai}%, USING PRELIMINARY={final}%` | When preliminary and AI scores differ significantly | Score discrepancy detected, using preliminary score | `enhanced_qualifications_analyzer.py` |
| 20 | Active | `Warning: Could not generate preliminary_analysis: {error}` | When preliminary analysis generation fails | Preliminary analysis failed, continuing without it | `ai_analyzer.py` |
| 21 | Active | `Warning: Could not generate badge display: {error}` | When badge generation fails | Badge display generation failed | `document_generator.py` |
| 22 | Active | `Warning: Could not generate rewards by category: {error}` | When rewards generation fails | Rewards display generation failed | `document_generator.py` |
| 23 | Active | `Warning: Could not parse timestamp for update {file}: {error}` | When timestamp parsing fails | Update timestamp can't be parsed | `document_generator.py` |
| 24 | Active | `Warning: Could not extract content from {file}: {error}` | When content extraction fails | Can't extract content from update file | `document_generator.py` |

### Completion Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 25 | Active | `✓ All documents generated successfully!` | When all documents are created | All application documents generated | `document_generator.py` |
| 26 | Inactive | `✅ Research file generated: {path}` | When research file is created | Research file successfully created | `document_generator.py` |
| 27 | Inactive | `✅ Enhanced Qualifications Analyzer loaded - using preliminary matching + focused AI analysis` | When enhanced analyzer initializes | Enhanced analyzer ready to use | `ai_analyzer.py` |
| 28 | Inactive | `✅ Found {count} news items for {company_name}` | When news search succeeds | Company news successfully retrieved | `document_generator.py` |
| 29 | Inactive | `✅ Found {count} key personnel for {company_name}` | When personnel search succeeds | Company personnel successfully retrieved | `document_generator.py` |
| 30 | Inactive | `✓ Updating existing summary page: {filename}` | When updating existing summary | Summary page being updated | `document_generator.py` |
| 31 | Inactive | `✓ Creating new summary page: {filename}` | When creating new summary | New summary page being created | `document_generator.py` |
| 32 | Inactive | `✓ Created networking contact: {person} at {company}` | When networking contact is created | Networking contact successfully created | `networking_processor.py` |
| 33 | Inactive | `✓ Updated contact status to: {status}` | When contact status is updated | Networking contact status changed | `networking_processor.py` |
| 34 | Inactive | `✓ Regenerated contact summary with updated badges` | When contact summary is regenerated | Networking contact summary updated | `networking_processor.py` |

---

## Medium Priority Messages

### Document Generation Progress

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 35 | Active | `Generating documents for {company} - {job_title}...` | At start of document generation | Beginning document generation process | `document_generator.py` |
| 36 | Active | `  → Analyzing qualifications and extracting features...` | During qualifications analysis | Starting qualifications matching | `document_generator.py` |
| 37 | Inactive | `  → Generating company research...` | During research generation | Starting company research | `document_generator.py` |
| 38 | Inactive | `  → Generating cover letter...` | During cover letter generation | Starting cover letter creation | `document_generator.py` |
| 39 | Inactive | `  → Skipping intro messages (deferred; generate from Cover Letter tab if needed)` | When intro messages are skipped | Intro messages deferred for on-demand generation | `document_generator.py` |
| 40 | Inactive | `  → Skipping customized resume (deferred; generate from Resume tab if needed)` | When resume is skipped | Custom resume deferred for on-demand generation | `document_generator.py` |
| 41 | Active | `  → Generating summary page...` | During summary generation | Starting summary page creation | `document_generator.py` |
| 42 | Inactive | `  → Scanning cover letter for grammar and repetitive phrases...` | During cover letter improvement | Improving cover letter quality | `document_generator.py` |
| 43 | Inactive | `  🤖 Generating structured research for {company}...` | During AI research generation | AI generating company research | `document_generator.py` |
| 44 | Inactive | `📖 Reading AI-generated research from: {path}` | When loading existing research | Loading previously generated research | `document_generator.py` |

### AI Analysis Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 45 | Active | `🚀 Using Enhanced Qualifications Analyzer (Preliminary Matching + Focused AI)` | When enhanced analyzer is used | Using advanced analysis method | `ai_analyzer.py` |
| 46 | Inactive | `🤖 Creating focused AI analysis prompt...` | During AI prompt creation | Building focused AI prompt | `enhanced_qualifications_analyzer.py` |
| 47 | Inactive | `🧠 Running AI analysis with preliminary context...` | During AI analysis | Running AI with preliminary results | `enhanced_qualifications_analyzer.py` |
| 48 | Active | `📊 Combining preliminary and AI analysis results...` | During result combination | Merging preliminary and AI results | `enhanced_qualifications_analyzer.py` |

### Job Engine Status

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 49 | Active | `🚀 Job Engine V2 Active` | When Job Engine V2 is enabled | Advanced job engine is active | `preliminary_matcher.py` |
| 50 | Active | `⚙️  Job Engine V1 Active (Legacy)` | When Job Engine V1 is used | Legacy job engine is active | `preliminary_matcher.py` |
| 51 | Inactive | `   Word Cloud Scan (Frequency Analysis): ✅` | When Phase 1.1 is enabled | Frequency analysis phase active | `preliminary_matcher.py` |
| 52 | Inactive | `   Critical Requirements Highlighting: ✅` | When Phase 1.2 is enabled | Critical requirements phase active | `preliminary_matcher.py` |
| 53 | Inactive | `   Hard Skills from Sections: ✅` | When Phase 2.1 is enabled | Hard skills extraction phase active | `preliminary_matcher.py` |

### Research and Search Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 54 | Inactive | `🔍 Generating comprehensive research for {company_name}...` | When starting company research | Beginning comprehensive research | `document_generator.py` |
| 55 | Inactive | `🔍 Searching for real news about {company_name}...` | When searching for news | Searching web for company news | `document_generator.py` |
| 56 | Inactive | `🔍 Searching for key personnel at {company_name}...` | When searching for personnel | Searching web for company personnel | `document_generator.py` |
| 57 | Inactive | `Error in company research: {error}` | When research fails | Company research encountered error | `document_generator.py` |
| 58 | Active | `Error in AI research: {error}` | When AI research fails | AI research generation failed | `document_generator.py` |
| 59 | Active | `Error parsing research response: {error}` | When parsing fails | Can't parse AI research response | `document_generator.py` |
| 60 | Active | `Error in fallback search: {error}` | When fallback fails | Fallback search method failed | `document_generator.py` |
| 61 | Active | `Error parsing DuckDuckGo results: {error}` | When parsing fails | Can't parse search results | `document_generator.py` |
| 62 | Active | `Error parsing search results: {error}` | When parsing fails | Can't parse general search results | `document_generator.py` |
| 63 | Active | `Products/services search failed: {error}` | When product search fails | Product search encountered error | `document_generator.py` |
| 64 | Active | `Error searching products/services: {error}` | When product search fails | Product search error | `document_generator.py` |
| 65 | Active | `Competitors search failed: {error}` | When competitor search fails | Competitor search encountered error | `document_generator.py` |
| 66 | Active | `Error searching competitors: {error}` | When competitor search fails | Competitor search error | `document_generator.py` |

---

## Low Priority Messages

### Phase Activation Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 67 | Inactive | `📊 Job Engine V2 - Phase 1.1: Frequency Analysis active` | When Phase 1.1 runs | Frequency analysis phase starting | `preliminary_matcher.py` |
| 68 | Inactive | `🎯 Job Engine V2 - Phase 1.2: Critical Requirements Highlighting active` | When Phase 1.2 runs | Critical requirements phase starting | `preliminary_matcher.py` |
| 69 | Inactive | `🔧 Job Engine V2 - Phase 2.1: Hard Skills Extraction active` | When Phase 2.1 runs | Hard skills extraction phase starting | `preliminary_matcher.py` |

### Match Score Debug Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 70 | Active | `🔍 Match Score Debug: total_unmatched={count}, critical_missing={count}, non_critical={count}` | During match score calculation | Detailed match score breakdown | `preliminary_matcher.py` |
| 71 | Active | `   Critical missing: {list}` | When critical skills are missing | List of missing critical skills | `preliminary_matcher.py` |
| 72 | Active | `   Non-critical missing: {list}...` | When non-critical skills are missing | List of missing non-critical skills (first 5) | `preliminary_matcher.py` |
| 73 | Active | `   ⚠️  Capping at 95% due to {count} critical missing skill(s)` | When score is capped | Score limited due to critical missing skills | `preliminary_matcher.py` |
| 74 | Active | `   ✅ Allowing up to 100% despite {count} non-critical missing skill(s)` | When score can reach 100% | Score not limited by non-critical missing skills | `preliminary_matcher.py` |

### Detailed Progress Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 75 | Inactive | `Preliminary Analysis Results:` | During test/debug runs | Summary of preliminary analysis | `preliminary_matcher.py` |
| 76 | Inactive | `Match Score: {score}%` | During test/debug runs | Final match score | `preliminary_matcher.py` |
| 77 | Inactive | `Exact Matches: {count}` | During test/debug runs | Number of exact skill matches | `preliminary_matcher.py` |
| 78 | Inactive | `Partial Matches: {count}` | During test/debug runs | Number of partial skill matches | `preliminary_matcher.py` |
| 79 | Inactive | `AI Focus Areas: {areas}` | During test/debug runs | Areas for AI to focus on | `preliminary_matcher.py` |
| 80 | Inactive | `Enhanced Analysis Complete!` | When enhanced analysis finishes | Enhanced analysis completed | `enhanced_qualifications_analyzer.py` |
| 81 | Inactive | `Match Score: {score}%` | When analysis completes | Final qualifications match score | `enhanced_qualifications_analyzer.py` |
| 82 | Inactive | `Strong Matches: {count}` | When analysis completes | Number of strong skill matches | `enhanced_qualifications_analyzer.py` |
| 83 | Inactive | `Missing Skills: {count}` | When analysis completes | Number of missing skills | `enhanced_qualifications_analyzer.py` |
| 84 | Inactive | `Recommendations: {count}` | When analysis completes | Number of recommendations | `enhanced_qualifications_analyzer.py` |

### Application Processing Messages

| ID | Active | Message | When It Appears | Meaning | Source |
|----|--------|---------|----------------|---------|--------|
| 85 | Active | `🚀 Processing: {company} - {job_title}` | At start of processing | Beginning application processing | `process_next_application.py` |
| 86 | Active | `📋 Application loaded: {company} - {job_title}` | When application loads | Application successfully loaded | `process_next_application.py` |
| 87 | Inactive | `1️⃣ Generating Research Section...` | During research generation | Starting research section | `process_next_application.py` |
| 88 | Inactive | `2️⃣ Generating Hiring Manager Intro Messages...` | During intro generation | Starting intro message generation | `process_next_application.py` |
| 89 | Inactive | `🔄 Regenerating qualifications for {company}...` | During regeneration | Starting qualifications regeneration | `reprocess_audubon_qualifications.py` |
| 90 | Inactive | `✓ Found application: {company} - {job_title}` | When application found | Application located | `reprocess_audubon_qualifications.py` |
| 91 | Inactive | `✓ Loaded job description ({chars} characters)` | When job description loads | Job description loaded | `reprocess_audubon_qualifications.py` |
| 92 | Inactive | `✓ Loaded resume ({chars} characters)` | When resume loads | Resume loaded | `reprocess_audubon_qualifications.py` |
| 93 | Inactive | `📊 Regenerating qualifications analysis with Job Engine V2...` | During regeneration | Starting V2 qualifications regeneration | `reprocess_audubon_qualifications.py` |
| 94 | Active | `✅ Qualifications regenerated successfully!` | When regeneration completes | Qualifications successfully regenerated | `reprocess_audubon_qualifications.py` |
| 95 | Inactive | `📄 Regenerating summary page...` | During summary regeneration | Starting summary regeneration | `reprocess_audubon_qualifications.py` |
| 96 | Inactive | `✅ Summary page regenerated!` | When summary regenerates | Summary successfully regenerated | `reprocess_audubon_qualifications.py` |
| 97 | Inactive | `✅ Application metadata updated!` | When metadata updates | Application metadata saved | `reprocess_audubon_qualifications.py` |

---

## Message Categories Summary

### By Service

- **preliminary_matcher.py**: Job Engine status, phase activations, match score debug
- **document_generator.py**: Document generation progress, research/search operations
- **ai_analyzer.py**: AI analyzer selection and status
- **enhanced_qualifications_analyzer.py**: Enhanced analysis progress and results
- **networking_processor.py**: Networking contact operations
- **process_next_application.py**: Application processing workflow
- **reprocess_audubon_qualifications.py**: Application reprocessing workflow

### By Priority Distribution

- **High Priority**: ~30 messages (errors, warnings, completion)
- **Medium Priority**: ~25 messages (progress, status updates)
- **Low Priority**: ~20 messages (debug details, verbose progress)

---

## Notes

- Messages with emoji indicators (🚀, ✅, ⚠️, ❌, etc.) are easier to spot in terminal output
- Error messages always include the error details in `{error}` format
- Progress messages use arrows (→) to indicate steps in a sequence
- Debug messages are typically only visible when processing applications or during development
- Some messages only appear when specific features are enabled (e.g., Job Engine V2 phases)
- **Inactive** messages are suppressed and will not appear in terminal output
