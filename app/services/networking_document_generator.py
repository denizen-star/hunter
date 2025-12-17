"""Document generation service for networking contacts"""
import json
import html
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
        
        # 3. Generate AI research
        print("  → Generating company and contact research...")
        research_content = self.generate_ai_research(contact, profile_details)
        research_path = contact.folder_path / f"{contact.person_name.replace(' ', '-')}-research.txt"
        write_text_file(research_content, research_path)
        contact.research_path = research_path
        print("  ✓ Research generated")
        
        # 4. Generate calendar invite
        print("  → Generating calendar invite...")
        calendar_invite = self.generate_calendar_invite(contact)
        calendar_path = contact.folder_path / "calendar_reminder.txt"
        write_text_file(calendar_invite, calendar_path)
        contact.calendar_invite_generated = True
        print("  ✓ Calendar invite generated")
        
        # 5. Generate summary page
        print("  → Generating summary page...")
        self.generate_summary_page(contact, match_result['detailed_analysis'], messages, research_content)
        print("  ✓ Summary page generated")
    
    def generate_simple_intro_message(
        self,
        contact: NetworkingContact,
        resume_content: str
    ) -> None:
        """Generate a simple personalized intro message for contacts that don't require full AI processing"""
        print(f"  → Generating simple intro message for {contact.person_name}...")
        
        # Extract basic info from resume (first line is usually the name)
        resume_lines = resume_content.split('\n')
        your_name = resume_lines[0].strip() if resume_lines else "Kervin"
        # Remove markdown headers if present
        your_name = your_name.replace('#', '').strip()
        
        # Create a simple personalized intro message using AI but minimal processing
        intro_prompt = f"""Write a brief, professional LinkedIn connection request message (under 300 characters) for:

Your name: {your_name}
Their name: {contact.person_name}
Company: {contact.company_name}
{f'Their title: {contact.job_title}' if contact.job_title else ''}

Your background (from resume):
{resume_content[:500]}

Their profile:
{read_text_file(contact.profile_path) if contact.profile_path and contact.profile_path.exists() else 'No profile details available'}

Requirements:
- Maximum 300 characters (including spaces)
- Professional and personable
- Reference something specific from their profile or company
- Mention your relevant background briefly
- No generic "I'd like to connect" phrases
- Make it engaging and worth accepting

Return just the message text, no subject line or extra formatting."""

        try:
            # Check if Ollama is available
            if self.ai_analyzer.check_connection():
                intro_message = self.ai_analyzer._call_ollama(intro_prompt)
                # Ensure it's under 300 chars
                if len(intro_message) > 300:
                    intro_message = intro_message[:297] + "..."
                intro_message = intro_message.strip()
            else:
                raise ConnectionError("Ollama not available")
        except Exception as e:
            print(f"  ⚠ Warning: Could not generate intro message with AI: {e}")
            # Fallback to template-based personalized message
            profile_text = read_text_file(contact.profile_path) if contact.profile_path and contact.profile_path.exists() else ""
            job_context = ""
            if contact.job_title:
                job_context = f" as a {contact.job_title}"
            
            # Extract key skills/technologies from resume (simple extraction)
            resume_lower = resume_content.lower()
            tech_keywords = ['data', 'engineering', 'analytics', 'python', 'sql', 'cloud', 'machine learning', 'ai']
            relevant_skills = [kw for kw in tech_keywords if kw in resume_lower][:3]
            skills_text = ", ".join(relevant_skills) if relevant_skills else "data and analytics"
            
            intro_message = f"Hi {contact.person_name}, I came across your profile{job_context} at {contact.company_name}. I'm a professional with expertise in {skills_text} and would like to connect to exchange insights and explore potential opportunities. Would love to connect!"
            
            # Ensure under 300 chars
            if len(intro_message) > 300:
                intro_message = intro_message[:297] + "..."
        
        # Save simple message file
        messages_path = contact.folder_path / f"{contact.person_name.replace(' ', '-')}-messages.txt"
        messages_content = f"""SIMPLE INTRO MESSAGE
{'=' * 80}

INITIAL CONNECTION REQUEST (LinkedIn - Under 300 chars)
{'-' * 80}
{intro_message}

Character count: {len(intro_message)}

NOTE: This is a simple contact. For full AI analysis, match scoring, and additional message templates, you can regenerate this contact with full AI processing.
"""
        write_text_file(messages_content, messages_path)
        contact.messages_path = messages_path
        
        print("  ✓ Simple intro message generated")
    
    def _get_standard_networking_messages(self) -> list:
        """Return the 4 standard networking message templates"""
        return [
            "Data/BI/Analytics Leader, with experience in FInancial services from Self Financiat to BoNY and RBC. I applied for POSITION (XX% match) on your site. Passionate about credit building and enabling financial success at COMPANY. Eager to discuss my experience!",
            "Hi XXX I am a Product/ Data/ Strategy Leader with 18+ years driving strategy, data analysis, and unprecedented growth. Applied to the [Target Role/Area]. Let's connect.",
            "Hello NAME! Your banner caught my eye.\nI'm Kervin, a Data Product Leader, and I applied for the POSITION role at COMPANY. I emailed you my resume & cover for reference. My experience is a great match. I hope to connect!\nCheers",
            "I am a hands on experienced Data Analytics and BI leader. I turn disparate data into strategic solutions and automation. Proficient in BI, Cloud, SQL, and Data tools. Always open to high-impact roles in [Target Industry]"
        ]
    
    def _replace_message_placeholders(self, message: str, contact: NetworkingContact) -> str:
        """Replace placeholders in message templates with contact data"""
        # Extract first name
        first_name = contact.person_name.split()[0] if contact.person_name else "there"
        
        # Replace placeholders
        message = message.replace("NAME", first_name)
        message = message.replace("XXX", first_name)
        message = message.replace("COMPANY", contact.company_name or "the company")
        message = message.replace("POSITION", contact.job_title or "a role")
        message = message.replace("[Target Role/Area]", contact.job_title or "[Target Role/Area]")
        # Leave [Target Industry] as-is if not set (user can edit manually)
        
        return message
    
    def _get_next_step_recommendation(self, contact: NetworkingContact) -> str:
        """Get rule-based next step recommendation based on status and days since update"""
        status = contact.status or "To Research"
        days_since = contact.get_days_since_update()
        
        if status == "To Research":
            return "Review profile and find 1-2 warm intro angles"
        elif status in ["Contacted", "Contacted - Sent"]:
            if days_since < 7:
                return "Wait 5-7 days, then consider a follow-up"
            elif days_since < 14:
                return "Consider sending a polite follow-up message"
            else:
                return "Overdue follow-up - send a brief check-in"
        elif status == "In Conversation":
            return "Continue engagement and explore mutual interests"
        elif status == "Meeting Scheduled":
            return "Prep agenda and talking points for the meeting"
        elif status == "Meeting Completed":
            return "Send thank you note and follow up on action items"
        elif status in ["Cold/Archive", "Inactive/Dormant"]:
            return "Consider re-engaging if relevant opportunity arises"
        else:
            return "Review status and determine next action"
    
    def generate_simple_summary_page(self, contact: NetworkingContact) -> None:
        """Generate lightweight summary page for simple contacts (no AI processing) - uses same structure as full AI version"""
        print(f"  → Generating simple summary page for {contact.person_name}...")
        
        # Read raw profile
        raw_profile = ""
        if contact.raw_profile_path and contact.raw_profile_path.exists():
            raw_profile = read_text_file(contact.raw_profile_path)
        
        # Get standard messages with placeholders replaced
        standard_messages = self._get_standard_networking_messages()
        personalized_messages = [self._replace_message_placeholders(msg, contact) for msg in standard_messages]
        
        # Get next step recommendation
        next_step = self._get_next_step_recommendation(contact)
        
        # Create messages dict in format expected by Updates tab (same as full AI version)
        messages_for_updates = {
            'connection_request': personalized_messages[0] if len(personalized_messages) > 0 else '',
            'meeting_invitation': personalized_messages[1] if len(personalized_messages) > 1 else '',
            'thank_you': personalized_messages[2] if len(personalized_messages) > 2 else '',
            'consulting_offer': personalized_messages[3] if len(personalized_messages) > 3 else ''
        }
        
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
    
    <!-- Quill.js Rich Text Editor -->
    <link href="/static/css/quill.snow.css" rel="stylesheet">
    <script src="/static/js/quill.min.js"></script>
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            color: #1f2937;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}
        
        .header {{
            background: white;
            border-bottom: 1px solid #e5e7eb;
            padding: 20px 32px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #3b82f6;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 12px;
            transition: color 0.2s ease;
        }}
        
        .back-link:hover {{
            color: #2563eb;
        }}
        
        .back-link::before {{
            content: '←';
            font-size: 18px;
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        
        .header .subtitle {{
            font-size: 14px;
            color: #6b7280;
        }}
        
        /* Application Header Card */
        .app-header-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 24px;
            margin: 24px 32px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        
        .app-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            justify-content: center;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #6b7280;
        }}
        
        .meta-item strong {{
            color: #374151;
        }}
        
        .status-pill {{
            font-size: 12px;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 12px;
            display: inline-block;
        }}
        
        .tag-green {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .tag-blue {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .tag-gray {{
            background: #f3f4f6;
            color: #4b5563;
        }}
        
        .tabs {{
            background: white;
            border-bottom: 1px solid #e5e7eb;
            padding: 0;
            display: flex;
            gap: 0;
            margin: 0 32px;
        }}
        
        .tab {{
            padding: 16px 24px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-weight: 400;
            color: #6b7280;
            transition: all 0.15s ease;
            position: relative;
        }}
        
        .tab:hover {{
            color: #374151;
            background: #f9fafb;
        }}
        
        .tab.active {{
            color: #1f2937;
            border-bottom-color: #3b82f6;
            font-weight: 500;
        }}
        
        .tab.hidden {{
            display: none;
        }}
        
        .content {{
            margin: 0 32px;
            padding: 0;
            padding-top: 0;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .section {{
            background: white;
            border-radius: 0;
            padding: 0;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
            border: 1px solid #e5e7eb;
            border-top: none;
            overflow: hidden;
            width: 100%;
        }}
        
        .section.collapsed .section-content {{
            display: none;
        }}
        
        .section-header {{
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            padding: 16px 24px;
            margin: 0;
        }}

        .section-header.clickable {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
        }}

        .section-toggle-indicator {{
            font-size: 18px;
            color: #9ca3af;
            transition: transform 0.2s ease, color 0.2s ease;
        }}

        .section:not(.collapsed) .section-toggle-indicator {{
            transform: rotate(90deg);
            color: #4b5563;
        }}
        
        .section h2 {{
            font-size: 18px;
            font-weight: 500;
            margin: 0;
            color: #1f2937;
            padding: 0;
            border-bottom: none;
        }}
        
        .section-content {{
            padding: 28px;
        }}
        
        .section-content h3 {{
            font-size: 16px;
            font-weight: 600;
            margin: 20px 0 12px 0;
            color: #374151;
        }}
        
        .section-content h3:first-child {{
            margin-top: 0;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}
        
        .info-card {{
            background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .info-card-label {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            color: #6b7280;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .info-card-value {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
        }}
        
        .analysis-section {{
            background: #f9fafb;
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 20px;
            margin: 16px 0;
        }}
        
        .analysis-section h4 {{
            font-size: 14px;
            font-weight: 700;
            color: #1e40af;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .analysis-text {{
            font-size: 14px;
            color: #374151;
            line-height: 1.7;
            white-space: pre-wrap;
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
            padding: 20px;
            border-left: 3px solid #e5e7eb;
            margin-bottom: 20px;
            background: #f9fafb;
            border-radius: 0 8px 8px 0;
        }}
        
        .timeline-item.latest {{
            border-left-color: #3b82f6;
            background: #f0f9ff;
        }}
        
        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        
        .timeline-status {{
            display: inline-block;
            padding: 6px 12px;
            background: #3b82f6;
            color: white;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
        }}
        
        .timeline-date {{
            font-size: 13px;
            color: #6b7280;
            font-weight: 500;
        }}
        
        .timeline-notes-label {{
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .timeline-notes {{
            color: #374151;
            font-size: 14px;
            line-height: 1.6;
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
        
        .template-btn {{
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 6px;
            border: 1px solid #d1d5db;
            background: white;
            color: #374151;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .template-btn:hover {{
            background: #f3f4f6;
            border-color: #3b82f6;
            color: #3b82f6;
        }}
        
        /* Quill Editor Styles */
        .ql-editor {{
            min-height: 150px;
            font-size: 14px;
            font-family: 'Poppins', sans-serif;
            line-height: 1.6;
        }}
        
        .ql-toolbar.ql-snow {{
            border: 1px solid #d1d5db;
            border-radius: 8px 8px 0 0;
            background: #f9fafb;
        }}
        
        .ql-container.ql-snow {{
            border: 1px solid #d1d5db;
            border-top: none;
            border-radius: 0 0 8px 8px;
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
        
        .relationship-card {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        
        .relationship-card h3 {{
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            color: #1e40af;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }}
        
        .relationship-card .status {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
        }}
        
        .relationship-card .next-step {{
            font-size: 14px;
            color: #374151;
            line-height: 1.5;
        }}
        
        .upgrade-banner {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px 20px;
            margin: 24px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}
        
        .upgrade-banner-text {{
            flex: 1;
            font-size: 14px;
            color: #6b7280;
        }}
        
        .upgrade-banner strong {{
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <!-- Main Content -->
    <div class="header">
        <a href="/networking" class="back-link">Back to Network Dash</a>
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1>{contact.person_name}</h1>
                <div class="subtitle">{contact.company_name}{f' • {contact.job_title}' if contact.job_title else ''}</div>
            </div>
            <div style="display: flex; gap: 12px;">
                <a href="{self.generate_google_calendar_url(contact)}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">
                    📅 Add to GCal
                </a>
            </div>
        </div>
    </div>
    
    <!-- Hero Card with Metadata -->
    <div class="app-header-card">
        <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 20px;">
            <span id="statusPill" class="status-pill tag tag-blue">{contact.status or 'To Research'}</span>
        </div>
        {self._generate_contact_rewards_cards(contact)}
        <div class="app-meta">
            <div class="meta-item">
                <span>📍</span>
                <span>{contact.location or 'N/A'}</span>
            </div>
            <div class="meta-item">
                <span>📅</span>
                <span><strong>Connected:</strong> {format_for_display(contact.created_at)}</span>
            </div>
            <div class="meta-item">
                <span>🔄</span>
                <span id="statusUpdated"><strong>Updated:</strong> {format_for_display(contact.status_updated_at or contact.created_at)}</span>
            </div>
            <div class="meta-item">
                <span>📊</span>
                <span><strong>Status:</strong> <span id="statusDisplay">{contact.status or 'To Research'}</span></span>
            </div>
            {f'<div class="meta-item"><span>🔗</span><a href="{contact.linkedin_url}" target="_blank" style="color: #3b82f6; text-decoration: none;">LinkedIn Profile</a></div>' if contact.linkedin_url else ''}
            <div class="meta-item" id="emailMetaItem">
                <span>📧</span>
                {f'<span id="emailDisplay" style="cursor: pointer; text-decoration: underline; text-decoration-style: dotted;" onclick="editEmailInline()" title="Click to edit">{contact.email}</span>' if contact.email else '<span id="emailDisplay" style="cursor: pointer; color: #3b82f6; text-decoration: underline;" onclick="editEmailInline()">Add Email</span>'}
                <input type="email" id="emailInput" value="{contact.email or ''}" style="display: none; padding: 4px 8px; border: 1px solid #3b82f6; border-radius: 4px; font-size: 14px; width: 200px;" onblur="saveEmailInline()" onkeypress="if(event.key==='Enter') saveEmailInline()">
            </div>
        </div>
    </div>
    
    <div class="tabs">
        <div class="tab active" onclick="switchTab('summary')">Summary</div>
        <div class="tab" onclick="switchTab('raw')">Raw Entry</div>
        <div class="tab hidden" onclick="switchTab('skills')">Skills</div>
        <div class="tab hidden" onclick="switchTab('research')">Research</div>
        <div class="tab" onclick="switchTab('messages')">Messages</div>
        <div class="tab" onclick="switchTab('updates')">Updates & Notes</div>
    </div>
    
    <div class="content">
        <!-- Summary Tab -->
        <div id="summary" class="tab-content active">
            <!-- Contact Details Section -->
            <div class="section collapsed" id="contact-details-section">
                <div class="section-header clickable" onclick="toggleSection('contact-details-section')">
                    <h2>Contact Details</h2>
                    <span class="section-toggle-indicator">▶</span>
                </div>
                <div class="section-content">
                <form id="contactDetailsForm" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                    <div class="form-group" style="margin-bottom: 0;">
                        <label for="contactEmail" style="font-weight: 600; color: #374151; margin-bottom: 8px; display: block;">Email Address</label>
                        <input type="email" id="contactEmail" name="email" value="{contact.email or ''}" placeholder="email@example.com" style="width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid #d1d5db; border-radius: 8px; transition: all 0.15s ease;">
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label for="contactLocation" style="font-weight: 600; color: #374151; margin-bottom: 8px; display: block;">Location</label>
                        <input type="text" id="contactLocation" name="location" value="{contact.location or ''}" placeholder="City, State/Country" style="width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid #d1d5db; border-radius: 8px; transition: all 0.15s ease;">
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label for="contactJobTitle" style="font-weight: 600; color: #374151; margin-bottom: 8px; display: block;">Job Title</label>
                        <input type="text" id="contactJobTitle" name="job_title" value="{contact.job_title or ''}" placeholder="Job Title" style="width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid #d1d5db; border-radius: 8px; transition: all 0.15s ease;">
                    </div>
                </form>
                <button onclick="saveContactDetails()" class="btn btn-primary" style="margin-top: 16px;" id="saveDetailsBtn">Save Contact Details</button>
                <div id="detailsAlert" style="margin-top: 12px; display: none; padding: 12px; border-radius: 6px; font-size: 14px;"></div>
                </div>
            </div>
            
            <!-- Relationship / Next Step Card -->
            <div class="relationship-card">
                <h3>Relationship Status</h3>
                <div class="status">Current Status: <span id="currentStatusDisplay">{contact.status or 'To Research'}</span></div>
                <div class="next-step">Next Step: {next_step}</div>
            </div>
        </div>
        
        <!-- Raw Tab -->
        <div id="raw" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2>Raw Profile Details</h2>
                </div>
                <div class="section-content">
                <pre style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.5;">{raw_profile or 'No raw profile available'}</pre>
                </div>
            </div>
        </div>
        
        <!-- Messages Tab -->
        <div id="messages" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2>Networking Messages</h2>
                </div>
                <div class="section-content">
                <div class="message-box">
                    <h3>
                        <span>1. Initial Connection Request (LinkedIn)</span>
                        <button class="copy-btn" onclick="copyMessage('connection')">Copy</button>
                    </h3>
                    <div id="connection-message">{messages_for_updates.get('connection_request', 'N/A')}</div>
                    <div class="char-count">{len(messages_for_updates.get('connection_request', ''))} characters</div>
                </div>
                
                <div class="message-box">
                    <h3>
                        <span>2. Meeting Invitation</span>
                        <button class="copy-btn" onclick="copyMessage('meeting')">Copy</button>
                    </h3>
                    <div id="meeting-message">{messages_for_updates.get('meeting_invitation', 'N/A')}</div>
                </div>
                
                <div class="message-box">
                    <h3>
                        <span>3. Thank You Message</span>
                        <button class="copy-btn" onclick="copyMessage('thankyou')">Copy</button>
                    </h3>
                    <div id="thankyou-message">{messages_for_updates.get('thank_you', 'N/A')}</div>
                </div>
                
                <div class="message-box">
                    <h3>
                        <span>4. Consulting Services Offer</span>
                        <button class="copy-btn" onclick="copyMessage('consulting')">Copy</button>
                    </h3>
                    <div id="consulting-message">{messages_for_updates.get('consulting_offer', 'N/A')}</div>
                </div>
                </div>
            </div>
        </div>
        
        <!-- Updates & Notes Tab -->
        <div id="updates" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2>Update Status</h2>
                </div>
                <div class="section-content">
                
                <div id="updateAlert" class="alert"></div>
                
                <form id="statusUpdateForm">
                    <div class="form-group">
                        <label for="status">Select Status</label>
                        <select id="status" name="status" required>
                            <option value="">-- Select Status --</option>
                            <optgroup label="Prospecting">
                                <option value="To Research" {"selected" if contact.status == "To Research" else ""}>To Research</option>
                                <option value="Ready to Connect" {"selected" if contact.status == "Ready to Connect" else ""}>Ready to Connect</option>
                            </optgroup>
                            <optgroup label="Outreach">
                                <option value="Pending Reply" {"selected" if contact.status == "Pending Reply" else ""}>Pending Reply</option>
                                <option value="Connected - Initial" {"selected" if contact.status == "Connected - Initial" else ""}>Connected - Initial</option>
                                <option value="Cold/Inactive" {"selected" if contact.status == "Cold/Inactive" else ""}>Cold/Inactive</option>
                            </optgroup>
                            <optgroup label="Engagement">
                                <option value="In Conversation" {"selected" if contact.status == "In Conversation" else ""}>In Conversation</option>
                                <option value="Meeting Scheduled" {"selected" if contact.status == "Meeting Scheduled" else ""}>Meeting Scheduled</option>
                                <option value="Meeting Complete" {"selected" if contact.status == "Meeting Complete" else ""}>Meeting Complete</option>
                            </optgroup>
                            <optgroup label="Nurture">
                                <option value="Strong Connection" {"selected" if contact.status == "Strong Connection" else ""}>Strong Connection</option>
                                <option value="Referral Partner" {"selected" if contact.status == "Referral Partner" else ""}>Referral Partner</option>
                                <option value="Dormant" {"selected" if contact.status == "Dormant" else ""}>Dormant</option>
                            </optgroup>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="notes" style="display: flex; justify-content: space-between; align-items: center;">
                            <span>Notes</span>
                            <button type="button" onclick="copyEditorContent()" class="copy-btn" style="padding: 6px 12px; font-size: 12px;">Copy Notes</button>
                        </label>
                        <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                            <button type="button" class="template-btn" onclick="insertTemplate('connection')">Connection Request</button>
                            <button type="button" class="template-btn" onclick="insertTemplate('followup')">Follow-up</button>
                            <button type="button" class="template-btn" onclick="insertTemplate('meeting')">Meeting Notes</button>
                            <button type="button" class="template-btn" onclick="insertTemplate('thankyou')">Thank You</button>
                        </div>
                        <div id="editor" style="background: white; min-height: 150px;"></div>
                        <input type="hidden" id="notes" name="notes">
                        
                        <!-- Message Templates Dropdown -->
                        <div style="margin-top: 16px; display: flex; gap: 12px; align-items: center;">
                            <label for="messageTemplate" style="font-weight: 600; color: #1f2937; font-size: 14px;">Message Templates:</label>
                            <select id="messageTemplate" onchange="loadMessageIntoEditor()" style="padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; min-width: 250px; flex: 1;">
                                <option value="">-- Select a Message Template --</option>
                                <option value="connection">1. Connection Request</option>
                                <option value="meeting">2. Meeting Invitation</option>
                                <option value="thankyou">3. Thank You Message</option>
                                <option value="consulting">4. Consulting Services Offer</option>
                            </select>
                        </div>
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
    </div>
    
    <!-- Upgrade Banner at Bottom -->
    <div class="upgrade-banner">
        <div class="upgrade-banner-text">
            <strong>Simple Contact</strong> - This is a lightweight contact without full AI analysis. For match scoring, research, and advanced messaging, click below to upgrade.
        </div>
        <button onclick="upgradeToFullAI()" class="btn btn-primary">Upgrade to Full AI</button>
    </div>
    </div>
    
    <script>
        const contactId = '{contact.id}';
        let quill;
        
        // Load timeline on page load
        document.addEventListener('DOMContentLoaded', () => {{
            loadTimeline();
            initializeEditor();
        }});
        
        // Initialize Quill Rich Text Editor
        function initializeEditor() {{
            quill = new Quill('#editor', {{
                theme: 'snow',
                modules: {{
                    toolbar: [
                        ['bold', 'italic', 'underline', 'strike'],
                        [{{ 'list': 'ordered' }}, {{ 'list': 'bullet' }}],
                        ['link'],
                        ['clean']
                    ]
                }},
                placeholder: 'Add notes about this status update...'
            }});
        }}
        
        // Template insertion
        function insertTemplate(type) {{
            if (!quill) return;
            
            const templates = {{
                'connection': '<p><strong>Connection Request Sent</strong></p><p>Sent LinkedIn connection request with personalized message.</p><p>Next step: Follow up in 5-7 business days if no response.</p>',
                'followup': '<p><strong>Follow-up</strong></p><p>Following up on previous outreach.</p><p>Key points discussed:</p><ul><li>Point 1</li><li>Point 2</li></ul>',
                'meeting': '<p><strong>Meeting Notes</strong></p><p>Date: [Date]</p><p>Duration: [Duration]</p><p>Discussion Topics:</p><ul><li>Topic 1</li><li>Topic 2</li></ul><p>Action Items:</p><ul><li>Action 1</li><li>Action 2</li></ul><p>Next Steps: [Next Steps]</p>',
                'thankyou': '<p><strong>Thank You Note Sent</strong></p><p>Thanked {contact.person_name} for their time and insights.</p><p>Key takeaways:</p><ul><li>Takeaway 1</li><li>Takeaway 2</li></ul><p>Next step: [Next Step]</p>'
            }};
            
            const template = templates[type] || '';
            quill.root.innerHTML = template;
        }}

        function toggleSection(sectionId) {{
            const section = typeof sectionId === 'string' ? document.getElementById(sectionId) : sectionId.closest('.section');
            if (!section) {{
                return;
            }}
            section.classList.toggle('collapsed');
        }}
        
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
        
        // Load message template into editor
        function loadMessageIntoEditor() {{
            if (!quill) return;
            
            const select = document.getElementById('messageTemplate');
            const selectedValue = select.value;
            
            if (!selectedValue) {{
                return;
            }}
            
            // Get message from Messages tab
            const messageElement = document.getElementById(selectedValue + '-message');
            if (!messageElement) {{
                console.error('Message element not found:', selectedValue);
                return;
            }}
            
            const text = messageElement.textContent.trim();
            
            // Convert plain text to HTML paragraphs for Quill
            const paragraphs = text.split('\\n\\n').filter(p => p.trim());
            const htmlContent = paragraphs.map(p => `<p>${{p.trim().replace(/\\n/g, '<br>')}}</p>`).join('');
            
            // Set the editor content
            quill.root.innerHTML = htmlContent || `<p>${{text}}</p>`;
        }}
        
        // Copy editor content to clipboard
        function copyEditorContent() {{
            if (!quill) {{
                alert('Editor not initialized');
                return;
            }}
            
            // Get plain text from Quill editor
            const text = quill.getText();
            
            if (!text.trim()) {{
                alert('Notes box is empty');
                return;
            }}
            
            navigator.clipboard.writeText(text).then(() => {{
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                btn.style.background = '#10b981';
                btn.style.color = 'white';
                
                setTimeout(() => {{
                    btn.textContent = originalText;
                    btn.style.background = '';
                    btn.style.color = '';
                }}, 2000);
            }}).catch(err => {{
                console.error('Failed to copy:', err);
                alert('Failed to copy notes to clipboard');
            }});
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
            
            // Get HTML content from Quill editor
            const notes = quill.root.innerHTML;
            
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
                    
                    // Update status displays immediately
                    const statusPill = document.getElementById('statusPill');
                    const statusDisplay = document.getElementById('statusDisplay');
                    const currentStatusDisplay = document.getElementById('currentStatusDisplay');
                    const statusUpdated = document.getElementById('statusUpdated');
                    
                    if (statusPill) statusPill.textContent = status;
                    if (statusDisplay) statusDisplay.textContent = status;
                    if (currentStatusDisplay) currentStatusDisplay.textContent = status;
                    if (statusUpdated) {{
                        const now = new Date();
                        const dateStr = now.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric', year: 'numeric' }});
                        const timeStr = now.toLocaleTimeString('en-US', {{ hour: 'numeric', minute: '2-digit', hour12: true }});
                        statusUpdated.innerHTML = `<strong>Updated:</strong> ${{dateStr}} ${{timeStr}}`;
                    }}
                    
                    // Update dropdown selection
                    const statusSelect = document.getElementById('status');
                    if (statusSelect) {{
                        statusSelect.value = status;
                    }}
                    
                    // Clear editor
                    quill.root.innerHTML = '';
                    
                    // Reload timeline
                    await loadTimeline();
                    
                    // Update page metadata if needed - wait longer to ensure save completes
                    setTimeout(() => {{
                        location.reload();
                    }}, 3000);
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
                        
                        const dateStr = date.toLocaleDateString('en-US', {{ 
                            month: 'long', 
                            day: 'numeric', 
                            year: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit'
                        }}) + ' EST';
                        
                        return `
                            <div class="timeline-item ${{isLatest ? 'latest' : ''}}">
                                <div class="timeline-header">
                                    <span class="timeline-status">${{update.status}}</span>
                                    <span class="timeline-date">${{dateStr}}</span>
                                </div>
                                ${{update.notes ? `
                                    <div class="timeline-notes-label">Notes:</div>
                                    <div class="timeline-notes">${{update.notes}}</div>
                                ` : ''}}
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
        
        async function upgradeToFullAI() {{
            if (!confirm('Upgrade this contact to Full AI processing? This will take 5-6 minutes and generate match scoring, research, and advanced messaging.')) {{
                return;
            }}
            
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = 'Upgrading...';
            
            try {{
                const response = await fetch(`/api/networking/contacts/${{contactId}}/regenerate`, {{
                    method: 'POST'
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    alert('Contact upgraded successfully! Reloading page...');
                    window.location.reload();
                }} else {{
                    alert('Error: ' + (data.error || 'Unknown error'));
                    btn.disabled = false;
                    btn.textContent = 'Upgrade to Full AI';
                }}
            }} catch (error) {{
                console.error('Error upgrading contact:', error);
                alert('Error upgrading contact: ' + error.message);
                btn.disabled = false;
                btn.textContent = 'Upgrade to Full AI';
            }}
        }}
        
        async function saveContactDetails() {{
            const btn = document.getElementById('saveDetailsBtn');
            const alert = document.getElementById('detailsAlert');
            const email = document.getElementById('contactEmail').value.trim() || null;
            const location = document.getElementById('contactLocation').value.trim() || null;
            const jobTitle = document.getElementById('contactJobTitle').value.trim() || null;
            
            btn.disabled = true;
            btn.textContent = 'Saving...';
            alert.style.display = 'none';
            
            try {{
                const response = await fetch(`/api/networking/contacts/${{contactId}}/details`, {{
                    method: 'PUT',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ email, location, job_title: jobTitle }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    alert.style.display = 'block';
                    alert.style.background = '#d1fae5';
                    alert.style.color = '#065f46';
                    alert.style.border = '1px solid #10b981';
                    alert.textContent = 'Contact details updated successfully!';
                    
                    setTimeout(() => {{
                        location.reload();
                    }}, 1000);
                }} else {{
                    alert.style.display = 'block';
                    alert.style.background = '#fee2e2';
                    alert.style.color = '#991b1b';
                    alert.style.border = '1px solid #ef4444';
                    alert.textContent = 'Failed to update: ' + (data.error || 'Unknown error');
                }}
            }} catch (error) {{
                console.error('Error updating contact details:', error);
                alert.style.display = 'block';
                alert.style.background = '#fee2e2';
                alert.style.color = '#991b1b';
                alert.style.border = '1px solid #ef4444';
                alert.textContent = 'Error updating contact details: ' + error.message;
            }} finally {{
                btn.disabled = false;
                btn.textContent = 'Save Contact Details';
            }}
        }}
        
        // Inline email editing in hero card
        function editEmailInline() {{
            const emailDisplay = document.getElementById('emailDisplay');
            const emailInput = document.getElementById('emailInput');
            
            if (emailDisplay && emailInput) {{
                emailDisplay.style.display = 'none';
                emailInput.style.display = 'inline-block';
                emailInput.focus();
                emailInput.select();
            }}
        }}
        
        async function saveEmailInline() {{
            const emailDisplay = document.getElementById('emailDisplay');
            const emailInput = document.getElementById('emailInput');
            
            if (!emailInput) return;
            
            const newEmail = emailInput.value.trim();
            
            // Hide input, show display
            emailInput.style.display = 'none';
            
            try {{
                const response = await fetch(`/api/networking/contacts/${{contactId}}/details`, {{
                    method: 'PUT',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ email: newEmail || null }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    // Update display
                    if (emailDisplay) {{
                        if (newEmail) {{
                            emailDisplay.textContent = newEmail;
                            emailDisplay.style.color = '';
                            emailDisplay.style.textDecoration = 'underline';
                            emailDisplay.style.textDecorationStyle = 'dotted';
                            emailDisplay.title = 'Click to edit';
                        }} else {{
                            emailDisplay.textContent = 'Add Email';
                            emailDisplay.style.color = '#3b82f6';
                            emailDisplay.style.textDecoration = 'underline';
                            emailDisplay.style.textDecorationStyle = 'solid';
                            emailDisplay.title = '';
                        }}
                        emailDisplay.style.display = 'inline';
                    }}
                    // Update input value
                    emailInput.value = newEmail;
                    
                    // Update contact details form
                    const contactEmailField = document.getElementById('contactEmail');
                    if (contactEmailField) {{
                        contactEmailField.value = newEmail;
                    }}
                    
                    // Show success feedback
                    showInlineSuccess(emailDisplay);
                    
                    // Reload page after short delay to sync all fields
                    setTimeout(() => {{
                        location.reload();
                    }}, 1000);
                }} else {{
                    // Show error
                    alert('Failed to update email: ' + (data.error || 'Unknown error'));
                    if (emailDisplay) emailDisplay.style.display = 'inline';
                }}
            }} catch (error) {{
                console.error('Error updating email:', error);
                alert('Error updating email: ' + error.message);
                if (emailDisplay) emailDisplay.style.display = 'inline';
            }}
        }}
        
        function showInlineSuccess(element) {{
            if (!element) return;
            const originalBg = element.style.backgroundColor;
            element.style.backgroundColor = '#d1fae5';
            setTimeout(() => {{
                element.style.backgroundColor = originalBg;
            }}, 2000);
        }}
        
    </script>
</body>
</html>"""
        
        # Save summary page
        summary_filename = f"{contact.person_name.replace(' ', '-')}-summary.html"
        summary_path = contact.folder_path / summary_filename
        write_text_file(html, summary_path)
        contact.summary_path = summary_path
        
        print("  ✓ Simple summary page generated")
    
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
    
    def _get_default_research(self, contact: NetworkingContact) -> str:
        """Get default research template if AI generation fails"""
        return f"""## COMPANY BACKGROUND: {contact.company_name}

Research the company's mission, values, recent news, and strategic initiatives.

## RECENT COMPANY NEWS & UPDATES

Check {contact.company_name}'s newsroom, LinkedIn page, and recent industry articles.

## {contact.person_name}'S RECENT ACTIVITY

Review their LinkedIn profile for recent posts, articles shared, and professional updates.

## MUTUAL CONNECTIONS & NETWORKS

Check for mutual connections on LinkedIn that could provide warm introductions.

## KEY TALKING POINTS

- Shared background in data and analytics
- Common experience with modern platforms
- Mutual interest in driving business value"""
    
    def _generate_talking_points(self, match_analysis: str, contact: NetworkingContact) -> str:
        """Generate talking points from match analysis"""
        talking_points = []
        
        # Extract key points from match analysis
        lines = match_analysis.split('\n')
        for line in lines:
            line = line.strip()
            # Look for lines that indicate shared experience or commonalities
            if any(keyword in line.lower() for keyword in ['shared', 'common', 'both', 'similar', 'experience in', 'background in']):
                if len(line) > 20 and not line.startswith('#'):
                    # Clean up the line
                    point = line.lstrip('-•* ').strip()
                    if point and len(point) > 15:
                        talking_points.append(point)
        
        # If we didn't find enough, add generic ones based on the contact
        if len(talking_points) < 3:
            talking_points = [
                f"Shared background in data and analytics",
                f"Common experience with modern data platforms and tools",
                f"Mutual interest in driving business value through data insights",
                f"Similar career progression in technical leadership roles"
            ]
        
        # Limit to top 5 points
        talking_points = talking_points[:5]
        
        # Format as HTML list
        html = '<ul style="margin: 0; padding-left: 20px; color: #166534; line-height: 1.8;">\n'
        for point in talking_points:
            html += f'    <li>{point}</li>\n'
        html += '</ul>'
        
        return html
    
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
    
    def generate_ai_research(self, contact: NetworkingContact, profile_details: str) -> str:
        """Generate AI-powered research about the company and contact"""
        research_prompt = f"""Based on the LinkedIn profile details provided, generate comprehensive research notes about this professional contact and their company.

CONTACT INFORMATION:
Name: {contact.person_name}
Company: {contact.company_name}
Title: {contact.job_title or 'N/A'}

LINKEDIN PROFILE DATA:
{profile_details[:2000]}

Generate research in the following format:

## COMPANY BACKGROUND: {contact.company_name}

[Analyze what the company does based on the profile context. Include industry, size indicators, and mission/values if mentioned]

## RECENT COMPANY NEWS & UPDATES

[Extract any recent company achievements, initiatives, or news mentioned in the profile]

## {contact.person_name}'S RECENT ACTIVITY

[Summarize their recent posts, articles, or professional activities mentioned in their profile]

## MUTUAL CONNECTIONS & NETWORKS

[Identify any shared groups, schools, previous companies, or potential mutual connections mentioned]

## KEY TALKING POINTS

[List 3-5 specific topics you could discuss based on their profile, recent activity, and background]

Keep responses factual and based only on the provided profile data. If information is not available, state "Not available in profile data" rather than making assumptions."""

        try:
            research = self.ai_analyzer._call_ollama(research_prompt)
            return research
        except Exception as e:
            print(f"  ⚠ Warning: Could not generate AI research: {e}")
            return f"""## COMPANY BACKGROUND: {contact.company_name}

Research the company's mission, values, recent news, and strategic initiatives.

## RECENT COMPANY NEWS & UPDATES

Check {contact.company_name}'s newsroom, LinkedIn page, and recent industry articles.

## {contact.person_name}'S RECENT ACTIVITY

Review their LinkedIn profile for recent posts, articles shared, and professional updates.

## MUTUAL CONNECTIONS & NETWORKS

Check for mutual connections on LinkedIn that could provide warm introductions.

## KEY TALKING POINTS

- Shared background in data and analytics
- Common experience with modern platforms
- Mutual interest in driving business value"""
    
    def generate_summary_page(
        self,
        contact: NetworkingContact,
        match_analysis: str,
        messages: Dict[str, str],
        research_content: str = ""
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
    
    <!-- Quill.js Rich Text Editor -->
    <link href="/static/css/quill.snow.css" rel="stylesheet">
    <script src="/static/js/quill.min.js"></script>
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fafafa;
            color: #1f2937;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}
        
        .header {{
            background: white;
            border-bottom: 1px solid #e5e7eb;
            padding: 20px 32px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #3b82f6;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 12px;
            transition: color 0.2s ease;
        }}
        
        .back-link:hover {{
            color: #2563eb;
        }}
        
        .back-link::before {{
            content: '←';
            font-size: 18px;
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        
        .header .subtitle {{
            font-size: 14px;
            color: #6b7280;
        }}
        
        /* Application Header Card */
        .app-header-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 24px;
            margin: 24px 32px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}
        
        .app-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            justify-content: center;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #6b7280;
        }}
        
        .meta-item strong {{
            color: #374151;
        }}
        
        .status-pill {{
            font-size: 12px;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 12px;
            display: inline-block;
        }}
        
        .tag-green {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .tag-blue {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .tag-gray {{
            background: #f3f4f6;
            color: #4b5563;
        }}
        
        .tabs {{
            background: white;
            border-bottom: 1px solid #e5e7eb;
            padding: 0;
            display: flex;
            gap: 0;
            margin: 0 32px;
        }}
        
        .tab {{
            padding: 16px 24px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-weight: 400;
            color: #6b7280;
            transition: all 0.15s ease;
            position: relative;
        }}
        
        .tab:hover {{
            color: #374151;
            background: #f9fafb;
        }}
        
        .tab.active {{
            color: #1f2937;
            border-bottom-color: #3b82f6;
            font-weight: 500;
        }}
        
        .content {{
            margin: 0 32px;
            padding: 0;
            padding-top: 0;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .section {{
            background: white;
            border-radius: 0;
            padding: 0;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06);
            border: 1px solid #e5e7eb;
            border-top: none;
            overflow: hidden;
            width: 100%;
        }}
        
        .section.collapsed .section-content {{
            display: none;
        }}
        
        .section-header {{
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            padding: 16px 24px;
            margin: 0;
        }}

        .section-header.clickable {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
        }}

        .section-toggle-indicator {{
            font-size: 18px;
            color: #9ca3af;
            transition: transform 0.2s ease, color 0.2s ease;
        }}

        .section:not(.collapsed) .section-toggle-indicator {{
            transform: rotate(90deg);
            color: #4b5563;
        }}
        
        .section h2 {{
            font-size: 18px;
            font-weight: 500;
            margin: 0;
            color: #1f2937;
            padding: 0;
            border-bottom: none;
        }}
        
        .section-content {{
            padding: 28px;
        }}
        
        .section-content h3 {{
            font-size: 16px;
            font-weight: 600;
            margin: 20px 0 12px 0;
            color: #374151;
        }}
        
        .section-content h3:first-child {{
            margin-top: 0;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }}
        
        .info-card {{
            background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .info-card-label {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            color: #6b7280;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .info-card-value {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
        }}
        
        .analysis-section {{
            background: #f9fafb;
            border-left: 4px solid #3b82f6;
            border-radius: 8px;
            padding: 20px;
            margin: 16px 0;
        }}
        
        .analysis-section h4 {{
            font-size: 14px;
            font-weight: 700;
            color: #1e40af;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .analysis-text {{
            font-size: 14px;
            color: #374151;
            line-height: 1.7;
            white-space: pre-wrap;
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
            padding: 20px;
            border-left: 3px solid #e5e7eb;
            margin-bottom: 20px;
            background: #f9fafb;
            border-radius: 0 8px 8px 0;
        }}
        
        .timeline-item.latest {{
            border-left-color: #3b82f6;
            background: #f0f9ff;
        }}
        
        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        
        .timeline-status {{
            display: inline-block;
            padding: 6px 12px;
            background: #3b82f6;
            color: white;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
        }}
        
        .timeline-date {{
            font-size: 13px;
            color: #6b7280;
            font-weight: 500;
        }}
        
        .timeline-notes-label {{
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        
        .timeline-notes {{
            color: #374151;
            font-size: 14px;
            line-height: 1.6;
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
        
        .template-btn {{
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 6px;
            border: 1px solid #d1d5db;
            background: white;
            color: #374151;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .template-btn:hover {{
            background: #f3f4f6;
            border-color: #3b82f6;
            color: #3b82f6;
        }}
        
        /* Quill Editor Styles */
        .ql-editor {{
            min-height: 150px;
            font-size: 14px;
            font-family: 'Poppins', sans-serif;
            line-height: 1.6;
        }}
        
        .ql-toolbar.ql-snow {{
            border: 1px solid #d1d5db;
            border-radius: 8px 8px 0 0;
            background: #f9fafb;
        }}
        
        .ql-container.ql-snow {{
            border: 1px solid #d1d5db;
            border-top: none;
            border-radius: 0 0 8px 8px;
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
    <!-- Main Content -->
    <div class="header">
        <a href="/networking" class="back-link">Back to Network Dash</a>
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1>{contact.person_name}</h1>
                <div class="subtitle">{contact.company_name}{f' • {contact.job_title}' if contact.job_title else ''}</div>
            </div>
            <div style="display: flex; gap: 12px;">
                    <a href="{self.generate_google_calendar_url(contact)}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary">
                        📅 Add to GCal
                    </a>
                    <button onclick="regenerateDocuments()" class="btn btn-secondary" id="regenerateBtn">
                        🔄 Regen
                    </button>
            </div>
        </div>
    </div>
    
    <!-- Hero Card with Metadata -->
    <div class="app-header-card">
        <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 20px;">
            <span id="statusPill" class="status-pill tag tag-blue">{contact.status or 'To Research'}</span>
            {f'<span class="status-pill tag tag-green">{contact.match_score:.0f}% Match</span>' if contact.match_score is not None else ''}
        </div>
        {self._generate_contact_rewards_cards(contact)}
        <div class="app-meta">
            <div class="meta-item">
                <span>📍</span>
                <span>{contact.location or 'N/A'}</span>
            </div>
            <div class="meta-item">
                <span>📅</span>
                <span><strong>Connected:</strong> {format_for_display(contact.created_at)}</span>
            </div>
            <div class="meta-item">
                <span>🔄</span>
                <span id="statusUpdated"><strong>Updated:</strong> {format_for_display(contact.status_updated_at or contact.created_at)}</span>
            </div>
            <div class="meta-item">
                <span>📊</span>
                <span><strong>Status:</strong> <span id="statusDisplay">{contact.status or 'To Research'}</span></span>
            </div>
            {f'<div class="meta-item"><span>🔗</span><a href="{contact.linkedin_url}" target="_blank" style="color: #3b82f6; text-decoration: none;">LinkedIn Profile</a></div>' if contact.linkedin_url else ''}
            <div class="meta-item" id="emailMetaItem">
                <span>📧</span>
                {f'<span id="emailDisplay" style="cursor: pointer; text-decoration: underline; text-decoration-style: dotted;" onclick="editEmailInline()" title="Click to edit">{contact.email}</span>' if contact.email else '<span id="emailDisplay" style="cursor: pointer; color: #3b82f6; text-decoration: underline;" onclick="editEmailInline()">Add Email</span>'}
                <input type="email" id="emailInput" value="{contact.email or ''}" style="display: none; padding: 4px 8px; border: 1px solid #3b82f6; border-radius: 4px; font-size: 14px; width: 200px;" onblur="saveEmailInline()" onkeypress="if(event.key==='Enter') saveEmailInline()">
            </div>
        </div>
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
            <!-- Contact Details Section (collapsible, starts collapsed) -->
            <div class="section collapsed" id="contact-details-section">
                <div class="section-header clickable" onclick="toggleSection('contact-details-section')">
                    <h2>Contact Details</h2>
                    <span class="section-toggle-indicator">▶</span>
                </div>
                <div class="section-content">
                <form id="contactDetailsForm" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                    <div class="form-group" style="margin-bottom: 0;">
                        <label for="contactEmail" style="font-weight: 600; color: #374151; margin-bottom: 8px; display: block;">Email Address</label>
                        <input type="email" id="contactEmail" name="email" value="{contact.email or ''}" placeholder="email@example.com" style="width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid #d1d5db; border-radius: 8px; transition: all 0.15s ease;">
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label for="contactLocation" style="font-weight: 600; color: #374151; margin-bottom: 8px; display: block;">Location</label>
                        <input type="text" id="contactLocation" name="location" value="{contact.location or ''}" placeholder="City, State/Country" style="width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid #d1d5db; border-radius: 8px; transition: all 0.15s ease;">
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label for="contactJobTitle" style="font-weight: 600; color: #374151; margin-bottom: 8px; display: block;">Job Title</label>
                        <input type="text" id="contactJobTitle" name="job_title" value="{contact.job_title or ''}" placeholder="Job Title" style="width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid #d1d5db; border-radius: 8px; transition: all 0.15s ease;">
                    </div>
                </form>
                <button onclick="saveContactDetails()" class="btn btn-primary" style="margin-top: 16px;" id="saveDetailsBtn">Save Contact Details</button>
                <div id="detailsAlert" style="margin-top: 12px; display: none; padding: 12px; border-radius: 6px; font-size: 14px;"></div>
                </div>
            </div>
            
            <!-- Match Analysis Section -->
            <div class="section">
                <div class="section-header">
                    <h2>Match Analysis</h2>
                </div>
                <div class="section-content">
                <div class="analysis-section">
                    <div class="analysis-text">{match_analysis}</div>
                </div>
                </div>
            </div>
            
            <!-- Key Strengths & Talking Points -->
            <div class="section">
                <div class="section-header">
                    <h2>Key Strengths & Talking Points</h2>
                </div>
                <div class="section-content">
                <div style="background: #f0fdf4; border-left: 4px solid #10b981; border-radius: 8px; padding: 20px;">
                    {self._generate_talking_points(match_analysis, contact)}
                </div>
                </div>
            </div>
        </div>
        
        <!-- Raw Entry Tab -->
        <div id="raw" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2>Raw Profile Details</h2>
                </div>
                <div class="section-content">
                <pre>{raw_profile}</pre>
                </div>
            </div>
        </div>
        
        <!-- Skills Tab -->
        <div id="skills" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2>Skills Analysis</h2>
                </div>
                <div class="section-content">
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
        </div>
        
        <!-- Research Tab -->
        <div id="research" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2>AI-Generated Research & Background</h2>
                </div>
                <div class="section-content">
                <div style="background: #eff6ff; border: 1px solid #3b82f6; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                    <p style="color: #1e40af; font-size: 14px; margin-bottom: 12px;">
                        <strong>Note:</strong> This research was automatically generated from the LinkedIn profile data and available information.
                    </p>
                </div>
                <div class="analysis-text" style="white-space: pre-wrap; line-height: 1.8;">
{research_content if research_content else self._get_default_research(contact)}
                </div>
                </div>
            </div>
        </div>
        
        <!-- Messages Tab -->
        <div id="messages" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2>Networking Messages</h2>
                </div>
                <div class="section-content">
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
        </div>
        
        <!-- Updates & Notes Tab -->
        <div id="updates" class="tab-content">
            <div class="section">
                <div class="section-header">
                    <h2>Update Status</h2>
                </div>
                <div class="section-content">
                
                <div id="updateAlert" class="alert"></div>
                
                <form id="statusUpdateForm">
                    <div class="form-group">
                        <label for="status">Select Status</label>
                        <select id="status" name="status" required>
                            <option value="">-- Select Status --</option>
                            <optgroup label="Prospecting">
                                <option value="To Research" {"selected" if contact.status == "To Research" else ""}>To Research</option>
                                <option value="Ready to Connect" {"selected" if contact.status == "Ready to Connect" else ""}>Ready to Connect</option>
                            </optgroup>
                            <optgroup label="Outreach">
                                <option value="Pending Reply" {"selected" if contact.status == "Pending Reply" else ""}>Pending Reply</option>
                                <option value="Connected - Initial" {"selected" if contact.status == "Connected - Initial" else ""}>Connected - Initial</option>
                                <option value="Cold/Inactive" {"selected" if contact.status == "Cold/Inactive" else ""}>Cold/Inactive</option>
                            </optgroup>
                            <optgroup label="Engagement">
                                <option value="In Conversation" {"selected" if contact.status == "In Conversation" else ""}>In Conversation</option>
                                <option value="Meeting Scheduled" {"selected" if contact.status == "Meeting Scheduled" else ""}>Meeting Scheduled</option>
                                <option value="Meeting Complete" {"selected" if contact.status == "Meeting Complete" else ""}>Meeting Complete</option>
                            </optgroup>
                            <optgroup label="Nurture">
                                <option value="Strong Connection" {"selected" if contact.status == "Strong Connection" else ""}>Strong Connection</option>
                                <option value="Referral Partner" {"selected" if contact.status == "Referral Partner" else ""}>Referral Partner</option>
                                <option value="Dormant" {"selected" if contact.status == "Dormant" else ""}>Dormant</option>
                            </optgroup>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="notes" style="display: flex; justify-content: space-between; align-items: center;">
                            <span>Notes</span>
                            <button type="button" onclick="copyEditorContent()" class="copy-btn" style="padding: 6px 12px; font-size: 12px;">Copy Notes</button>
                        </label>
                        <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                            <button type="button" class="template-btn" onclick="insertTemplate('connection')">Connection Request</button>
                            <button type="button" class="template-btn" onclick="insertTemplate('followup')">Follow-up</button>
                            <button type="button" class="template-btn" onclick="insertTemplate('meeting')">Meeting Notes</button>
                            <button type="button" class="template-btn" onclick="insertTemplate('thankyou')">Thank You</button>
                        </div>
                        <div id="editor" style="background: white; min-height: 150px;"></div>
                        <input type="hidden" id="notes" name="notes">
                        
                        <!-- Message Templates Dropdown -->
                        <div style="margin-top: 16px; display: flex; gap: 12px; align-items: center;">
                            <label for="messageTemplate" style="font-weight: 600; color: #1f2937; font-size: 14px;">Message Templates:</label>
                            <select id="messageTemplate" onchange="loadMessageIntoEditor()" style="padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; min-width: 250px; flex: 1;">
                                <option value="">-- Select a Message Template --</option>
                                <option value="connection">1. Connection Request</option>
                                <option value="meeting">2. Meeting Invitation</option>
                                <option value="thankyou">3. Thank You Message</option>
                                <option value="consulting">4. Consulting Services Offer</option>
                            </select>
                        </div>
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
    </div>
    
    <script>
        const contactId = '{contact.id}';
        let quill;
        
        // Load timeline on page load
        document.addEventListener('DOMContentLoaded', () => {{
            loadTimeline();
            initializeEditor();
        }});
        
        // Initialize Quill Rich Text Editor
        function initializeEditor() {{
            quill = new Quill('#editor', {{
                theme: 'snow',
                modules: {{
                    toolbar: [
                        ['bold', 'italic', 'underline', 'strike'],
                        [{{ 'list': 'ordered' }}, {{ 'list': 'bullet' }}],
                        ['link'],
                        ['clean']
                    ]
                }},
                placeholder: 'Add notes about this status update...'
            }});
        }}
        
        // Template insertion
        function insertTemplate(type) {{
            if (!quill) return;
            
            const templates = {{
                'connection': '<p><strong>Connection Request Sent</strong></p><p>Sent LinkedIn connection request with personalized message.</p><p>Next step: Follow up in 5-7 business days if no response.</p>',
                'followup': '<p><strong>Follow-up</strong></p><p>Following up on previous outreach.</p><p>Key points discussed:</p><ul><li>Point 1</li><li>Point 2</li></ul>',
                'meeting': '<p><strong>Meeting Notes</strong></p><p>Date: [Date]</p><p>Duration: [Duration]</p><p>Discussion Topics:</p><ul><li>Topic 1</li><li>Topic 2</li></ul><p>Action Items:</p><ul><li>Action 1</li><li>Action 2</li></ul><p>Next Steps: [Next Steps]</p>',
                'thankyou': '<p><strong>Thank You Note Sent</strong></p><p>Thanked {contact.person_name} for their time and insights.</p><p>Key takeaways:</p><ul><li>Takeaway 1</li><li>Takeaway 2</li></ul><p>Next step: [Next Step]</p>'
            }};
            
            const template = templates[type] || '';
            quill.root.innerHTML = template;
        }}

        function toggleSection(sectionId) {{
            const section = document.getElementById(sectionId);
            if (!section) {{
                return;
            }}
            section.classList.toggle('collapsed');
        }}
        
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
        
        // Load message template into editor
        function loadMessageIntoEditor() {{
            if (!quill) return;
            
            const select = document.getElementById('messageTemplate');
            const selectedValue = select.value;
            
            if (!selectedValue) {{
                return;
            }}
            
            // Get message from Messages tab
            const messageElement = document.getElementById(selectedValue + '-message');
            if (!messageElement) {{
                console.error('Message element not found:', selectedValue);
                return;
            }}
            
            const text = messageElement.textContent.trim();
            
            // Convert plain text to HTML paragraphs for Quill
            const paragraphs = text.split('\\n\\n').filter(p => p.trim());
            const htmlContent = paragraphs.map(p => `<p>${{p.trim().replace(/\\n/g, '<br>')}}</p>`).join('');
            
            // Set the editor content
            quill.root.innerHTML = htmlContent || `<p>${{text}}</p>`;
        }}
        
        // Copy editor content to clipboard
        function copyEditorContent() {{
            if (!quill) {{
                alert('Editor not initialized');
                return;
            }}
            
            // Get plain text from Quill editor
            const text = quill.getText();
            
            if (!text.trim()) {{
                alert('Notes box is empty');
                return;
            }}
            
            navigator.clipboard.writeText(text).then(() => {{
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                btn.style.background = '#10b981';
                btn.style.color = 'white';
                
                setTimeout(() => {{
                    btn.textContent = originalText;
                    btn.style.background = '';
                    btn.style.color = '';
                }}, 2000);
            }}).catch(err => {{
                console.error('Failed to copy:', err);
                alert('Failed to copy notes to clipboard');
            }});
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
            
            // Get HTML content from Quill editor
            const notes = quill.root.innerHTML;
            
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
                    
                    // Update status displays immediately
                    const statusPill = document.getElementById('statusPill');
                    const statusDisplay = document.getElementById('statusDisplay');
                    const currentStatusDisplay = document.getElementById('currentStatusDisplay');
                    const statusUpdated = document.getElementById('statusUpdated');
                    
                    if (statusPill) statusPill.textContent = status;
                    if (statusDisplay) statusDisplay.textContent = status;
                    if (currentStatusDisplay) currentStatusDisplay.textContent = status;
                    if (statusUpdated) {{
                        const now = new Date();
                        const dateStr = now.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric', year: 'numeric' }});
                        const timeStr = now.toLocaleTimeString('en-US', {{ hour: 'numeric', minute: '2-digit', hour12: true }});
                        statusUpdated.innerHTML = `<strong>Updated:</strong> ${{dateStr}} ${{timeStr}}`;
                    }}
                    
                    // Update dropdown selection
                    const statusSelect = document.getElementById('status');
                    if (statusSelect) {{
                        statusSelect.value = status;
                    }}
                    
                    // Clear editor
                    quill.root.innerHTML = '';
                    
                    // Reload timeline
                    await loadTimeline();
                    
                    // Update page metadata if needed - wait longer to ensure save completes
                    setTimeout(() => {{
                        location.reload();
                    }}, 3000);
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
                        
                        const dateStr = date.toLocaleDateString('en-US', {{ 
                            month: 'long', 
                            day: 'numeric', 
                            year: 'numeric',
                            hour: 'numeric',
                            minute: '2-digit'
                        }}) + ' EST';
                        
                        return `
                            <div class="timeline-item ${{isLatest ? 'latest' : ''}}">
                                <div class="timeline-header">
                                    <span class="timeline-status">${{update.status}}</span>
                                    <span class="timeline-date">${{dateStr}}</span>
                                </div>
                                ${{update.notes ? `
                                    <div class="timeline-notes-label">Notes:</div>
                                    <div class="timeline-notes">${{update.notes}}</div>
                                ` : ''}}
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
                    regenerateBtn.textContent = '🔄 Regen';
                }}
            }} catch (error) {{
                alert(`Error: ${{error.message}}`);
                regenerateBtn.disabled = false;
                regenerateBtn.textContent = '🔄 Regen';
            }}
        }}
        
        // Inline email editing in hero card
        function editEmailInline() {{
            const emailDisplay = document.getElementById('emailDisplay');
            const emailInput = document.getElementById('emailInput');
            
            if (emailDisplay && emailInput) {{
                emailDisplay.style.display = 'none';
                emailInput.style.display = 'inline-block';
                emailInput.focus();
                emailInput.select();
            }}
        }}
        
        async function saveEmailInline() {{
            const emailDisplay = document.getElementById('emailDisplay');
            const emailInput = document.getElementById('emailInput');
            
            if (!emailInput) return;
            
            const newEmail = emailInput.value.trim();
            
            // Hide input, show display
            emailInput.style.display = 'none';
            
            try {{
                const response = await fetch(`/api/networking/contacts/${{contactId}}/details`, {{
                    method: 'PUT',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ email: newEmail || null }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    // Update display
                    if (emailDisplay) {{
                        if (newEmail) {{
                            emailDisplay.textContent = newEmail;
                            emailDisplay.style.color = '';
                            emailDisplay.style.textDecoration = 'underline';
                            emailDisplay.style.textDecorationStyle = 'dotted';
                            emailDisplay.title = 'Click to edit';
                        }} else {{
                            emailDisplay.textContent = 'Add Email';
                            emailDisplay.style.color = '#3b82f6';
                            emailDisplay.style.textDecoration = 'underline';
                            emailDisplay.style.textDecorationStyle = 'solid';
                            emailDisplay.title = '';
                        }}
                        emailDisplay.style.display = 'inline';
                    }}
                    // Update input value
                    emailInput.value = newEmail;
                    
                    // Update contact details form
                    const contactEmailField = document.getElementById('contactEmail');
                    if (contactEmailField) {{
                        contactEmailField.value = newEmail;
                    }}
                    
                    // Show success feedback
                    showInlineSuccess(emailDisplay);
                    
                    // Reload page after short delay to sync all fields
                    setTimeout(() => {{
                        location.reload();
                    }}, 1000);
                }} else {{
                    // Show error
                    alert('Failed to update email: ' + (data.error || 'Unknown error'));
                    if (emailDisplay) emailDisplay.style.display = 'inline';
                }}
            }} catch (error) {{
                console.error('Error updating email:', error);
                alert('Error updating email: ' + error.message);
                if (emailDisplay) emailDisplay.style.display = 'inline';
            }}
        }}
        
        function showInlineSuccess(element) {{
            if (!element) return;
            const originalBg = element.style.backgroundColor;
            element.style.backgroundColor = '#d1fae5';
            setTimeout(() => {{
                element.style.backgroundColor = originalBg;
            }}, 2000);
        }}
        
        // Save contact details from Summary tab form
        async function saveContactDetails() {{
            const btn = document.getElementById('saveDetailsBtn');
            const alert = document.getElementById('detailsAlert');
            const email = document.getElementById('contactEmail').value.trim() || null;
            const location = document.getElementById('contactLocation').value.trim() || null;
            const jobTitle = document.getElementById('contactJobTitle').value.trim() || null;
            
            btn.disabled = true;
            btn.textContent = 'Saving...';
            alert.style.display = 'none';
            
            try {{
                const response = await fetch(`/api/networking/contacts/${{contactId}}/details`, {{
                    method: 'PUT',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ email, location, job_title: jobTitle }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    alert.style.display = 'block';
                    alert.style.background = '#d1fae5';
                    alert.style.color = '#065f46';
                    alert.style.border = '1px solid #10b981';
                    alert.textContent = 'Contact details updated successfully!';
                    
                    // Update hero card email display if email changed
                    const emailDisplay = document.getElementById('emailDisplay');
                    const emailInput = document.getElementById('emailInput');
                    if (emailDisplay && emailInput) {{
                        if (email) {{
                            emailDisplay.textContent = email;
                            emailDisplay.style.color = '';
                            emailDisplay.style.textDecoration = 'underline';
                            emailDisplay.style.textDecorationStyle = 'dotted';
                            emailDisplay.title = 'Click to edit';
                        }} else {{
                            emailDisplay.textContent = 'Add Email';
                            emailDisplay.style.color = '#3b82f6';
                            emailDisplay.style.textDecoration = 'underline';
                            emailDisplay.style.textDecorationStyle = 'solid';
                            emailDisplay.title = '';
                        }}
                        emailInput.value = email || '';
                    }}
                    
                    // Reload page after 1 second to update all fields
                    setTimeout(() => {{
                        location.reload();
                    }}, 1000);
                }} else {{
                    alert.style.display = 'block';
                    alert.style.background = '#fee2e2';
                    alert.style.color = '#991b1b';
                    alert.style.border = '1px solid #ef4444';
                    alert.textContent = 'Failed to update: ' + (data.error || 'Unknown error');
                }}
            }} catch (error) {{
                console.error('Error updating contact details:', error);
                alert.style.display = 'block';
                alert.style.background = '#fee2e2';
                alert.style.color = '#991b1b';
                alert.style.border = '1px solid #ef4444';
                alert.textContent = 'Error updating contact details: ' + error.message;
            }} finally {{
                btn.disabled = false;
                btn.textContent = 'Save Contact Details';
            }}
        }}
        
    </script>
</body>
</html>"""
        
        # Save summary page
        summary_path = contact.folder_path / f"{contact.person_name.replace(' ', '-')}-summary.html"
        write_text_file(html, summary_path)
        contact.summary_path = summary_path
    
    def _generate_contact_rewards_cards(self, contact: NetworkingContact) -> str:
        """Generate all 8 badges for a single contact with cumulative points"""
        try:
            from app.services.badge_calculation_service import BadgeCalculationService
            
            badge_service = BadgeCalculationService()
            
            # Status mapping for legacy statuses
            status_mapping = {
                'Ready to Contact': 'Ready to Connect',
                'Contacted - Sent': 'Pending Reply',
                'Contacted - No Response': 'Pending Reply',
                'Contacted - Replied': 'Connected - Initial',
                'New Connection': 'Connected - Initial',
                'Cold/Archive': 'Cold/Inactive',
                'Action Pending - You': 'In Conversation',
                'Action Pending - Them': 'In Conversation',
                'Nurture (1-3 Mo.)': 'Strong Connection',
                'Nurture (4-6 Mo.)': 'Strong Connection',
                'Inactive/Dormant': 'Dormant'
            }
            
            # Normalize status
            normalized_status = status_mapping.get(contact.status, contact.status)
            
            # Define status progression order (for cumulative points)
            # Each status awards points for all badges up to and including that status
            status_progression = [
                'Ready to Connect',      # Deep Diver (+10)
                'Pending Reply',         # Profile Magnet (+3)
                'Connected - Initial',   # Qualified Lead (+15)
                'In Conversation',       # Conversation Starter (+20)
                'Meeting Scheduled',     # Scheduler Master (+30)
                'Meeting Complete',      # Rapport Builder (+50)
                'Strong Connection',     # Relationship Manager (+2, recurring)
                'Referral Partner'       # Super Connector (+100)
            ]
            
            # Calculate cumulative points - get all badges up to current status
            earned_badge_ids = set()
            total_points = 0
            
            # Find current status position in progression
            current_index = -1
            for i, status in enumerate(status_progression):
                if normalized_status == status:
                    current_index = i
                    break
            
            # If status is in progression, award all badges up to and including it
            if current_index >= 0:
                for i in range(current_index + 1):
                    status_in_progression = status_progression[i]
                    badge_id = badge_service.status_to_badge.get(status_in_progression)
                    if badge_id:
                        earned_badge_ids.add(badge_id)
                        badge_def = badge_service.badge_definitions[badge_id]
                        total_points += badge_def['points']
            
            # Generate all 8 badges (earned and unearned)
            all_badges_html = []
            for badge_id, badge_def in badge_service.badge_definitions.items():
                is_earned = badge_id in earned_badge_ids
                
                border_color = '#3b82f6' if is_earned else '#d1d5db'
                icon_color = '#3b82f6' if is_earned else '#9ca3af'
                points_color = '#10b981' if is_earned else '#9ca3af'
                icon = '✓' if is_earned else '○'
                
                # Build tooltip with requirements
                tooltip_parts = [badge_def['description']]
                if 'trigger_status' in badge_def:
                    tooltip_parts.append(f"Trigger: {badge_def['trigger_status']}")
                tooltip_text = " | ".join(tooltip_parts)
                # Escape HTML entities for title attribute
                tooltip_text = html.escape(tooltip_text)
                
                all_badges_html.append(f'''
                    <div style="padding: 10px; min-width: 160px; border: 2px solid {border_color}; border-radius: 8px; background: white; cursor: help;" title="{tooltip_text}">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <div style="width: 24px; height: 24px; font-size: 16px; color: {icon_color}; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                                {icon}
                            </div>
                            <div style="flex: 1; min-width: 0;">
                                <div style="font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #1f2937;">{badge_def['name']}</div>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <div style="flex: 1; height: 6px; min-width: 50px; background: #e5e7eb; border-radius: 3px; overflow: hidden;">
                                        <div style="width: {'100' if is_earned else '0'}%; height: 100%; background: {'linear-gradient(90deg, #3b82f6, #10b981)' if is_earned else '#d1d5db'}; transition: width 0.3s ease;"></div>
                                    </div>
                                </div>
                            </div>
                            <div style="font-size: 13px; font-weight: 700; color: {points_color}; white-space: nowrap;">+{badge_def['points']}</div>
                        </div>
                    </div>
                ''')
            
            return f'''
            <div style="margin: 20px 0;">
                <!-- All 8 Badges -->
                <div style="padding: 16px; background: white; border: 1px solid #e5e7eb; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; cursor: pointer;" onclick="toggleBadgeSection()">
                        <h3 style="margin: 0; font-size: 14px; font-weight: 600; color: #1f2937;">Networking Rewards ({total_points} pts)</h3>
                        <svg id="badge-toggle-icon" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #6b7280; transition: transform 0.3s ease;">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                        </svg>
                    </div>
                    <div id="badge-grid-content" style="display: flex; gap: 8px; flex-wrap: wrap; max-height: 300px; overflow-y: auto;">
                        {''.join(all_badges_html)}
                    </div>
                    <script>
                        let badgeSectionExpanded = true;
                        function toggleBadgeSection() {{
                            const content = document.getElementById('badge-grid-content');
                            const icon = document.getElementById('badge-toggle-icon');
                            if (!badgeSectionExpanded) {{
                                content.style.display = 'flex';
                                icon.style.transform = 'rotate(0deg)';
                                badgeSectionExpanded = true;
                            }} else {{
                                content.style.display = 'none';
                                icon.style.transform = 'rotate(180deg)';
                                badgeSectionExpanded = false;
                            }}
                        }}
                    </script>
                </div>
            </div>
            '''
        except Exception as e:
            print(f"Warning: Could not generate contact rewards cards: {e}")
            import traceback
            traceback.print_exc()
            return ''
