"""Qualification analysis data model"""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class QualificationAnalysis:
    """Represents a qualification analysis result"""
    
    match_score: float
    features_compared: int
    strong_matches: List[str]
    missing_skills: List[str]
    partial_matches: List[str]
    soft_skills: List[Dict[str, str]]
    recommendations: List[str]
    detailed_analysis: str
    preliminary_analysis: Optional[Dict] = None  # Single source of truth for matching data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QualificationAnalysis':
        """Create QualificationAnalysis instance from dictionary"""
        return cls(
            match_score=data.get('match_score', 0.0),
            features_compared=data.get('features_compared', 0),
            strong_matches=data.get('strong_matches', []),
            missing_skills=data.get('missing_skills', []),
            partial_matches=data.get('partial_matches', []),
            soft_skills=data.get('soft_skills', []),
            recommendations=data.get('recommendations', []),
            detailed_analysis=data.get('detailed_analysis', ''),
            preliminary_analysis=data.get('preliminary_analysis', None)
        )
    
    def to_dict(self) -> dict:
        """Convert QualificationAnalysis instance to dictionary"""
        return {
            'match_score': self.match_score,
            'features_compared': self.features_compared,
            'strong_matches': self.strong_matches,
            'missing_skills': self.missing_skills,
            'partial_matches': self.partial_matches,
            'soft_skills': self.soft_skills,
            'recommendations': self.recommendations,
            'detailed_analysis': self.detailed_analysis,
            'preliminary_analysis': self.preliminary_analysis
        }
    
    def get_strong_matches(self) -> List[str]:
        """Extract strong matches from preliminary_analysis (backward compatibility)"""
        if not self.preliminary_analysis:
            return self.strong_matches  # Fallback to stored list
        
        strong_matches = []
        for match in self.preliminary_analysis.get('exact_matches', []):
            skill = match.get('skill', '')
            if skill and skill not in strong_matches:
                strong_matches.append(skill)
        return strong_matches
    
    def get_partial_matches(self) -> List[str]:
        """Extract partial matches from preliminary_analysis (backward compatibility)"""
        if not self.preliminary_analysis:
            return self.partial_matches  # Fallback to stored list
        
        partial_matches = []
        for match in self.preliminary_analysis.get('partial_matches', []):
            skill = match.get('skill', '')
            if skill and skill not in partial_matches:
                partial_matches.append(skill)
        return partial_matches
    
    def get_soft_skills(self) -> List[Dict[str, str]]:
        """Extract soft skills from preliminary_analysis (backward compatibility)"""
        if not self.preliminary_analysis:
            return self.soft_skills  # Fallback to stored list
        
        soft_skills = []
        soft_categories = ['Leadership', 'Communication', 'Strategic Thinking', 'Problem Solving']
        for match in self.preliminary_analysis.get('exact_matches', []):
            category = match.get('category', '')
            if category in soft_categories:
                soft_skills.append({
                    'skill': match.get('skill', ''),
                    'category': category,
                    'match_level': 'Strong Match'
                })
        return soft_skills

