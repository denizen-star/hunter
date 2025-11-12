"""AI prompt templates"""

QUALIFICATION_ANALYSIS_PROMPT = """You are a career advisor analyzing how well a candidate's resume matches a job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_content}

---
TECHNOLOGY ANALYSIS (PRE-COMPUTED - DO NOT MODIFY):

{tech_summary}

Matched Technologies: {matched_technologies}
Missing Technologies: {missing_technologies}
---

IMPORTANT: The technology matching above has been pre-computed using exact string matching. DO NOT attempt to re-analyze or modify the technology matches. Simply use this information in your analysis.

CRITICAL: Before listing any skill as "Missing", carefully examine the resume for evidence of that skill. Look for:
- Job titles that indicate the skill (e.g., "Product Manager" indicates product management experience)
- Bullet points describing relevant experience
- Years of experience in related roles
- Specific achievements that demonstrate the skill
- Related technologies or tools that demonstrate the skill
- Industry experience that implies the skill
- Educational background that supports the skill
- EQUIVALENT or RELATED skills that demonstrate the same capabilities

IMPORTANT: Be GENEROUS in recognizing skills. For overqualified candidates, look for:
- "AWS Lake Formation" is covered by general AWS experience
- "Amazon Kinesis" is covered by AWS streaming/data experience
- "Budget Management" is covered by leadership, management, or financial experience
- "Financial Management" is covered by budget, management, or leadership experience
- "Product Strategy" is covered by strategy, planning, or product experience
- "Data Engineering" is covered by data warehousing, ETL, or data processing experience

For example:
- "Leadership" is demonstrated by managing teams, directing projects, or having leadership titles
- "Product Management" is demonstrated by product manager roles, roadmaps, feature specifications, etc.
- "Data Strategy" is demonstrated by strategic planning, roadmaps, data initiatives, etc.
- "Business Intelligence" is demonstrated by experience with BI tools, analytics, reporting, dashboards
- "Data Engineering" is demonstrated by ETL processes, data pipelines, data warehousing, etc.
- "Cloud Platforms" is demonstrated by AWS, Azure, GCP experience or cloud-related projects
- "AWS Services" (specific) are demonstrated by general AWS experience or cloud platform experience

Please provide a detailed analysis in the following format:

## Skills Match Summary
- Match Score: [percentage as a number, e.g., 85]
  * Consider: Technical skills (40%), Technologies/Tools (30%), Experience level (15%), Soft skills (10%), Other factors (5%)
- Features Compared: [total number of features/skills you analyzed]
- Strong Matches: {matched_technologies}
- Missing Skills: [ONLY list skills that are genuinely absent from the resume after careful examination, separated by commas]
- Missing Technologies: {missing_technologies}

## Technology Comparison

**Match Score: {tech_summary}**

### ✅ Matched Technologies
{matched_technologies}

### ❌ Missing Technologies
{missing_technologies}

## Detailed Skill Analysis

For each major skill/requirement in the job description (EXCLUDE TECHNOLOGIES - focus on conceptual skills, experience, and responsibilities):

| Skill Name | Job Requirement | Resume Evidence | Match Level |
| --- | --- | --- | --- |
| [Skill] | [Quote from job description] | [Quote from resume or "Not demonstrated"] | Strong Match / Partial Match / No Match |

IMPORTANT: When evaluating "Resume Evidence", look for:
- Direct job titles that indicate the skill
- Bullet points that describe relevant experience
- Years of experience in related roles
- Specific achievements or responsibilities that demonstrate the skill
- Leadership experience (managing teams, directing projects, etc.)
- Strategic experience (roadmaps, planning, initiatives, etc.)

## Soft Skills Alignment

| Soft Skill | Job Description | Resume Evidence | Match Level |
| --- | --- | --- | --- |
| [Skill] | [Quote from job] | [Evidence or "Not demonstrated"] | Strong Match / Partial Match / No Match |

## Recommendations

1. [Recommendation to emphasize relevant experience]
2. [Recommendation to address gaps]
3. [Recommendation for interview preparation]
4. [Optional: Additional recommendations]
5. [Optional: Additional recommendations]"""


COVER_LETTER_PROMPT = """You are a professional cover letter writer. Generate the actual cover letter content directly - do not provide explanations or meta-commentary about creating a cover letter.

CANDIDATE STRENGTHS:
{strong_matches}

MISSING SKILLS TO ADDRESS:
{missing_skills}

SOFT SKILLS TO EMPHASIZE (use 50% of these):
{soft_skills}

COMPANY: {company}
JOB TITLE: {job_title}

{research_section}

Generate a professional cover letter following this structure and style:

**STRUCTURE:**
- Opening paragraph: Express interest and state why you're a great fit. Lead with years of experience and "numerous roles of responsibility." Emphasize steadfast dedication to delivering high-level customer satisfaction and achieving success by aligning products/services with bottom-line organizational goals. Close with "my pleasure to present my resume for your consideration."

- Body paragraph 1 (Leadership & Strategic Impact): Showcase leadership skills as critical in developing strategic plans that align with corporate strategies. Demonstrate a proactive, innovative mindset: passionate about redirecting focus, shifting from traditional methodologies to drive alignment and unleash unprecedented growth opportunities. Highlight track record of "piecing together the larger picture, devising critical solutions to streamline processes." Emphasize ability to analyze inefficiencies and sluggish workflows, then mastermind successful solutions. Mention ability to "unify teams and impress even the toughest of customers."

- Body paragraph 2 (Personal Attributes & Teamwork): Position yourself as a "natural leader, owning a rare blend of adaptability and vision." Emphasize "unique mix of people management skills" leading to outstanding results across all segments. Describe yourself as an "excellent communicator and firm believer in the value of relationships." Highlight ability to "easily connect with others, shaping top-performing, cross-functional teams." Add specific details about why the company is a great fit for you and why you are a great fit for the company. Use the research information provided above to reference specific company details such as their mission, recent news, products/services, or market position. Include soft skills and strong matches from the qualifications analysis.

- Closing paragraph: Thank the reader for their time in reviewing your resume. Provide a clear call to action inviting them to discuss your skills, professional experiences, and career accomplishments further.

**TONE & STYLE REQUIREMENTS:**
- Professional yet confident, sophisticated and personable
- Experience-driven: Emphasize years of experience and diverse roles
- Results-oriented: Focus on customer satisfaction, bottom-line goals, profitable conclusions, and outstanding results
- Strategic and analytical: Highlight strategic planning, identifying trends, analyzing inefficiencies, and devising critical solutions
- Leadership and team-focused: Stress leadership skills, unifying teams, people management, and shaping cross-functional teams
- Proactive and innovative: Mention shifting methodologies and unleashing growth opportunities
- Use strong action verbs: "piecing together," "devising," "mastermind," "unify," "shaping," "redirecting," "unleashing"
- Clear, concise language that conveys competence and dedication
- Sound like a human, not a robot - current, relevant, and confident
- Personalize it to each job description and company using the research information provided

**LENGTH:** 300-350 words (slightly longer to accommodate company interest section)

**CLOSING FORMAT:**
- End with "Sincerely," on its own line
- Follow with the candidate's actual name on the next line
- NEVER use placeholders like "[Your Name]", "[YOUR NAME]", or "[Name]" in the closing
- Do NOT include contact information in the closing (it will be added separately if needed)

Start directly with "Dear Hiring Manager," and end with "Sincerely," followed by the actual name.

IMPORTANT: Generate the actual cover letter content. Do not include any introductory text like "Here is a cover letter" or explanations. Start immediately with the salutation. Never use placeholders like [YOUR NAME], [YOUR SIGNATURE], or [Name] anywhere in the letter. Use the research information naturally and organically to demonstrate genuine interest in the company.
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

## 12. Additional Insights
[Extract any competitive insights or applicant information from sections like "See how you compare to others who clicked apply", "About applicants", "X applicants", "Competition level", or similar. Include:
- Number of applicants who have applied
- Skills comparison data
- Application statistics
- Any other competitive intelligence
If not found, write "Not available"]

## 13. Hiring Team Information
[Extract hiring team details from sections with ANY of these headings: "Meet the hiring team", "People you can reach out to", "About the hiring manager", "Contact the hiring team", or similar variations. For each person, capture:
- Name
- Position/Title  
- Company
- Connection degree (1st, 2nd, 3rd, etc.)
- Role in this job (Job poster, Hiring manager, etc.)
Format as: "Name | Position at Company | Connection: X degree | Role: Y"
If no hiring team information is found, write "Not available"]

## Other Information
[Any other relevant information that doesn't fit the above categories, such as application instructions, equal opportunity statements, accommodation processes, etc.]

Be thorough and extract all relevant information from the job description."""


HIRING_MANAGER_INTRO_PROMPT = """You are creating professional intro messages for hiring managers. Generate 3 versions of an intro message based on the provided information.

COMPANY: {company}
JOB TITLE: {job_title}
MATCH SCORE: {match_score}%
STRONG MATCHES: {strong_matches}
CANDIDATE NAME: {candidate_name}

CANDIDATE BACKGROUND: 15+ years data leadership, managed $3T daily transactions at BoNY Mellon, VP BI experience, led 250+ employees, Databricks/MLOps expertise, lakehouse solutions, data governance.

{research_section}

**TONE & STYLE REQUIREMENTS:**
- Professional yet confident, sophisticated and personable
- Experience-driven: Emphasize years of experience and diverse roles
- Results-oriented: Focus on bottom-line goals, profitable conclusions, and outstanding results
- Strategic and analytical: Highlight strategic planning, identifying trends, analyzing inefficiencies, and devising critical solutions
- Leadership and team-focused: Stress leadership skills, unifying teams, people management, and shaping cross-functional teams
- Proactive and innovative: Mention shifting methodologies and unleashing growth opportunities
- Use strong action verbs: "piecing together," "devising," "mastermind," "unify," "shaping," "redirecting," "unleashing"
- Clear, concise language that conveys competence and dedication
- Sound like a human, not a robot - current, relevant, and confident
- Use the research information to reference specific company details naturally (mission, recent news, products/services, challenges) to demonstrate genuine interest

Create exactly 3 versions with specific character counts. Be specific about actual achievements and experience. Where appropriate and within character limits, naturally incorporate relevant research details about the company.

Format each message as:
"RE: " {job_title}

"Hi Person, 

I recently applied for this role (leacock.kervin@gmail.com)." [intro message with specified character count]

**MESSAGE 1:**
RE: {job_title}

Hi Person, 

I recently applied for this role (leacock.kervin@gmail.com). [~275 characters total - Emphasize years of experience and "numerous roles of responsibility." Be specific about $3T transactions, 250+ team leadership, and key technical achievements. Use professional yet confident tone with strong action verbs. If space allows, briefly reference a relevant company detail from the research.]

**MESSAGE 2:**
RE: {job_title}

Hi Person, 

I recently applied for this role (leacock.kervin@gmail.com). [~500 characters total - Showcase leadership skills in developing strategic plans. Demonstrate proactive, innovative mindset: passionate about redirecting focus and unleashing growth opportunities. Highlight track record of piecing together the larger picture and devising critical solutions. Be specific about Databricks/lakehouse, data governance, and business impact. Emphasize ability to unify teams and deliver outstanding results. Reference specific company details from the research (mission, recent news, or challenges) to show genuine interest and alignment.]

**MESSAGE 3:**
RE: {job_title}

Hi Person, 

I recently applied for this role (leacock.kervin@gmail.com). [~500 characters total - VP/SVP/Director tone with business language and outrageous touch to drive attention. Be bold and confident about achievements. Use research details strategically to demonstrate deep understanding of the company's direction and how your expertise aligns with their needs.]

Each message should be direct, specific about actual achievements, and use the exact character counts specified. Message 3 should be particularly attention-grabbing while remaining professional. Naturally weave in relevant research details where they enhance the message without making it feel forced."""


RECRUITER_INTRO_PROMPT = """You are creating professional intro messages for recruiters. Generate 3 versions of an intro message based on the provided information.

COMPANY: {company}
JOB TITLE: {job_title}
MATCH SCORE: {match_score}%
STRONG MATCHES: {strong_matches}
CANDIDATE NAME: {candidate_name}

CANDIDATE BACKGROUND: 15+ years data leadership, managed $3T daily transactions at BoNY Mellon, VP BI experience, led 250+ employees, Databricks/MLOps expertise, lakehouse solutions, data governance.

{research_section}

IMPORTANT: Recruiters are typically not technical, so avoid jargon and technical terms. Use business language. Focus on business impact and leadership achievements.

**TONE & STYLE REQUIREMENTS:**
- Professional yet confident, sophisticated and personable
- Experience-driven: Emphasize years of experience and diverse roles
- Results-oriented: Focus on customer satisfaction, bottom-line goals, profitable conclusions, and outstanding results
- Strategic and analytical: Highlight strategic planning, identifying trends, analyzing inefficiencies, and devising critical solutions (expressed in business terms)
- Leadership and team-focused: Stress leadership skills, unifying teams, people management, and shaping cross-functional teams
- Proactive and innovative: Mention shifting methodologies and unleashing growth opportunities
- Use strong action verbs: "piecing together," "devising," "mastermind," "unify," "shaping," "redirecting," "unleashing"
- Clear, concise language that conveys competence and dedication
- Sound like a human, not a robot - current, relevant, and confident
- Use business language, not technical jargon
- Use the research information to reference specific company details naturally (mission, recent news, products/services) in business terms to demonstrate genuine interest

Create exactly 3 versions with specific character counts. Be specific about actual business achievements. Where appropriate and within character limits, naturally incorporate relevant research details about the company in business language.

Format each message as:
"RE: " {job_title}

"Hi Person, 

I recently applied for this role (leacock.kervin@gmail.com)." [intro message with specified character count]

**MESSAGE 1:**
RE: {job_title}

Hi Person, 

I recently applied for this role (leacock.kervin@gmail.com). [~275 characters total - Emphasize years of experience and "numerous roles of responsibility." Be specific about $3T transactions, 250+ team leadership, and business impact. Use professional yet confident tone with strong action verbs. Avoid technical jargon - focus on business value and results. If space allows, briefly reference a relevant company detail from the research in business terms.]

**MESSAGE 2:**
RE: {job_title}

Hi Person, 

I recently applied for this role (leacock.kervin@gmail.com). [~500 characters total - Showcase leadership skills in developing strategic plans that align with corporate strategies. Demonstrate proactive, innovative mindset: passionate about redirecting focus and unleashing unprecedented growth opportunities. Highlight track record of piecing together the larger picture and devising critical solutions to streamline processes. Be specific about VP BI achievements, data strategy, and business value. Emphasize ability to unify teams and deliver outstanding results across all segments. Focus on results and business impact - avoid technical jargon. Reference specific company details from the research (mission, recent news, or market position) in business language to show genuine interest and alignment.]

**MESSAGE 3:**
RE: {job_title}

Hi Person, 

I recently applied for this role (leacock.kervin@gmail.com). [~500 characters total - VP/SVP/Director tone with business language and outrageous touch to drive attention. Be bold and confident about business achievements. Use research details strategically in business terms to demonstrate deep understanding of the company's direction and how your expertise aligns with their business needs.]

Each message should be direct, specific about actual business achievements, and use the exact character counts specified. Message 3 should be particularly attention-grabbing while remaining professional. Avoid technical jargon - use business language throughout. Naturally weave in relevant research details where they enhance the message without making it feel forced."""


def get_prompt(prompt_name: str, **kwargs) -> str:
    """Get a formatted prompt by name"""
    prompts = {
        'qualification_analysis': QUALIFICATION_ANALYSIS_PROMPT,
        'cover_letter': COVER_LETTER_PROMPT,
        'resume_rewrite': RESUME_REWRITE_PROMPT,
        'summary_generation': SUMMARY_GENERATION_PROMPT,
        'job_description_extraction': JOB_DESCRIPTION_EXTRACTION_PROMPT,
        'hiring_manager_intro': HIRING_MANAGER_INTRO_PROMPT,
        'recruiter_intro': RECRUITER_INTRO_PROMPT
    }
    
    if prompt_name not in prompts:
        raise ValueError(f"Unknown prompt: {prompt_name}")
    
    return prompts[prompt_name].format(**kwargs)

