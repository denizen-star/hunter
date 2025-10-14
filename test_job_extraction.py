#!/usr/bin/env python3
"""
Test script for comprehensive job description extraction
"""
from app.services.ai_analyzer import AIAnalyzer
from app.utils.file_utils import read_text_file
from pathlib import Path

def test_extraction():
    """Test the comprehensive job description extraction"""
    
    # Sample job description (LinkedIn format with metadata)
    sample_job = """Skip to main content
LinkedIn

Jobs
SVP, Aviva Data Intelligence
Clear text
Toronto, ON
Clear text

Sign in
Join now
Aviva Canada
SVP, Aviva Data Intelligence
Aviva Canada Markham, Ontario, Canada
Apply 
Aviva Canada
SVP, Aviva Data Intelligence
Aviva Canada  Markham, Ontario, Canada
4 days ago  116 applicants

Individually we are people, but together we are Aviva. Individually these are just words, but together they are our Values – Care, Commitment, Community, and Confidence.

The SVP, Data Intelligence is a visionary and strategic leader responsible for shaping and executing Aviva Canada's enterprise-wide data strategy.

What You'll Do

Data Strategy & Leadership

Define and implement a long-term data strategy aligned with Aviva Canada's business goals.
Champion data-driven insights and decision-making.

What You'll Bring

Bachelor's or Master's degree in Computer Science, Data Science, Information Science, Engineering, or a related field.
15+ years of progressive experience in technology and data.

What You'll Get

Competitive compensation including base salary, annual bonus eligibility, retirement savings.
Executive-level health and wellness benefits.
Generous vacation package.

Why Join Us?

This is a rare opportunity to lead the transformation of data into a strategic asset.
"""
    
    print("🧪 Testing Comprehensive Job Description Extraction")
    print("=" * 60)
    
    # Initialize AI analyzer
    ai_analyzer = AIAnalyzer()
    
    # Check Ollama connection
    print("\n1. Checking Ollama connection...")
    if not ai_analyzer.check_connection():
        print("❌ Ollama is not running!")
        print("Please start Ollama: ollama serve")
        return False
    print("✓ Ollama connected")
    
    # Test posting date extraction
    print("\n2. Testing posting date extraction...")
    posted_date = ai_analyzer._extract_posting_date(sample_job)
    print(f"✓ Posted date: {posted_date}")
    
    # Test comprehensive extraction
    print("\n3. Testing comprehensive job details extraction...")
    print("   (This may take a minute...)")
    
    try:
        # Clean the job description (basic cleaning)
        cleaned = sample_job.replace("Skip to main content", "").replace("LinkedIn", "")
        
        # Extract comprehensive details
        result = ai_analyzer.extract_comprehensive_job_details(
            cleaned,
            sample_job
        )
        
        print("\n✓ Extraction successful!")
        print("\n" + "=" * 60)
        print("EXTRACTED JOB DESCRIPTION:")
        print("=" * 60)
        print(result[:1000] + "..." if len(result) > 1000 else result)
        print("\n" + "=" * 60)
        
        # Verify key sections are present
        sections_to_check = [
            "Job Title",
            "Location and Employment Type",
            "Compensation",
            "Job Summary",
            "Key Responsibilities",
            "Required Qualifications",
            "Benefits",
            "Posted Date"
        ]
        
        print("\n4. Verifying extracted sections:")
        for section in sections_to_check:
            if section in result:
                print(f"   ✓ {section}")
            else:
                print(f"   ✗ {section} (missing)")
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_extraction()
    exit(0 if success else 1)

