"""AI prompt templates"""

QUALIFICATION_ANALYSIS_PROMPT = """You are a career advisor analyzing how well a candidate's resume matches a job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_content}

Please provide a detailed analysis in the following format:

## Skills Match Summary
- Match Score: [percentage as a number, e.g., 85]
  * Consider: Technical skills (40%), Technologies/Tools (30%), Experience level (15%), Soft skills (10%), Other factors (5%)
- Features Compared: [total number of features/skills you analyzed]
- Strong Matches: [list top 5 matching skills, separated by commas]
- Missing Skills: [list skills mentioned in job but not in resume, separated by commas]
- Missing Technologies: [list key technologies mentioned in job but not in resume, separated by commas]

## Detailed Skill Analysis
**Skills Analyzed: [count of skills below]**

For each major skill/requirement in the job description:
1. Skill Name
2. Job Requirement (quote from description)
3. Resume Evidence (quote from resume if match exists)
4. Match Level: Strong Match / Partial Match / No Match

## Technologies & Tools
**Technologies Compared: [count of technologies analyzed]**
**Technologies Matched: [count found in resume] | Missing: [count not in resume]**

Extract ALL technologies, tools, platforms, programming languages, frameworks, databases, and software mentioned in the job description. For each one:
- Technology Name
- Required in Job: Yes/No
- Found in Resume: Yes/No/Partial
- Resume Evidence: [specific mention or related experience]

Group by categories (show both matched and missing):
- Programming Languages: [list matched ✓ and missing ✗]
- Frameworks & Libraries: [list matched ✓ and missing ✗]
- Databases: [list matched ✓ and missing ✗]
- Cloud Platforms: [list matched ✓ and missing ✗]
- Tools & Software: [list matched ✓ and missing ✗]
- Other Technologies: [list matched ✓ and missing ✗]

**Critical Missing Technologies:**
[List the most important technologies mentioned in the job description that are NOT found in the resume]

## Soft Skills Alignment
**Soft Skills Analyzed: [count of soft skills below]**

List relevant soft skills from job description and indicate if demonstrated in resume.

## Recommendations
Suggest 3-5 ways to emphasize relevant experience or address gaps.

Please be thorough and specific in your analysis. Count every technology, tool, and skill you analyze."""


COVER_LETTER_PROMPT = """You are a professional cover letter writer.

Write an eloquent, professional cover letter based on:

QUALIFICATIONS ANALYSIS:
{qualifications}

SOFT SKILLS TO EMPHASIZE (use 50% of these):
{soft_skills}

COMPANY: {company}
JOB TITLE: {job_title}

REQUIREMENTS:
- Opening paragraph: Express interest and briefly state why you're a great fit
- 2-3 body paragraphs: Integrate the provided soft skills naturally
- Emphasize strengths from the qualifications analysis
- Closing: Call to action
- Tone: Professional yet personable
- Length: 300-400 words

Format as markdown with proper structure.
Start with a proper salutation like "Dear Hiring Manager," and end with "Sincerely, [Name]"
"""


RESUME_REWRITE_PROMPT = """You are a professional resume writer specializing in ATS optimization.

ORIGINAL RESUME:
{original_resume}

QUALIFICATIONS ANALYSIS:
{qualifications}

Rewrite each job description bullet point to:
1. Align with keywords and requirements from the qualifications analysis
2. Keep bullets short (1-2 lines maximum)
3. Use strong action verbs
4. Quantify achievements where possible
5. Maintain professional tone
6. Ensure relevance to target job

Return the complete resume with rewritten bullets, maintaining the original structure and format.
Keep the contact information and overall structure the same, only improve the bullet points under each job/experience."""


SUMMARY_GENERATION_PROMPT = """You are a career advisor providing actionable next steps for a job application.

JOB INFORMATION:
Company: {company}
Job Title: {job_title}
Match Score: {match_score}%

QUALIFICATIONS ANALYSIS:
{qualifications_summary}

Based on this analysis, provide:

## Recommended Next Steps
1. [First action item]
2. [Second action item]
3. [Third action item]

## Key Talking Points for Interview
- [Point 1]
- [Point 2]
- [Point 3]

## Areas to Research Before Interview
- [Research area 1]
- [Research area 2]

Be specific and actionable. Focus on what the candidate should do to increase their chances of success."""


JOB_DESCRIPTION_EXTRACTION_PROMPT = """You are an expert at parsing job descriptions from LinkedIn and extracting structured information.

IMPORTANT: Extract information ONLY if it is explicitly stated in the job description. If information is not found, respond with "Not specified".

JOB DESCRIPTION:
{job_description}

Please extract and organize the following information in this EXACT format:

## 1. Job Title
[Extract the job title]

## 2. Location and Employment Type
**Location:** [City, State/Province, Country or Remote/Hybrid]
**Employment Type:** [Full-time/Part-time/Contract/etc.]

## 3. Compensation
**Salary Range:** [e.g., "$120,000 - $150,000 per year" or "Not specified"]
**Bonus Structure:** [e.g., "Annual bonus eligibility" or "Not specified"]

## 4. Job Summary/Overview
[Extract the 3-5 sentence overview that explains the role's purpose and importance. If there's a section like "About the Role" or introductory paragraph, extract it here.]

## 5. Key Responsibilities and Duties
[Extract all bullet points or paragraphs describing main tasks and expectations. Maintain original format if possible.]

## 6. Required Qualifications and Skills
[Extract mandatory requirements including:
- Education/Certifications
- Years of Experience
- Must-have Technical Skills
- Must-have Soft Skills]

## 7. Preferred Qualifications (Optional)
[Extract "nice-to-have" skills, experience, or attributes if mentioned separately. If not separated from required qualifications, write "Not separated from required qualifications"]

## 8. Benefits
[Extract details about benefits like health insurance, 401k, PTO, retirement, flexible work, etc.]

## 9. Company Culture/EVP
[Extract information about company values, diversity and inclusion, growth opportunities, work environment, etc.]

## 10. Company Overview
[Extract the company introduction, mission, and culture description if provided]

## 11. Job URL
[If there's a URL or link mentioned, extract it. Otherwise write "Not specified"]

## Other Information
[Any other relevant information that doesn't fit the above categories, such as application instructions, equal opportunity statements, accommodation processes, etc.]

Be thorough and extract all relevant information from the job description."""


def get_prompt(prompt_name: str, **kwargs) -> str:
    """Get a formatted prompt by name"""
    prompts = {
        'qualification_analysis': QUALIFICATION_ANALYSIS_PROMPT,
        'cover_letter': COVER_LETTER_PROMPT,
        'resume_rewrite': RESUME_REWRITE_PROMPT,
        'summary_generation': SUMMARY_GENERATION_PROMPT,
        'job_description_extraction': JOB_DESCRIPTION_EXTRACTION_PROMPT
    }
    
    if prompt_name not in prompts:
        raise ValueError(f"Unknown prompt: {prompt_name}")
    
    return prompts[prompt_name].format(**kwargs)

