# Networking Workflow - Original Requirements

## User Request (December 12, 2025)

### Overview
"This is a big change so please act with the rigor that it requires and do not guess or change the existing functionality. Today the app focuses on tracking job applications I want to create a similar workflow for networking."

### Core Functionality

#### Input & Profile Creation
In this workflow I will provide you with a person's resume from LinkedIn or articles written by the person. You will create a dashboard (Networking Dashboard).

#### Dashboard Tiles
The tiles will have the same information as the current dashboard. Each tile will have the following:
- `<person Name>`
- `<matchPercent>% (⚐)`
- `<latest company name>`
- `<latest job title>`
- `<networking Status>`
- `📅 Connection sent: <creation datetime in EST>`
- `🔄 Updated: <last update change datetime in EST>`
- `<view Summary Button>`

#### Details Page Tabs
The details page will render in the same format as the existing pages for job applications with the following tabs:

1. **Summary** - Suggest a summary of relevant items about the person
2. **Raw Entry** - Raw text entered in the person's profiling
3. **Skills** - Match Skills as you do today
4. **Research** - Public information found about the person
   - Suggest sections (Research their background, company, or recent activity to personalize your message)
5. **Qualifications Analysis (Rename to "Match")** - This is important. This is where you will find commonalities and differences and suggest topics of conversations for networking meeting.
6. **Messages**:
   - **Initial connection request or message**: Draft the same messages you do to hiring managers (Less than 300 Characters) but instead of focus on a position will be an intro of myself to the person. These messages can be provocative and must have linkage with the commonalities found on the qualifications analysis.
   - **Meeting invitation**: A short message inviting them to meet with me 1:1 for a meet and greet thanking them for accepting the connection invitation
   - **Thank you message**: Message to thank them for meeting with me
   - **Consulting services offer**: One more message that offers consulting services
7. **Updates and Notes** - Everything exactly the same except for the "Select Status" Dropdown content

**DO NOT CREATE**: Customized resume or cover letter

#### Google Calendar Integration
- Create a Google calendar invite
- Set a follow-up reminder for 7 business days after initial connection for a response
- Event type: All day event
- Status: Free
- Title/Subject: `<Person Name>`
- Description: Follow up LinkedIn message draft, link to LinkedIn profile, email address if available

### 16-Status Networking Workflow

#### Prospecting Phase
1. **To Research**
   - Description: The contact is identified (e.g., from an event list, LinkedIn search, article) but you haven't yet gathered personalized talking points
   - Next Action: Research their background, company, or recent activity to personalize your message

2. **Ready to Contact**
   - Description: Research is complete. You have a personalized message drafted and are ready to send
   - Next Action: Send the initial connection request or message (e.g., on LinkedIn, email)

3. **Contacted - Sent**
   - Description: The initial connection request or message has been sent
   - Next Action: Set a follow-up reminder. Wait a few days (e.g., 5-7 business days) for a response

#### Engagement Phase
4. **Contacted - Replied**
   - Description: The contact has responded to your initial message (Move to Engagement Phase)
   - Next Action: Log the reply, craft a thoughtful response, and propose a specific next step (e.g., a brief call)

5. **Contacted - No Response**
   - Description: The initial follow-up window has passed without a reply
   - Next Action: Send a second, polite follow-up message

6. **Cold/Archive**
   - Description: After one or two follow-ups, there is still no response
   - Next Action: Stop active outreach. Move them to a "Cold" list for occasional, low-effort contact (e.g., sending an interesting article relevant to their work 3-6 months later)

7. **In Conversation**
   - Description: You are currently exchanging messages or emails to set up a meeting or discuss a topic
   - Next Action: Keep the conversation moving toward a scheduled call or meeting

#### Meeting Phase
8. **Meeting Scheduled**
   - Description: A call, video chat, or in-person meeting has been confirmed on the calendar
   - Next Action: Prepare for the meeting, send a brief confirmation/agenda, and log meeting details afterward

9. **Meeting Complete**
   - Description: You have had the informational interview, coffee chat, or initial discovery call
   - Next Action: Send a thank-you note within 24 hours. Log key takeaways and the agreed-upon next step

10. **Action Pending - You**
    - Description: You committed to an action (e.g., sending a resource, making an introduction)
    - Next Action: Complete the action and update the status

11. **Action Pending - Them**
    - Description: The contact committed to an action (e.g., providing a referral, reviewing material)
    - Next Action: Set a reminder to follow up if their promised action isn't delivered in a reasonable timeframe

#### Relationship Phase (Successful Establishment)
12. **New Connection**
    - Description: A successful initial conversation is complete, but the relationship is still nascent
    - Next Action: Schedule a light, value-add check-in in 1-2 months

13. **Nurture (1-3 Mo.)**
    - Description: A valuable connection that you want to check in with every 1 to 3 months
    - Next Action: Set a specific date for your next check-in (e.g., send a relevant article, a brief note)

14. **Nurture (4-6 Mo.)**
    - Description: A strong, established connection that requires less frequent, but still intentional, engagement
    - Next Action: Schedule a reminder to reach out in 4-6 months, perhaps to catch up on recent projects

15. **Referral Partner**
    - Description: This contact is a strong advocate or a source of valuable referrals/opportunities
    - Next Action: Prioritize providing value to them and proactively seek ways to help them in return

16. **Inactive/Dormant**
    - Description: A good connection, but you haven't engaged in over 6-12 months
    - Next Action: Look for an opportunity to genuinely re-engage (e.g., congratulate them on a work anniversary)

### Color Coding by Timing

**Revised Color Scheme:**
- **White**: Recent activity (<7 days)
- **Green**: Needs activity (8-15 days)
- **Yellow**: Approaching follow-up (15-30 days)
- **Red**: Overdue follow-ups (30-60 days for "Contacted" status)
- **Blue**: Nurture/scheduled future contact (60-90 days for "Contacted" status)
- **Gray**: Cold/Archive (>90 days for workflow Prospecting statuses)

**Dashboard Filters**: Create filters for these timing categories

### Entry Fields (New Networking Connection Form)
- **Person Name** (mandatory)
- **Company Name** (mandatory)
- **Job Title** (optional)
- **Link** (optional)
- **Profile details** (mandatory)

### Implementation Requirements
- Organize the provided information
- Reuse as much code as possible from the existing codebase
- Keep this implementation simple and not affect any current functionality
- Discuss impact on daily activities, reports, and analytics modules
- Create a plan to implement this with milestones

### Key Design Decisions (User Clarifications)

#### Data Architecture
- Separate `NetworkingContact` model with its own `data/networking/` folder structure
- Reuse patterns from the `Application` model

#### Match Score Basis
- Comprehensive score based on:
  - Skill overlap
  - Career similarity
  - Common interests
  - Overall networking value

#### Reports Integration
- Combined reports with a filter to switch between "Jobs", "Networking", or "Both"

#### Daily Activities Integration
- Mixed chronological view with visual indicators for type

#### Profile Details Format
- Markdown formatted text

#### Extended Metadata Fields
- Location
- Latest Company
- Job Title
- Connection Date
- Updated Date
- Contact Count
- LinkedIn URL
- Email (if available)
- Last Interaction Type

### Navigation Requirements

#### Standard Menu Structure
All pages should have consistent navigation:
1. **App Dash** (renamed from Dashboard)
2. New Application
3. **Network Dash** (renamed from Networking)
4. New Contact
5. Templates
6. Progress
7. Reports
8. Analytics
9. Daily Activities
10. Check AI Status
11. Manage Resume

#### Menu Format
- Text-based navigation (no emojis)
- Consistent styling across all pages
- Standard sidebar layout (180px width)

---

## Success Criteria

The networking workflow implementation is considered complete when:

1. ✅ Users can create networking contacts with profile information
2. ✅ AI analyzes match percentage and generates conversation topics
3. ✅ Four types of messages are auto-generated
4. ✅ Google Calendar reminders can be created
5. ✅ 16-status workflow is fully functional
6. ✅ Color-coded timing system works on dashboard
7. ✅ Integrated into Reports (with type filter)
8. ✅ Integrated into Daily Activities (mixed view)
9. ✅ No impact on existing job application functionality
10. ✅ Consistent navigation across all pages
11. ✅ Complete documentation provided

---

**Date**: December 12, 2025
**Requestor**: Kervin Leacock
**Implementation**: Complete - All phases delivered
