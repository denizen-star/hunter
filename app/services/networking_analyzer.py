"""AI analysis service for networking contacts"""
from typing import Dict, List, Optional
from app.services.ai_analyzer import AIAnalyzer


class NetworkingAnalyzer:
    """Analyzes networking contacts using AI for matching and conversation topics"""
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
    
    def analyze_networking_match(
        self,
        resume_content: str,
        profile_details: str,
        person_name: str,
        company_name: str,
        job_title: Optional[str] = None
    ) -> Dict:
        """
        Perform comprehensive networking match analysis.
        Returns match score (0-100) and detailed breakdown of commonalities.
        """
        
        prompt = f"""Analyze this professional networking opportunity and provide a comprehensive match score.

YOUR RESUME/BACKGROUND:
{resume_content}

PROFESSIONAL CONTACT TO ANALYZE:
Name: {person_name}
Company: {company_name}
{f'Title: {job_title}' if job_title else ''}

THEIR PROFILE:
{profile_details}

Provide a comprehensive networking match analysis with these components:

1. OVERALL MATCH SCORE (0-100):
   - Calculate based on skill overlap, career similarity, common interests, and networking value
   - Weight: 25% skill overlap + 25% career path similarity + 25% common interests + 25% networking value

2. SKILL OVERLAP:
   - List shared technical skills
   - List shared domain expertise
   - Rate: Low/Medium/High

3. CAREER PATH SIMILARITY:
   - Analyze similar career trajectories
   - Identify common industries or roles
   - Rate: Low/Medium/High

4. COMMON INTERESTS:
   - Identify shared professional interests
   - Note common topics of discussion
   - List potential conversation starters

5. NETWORKING VALUE:
   - Assess potential for collaboration
   - Identify learning opportunities
   - Note referral/introduction potential
   - Rate: Low/Medium/High

6. CONVERSATION TOPICS (5-7 specific topics):
   - Be specific and provocative
   - Reference actual skills, experiences, or interests from both profiles
   - Make them engaging conversation starters

Format your response as:

MATCH SCORE: [number 0-100]

SKILL OVERLAP: [High/Medium/Low]
Shared Skills:
- [skill 1]
- [skill 2]
...

CAREER SIMILARITY: [High/Medium/Low]
Common Elements:
- [element 1]
- [element 2]
...

COMMON INTERESTS:
- [interest 1]
- [interest 2]
...

NETWORKING VALUE: [High/Medium/Low]
Opportunities:
- [opportunity 1]
- [opportunity 2]
...

CONVERSATION TOPICS:
1. [Topic 1 - specific and provocative]
2. [Topic 2 - reference shared experience]
3. [Topic 3 - ask about their expertise]
4. [Topic 4 - share your perspective]
5. [Topic 5 - explore collaboration]

SYNTHESIS:
[2-3 paragraphs explaining why this is a valuable connection and how to approach them]
"""
        
        try:
            analysis = self.ai_analyzer._call_ollama(prompt)
            
            # Parse match score
            match_score = 0
            if "MATCH SCORE:" in analysis:
                try:
                    score_line = [line for line in analysis.split('\n') if 'MATCH SCORE:' in line][0]
                    match_score = float(score_line.split(':')[1].strip())
                except:
                    match_score = 75  # Default if parsing fails
            
            return {
                'match_score': match_score,
                'detailed_analysis': analysis,
                'person_name': person_name,
                'company_name': company_name
            }
        except Exception as e:
            print(f"Error in AI networking analysis: {e}")
            return {
                'match_score': 0,
                'detailed_analysis': f"Error performing analysis: {str(e)}",
                'person_name': person_name,
                'company_name': company_name
            }
    
    def extract_conversation_starters(self, match_analysis: str) -> List[str]:
        """Extract conversation topics from match analysis"""
        topics = []
        in_topics_section = False
        
        for line in match_analysis.split('\n'):
            if 'CONVERSATION TOPICS:' in line:
                in_topics_section = True
                continue
            if in_topics_section:
                if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
                    # Remove number/bullet and clean up
                    topic = line.strip()
                    if topic[0].isdigit():
                        topic = '.'.join(topic.split('.')[1:]).strip()
                    elif topic.startswith('-'):
                        topic = topic[1:].strip()
                    if topic:
                        topics.append(topic)
                elif line.strip().isupper() or line.strip().startswith('SYNTHESIS'):
                    # End of topics section
                    break
        
        return topics if topics else [
            "Ask about their experience in their current role",
            "Discuss industry trends and challenges",
            "Share insights from your own work",
            "Explore potential collaboration opportunities"
        ]
    
    def generate_connection_commonalities(self, match_analysis: str) -> Dict[str, List[str]]:
        """
        Extract structured commonalities from match analysis for message generation.
        Returns categorized lists of shared elements.
        """
        commonalities = {
            'skills': [],
            'experiences': [],
            'interests': [],
            'industries': []
        }
        
        # Parse the analysis to extract structured data
        current_section = None
        
        for line in match_analysis.split('\n'):
            line = line.strip()
            
            # Identify sections
            if 'SKILL OVERLAP:' in line or 'Shared Skills:' in line:
                current_section = 'skills'
                continue
            elif 'CAREER SIMILARITY:' in line or 'Common Elements:' in line:
                current_section = 'experiences'
                continue
            elif 'COMMON INTERESTS:' in line:
                current_section = 'interests'
                continue
            
            # Extract bullet points
            if current_section and line.startswith('-'):
                item = line[1:].strip()
                if item:
                    commonalities[current_section].append(item)
        
        return commonalities
