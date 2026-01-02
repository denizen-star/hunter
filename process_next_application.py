#!/usr/bin/env python3
"""
Script to process the next application with new structured research format
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, '/Users/kervinleacock/Documents/Development/hunter')

from app.services.ai_analyzer import AIAnalyzer
from app.services.job_processor import JobProcessor
from app.services.document_generator import DocumentGenerator
from app.models.qualification import QualificationAnalysis
from app.utils.file_utils import write_text_file, read_text_file

def generate_structured_research(application_folder_path, company, job_title, job_url=None):
    """Generate a properly structured research section with the exact format requested"""
    
    ai_analyzer = AIAnalyzer()
    
    # Create a detailed, structured research prompt
    research_prompt = f"""You are a professional business researcher. Generate a comprehensive, company-specific research section for a job application.

COMPANY: {company}
JOB TITLE: {job_title}
JOB URL: {job_url if job_url else 'Not provided'}

Please provide a detailed, company-specific research section that follows this EXACT structure and format:

# Company Research: {company}

**Company Website:** https://www.{company.lower().replace(' ', '').replace(',', '').replace('-', '').replace('.', '')}.com

## Company Overview & Mission
- Provide a specific, accurate overview of {company}
- Include their actual mission statement and company values
- Mention their industry focus and market position
- Include company size, headquarters location, and key facts

## Recent News & Developments
- List 3-5 recent news items, developments, or announcements from {company}
- Include specific dates, achievements, partnerships, or expansions
- Focus on business-relevant news that shows company growth and direction

## Products & Services
- Detail the specific products and services that {company} offers
- Include their core business model and revenue streams
- Mention any unique or innovative offerings

## Market Position & Competitors
- Identify {company}'s main competitors in their industry
- Describe their competitive advantages and market position
- Include any industry rankings or recognition

# Role-Specific Research

## Key Personnel (Data & Analytics)
Research and identify key personnel at {company} who work in data, analytics, business intelligence, or technology roles. Include:
- Names and titles of key executives (CEO, CTO, VP of Data, Head of Analytics, etc.)
- Employees with leadership roles in Data, Business Intelligence, and Analytics
- Brief descriptions of their backgrounds and expertise
- Focus on people who would be relevant to a {job_title} role

## Key Challenges
- Specific challenges that {company} faces in data and analytics
- Industry-wide challenges that affect their business
- How a {job_title} role would address these challenges

## Why This Role/Company

### Career Alignment
- Specific reasons why this {job_title} role at {company} aligns with career goals
- How the role fits into the candidate's career progression
- Unique learning and growth opportunities

### Mission Resonance
- How {company}'s mission and values align with personal and professional goals
- Specific aspects of their culture and approach that are appealing
- How the candidate's values match the company's direction

### Unique Opportunities
- Specific opportunities this role offers that are unique to {company}
- Projects, technologies, or initiatives the candidate would work on
- Potential for impact and career advancement

# Research Sources
- List the specific sources used for this research
- Include company website, news articles, LinkedIn profiles, industry reports
- Note any limitations in publicly available information

IMPORTANT: 
1. Make this research specific to {company}, not generic
2. Use real information about the company, their industry, and their specific challenges and opportunities
3. Avoid generic statements that could apply to any company
4. Include actual URLs where possible
5. Use the EXACT heading structure shown above
6. Format as clean markdown with proper bullet points and sections

Format this as a professional research document that demonstrates thorough preparation and genuine interest in {company} specifically."""

    try:
        # Generate research content using AI
        print(f"🤖 Generating structured research for {company}...")
        research_content = ai_analyzer._call_ollama(research_prompt)
        
        # Save to file
        research_filename = f"{company.replace(' ', '-')}-{job_title.replace(' ', '-')}-Research.md"
        research_path = application_folder_path / research_filename
        
        write_text_file(research_content, research_path)
        print(f"✅ Structured research section generated: {research_path}")
        
        return research_path
        
    except Exception as e:
        print(f"❌ Error generating structured research section: {e}")
        return None

def process_application(app_id, company, job_title, job_url=None):
    """Process any application with all required sections"""
    
    print(f"🚀 Processing: {company} - {job_title}")
    print("=" * 60)
    
    # Initialize services
    job_processor = JobProcessor()
    doc_generator = DocumentGenerator()
    ai_analyzer = AIAnalyzer()
    
    # Load application
    application = job_processor.get_application_by_id(app_id)
    if not application:
        print(f"❌ Application with ID {app_id} not found.")
        return False
    
    print(f"📋 Application loaded: {application.company} - {application.job_title}")
    
    # 1. Generate structured research section
    from app.utils.message_logger import log_message
    log_message(87, "\n1️⃣ Generating Research Section...")
    research_path = generate_structured_research(
        application.folder_path, 
        company, 
        job_title, 
        job_url
    )
    
    if research_path:
        # Update application metadata
        application.research_path = research_path
        job_processor._save_application_metadata(application)
        print(f"✅ Research section generated and metadata updated")
    else:
        print("❌ Failed to generate research section")
        return False
    
    # 2. Generate hiring manager intro messages
    from app.utils.message_logger import log_message
    log_message(88, "\n2️⃣ Generating Hiring Manager Intro Messages...")
    try:
        # Load qualifications for intro message generation
        if application.qualifications_path and Path(application.qualifications_path).exists():
            qual_content = read_text_file(application.qualifications_path)
            
            # Extract match score from qualifications
            import re
            match_score = 0.0
            score_match = re.search(r'Match Score:?\s*(\d+)', qual_content, re.IGNORECASE)
            if score_match:
                match_score = float(score_match.group(1))
            
            # Create a basic QualificationAnalysis object
            qualifications = QualificationAnalysis(
                match_score=match_score,
                features_compared=0,
                strong_matches=["Technical expertise", "Data analysis", "Project management"],
                missing_skills=[],
                partial_matches=[],
                soft_skills=[],
                recommendations=[],
                detailed_analysis=qual_content
            )
            
            # Load research content if available
            research_content = None
            if application.research_path and Path(application.research_path).exists():
                try:
                    research_content = read_text_file(application.research_path)
                except Exception as e:
                    print(f"  ⚠️ Warning: Could not load research file: {e}")
            
            hiring_manager_intros = ai_analyzer.generate_hiring_manager_intros(
                qualifications,
                company,
                job_title,
                "Kervin Leacock",
                research_content=research_content
            )
        else:
            print("❌ Qualifications file not found for intro generation")
            return False
        
        # Save hiring manager intro messages
        hiring_manager_filename = f"KervinLeacock-{company.replace(' ', '-')}-{job_title.replace(' ', '-')}-hiring-manager-intros.md"
        hiring_manager_path = application.folder_path / hiring_manager_filename
        write_text_file(hiring_manager_intros, hiring_manager_path)
        
        # Update application metadata
        application.hiring_manager_intros_path = hiring_manager_path
        print(f"✅ Hiring manager intro messages generated: {hiring_manager_path}")
        
    except Exception as e:
        print(f"❌ Error generating hiring manager intro messages: {e}")
        return False
    
    # 3. Generate recruiter intro messages
    print("\n3️⃣ Generating Recruiter Intro Messages...")
    try:
        # Load research content if available (reload in case it wasn't loaded above)
        research_content = None
        if application.research_path and Path(application.research_path).exists():
            try:
                research_content = read_text_file(application.research_path)
            except Exception as e:
                print(f"  ⚠️ Warning: Could not load research file: {e}")
        
        recruiter_intros = ai_analyzer.generate_recruiter_intros(
            qualifications,
            company,
            job_title,
            "Kervin Leacock",
            research_content=research_content
        )
        
        # Save recruiter intro messages
        recruiter_filename = f"KervinLeacock-{company.replace(' ', '-')}-{job_title.replace(' ', '-')}-recruiter-intros.md"
        recruiter_path = application.folder_path / recruiter_filename
        write_text_file(recruiter_intros, recruiter_path)
        
        # Update application metadata
        application.recruiter_intros_path = recruiter_path
        print(f"✅ Recruiter intro messages generated: {recruiter_path}")
        
    except Exception as e:
        print(f"❌ Error generating recruiter intro messages: {e}")
        return False
    
    # 4. Regenerate summary page
    print("\n4️⃣ Regenerating Summary Page...")
    try:
        # Regenerate summary page
        doc_generator.generate_summary_page(application, qualifications)
        
        # Save updated metadata
        job_processor._save_application_metadata(application)
        
        print(f"✅ Summary page regenerated: {application.summary_path}")
        
    except Exception as e:
        print(f"❌ Error regenerating summary page: {e}")
        return False
    
    print("\n" + "=" * 60)
    print(f"🎉 {company} application processing completed successfully!")
    print(f"📁 Application folder: {application.folder_path}")
    print(f"📄 Research file: {research_path}")
    print(f"📄 Hiring manager intros: {hiring_manager_path}")
    print(f"📄 Recruiter intros: {recruiter_path}")
    print(f"📄 Summary page: {application.summary_path}")
    
    return True

if __name__ == "__main__":
    # Process MHS application (October 16th)
    app_id = "20251016195713-MHS-Senior Director - Business Intelligenc"
    company = "MHS"
    job_title = "Senior Director - Business Intelligence"
    job_url = "https://jobs.mhs.com/job/senior-director-business-intelligence"
    
    success = process_application(app_id, company, job_title, job_url)
    
    if success:
        print("\n✅ Ready to proceed to next application!")
    else:
        print("\n❌ Processing failed. Please check the errors above.")
