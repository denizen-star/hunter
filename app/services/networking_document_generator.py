"""Document generation service for networking contacts"""
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.models.networking_contact import NetworkingContact
from app.services.networking_analyzer import NetworkingAnalyzer
from app.services.ai_analyzer import AIAnalyzer
from app.utils.file_utils import write_text_file, read_text_file
from app.utils.datetime_utils import format_for_display


class NetworkingDocumentGenerator:
    """Generates documents and messages for networking contacts"""
    
    def __init__(self):
        self.networking_analyzer = NetworkingAnalyzer()
        self.ai_analyzer = AIAnalyzer()
    
    def generate_all_documents(
        self,
        contact: NetworkingContact,
        resume_content: str
    ) -> None:
        """Generate all networking documents for a contact"""
        print(f"  → Generating networking documents for {contact.person_name}...")
        
        # Read profile details
        if not contact.profile_path or not contact.profile_path.exists():
            print("  ⚠ Warning: Profile path not found, skipping document generation")
            return
        
        profile_details = read_text_file(contact.profile_path)
        
        # 1. Generate AI match analysis
        print("  → Analyzing networking match...")
        match_result = self.networking_analyzer.analyze_networking_match(
            resume_content=resume_content,
            profile_details=profile_details,
            person_name=contact.person_name,
            company_name=contact.company_name,
            job_title=contact.job_title
        )
        
        # Save match analysis
        match_analysis_path = contact.folder_path / f"{contact.person_name.replace(' ', '-')}-match-analysis.txt"
        write_text_file(match_result['detailed_analysis'], match_analysis_path)
        contact.match_analysis_path = match_analysis_path
        contact.match_score = match_result['match_score']
        
        print(f"  ✓ Match score: {contact.match_score:.1f}%")
        
        # 2. Generate messages
        print("  → Generating networking messages...")
        messages = self.generate_networking_messages(
            contact=contact,
            match_analysis=match_result['detailed_analysis'],
            your_name="Kervin"  # TODO: Get from resume
        )
        
        # Save messages
        messages_path = contact.folder_path / f"{contact.person_name.replace(' ', '-')}-messages.txt"
        messages_content = self._format_messages_file(messages)
        write_text_file(messages_content, messages_path)
        contact.messages_path = messages_path
        
        print("  ✓ Messages generated")
        
        # 3. Generate calendar invite
        print("  → Generating calendar invite...")
        calendar_invite = self.generate_calendar_invite(contact)
        calendar_path = contact.folder_path / "calendar_reminder.txt"
        write_text_file(calendar_invite, calendar_path)
        contact.calendar_invite_generated = True
        print("  ✓ Calendar invite generated")
        
        # 4. Generate summary page
        print("  → Generating summary page...")
        self.generate_summary_page(contact, match_result['detailed_analysis'], messages)
        print("  ✓ Summary page generated")
    
    def generate_networking_messages(
        self,
        contact: NetworkingContact,
        match_analysis: str,
        your_name: str
    ) -> Dict[str, str]:
        """
        Generate 4 types of networking messages:
        1. Initial connection request (<300 chars)
        2. Meeting invitation
        3. Thank you message
        4. Consulting services offer
        """
        
        # Extract conversation starters and commonalities
        conversation_topics = self.networking_analyzer.extract_conversation_starters(match_analysis)
        commonalities = self.networking_analyzer.generate_connection_commonalities(match_analysis)
        
        messages = {}
        
        # 1. Initial Connection Request (LinkedIn - <300 chars)
        connection_prompt = f"""Write a LinkedIn connection request message (MUST BE UNDER 300 CHARACTERS).

PERSON: {contact.person_name}
COMPANY: {contact.company_name}
{f'TITLE: {contact.job_title}' if contact.job_title else ''}

SHARED CONTEXT:
{', '.join(conversation_topics[:2])}

REQUIREMENTS:
- MAXIMUM 300 characters (including spaces)
- Provocative and engaging
- Reference a specific commonality or their work
- Professional but personable
- No generic "I'd like to connect" phrases
- Make them curious to accept

Format: Just the message text, no subject line."""

        try:
            connection_msg = self.ai_analyzer._call_ollama(connection_prompt)
            # Ensure it's under 300 chars
            if len(connection_msg) > 300:
                connection_msg = connection_msg[:297] + "..."
            messages['connection_request'] = connection_msg.strip()
        except Exception as e:
            messages['connection_request'] = f"Hi {contact.person_name}, I noticed your work at {contact.company_name} and would love to connect and exchange insights."
        
        # 2. Meeting Invitation Message
        meeting_prompt = f"""Write a message inviting them to a 1:1 meet & greet after they accepted your LinkedIn connection.

PERSON: {contact.person_name}
COMPANY: {contact.company_name}

CONVERSATION TOPICS:
{chr(10).join(f'- {topic}' for topic in conversation_topics[:3])}

REQUIREMENTS:
- Thank them for accepting the connection
- Briefly mention why you're reaching out (reference commonality)
- Suggest a casual 15-20 minute virtual coffee chat
- Keep it light and low-pressure
- 3-4 short paragraphs

Format as a LinkedIn message or email."""

        try:
            messages['meeting_invitation'] = self.ai_analyzer._call_ollama(meeting_prompt).strip()
        except:
            messages['meeting_invitation'] = f"Thanks for connecting! I'd love to chat briefly about our shared interests in [topic]. Would you have 15-20 minutes for a virtual coffee?"
        
        # 3. Thank You Message (Post-Meeting)
        thankyou_prompt = f"""Write a thank you message to send after meeting with them.

PERSON: {contact.person_name}
COMPANY: {contact.company_name}

REQUIREMENTS:
- Thank them for their time
- Reference 1-2 specific things discussed (use placeholders like [topic discussed])
- Mention one actionable follow-up or insight gained
- Keep it warm and genuine
- Offer to stay in touch
- 2-3 short paragraphs

Format as a LinkedIn message or email."""

        try:
            messages['thank_you'] = self.ai_analyzer._call_ollama(thankyou_prompt).strip()
        except:
            messages['thank_you'] = f"Thanks for the great conversation! I really enjoyed discussing [topic]. Let's definitely stay in touch."
        
        # 4. Consulting Services Offer
        consulting_prompt = f"""Write a professional message offering consulting services (appropriate timing: after building rapport).

PERSON: {contact.person_name}
COMPANY: {contact.company_name}

YOUR EXPERTISE: Data Engineering, Analytics, AI/ML Implementation, Technical Leadership

REQUIREMENTS:
- Position yourself as someone who can provide value
- Reference their company's potential needs (generic but relevant to their industry)
- Keep it consultative, not salesy
- Offer a brief discovery call
- Professional and respectful of their time
- 3-4 short paragraphs

Format as an email or LinkedIn message."""

        try:
            messages['consulting_offer'] = self.ai_analyzer._call_ollama(consulting_prompt).strip()
        except:
            messages['consulting_offer'] = f"Given our previous conversations, I wanted to reach out about potential consulting opportunities where I could add value to {contact.company_name}'s data initiatives."
        
        return messages
    
    def _extract_skills_html(self, match_analysis: str, skill_type: str) -> str:
        """Extract and format skills from match analysis as HTML badges"""
        # Parse skills from match analysis
        skills = []
        
        if skill_type == 'shared':
            # Extract shared skills from "Shared Skills:" section
            in_section = False
            for line in match_analysis.split('\n'):
                if 'Shared Skills:' in line or 'SKILL OVERLAP:' in line:
                    in_section = True
                    continue
                if in_section:
                    if line.strip().startswith('-'):
                        skill = line.strip()[1:].strip()
                        # Split by comma if multiple skills on one line
                        skills.extend([s.strip() for s in skill.split(',')])
                    elif line.strip() and not line.strip().startswith('-'):
                        # End of section
                        break
        
        # For "yours" and "theirs", we'll just show a message for now
        # since the AI doesn't separate them explicitly
        if not skills and skill_type == 'shared':
            skills = ['Data Engineering', 'Analytics', 'Python', 'SQL', 'Cloud Computing']
        
        if skill_type == 'yours':
            return '<span style="padding: 6px 12px; background: #dbeafe; color: #1e40af; border-radius: 6px; font-size: 13px;">Your unique skills will be highlighted in future updates</span>'
        elif skill_type == 'theirs':
            return '<span style="padding: 6px 12px; background: #fef3c7; color: #92400e; border-radius: 6px; font-size: 13px;">Their unique skills will be highlighted in future updates</span>'
        
        # Return HTML badges for shared skills
        if not skills:
            return '<span style="color: #6b7280;">No skills identified</span>'
        
        return ''.join([
            f'<span style="padding: 6px 12px; background: #d1fae5; color: #065f46; border-radius: 6px; font-size: 13px; font-weight: 500;">{skill}</span>'
            for skill in skills[:10]  # Limit to 10 skills
        ])
    
    def generate_google_calendar_url(self, contact: NetworkingContact) -> str:
        """Generate Google Calendar URL for follow-up reminder"""
        from datetime import timedelta
        from urllib.parse import urlencode
        
        # Calculate 7 business days from connection date
        follow_up_date = contact.created_at
        business_days = 0
        while business_days < 7:
            follow_up_date += timedelta(days=1)
            # Skip weekends (5=Saturday, 6=Sunday)
            if follow_up_date.weekday() < 5:
                business_days += 1
        
        # Format as all-day event (date only, no time)
        date_str = follow_up_date.strftime('%Y%m%d')
        
        # Event title
        title = f"Follow up: {contact.person_name}"
        
        # Event description
        description = f"""Follow-up for LinkedIn connection with {contact.person_name}

Company: {contact.company_name}
{f'Title: {contact.job_title}' if contact.job_title else ''}
Status: {contact.status}

LinkedIn: {contact.linkedin_url if contact.linkedin_url else 'N/A'}
Email: {contact.email if contact.email else 'Not available'}

Suggested Actions:
- Check if they accepted your connection request
- Send meeting invitation if they accepted
- Review their recent LinkedIn activity
- Send polite follow-up if no response

View Profile: http://localhost:51003/networking/{contact.folder_path.name}/{contact.person_name.replace(' ', '-')}-summary.html
"""
        
        # Build Google Calendar URL
        params = {
            'action': 'TEMPLATE',
            'text': title,
            'dates': f'{date_str}/{date_str}',  # All-day event (same start and end date)
            'details': description,
            'location': contact.company_name,
            'sf': 'true',  # Show event details
            'output': 'xml'  # XML output
        }
        
        return f"https://calendar.google.com/calendar/render?{urlencode(params)}"
    
    def generate_calendar_invite(self, contact: NetworkingContact) -> str:
        """Generate Google Calendar invite details for follow-up reminder"""
        from datetime import timedelta
        
        # Calculate 7 business days from connection date
        follow_up_date = contact.created_at
        business_days = 0
        while business_days < 7:
            follow_up_date += timedelta(days=1)
            # Skip weekends (5=Saturday, 6=Sunday)
            if follow_up_date.weekday() < 5:
                business_days += 1
        
        # Format calendar invite
        invite_content = f"""GOOGLE CALENDAR FOLLOW-UP REMINDER

Event Details:
-------------
Title: Follow up: {contact.person_name}
Date: {follow_up_date.strftime('%B %d, %Y')} (7 business days after connection)
Time: All-day event
Status: Free
Reminder: 1 day before

Description:
-----------
Follow-up for LinkedIn connection with {contact.person_name}

Company: {contact.company_name}
{f'Title: {contact.job_title}' if contact.job_title else ''}
Status: {contact.status}

LinkedIn Profile: {contact.linkedin_url if contact.linkedin_url else 'N/A'}
Email: {contact.email if contact.email else 'Not available'}

Suggested follow-up action:
- If no response: Send polite follow-up message
- If accepted: Send meeting invitation message
- Check their recent activity on LinkedIn

View full profile: http://localhost:51003/networking/{contact.folder_path.name}/{contact.person_name.replace(' ', '-')}-summary.html

---
Generated by Hunter Networking System
"""
        
        return invite_content
    
    def _format_messages_file(self, messages: Dict[str, str]) -> str:
        """Format messages into a readable text file"""
        content = "NETWORKING MESSAGES\n"
        content += "=" * 80 + "\n\n"
        
        content += "1. INITIAL CONNECTION REQUEST (LinkedIn - Under 300 chars)\n"
        content += "-" * 80 + "\n"
        content += messages.get('connection_request', 'N/A')
        content += f"\n\nCharacter count: {len(messages.get('connection_request', ''))}\n\n"
        
        content += "2. MEETING INVITATION MESSAGE\n"
        content += "-" * 80 + "\n"
        content += messages.get('meeting_invitation', 'N/A')
        content += "\n\n"
        
        content += "3. THANK YOU MESSAGE (Post-Meeting)\n"
        content += "-" * 80 + "\n"
        content += messages.get('thank_you', 'N/A')
        content += "\n\n"
        
        content += "4. CONSULTING SERVICES OFFER\n"
        content += "-" * 80 + "\n"
        content += messages.get('consulting_offer', 'N/A')
        content += "\n"
        
        return content
    
    def generate_summary_page(
        self,
        contact: NetworkingContact,
        match_analysis: str,
        messages: Dict[str, str]
    ) -> None:
        """Generate HTML summary page with tabs"""
        
        # Read raw profile
        raw_profile = ""
        if contact.raw_profile_path and contact.raw_profile_path.exists():
            raw_profile = read_text_file(contact.raw_profile_path)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{contact.person_name} - {contact.company_name}</title>
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            color: #1f2937;
            line-height: 1.6;
        }}
        
        .header {{
            background: white;
            border-bottom: 2px solid #e5e7eb;
            padding: 24px 32px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            color: #6b7280;
        }}
        
        .match-badge {{
            display: inline-block;
            padding: 6px 16px;
            background: #d1fae5;
            color: #065f46;
            border-radius: 6px;
            font-weight: 600;
            font-size: 18px;
            margin-left: 12px;
        }}
        
        .metadata {{
            background: #f9fafb;
            padding: 16px 32px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            font-size: 14px;
        }}
        
        .metadata-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .metadata-item strong {{
            color: #374151;
        }}
        
        .tabs {{
            background: white;
            border-bottom: 1px solid #e5e7eb;
            padding: 0 32px;
            display: flex;
            gap: 8px;
        }}
        
        .tab {{
            padding: 16px 24px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            font-weight: 600;
            color: #6b7280;
            transition: all 0.15s ease;
        }}
        
        .tab:hover {{
            color: #374151;
        }}
        
        .tab.active {{
            color: #3b82f6;
            border-bottom-color: #3b82f6;
        }}
        
        .content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 32px;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .section {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        
        .section h2 {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1f2937;
        }}
        
        .section h3 {{
            font-size: 16px;
            font-weight: 600;
            margin: 16px 0 8px 0;
            color: #374151;
        }}
        
        .message-box {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            position: relative;
        }}
        
        .message-box h3 {{
            margin-top: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        .form-group label {{
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }}
        
        .form-group select,
        .form-group textarea {{
            width: 100%;
            padding: 10px 14px;
            font-size: 14px;
            font-family: inherit;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            background: white;
            color: #1f2937;
            transition: all 0.15s ease;
        }}
        
        .form-group select:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}
        
        .form-group textarea {{
            min-height: 100px;
            resize: vertical;
        }}
        
        .btn {{
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.15s ease;
            font-family: inherit;
        }}
        
        .btn-primary {{
            background: #3b82f6;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #2563eb;
        }}
        
        .btn-primary:disabled {{
            background: #9ca3af;
            cursor: not-allowed;
        }}
        
        .timeline {{
            margin-top: 32px;
        }}
        
        .timeline-item {{
            padding: 16px;
            border-left: 3px solid #e5e7eb;
            margin-bottom: 16px;
            background: #f9fafb;
            border-radius: 0 8px 8px 0;
        }}
        
        .timeline-item.latest {{
            border-left-color: #3b82f6;
        }}
        
        .timeline-date {{
            font-size: 13px;
            color: #6b7280;
            margin-bottom: 4px;
        }}
        
        .timeline-status {{
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
        }}
        
        .timeline-notes {{
            color: #374151;
            font-size: 14px;
        }}
        
        .alert {{
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }}
        
        .alert.success {{
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #10b981;
        }}
        
        .alert.error {{
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #ef4444;
        }}
        
        .alert.show {{
            display: block;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }}
        
        .btn-secondary {{
            background: white;
            color: #374151;
            border: 1px solid #d1d5db;
        }}
        
        .btn-secondary:hover {{
            background: #f9fafb;
        }}
        
        .copy-btn {{
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 6px;
            border: 1px solid #d1d5db;
            background: white;
            color: #374151;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        
        .copy-btn:hover {{
            background: #f3f4f6;
        }}
        
        .char-count {{
            font-size: 12px;
            color: #6b7280;
            margin-top: 8px;
        }}
        
        pre {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1>
                    {contact.person_name}
                    <span class="match-badge">{contact.match_score:.0f}% Match</span>
                </h1>
                <div class="subtitle">{contact.company_name}{f' • {contact.job_title}' if contact.job_title else ''}</div>
                <div class="action-buttons">
                    <a href="{self.generate_google_calendar_url(contact)}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">
                        📅 Add Follow-up to Google Calendar
                    </a>
                    <button onclick="regenerateDocuments()" class="btn btn-secondary" id="regenerateBtn">
                        🔄 Regenerate Documents
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="metadata">
        <div class="metadata-item">
            <span>📍</span>
            <span>{contact.location or 'N/A'}</span>
        </div>
        <div class="metadata-item">
            <span>📅</span>
            <span><strong>Connected:</strong> {format_for_display(contact.created_at)}</span>
        </div>
        <div class="metadata-item">
            <span>🔄</span>
            <span><strong>Updated:</strong> {format_for_display(contact.status_updated_at or contact.created_at)}</span>
        </div>
        <div class="metadata-item">
            <span>📊</span>
            <span><strong>Status:</strong> {contact.status}</span>
        </div>
        {f'<div class="metadata-item"><span>🔗</span><a href="{contact.linkedin_url}" target="_blank">LinkedIn Profile</a></div>' if contact.linkedin_url else ''}
        {f'<div class="metadata-item"><span>📧</span><span>{contact.email}</span></div>' if contact.email else ''}
    </div>
    
    <div class="tabs">
        <div class="tab active" onclick="switchTab('summary')">Summary</div>
        <div class="tab" onclick="switchTab('raw')">Raw Entry</div>
        <div class="tab" onclick="switchTab('skills')">Skills</div>
        <div class="tab" onclick="switchTab('research')">Research</div>
        <div class="tab" onclick="switchTab('messages')">Messages</div>
        <div class="tab" onclick="switchTab('updates')">Updates & Notes</div>
    </div>
    
    <div class="content">
        <!-- Summary Tab -->
        <div id="summary" class="tab-content active">
            <div class="section">
                <h2>Match Analysis</h2>
                <pre>{match_analysis}</pre>
            </div>
        </div>
        
        <!-- Raw Entry Tab -->
        <div id="raw" class="tab-content">
            <div class="section">
                <h2>Raw Profile Details</h2>
                <pre>{raw_profile}</pre>
            </div>
        </div>
        
        <!-- Skills Tab -->
        <div id="skills" class="tab-content">
            <div class="section">
                <h2>Skills Analysis</h2>
                <p style="color: #6b7280; margin-bottom: 16px;">
                    Comparison of your skills with {contact.person_name}'s profile.
                </p>
                
                <h3>Shared Skills</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">
                    {self._extract_skills_html(match_analysis, 'shared')}
                </div>
                
                <h3>Your Unique Skills</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px;">
                    {self._extract_skills_html(match_analysis, 'yours')}
                </div>
                
                <h3>Their Skills (Learning Opportunities)</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    {self._extract_skills_html(match_analysis, 'theirs')}
                </div>
            </div>
        </div>
        
        <!-- Research Tab -->
        <div id="research" class="tab-content">
            <div class="section">
                <h2>Research & Background</h2>
                <p style="color: #6b7280; margin-bottom: 16px;">
                    Use this section to track research about {contact.person_name} and their work.
                </p>
                
                <h3>Company Background</h3>
                <p><strong>{contact.company_name}</strong></p>
                {f'<p style="margin-top: 8px;">Industry insights and company information relevant to your conversation.</p>' if contact.company_name else ''}
                
                <h3>Recent Activity</h3>
                <p style="color: #6b7280; margin-top: 8px;">
                    Track their LinkedIn posts, articles, or recent accomplishments here.
                </p>
                
                <h3>Common Connections</h3>
                <p style="color: #6b7280; margin-top: 8px;">
                    Note any mutual connections or shared networks.
                </p>
                
                <h3>Notes</h3>
                <p style="color: #6b7280; margin-top: 8px;">
                    Add your research notes about their background, interests, or recent projects.
                </p>
            </div>
        </div>
        
        <!-- Messages Tab -->
        <div id="messages" class="tab-content">
            <div class="section">
                <h2>Networking Messages</h2>
                
                <div class="message-box">
                    <h3>
                        <span>1. Initial Connection Request (LinkedIn)</span>
                        <button class="copy-btn" onclick="copyMessage('connection')">Copy</button>
                    </h3>
                    <div id="connection-message">{messages.get('connection_request', 'N/A')}</div>
                    <div class="char-count">{len(messages.get('connection_request', ''))} characters</div>
                </div>
                
                <div class="message-box">
                    <h3>
                        <span>2. Meeting Invitation</span>
                        <button class="copy-btn" onclick="copyMessage('meeting')">Copy</button>
                    </h3>
                    <div id="meeting-message">{messages.get('meeting_invitation', 'N/A')}</div>
                </div>
                
                <div class="message-box">
                    <h3>
                        <span>3. Thank You Message</span>
                        <button class="copy-btn" onclick="copyMessage('thankyou')">Copy</button>
                    </h3>
                    <div id="thankyou-message">{messages.get('thank_you', 'N/A')}</div>
                </div>
                
                <div class="message-box">
                    <h3>
                        <span>4. Consulting Services Offer</span>
                        <button class="copy-btn" onclick="copyMessage('consulting')">Copy</button>
                    </h3>
                    <div id="consulting-message">{messages.get('consulting_offer', 'N/A')}</div>
                </div>
            </div>
        </div>
        
        <!-- Updates & Notes Tab -->
        <div id="updates" class="tab-content">
            <div class="section">
                <h2>Update Status</h2>
                
                <div id="updateAlert" class="alert"></div>
                
                <form id="statusUpdateForm">
                    <div class="form-group">
                        <label for="status">Select Status</label>
                        <select id="status" name="status" required>
                            <option value="">-- Select Status --</option>
                            <optgroup label="Research & Contact">
                                <option value="To Research" {"selected" if contact.status == "To Research" else ""}>To Research</option>
                                <option value="Ready to Contact" {"selected" if contact.status == "Ready to Contact" else ""}>Ready to Contact</option>
                                <option value="Contacted - Sent" {"selected" if contact.status == "Contacted - Sent" else ""}>Contacted - Sent</option>
                                <option value="Contacted - Replied" {"selected" if contact.status == "Contacted - Replied" else ""}>Contacted - Replied</option>
                                <option value="Contacted - No Response" {"selected" if contact.status == "Contacted - No Response" else ""}>Contacted - No Response</option>
                                <option value="Cold/Archive" {"selected" if contact.status == "Cold/Archive" else ""}>Cold/Archive</option>
                            </optgroup>
                            <optgroup label="Engagement">
                                <option value="In Conversation" {"selected" if contact.status == "In Conversation" else ""}>In Conversation</option>
                                <option value="Meeting Scheduled" {"selected" if contact.status == "Meeting Scheduled" else ""}>Meeting Scheduled</option>
                                <option value="Meeting Complete" {"selected" if contact.status == "Meeting Complete" else ""}>Meeting Complete</option>
                                <option value="Action Pending - You" {"selected" if contact.status == "Action Pending - You" else ""}>Action Pending - You</option>
                                <option value="Action Pending - Them" {"selected" if contact.status == "Action Pending - Them" else ""}>Action Pending - Them</option>
                            </optgroup>
                            <optgroup label="Relationship">
                                <option value="New Connection" {"selected" if contact.status == "New Connection" else ""}>New Connection</option>
                                <option value="Nurture (1-3 Mo.)" {"selected" if contact.status == "Nurture (1-3 Mo.)" else ""}>Nurture (1-3 Mo.)</option>
                                <option value="Nurture (4-6 Mo.)" {"selected" if contact.status == "Nurture (4-6 Mo.)" else ""}>Nurture (4-6 Mo.)</option>
                                <option value="Referral Partner" {"selected" if contact.status == "Referral Partner" else ""}>Referral Partner</option>
                                <option value="Inactive/Dormant" {"selected" if contact.status == "Inactive/Dormant" else ""}>Inactive/Dormant</option>
                            </optgroup>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="notes">Notes (optional)</label>
                        <textarea id="notes" name="notes" placeholder="Add any notes about this status update..."></textarea>
                    </div>
                    
                    <button type="submit" class="btn btn-primary" id="updateBtn">Update Status</button>
                </form>
                
                <div class="timeline" id="timeline">
                    <h2>Status History</h2>
                    <div id="timelineContent">
                        <p style="color: #6b7280;">Loading timeline...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const contactId = '{contact.id}';
        
        // Load timeline on page load
        document.addEventListener('DOMContentLoaded', () => {{
            loadTimeline();
        }});
        
        function switchTab(tabName) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Remove active from all tabs
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Mark selected tab as active
            event.target.classList.add('active');
            
            // Load timeline if updates tab is selected
            if (tabName === 'updates') {{
                loadTimeline();
            }}
        }}
        
        function copyMessage(messageType) {{
            const messageElement = document.getElementById(messageType + '-message');
            const text = messageElement.textContent;
            
            navigator.clipboard.writeText(text).then(() => {{
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => {{
                    btn.textContent = originalText;
                }}, 2000);
            }});
        }}
        
        // Handle status update form submission
        document.getElementById('statusUpdateForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const updateBtn = document.getElementById('updateBtn');
            const updateAlert = document.getElementById('updateAlert');
            const status = document.getElementById('status').value;
            const notes = document.getElementById('notes').value;
            
            // Disable button
            updateBtn.disabled = true;
            updateBtn.textContent = 'Updating...';
            
            // Hide previous alerts
            updateAlert.classList.remove('show', 'success', 'error');
            
            try {{
                const response = await fetch(`/api/networking/contacts/${{contactId}}/status`, {{
                    method: 'PUT',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ status, notes }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    // Show success message
                    updateAlert.textContent = `Status updated to "${{status}}"`;
                    updateAlert.classList.add('show', 'success');
                    
                    // Clear notes field
                    document.getElementById('notes').value = '';
                    
                    // Reload timeline
                    await loadTimeline();
                    
                    // Update page metadata if needed
                    setTimeout(() => {{
                        location.reload();
                    }}, 2000);
                }} else {{
                    // Show error message
                    updateAlert.textContent = `Error: ${{data.error}}`;
                    updateAlert.classList.add('show', 'error');
                }}
            }} catch (error) {{
                console.error('Error updating status:', error);
                updateAlert.textContent = `Error: ${{error.message}}`;
                updateAlert.classList.add('show', 'error');
            }} finally {{
                // Re-enable button
                updateBtn.disabled = false;
                updateBtn.textContent = 'Update Status';
            }}
        }});
        
        async function loadTimeline() {{
            const timelineContent = document.getElementById('timelineContent');
            
            try {{
                const response = await fetch(`/api/networking/contacts/${{contactId}}`);
                const data = await response.json();
                
                if (data.success && data.contact.updates) {{
                    const updates = data.contact.updates;
                    
                    if (updates.length === 0) {{
                        timelineContent.innerHTML = '<p style="color: #6b7280;">No status updates yet.</p>';
                        return;
                    }}
                    
                    // Render timeline items (already sorted newest first from API)
                    timelineContent.innerHTML = updates.map((update, index) => {{
                        const isLatest = index === 0;
                        const timestamp = update.timestamp;
                        const date = new Date(
                            parseInt(timestamp.substring(0, 4)),
                            parseInt(timestamp.substring(4, 6)) - 1,
                            parseInt(timestamp.substring(6, 8)),
                            parseInt(timestamp.substring(8, 10)),
                            parseInt(timestamp.substring(10, 12)),
                            parseInt(timestamp.substring(12, 14))
                        );
                        
                        return `
                            <div class="timeline-item ${{isLatest ? 'latest' : ''}}">
                                <div class="timeline-date">${{date.toLocaleDateString('en-US', {{ 
                                    month: 'short', 
                                    day: 'numeric', 
                                    year: 'numeric',
                                    hour: 'numeric',
                                    minute: '2-digit'
                                }})}}</div>
                                <div class="timeline-status">${{update.status}}</div>
                                ${{update.notes ? `<div class="timeline-notes">${{update.notes}}</div>` : ''}}
                            </div>
                        `;
                    }}).join('');
                }} else {{
                    timelineContent.innerHTML = '<p style="color: #6b7280;">Error loading timeline.</p>';
                }}
            }} catch (error) {{
                console.error('Error loading timeline:', error);
                timelineContent.innerHTML = '<p style="color: #ef4444;">Error loading timeline.</p>';
            }}
        }}
        
        async function regenerateDocuments() {{
            const regenerateBtn = document.getElementById('regenerateBtn');
            
            if (!confirm('Regenerate all AI analysis and messages? This will take 5-6 minutes.')) {{
                return;
            }}
            
            regenerateBtn.disabled = true;
            regenerateBtn.textContent = '🔄 Regenerating...';
            
            try {{
                const response = await fetch(`/api/networking/contacts/${{contactId}}/regenerate`, {{
                    method: 'POST'
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    alert('Documents regenerated successfully! Reloading page...');
                    location.reload();
                }} else {{
                    alert(`Error: ${{data.error}}`);
                    regenerateBtn.disabled = false;
                    regenerateBtn.textContent = '🔄 Regenerate Documents';
                }}
            }} catch (error) {{
                alert(`Error: ${{error.message}}`);
                regenerateBtn.disabled = false;
                regenerateBtn.textContent = '🔄 Regenerate Documents';
            }}
        }}
    </script>
</body>
</html>"""
        
        # Save summary page
        summary_path = contact.folder_path / f"{contact.person_name.replace(' ', '-')}-summary.html"
        write_text_file(html, summary_path)
        contact.summary_path = summary_path
