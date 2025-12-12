# Networking Feature Guide

## Overview
The Networking feature allows you to track professional contacts, manage networking relationships, and generate AI-powered messages for LinkedIn outreach, similar to how job applications are tracked.

## Quick Start

### Creating a Networking Contact
1. Navigate to `/new-networking-contact` or click "New Contact" in the sidebar
2. Fill in the required fields:
   - **Person Name** (required): Full name of the contact
   - **Company Name** (required): Current company
   - **Job Title** (optional): Current position
   - **LinkedIn URL** (optional): Link to their LinkedIn profile
   - **Profile Details** (required): Paste their resume, LinkedIn profile text, or articles

### Viewing Networking Contacts
- **Dashboard**: Visit `/networking` to see all contacts in tiles
- **Filters**:
  - **Status Filters**: To Research, Contacted, In Conversation, Meetings, etc.
  - **Timing Filters**: All, Recent (<7 days), Needs Activity (8-15 days), Approaching (15-30 days), Overdue (30-60 days), Nurture (60-90 days), Cold (>90 days)

### Contact Details Page
Each contact has a detailed summary page (`/networking/<contact-folder>/<contact-name>-summary.html`) with tabs:
- **Summary**: AI-generated overview of relevant items
- **Raw Entry**: Original profile text you entered
- **Messages**: 4 AI-generated messages
  1. Initial connection request (<300 characters)
  2. Meeting invitation
  3. Thank you message
  4. Consulting services offer
- **Skills**: Skill overlap between your resume and their profile
- **Research**: Public information and background
- **Match**: Commonalities, differences, and conversation topics
- **Updates & Notes**: Timeline of status changes and custom notes

### Google Calendar Integration
Each contact page has a "📅 Add Follow-up to Google Calendar" button that creates a reminder event:
- **When**: 7 business days after initial connection
- **Type**: All-day event
- **Includes**: Contact details, LinkedIn URL, suggested actions

## 16-Status Networking Workflow

### Prospecting Phase
1. **To Research**: Contact identified, need to gather talking points
2. **Ready to Contact**: Research complete, message drafted
3. **Contacted - Sent**: Initial connection request/message sent

### Engagement Phase
4. **Contacted - Replied**: They responded (move to engagement)
5. **Contacted - No Response**: Follow-up window passed, no reply
6. **Cold/Archive**: No response after 1-2 follow-ups
7. **In Conversation**: Exchanging messages to set up meeting

### Meeting Phase
8. **Meeting Scheduled**: Call/meeting confirmed on calendar
9. **Meeting Complete**: Initial meeting finished
10. **Action Pending - You**: You committed to an action
11. **Action Pending - Them**: They committed to an action

### Relationship Phase
12. **New Connection**: Successful initial conversation complete
13. **Nurture (1-3 Mo.)**: Check in every 1-3 months
14. **Nurture (4-6 Mo.)**: Check in every 4-6 months
15. **Referral Partner**: Strong advocate/source of referrals
16. **Inactive/Dormant**: Haven't engaged in 6-12 months

## Reports Integration

### Accessing Reports
Visit `/reports` and use the **Type Filter**:
- **Jobs**: Show only job applications
- **Networking**: Show only networking contacts
- **Both**: Combined view with "Net:" prefix for networking statuses

### Metrics Included
- Total applications/contacts
- Status distribution charts
- Daily/cumulative activities
- Follow-up needed list (>7 days without update)
- Flagged items

## Daily Activities Integration

### Mixed Chronological View
Visit `/daily-activities` to see a combined timeline of all activities:
- **Job Activities**: 💼 icon with blue "Job" badge
- **Networking Activities**: 🤝 icon with green "Networking" badge
- Activities are sorted chronologically within each day
- Each activity shows:
  - Company name
  - Position/title
  - Activity type (Created, Status Changed, etc.)
  - Status badge
  - Timestamp (EST)

## API Endpoints

### Networking Contacts
- `POST /api/networking/contacts` - Create new contact
- `GET /api/networking/contacts` - List all contacts
- `GET /api/networking/contacts/<contact_id>` - Get contact details
- `PUT /api/networking/contacts/<contact_id>/status` - Update status
- `PUT /api/networking/contacts/<contact_id>/details` - Update details
- `PUT /api/networking/contacts/<contact_id>/flag` - Toggle flag
- `POST /api/networking/contacts/<contact_id>/regenerate` - Regenerate AI analysis
- `GET /networking/<path:filepath>` - Serve networking files

### Reports
- `GET /api/reports?period={period}&type={type}`
  - **period**: today, yesterday, 7days, 30days, all
  - **type**: jobs, networking, both

### Daily Activities
- `GET /api/daily-activities` - Returns combined job + networking activities

## Color Coding by Timing

Contact tiles are color-coded based on days since last update:
- **White**: Recent activity (<7 days)
- **Green**: Needs activity (8-15 days)
- **Yellow**: Approaching follow-up (15-30 days)
- **Red**: Overdue follow-ups (30-60 days for "Contacted" status)
- **Blue**: Nurture/scheduled future contact (60-90 days)
- **Gray**: Cold/Archive (>90 days for prospecting statuses)

## Best Practices

1. **Research First**: Always move from "To Research" to "Ready to Contact" after gathering personalized talking points
2. **Use AI Messages**: Review and customize the AI-generated messages before sending
3. **Set Follow-ups**: Use the Google Calendar integration to never miss a follow-up
4. **Flag Important**: Use the flag feature for high-priority contacts
5. **Update Status**: Keep the status current to benefit from timing-based color coding
6. **Add Notes**: Use "Updates & Notes" to track conversation details
7. **Review Match Tab**: Check conversation topics before meetings

## Data Storage

Networking contacts are stored in `data/networking/` with this structure:
```
data/networking/
  └── Person-Name-Company-Name/
      ├── metadata.yaml
      ├── YYYYMMDDHHMMSS-Person Name-raw.txt
      ├── YYYYMMDDHHMMSS-Person Name-profile.md
      ├── YYYYMMDDHHMMSS-Person Name-match_analysis.md
      ├── YYYYMMDDHHMMSS-Person Name-messages.md
      ├── Person-Name-summary.html
      └── YYYYMMDDHHMMSS-update-Status.html (multiple)
```

## Troubleshooting

### Contact Not Appearing
- Ensure Ollama is running and connected
- Check that base resume is loaded
- Verify profile details were provided

### Messages Not Generated
- Documents are generated asynchronously
- Check browser console for errors
- Try regenerating with the "🔄 Regenerate Documents" button

### Calendar Button Not Working
- Ensure popup blockers are disabled
- Check that Google Calendar is accessible
- Verify the Google Calendar URL is properly formatted

## Future Enhancements
- Email integration
- LinkedIn automation
- CRM export
- Relationship strength scoring
- Referral tracking
