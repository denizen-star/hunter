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
            detailed_analysis=data.get('detailed_analysis', '')
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
            'detailed_analysis': self.detailed_analysis
        }

