# Technical Reference - Enhanced Matching System

## API Reference

### PreliminaryMatcher Class

#### `__init__()`
```python
def __init__(self):
    self.skills_yaml_path = Path("/Users/kervinleacock/Documents/Development/hunter/data/resumes/skills.yaml")
    self.job_skills_path = Path("/Users/kervinleacock/Documents/Development/hunter/Jobdescr-General Skils.md")
    self.candidate_skills = {}
    self.job_skills = {}
    self.load_skills_data()
```

#### `find_skill_matches(job_description: str) -> Dict[str, any]`
**Purpose**: Find matches between job description and candidate skills

**Parameters**:
- `job_description` (str): The job description text to analyze

**Returns**:
```python
{
    'exact_matches': [
        {
            'skill': 'Python',
            'category': 'Programming Languages',
            'source': 'technical_skills'
        }
    ],
    'partial_matches': [...],
    'missing_skills': [...],
    'unmatched_job_skills': [...],
    'match_score': 81.6,
    'total_required': 125,
    'matched_count': 20,
    'missing_count': 23
}
```

#### `generate_preliminary_analysis(job_description: str) -> Dict[str, any]`
**Purpose**: Generate comprehensive preliminary analysis

**Parameters**:
- `job_description` (str): The job description text to analyze

**Returns**:
```python
{
    'preliminary_match_score': 81.6,
    'exact_matches': [...],
    'partial_matches': [...],
    'missing_skills': [...],
    'unmatched_job_skills': [...],
    'job_requirements': {
        'technical_skills': [...],
        'soft_skills': [...],
        'tools_technologies': [...],
        'experience_requirements': [...],
        'education_certifications': [...]
    },
    'match_summary': {
        'total_candidate_skills': 146,
        'matched_skills': 20,
        'missing_skills_count': 23,
        'match_percentage': 81.6
    },
    'ai_focus_areas': [
        'High match score - focus on experience depth and context',
        'Strong technical foundation - emphasize leadership experience'
    ]
}
```

#### `create_ai_prompt_context(job_description: str) -> str`
**Purpose**: Create context for AI analysis based on preliminary matching

**Parameters**:
- `job_description` (str): The job description text to analyze

**Returns**:
- `str`: Formatted context for AI analysis

### EnhancedQualificationsAnalyzer Class

#### `__init__()`
```python
def __init__(self):
    self.preliminary_matcher = PreliminaryMatcher()
    self.model = "llama3"
    self.base_url = "http://localhost:11434"
    self.timeout = 600
```

#### `analyze_qualifications_enhanced(job_description: str, resume_content: str) -> QualificationAnalysis`
**Purpose**: Enhanced qualifications analysis with preliminary matching

**Parameters**:
- `job_description` (str): The job description text to analyze
- `resume_content` (str): The candidate's resume content

**Returns**:
- `QualificationAnalysis`: Complete analysis object

**Process**:
1. Run preliminary matching
2. Create focused AI prompt based on preliminary results
3. Run AI analysis with focused prompt
4. Combine preliminary and AI results

#### `_run_focused_ai_analysis(job_description: str, resume_content: str, preliminary_analysis: Dict, ai_context: str) -> Dict`
**Purpose**: Run AI analysis with focused prompt based on preliminary results

**Parameters**:
- `job_description` (str): The job description text
- `resume_content` (str): The candidate's resume content
- `preliminary_analysis` (Dict): Results from preliminary matching
- `ai_context` (str): Context for AI analysis

**Returns**:
```python
{
    'match_score': 81.6,
    'features_compared': 126,
    'strong_matches': [...],
    'missing_skills': [...],
    'partial_matches': [...],
    'soft_skills': [...],
    'recommendations': [...],
    'detailed_analysis': '...'
}
```

## Data Structures

### Skills Database Format (`skills.yaml`)
```yaml
extracted_at: '2025-10-15T15:44:21.355280'
skills:
  Python:
    category: Programming Languages
    display_name: Python
    variations_found: [python]
    source: technical_skills
  AWS:
    category: Cloud Platforms
    display_name: AWS
    variations_found: [aws]
    source: technical_skills
  # ... more skills
total_skills: 146
```

### Job Skills Database Format (`Jobdescr-General Skils.md`)
```markdown
# Job Description General Skills Analysis

## Summary
- **Technical Skills**: 145 unique skills found
- **Soft Skills**: 93 unique skills found
- **Tools Technologies**: 108 unique skills found
- **Experience Requirements**: 65 unique skills found
- **Education Certifications**: 26 unique skills found

## Technical Skills
- Python
- SQL
- Tableau
- AWS
- ...

## Soft Skills
- Leadership
- Communication
- Strategic Planning
- ...
```

### QualificationAnalysis Object
```python
@dataclass
class QualificationAnalysis:
    match_score: float
    features_compared: int
    strong_matches: List[str]
    missing_skills: List[str]
    partial_matches: List[str]
    soft_skills: List[Dict[str, str]]
    recommendations: List[str]
    detailed_analysis: str
```

## Configuration

### Environment Variables
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_TIMEOUT=600

# Python Path (for imports)
PYTHONPATH=/Users/kervinleacock/Documents/Development/hunter
```

### File Paths
```python
# Skills Database
SKILLS_YAML_PATH = "/Users/kervinleacock/Documents/Development/hunter/data/resumes/skills.yaml"

# Job Skills Database
JOB_SKILLS_PATH = "/Users/kervinleacock/Documents/Development/hunter/Jobdescr-General Skils.md"

# Backup Directory
BACKUP_DIR = "/Users/kervinleacock/Documents/Development/hunter/backup_qualifications_engine_*"
```

## Error Handling

### Common Exceptions

#### `ConnectionError`
```python
try:
    response = self._call_ollama(prompt)
except ConnectionError as e:
    print("Cannot connect to Ollama. Please ensure Ollama is running:")
    print("  1. Install: brew install ollama")
    print("  2. Start: ollama serve")
    print("  3. Pull model: ollama pull llama3")
```

#### `TimeoutError`
```python
try:
    response = self._call_ollama(prompt)
except TimeoutError as e:
    print("Ollama request timed out. The model might be taking too long to respond.")
```

#### `FileNotFoundError`
```python
try:
    with open(self.skills_yaml_path, 'r') as f:
        skills_data = yaml.safe_load(f)
except FileNotFoundError:
    print(f"Skills database not found at {self.skills_yaml_path}")
    print("Please ensure skills.yaml exists in data/resumes/")
```

### Fallback Behavior
```python
# Enhanced analyzer not available
if not ENHANCED_ANALYZER_AVAILABLE:
    print("⚠️ Enhanced Qualifications Analyzer not available - using standard AI analysis")
    return self._analyze_qualifications_original(job_description, resume_content)

# Ollama not available
if not self.check_connection():
    raise ConnectionError("Ollama is not running")
```

## Performance Monitoring

### Metrics Collection
```python
import time
import logging

def analyze_qualifications_enhanced(self, job_description: str, resume_content: str):
    start_time = time.time()
    
    # Phase 1: Preliminary matching
    preliminary_start = time.time()
    preliminary_analysis = self.preliminary_matcher.generate_preliminary_analysis(job_description)
    preliminary_time = time.time() - preliminary_start
    
    # Phase 2: AI analysis
    ai_start = time.time()
    ai_analysis = self._run_focused_ai_analysis(...)
    ai_time = time.time() - ai_start
    
    total_time = time.time() - start_time
    
    # Log performance metrics
    logging.info(f"Analysis completed in {total_time:.2f}s")
    logging.info(f"Preliminary matching: {preliminary_time:.2f}s")
    logging.info(f"AI analysis: {ai_time:.2f}s")
    logging.info(f"Match score: {result.match_score}%")
    
    return result
```

### Performance Benchmarks
```python
# Expected performance metrics
PERFORMANCE_BENCHMARKS = {
    'preliminary_matching': {
        'target_time': 0.1,  # 100ms
        'max_time': 0.5      # 500ms
    },
    'ai_analysis': {
        'target_time': 2.0,  # 2 seconds
        'max_time': 5.0      # 5 seconds
    },
    'total_analysis': {
        'target_time': 2.5,  # 2.5 seconds
        'max_time': 6.0      # 6 seconds
    }
}
```

## Testing

### Unit Tests
```python
import unittest
from app.services.preliminary_matcher import PreliminaryMatcher
from app.services.enhanced_qualifications_analyzer import EnhancedQualificationsAnalyzer

class TestPreliminaryMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = PreliminaryMatcher()
    
    def test_exact_match(self):
        job_description = "We need someone with Python and SQL experience"
        matches = self.matcher.find_skill_matches(job_description)
        
        self.assertGreater(matches['match_score'], 0)
        self.assertIn('Python', [match['skill'] for match in matches['exact_matches']])
        self.assertIn('SQL', [match['skill'] for match in matches['exact_matches']])
    
    def test_partial_match(self):
        job_description = "Looking for data engineering experience"
        matches = self.matcher.find_skill_matches(job_description)
        
        # Should find partial matches for data-related skills
        self.assertGreater(len(matches['partial_matches']), 0)

class TestEnhancedAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = EnhancedQualificationsAnalyzer()
    
    def test_enhanced_analysis(self):
        job_description = "Senior Data Engineer with Python, AWS, and leadership experience"
        resume_content = "Kervin Leacock - Data Analytics Professional with Python, AWS, and team leadership"
        
        result = self.analyzer.analyze_qualifications_enhanced(job_description, resume_content)
        
        self.assertIsInstance(result.match_score, float)
        self.assertGreater(result.match_score, 0)
        self.assertIsInstance(result.strong_matches, list)
        self.assertIsInstance(result.recommendations, list)
```

### Integration Tests
```python
def test_full_integration():
    """Test the complete enhanced matching system"""
    # Load test data
    job_description = read_test_job_description()
    resume_content = read_test_resume()
    
    # Test enhanced analyzer
    analyzer = EnhancedQualificationsAnalyzer()
    result = analyzer.analyze_qualifications_enhanced(job_description, resume_content)
    
    # Verify results
    assert result.match_score > 0
    assert len(result.strong_matches) > 0
    assert len(result.recommendations) > 0
    assert "PRELIMINARY MATCHING RESULTS" in result.detailed_analysis
```

## Deployment

### Production Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama
ollama serve
ollama pull llama3

# 3. Set environment variables
export PYTHONPATH=/path/to/hunter
export OLLAMA_BASE_URL=http://localhost:11434

# 4. Start application
python3 app/web.py
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

EXPOSE 51003

CMD ["python3", "app/web.py"]
```

### Health Checks
```python
@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check Ollama connection
        if not ai_analyzer.check_connection():
            return jsonify({'status': 'unhealthy', 'error': 'Ollama not connected'}), 503
        
        # Check skills database
        if not os.path.exists(SKILLS_YAML_PATH):
            return jsonify({'status': 'unhealthy', 'error': 'Skills database not found'}), 503
        
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503
```

## Maintenance

### Updating Skills Database
```python
# Add new skills to skills.yaml
def add_skill(skill_name, category, source):
    with open(SKILLS_YAML_PATH, 'r') as f:
        skills_data = yaml.safe_load(f)
    
    skills_data['skills'][skill_name] = {
        'category': category,
        'display_name': skill_name,
        'variations_found': [skill_name.lower()],
        'source': source
    }
    
    skills_data['total_skills'] = len(skills_data['skills'])
    
    with open(SKILLS_YAML_PATH, 'w') as f:
        yaml.dump(skills_data, f, default_flow_style=False, sort_keys=False)
```

### Monitoring and Logging
```python
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_matching.log'),
        logging.StreamHandler()
    ]
)

def log_analysis_result(result, job_title, company):
    """Log analysis results for monitoring"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'job_title': job_title,
        'company': company,
        'match_score': result.match_score,
        'strong_matches_count': len(result.strong_matches),
        'missing_skills_count': len(result.missing_skills),
        'recommendations_count': len(result.recommendations)
    }
    
    logging.info(f"Analysis completed: {json.dumps(log_data)}")
```

This technical reference provides comprehensive documentation for developers working with the Enhanced Matching System, including API references, data structures, configuration, error handling, testing, deployment, and maintenance procedures.
