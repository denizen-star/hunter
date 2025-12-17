# Networking Status Management System - Migration Requirements

## Overview

This document outlines the requirements for revamping the networking status management system, including new status definitions, category changes, reward/badge system integration, and migration strategy.

**Date:** December 2025  
**Status:** Planning Phase

---

## 1. New Status System

### 1.1 Status Definitions

The new system will have 11 statuses (replacing the current 16):

| # | New Status | Pipeline Phase | Description |
|---|-----------|----------------|-------------|
| 1 | To Research | PROSPECTING | Initial entry point - contact created but research incomplete |
| 2 | Ready to Connect | PROSPECTING | Deep research complete, personalization hook defined |
| 3 | Pending Reply | OUTREACH | LinkedIn message sent, awaiting connection acceptance or response |
| 4 | Connected - Initial | OUTREACH | Any positive sign of engagement (profile viewed, connection accepted, email reply) |
| 5 | Cold/Inactive | OUTREACH | Follow-up window passed, no response after 2 attempts |
| 6 | In Conversation | ENGAGEMENT | Value-driven email sent, actively exchanging messages toward meeting |
| 7 | Meeting Scheduled | ENGAGEMENT | Call/meeting confirmed on calendar with specific date/time |
| 8 | Meeting Complete | ENGAGEMENT | Meeting occurred and debrief completed |
| 9 | Strong Connection | NURTURE | Relationship established, active maintenance check-ins (1-6 months) |
| 10 | Referral Partner | NURTURE | High-value relationship - contact provides referrals/opportunities |
| 11 | Dormant | NURTURE | 6-12 months since last contact, requires re-engagement |

### 1.2 Status Migration Mapping

| Old Status | New Status | Reason |
|-----------|-----------|--------|
| 1. To Research | 1. To Research | Status name identical |
| 2. Ready to Contact | 2. Ready to Connect | Represents completion of research and readiness for first action |
| 3. Contacted - Sent | 3. Pending Reply | Contact is out, waiting for any response |
| 5. Contacted - No Response | 3. Pending Reply | Failure to reply, but still requires follow-up before archiving |
| 4. Contacted - Replied | 4. Connected - Initial | Reply qualifies them as responsive |
| 12. New Connection | 4. Connected - Initial | First successful engagement post-initial outreach |
| 6. Cold/Archive | 5. Cold/Inactive | Official dead-end for active pursuit |
| 7. In Conversation | 6. In Conversation | Status name identical |
| 10. Action Pending - You | 6. In Conversation | Action items part of active conversation/pre-meeting stage |
| 11. Action Pending - Them | 6. In Conversation | Action items part of active conversation/pre-meeting stage |
| 8. Meeting Scheduled | 7. Meeting Scheduled | Status name identical |
| 9. Meeting Complete | 8. Meeting Complete | Status name identical |
| 13. Nurture (1-3 Mo.) | 9. Strong Connection | Time-based nurturing consolidated into one active status |
| 14. Nurture (4-6 Mo.) | 9. Strong Connection | Time-based nurturing consolidated into one active status |
| 15. Referral Partner | 10. Referral Partner | Status name identical |
| 16. Inactive/Dormant | 11. Dormant | Simplified name for long-term inactivity |

---

## 2. Category Changes

### 2.1 New Category Names

| Old Category | New Category | Notes |
|-------------|-------------|-------|
| 1. Prospecting | 1. Prospecting | No change |
| 2. Qualification | 2. Outreach | Renamed to reflect outreach activities |
| 3. Discovery/Needs Analysis | 3. Engagement | Renamed to reflect active engagement |
| 4. Closing/Relationship Established | 4. Nurture | Renamed to reflect ongoing relationship maintenance |

### 2.2 Category-to-Status Mapping

- **PROSPECTING:** To Research, Ready to Connect
- **OUTREACH:** Pending Reply, Connected - Initial, Cold/Inactive
- **ENGAGEMENT:** In Conversation, Meeting Scheduled, Meeting Complete
- **NURTURE:** Strong Connection, Referral Partner, Dormant

---

## 3. Reward/Badge System

### 3.1 System Requirements

- **Location:** 
  - Application Hero: Displayed on job application Hero section (application detail page header)
  - Contact Hero: Displayed on individual networking contact detail page header
  - Rewards Tab: Displayed as a tab in the application detail page
- **Storage:** JSON file with incremental updates (cached calculation with batch updates)
- **Scope:** 
  - **Per-Contact Badges:** Each contact earns badges based on their status progression
  - **Application Badges:** Shows the highest badge achieved across all contacts for that company
  - **Points:** Cumulative based on status progression (all preceding badges count)
- **Application Filter:** Only contacts where company name matches application company (exact match, case-insensitive, trimmed)
- **Display Format:** 
  - **Application Hero:** Shows max accomplished badge (left) and next badge to earn (right). For apps without contacts, shows "Deep Diver" as next badge.
  - **Contact Hero:** Shows all 8 badges in a collapsible section, with earned badges highlighted. Title shows total cumulative points.
  - **Rewards Tab:** Card-based layout showing points and badge counts by category (Prospecting, Outreach, Engagement, Nurture)
- **Historical Data:** Retroactively calculate badges for all existing contacts during migration

### 3.2 Badge Definitions (Current Implementation)

| # | Status | Badge Name | Points | Pipeline Phase | Notes |
|---|--------|-----------|--------|----------------|-------|
| 1 | To Research | None | 0 | PROSPECTING | No badge for initial creation |
| 2 | Ready to Connect | Deep Diver | +10 | PROSPECTING | First badge earned |
| 3 | Pending Reply | Profile Magnet | +3 | OUTREACH | Contact reached out |
| 4 | Connected - Initial | Qualified Lead | +15 | OUTREACH | Positive engagement |
| 5 | Cold/Inactive | None | 0 | OUTREACH | No badge for inactive contacts |
| 6 | In Conversation | Conversation Starter | +20 | ENGAGEMENT | Active dialogue |
| 7 | Meeting Scheduled | Scheduler Master | +30 | ENGAGEMENT | Meeting confirmed |
| 8 | Meeting Complete | Rapport Builder | +50 | ENGAGEMENT | Meeting completed |
| 9 | Strong Connection | Relationship Manager | +2 | NURTURE | Recurring (per check-in) |
| 10 | Referral Partner | Super Connector | +100 | NURTURE | Highest value badge |
| 11 | Dormant | None | 0 | NURTURE | No badge for dormant contacts |

**Points Calculation:** Points are cumulative. If a contact reaches "In Conversation", they earn points for all preceding badges: Deep Diver (+10) + Profile Magnet (+3) + Qualified Lead (+15) + Conversation Starter (+20) = 48 total points.

### 3.3 Points Tracking

- **Primary Display:** Points by badge + total points
- **Additional Report:** Points by category (Prospecting, Outreach, Engagement, Nurture) - new report in Reports section

### 3.4 Badge Calculation Logic

1. **Per-Contact Calculation:** Each contact earns ONE badge based on their current status
2. **Cumulative Points:** Points are cumulative - reaching a status earns points for all preceding badges in the progression
3. **Status Progression Order:**
   - Ready to Connect → Deep Diver (+10)
   - Pending Reply → Profile Magnet (+3)
   - Connected - Initial → Qualified Lead (+15)
   - In Conversation → Conversation Starter (+20)
   - Meeting Scheduled → Scheduler Master (+30)
   - Meeting Complete → Rapport Builder (+50)
   - Strong Connection → Relationship Manager (+2, recurring)
   - Referral Partner → Super Connector (+100)
4. **Application Display:** Shows the highest badge achieved across all contacts matching the application's company
5. **Contact Display:** Shows all 8 badges, with earned badges (based on current status) highlighted
6. **Cached Results:** Store calculated badge data in JSON file for performance
7. **Application Context:** Only count contacts linked to applications (company match, case-insensitive, trimmed)

### 3.5 Reward Tracking Rules

- **Application Requirement:** If a contact is created but there is no application related to the contact, there is no reward to track
- **Company Matching:** Contact company must exactly match application company (case-insensitive, trimmed)
- **Status History:** Analyze all status changes in contact's update history to determine badge eligibility

---

## 4. Workflow Integration

### 4.1 Human Workflow Representation

The system tracks from **Step 2.4** (Log Connection) onwards:

1. **Phase 1: Deep Discovery & Contact Creation** (Steps 1.1-1.4)
   - Status: To Research → Ready to Connect
   - Badge: Deep Diver (+10 points)

2. **Phase 2: Initial Outreach** (Steps 2.1-2.4)
   - Status: Ready to Connect → Pending Reply → Connected - Initial
   - Badges: Action Taker (+5), Qualified Lead (+15), Profile Magnet (+3)

3. **Phase 3: Secondary Outreach** (Steps 3.1-3.4)
   - Status: Connected - Initial → In Conversation
   - Badge: Conversation Starter (+20)

4. **Phase 4: Relationship Maintenance** (Steps 4.1-4.2)
   - Status: Strong Connection → Referral Partner
   - Badges: Relationship Manager (+2 per check-in), Super Connector (+100)

### 4.2 Status Transition Triggers

| Status | Trigger Event | Next Action |
|--------|--------------|-------------|
| To Research | Initial Contact Creation (Step 1.4) | Complete Deep Research (Steps 1.1-1.3) |
| Ready to Connect | Deep Research Complete (Steps 1.1-1.3) | Send Personalized LinkedIn Message (Step 2.1) |
| Pending Reply | Personalized LinkedIn Message Sent (Step 2.1) | Monitor for Reply/Connection (Steps 2.3-2.4) |
| Connected - Initial | Contact Viewed Profile (2.3) OR Connection Accepted (2.4) OR Email Reply Received (3.4) | Transition to Email Outreach (Steps 3.1-3.3) |
| Cold/Inactive | Follow-up Window Passed / No Response after 2 attempts | Archive for future, low-effort re-engagement |
| In Conversation | Value-Driven Email Sent (3.3) and Contact is Actively Responding | Keep momentum toward scheduled meeting/call |
| Meeting Scheduled | Call/Meeting Confirmed on Calendar (Step 8) | Prepare for the meeting/call |
| Meeting Complete | Meeting Occurred and Debrief is Done (Step 9) | Send Thank You Note & Define Next Check-in |
| Strong Connection | Next Check-in Scheduled (Step 4.1) or Maintenance Check-in Sent (Step 4.2) | Maintain consistent, value-add check-ins |
| Referral Partner | Contact Provides Referral/Opportunity OR Explicitly Offers Advocacy | Prioritize providing value to them |
| Dormant | 6-12 Months Have Passed Since Last Contact | Look for genuine opportunity to re-engage |

---

## 5. Data Storage & Architecture

### 5.1 Contact Metadata

- **Location:** `data/networking/{ContactName}-{CompanyName}/metadata.yaml`
- **Status Field:** Single `status` field containing current status string
- **Status History:** Tracked in `updates/` folder with timestamped HTML files
- **Migration:** Update `status` field in metadata.yaml files during migration

### 5.2 Badge/Points Storage

- **Location:** `data/output/networking_rewards.json`
- **Format:** JSON with structure:
  ```json
  {
    "last_calculated": "2025-12-15T10:00:00Z",
    "total_points": 250,
    "badges": {
      "deep_diver": {
        "earned": true,
        "points": 10,
        "count": 3,
        "last_earned": "2025-12-15T09:30:00Z"
      },
      ...
    },
    "points_by_category": {
      "prospecting": 30,
      "outreach": 50,
      "engagement": 100,
      "nurture": 70
    },
    "application_badges": {
      "application_id_1": {
        "total_points": 50,
        "badges": {...}
      }
    }
  }
  ```

### 5.3 Category Mapping

- **Location:** `app/web.py` - `categorize_networking_status()` function
- **Update:** Modify function to map new statuses to new categories
- **Backward Compatibility:** Maintain old status handling during transition period

---

## 6. Migration Strategy

### 6.1 Migration Steps

1. **Backup Existing Data**
   - Create backup of all `metadata.yaml` files
   - Export current status distribution report

2. **Update Status Definitions**
   - Update `NetworkingContact` model default status
   - Update `get_next_step()` method with new status mappings
   - Update `categorize_networking_status()` function

3. **Migrate Existing Contacts**
   - Read all contact metadata files
   - Apply status mapping (old → new)
   - Update metadata.yaml files
   - Preserve status_updated_at timestamps

4. **Update UI Components**
   - Update networking dashboard filters
   - Update status dropdowns
   - Update status display badges
   - Update category displays

5. **Calculate Historical Badges**
   - Analyze all contact status histories
   - Calculate badges retroactively
   - Initialize rewards.json file

6. **Update Activity Logging**
   - Ensure new statuses are logged correctly
   - Update activity log parsing if needed

### 6.2 Migration Script Requirements

- **Dry Run Mode:** Test migration without making changes
- **Rollback Capability:** Ability to restore from backup
- **Progress Reporting:** Show migration progress and statistics
- **Validation:** Verify all contacts migrated successfully
- **Error Handling:** Handle edge cases and malformed data gracefully

---

## 7. UI/UX Changes

### 7.1 Application Hero Section

**Location:** Application detail page header (sample_application_detail.html)

**New Components:**
- Badge display section showing:
  - Progress bars for in-progress badges
  - Achievement badges (locked/unlocked)
  - Total points earned
  - Points breakdown by badge

**Design Requirements:**
- Compact, non-intrusive design
- Visual distinction between locked/unlocked badges
- Progress indicators for badges in progress
- Tooltips showing badge requirements

### 7.2 Networking Dashboard

**Updates:**
- Update status filter buttons to new status names
- Update category groupings
- Update status badges styling
- Update next step text for new statuses

### 7.3 Reports Section

**New Report:** "Networking Rewards by Category"
- Display points earned by pipeline phase
- Show breakdown: Prospecting, Outreach, Engagement, Nurture
- Include total points and badge counts per category

---

## 8. Implementation Phases

### Phase 1: Core Status System Migration
- Update status definitions in code
- Create migration script
- Migrate existing contacts
- Update UI components

### Phase 2: Badge System Foundation
- Create badge calculation service
- Implement badge storage (JSON)
- Create badge display components
- Integrate into application hero section

### Phase 3: Reward Tracking & Reporting
- Implement real-time badge calculation
- Create points tracking system
- Build category-based points report
- Add historical badge calculation

### Phase 4: Testing & Refinement
- Test migration with real data
- Validate badge calculations
- Test UI components
- Performance optimization

---

## 9. Risk Mitigation

### 9.1 Data Loss Risks

**Risk:** Migration corrupts contact data  
**Mitigation:**
- Comprehensive backup before migration
- Dry-run mode for testing
- Rollback script availability
- Validation checks after migration

### 9.2 Breaking Changes

**Risk:** Existing functionality breaks with new statuses  
**Mitigation:**
- Maintain backward compatibility during transition
- Update all status references systematically
- Comprehensive testing before deployment
- Gradual rollout if possible

### 9.3 Performance Impact

**Risk:** Badge calculation slows down application  
**Mitigation:**
- Cache badge calculations
- Incremental updates on status changes
- Batch processing for historical data
- Lazy loading of badge data

### 9.4 Badge Calculation Accuracy

**Risk:** Incorrect badge awards or missing badges  
**Mitigation:**
- Comprehensive test cases for each badge
- Validation logic for badge triggers
- Audit trail for badge awards
- Manual review capability

---

## 10. Success Criteria

1. ✅ All existing contacts successfully migrated to new status system
2. ✅ All UI components display new statuses correctly
3. ✅ Badge system calculates and displays correctly
4. ✅ Historical badges calculated accurately
5. ✅ Application hero section displays badges appropriately
6. ✅ Category-based points report available in Reports section
7. ✅ No data loss during migration
8. ✅ Performance remains acceptable
9. ✅ All existing functionality continues to work
10. ✅ Documentation updated

---

## 11. Open Questions & Decisions

### Resolved Decisions

1. **Badge Display Location:** Application Hero section ✅
2. **Badge Storage:** JSON file with incremental updates ✅
3. **Application Filtering:** Company name exact match ✅
4. **Badge Display Format:** Progress bars + achievement badges ✅
5. **Historical Badges:** Retroactively calculate ✅
6. **Points Display:** By badge + total, with category report ✅

### Pending Clarifications

- None at this time

---

## 12. References

- Current Status System: `app/models/networking_contact.py`
- Status Categorization: `app/web.py` - `categorize_networking_status()`
- Contact Storage: `data/networking/{ContactName}-{CompanyName}/metadata.yaml`
- Application Detail Page: `app/templates/web/sample_application_detail.html`
- Networking Dashboard: `app/templates/web/networking_dashboard.html`

---

**Document Version:** 1.0  
**Last Updated:** December 15, 2025  
**Author:** Implementation Team
