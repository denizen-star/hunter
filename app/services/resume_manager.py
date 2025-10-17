"""Resume management service"""
from pathlib import Path
from typing import Optional, List, Dict
from app.models.resume import Resume
from app.utils.file_utils import (
    get_data_path, ensure_dir_exists, 
    load_yaml, save_yaml, read_text_file, write_text_file
)
from app.utils.simple_tech_extractor import SimpleTechExtractor


class ResumeManager:
    """Manages base and custom resumes"""
    
    def __init__(self):
        self.resumes_dir = get_data_path('resumes')
        ensure_dir_exists(self.resumes_dir)
        self.base_resume_path = self.resumes_dir / 'base_resume.md'
        self.base_resume_metadata_path = self.resumes_dir / 'base_resume.yaml'
        self.tech_yaml_path = self.resumes_dir / 'tech.yaml'
        self.tech_extractor = SimpleTechExtractor()
    
    def load_base_resume(self) -> Resume:
        """Load the base resume"""
        if not self.base_resume_path.exists():
            raise FileNotFoundError("Base resume not found. Please create one first.")
        
        content = read_text_file(self.base_resume_path)
        
        # Load metadata if exists
        metadata = {}
        if self.base_resume_metadata_path.exists():
            metadata = load_yaml(self.base_resume_metadata_path)
        
        return Resume(
            full_name=metadata.get('full_name', ''),
            email=metadata.get('email', ''),
            phone=metadata.get('phone', ''),
            linkedin=metadata.get('linkedin'),
            location=metadata.get('location'),
            content=content,
            file_path=self.base_resume_path,
            version=metadata.get('version', '1.0'),
            is_active=metadata.get('is_active', True)
        )
    
    def save_base_resume(self, resume: Resume) -> None:
        """Save the base resume and extract technologies"""
        # Save content
        write_text_file(resume.content, self.base_resume_path)
        
        # Save metadata
        metadata = {
            'full_name': resume.full_name,
            'email': resume.email,
            'phone': resume.phone,
            'linkedin': resume.linkedin,
            'location': resume.location,
            'version': resume.version,
            'is_active': resume.is_active
        }
        save_yaml(metadata, self.base_resume_metadata_path)
        
        # Extract and save technologies
        self.extract_and_save_technologies(resume.content)
    
    def create_base_resume_template(self) -> None:
        """Create a base resume template"""
        template_content = """# Your Name

## Contact Information
- Email: your.email@example.com
- Phone: +1-XXX-XXX-XXXX
- LinkedIn: linkedin.com/in/yourprofile
- Location: City, State

## Professional Summary
Brief summary of your professional background and key strengths (2-3 sentences).

## Experience

### Job Title | Company Name
*Month Year - Present*

- Accomplishment or responsibility with quantifiable results
- Another key achievement demonstrating skills and impact
- Technical skills used or leadership responsibilities

### Previous Job Title | Previous Company
*Month Year - Month Year*

- Key accomplishment showing growth and impact
- Project or initiative you led or contributed to
- Technologies, tools, or methodologies used

## Education

### Degree Name | University Name
*Year Graduated*

- Relevant coursework or honors
- GPA (if strong and recent)

## Skills

**Technical Skills:** List your technical skills, programming languages, tools, etc.

**Soft Skills:** Communication, Leadership, Problem Solving, etc.

## Certifications & Awards
- Certification Name (Year)
- Award or Recognition (Year)
"""
        
        template_metadata = {
            'full_name': 'Your Name',
            'email': 'your.email@example.com',
            'phone': '+1-XXX-XXX-XXXX',
            'linkedin': 'linkedin.com/in/yourprofile',
            'location': 'City, State',
            'version': '1.0',
            'is_active': True
        }
        
        write_text_file(template_content, self.base_resume_path)
        save_yaml(template_metadata, self.base_resume_metadata_path)
    
    def save_custom_resume(self, job_id: str, content: str, folder_path: Path) -> Path:
        """Save a custom resume for a specific job"""
        custom_resume_path = folder_path / f"custom_resume_{job_id}.md"
        write_text_file(content, custom_resume_path)
        return custom_resume_path
    
    def get_resume_for_job(self, application) -> Resume:
        """Get the resume to use for a job (custom or base)"""
        if application.custom_resume_path and application.custom_resume_path.exists():
            content = read_text_file(application.custom_resume_path)
            base_resume = self.load_base_resume()
            base_resume.content = content
            base_resume.file_path = application.custom_resume_path
            return base_resume
        else:
            return self.load_base_resume()
    
    def extract_and_save_technologies(self, resume_content: str) -> Dict[str, any]:
        """Extract technologies from resume content and save to tech.yaml"""
        # Extract technologies using the simple tech extractor
        extracted_techs = self.tech_extractor.extract_technologies(resume_content)
        
        # Create technology data structure
        tech_data = {
            'extracted_at': self._get_current_timestamp(),
            'total_technologies': len(extracted_techs),
            'technologies': {}
        }
        
        # Organize technologies by category
        for tech_name in extracted_techs:
            tech_data['technologies'][tech_name] = {
                'display_name': tech_name,
                'variations_found': [tech_name.lower()],  # Simple extractor doesn't track variations
                'category': self._get_technology_category(tech_name)
            }
        
        # Save to tech.yaml
        save_yaml(tech_data, self.tech_yaml_path)
        
        return tech_data
    
    def load_technologies(self) -> Optional[Dict[str, any]]:
        """Load technologies from tech.yaml"""
        if not self.tech_yaml_path.exists():
            return None
        
        try:
            return load_yaml(self.tech_yaml_path)
        except Exception as e:
            print(f"Warning: Could not load technologies from {self.tech_yaml_path}: {e}")
            return None
    
    def get_technology_list(self) -> List[str]:
        """Get a simple list of technology names from the cached tech.yaml"""
        tech_data = self.load_technologies()
        if not tech_data or 'technologies' not in tech_data:
            return []
        
        return list(tech_data['technologies'].keys())
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_technology_category(self, tech_name: str) -> str:
        """Get the category for a technology based on the tech matcher's categories"""
        # Programming Languages
        if tech_name in ['Python', 'Java', 'JavaScript', 'TypeScript', 'R', 'Scala', 'Go', 'Rust', 
                        'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Perl', 'Lua', 'Dart', 
                        'Elixir', 'Haskell', 'Objective-C', 'PowerShell', 'Bash', 'MATLAB', 'Julia', 'Groovy', 'PL/SQL']:
            return 'Programming Languages'
        
        # Databases
        elif tech_name in ['SQL', 'MySQL', 'PostgreSQL', 'Oracle', 'MongoDB', 'Redis', 'Cassandra', 
                          'DynamoDB', 'Aurora', 'RDS', 'DocumentDB', 'Neptune', 'Timestream', 'Redshift', 
                          'BigQuery', 'Snowflake', 'SQLite', 'DB2', 'MariaDB', 'Neo4j', 'CouchDB', 
                          'Elasticsearch', 'InfluxDB', 'Couchbase', 'HBase', 'Teradata', 'MemSQL', 
                          'SQL Server', 'ClickHouse', 'TimescaleDB', 'Sybase', 'ASE', 'ASA']:
            return 'Databases'
        
        # Cloud Platforms
        elif tech_name in ['AWS', 'Azure', 'GCP', 'IBM Cloud', 'Oracle Cloud', 'Alibaba Cloud', 
                          'DigitalOcean', 'Heroku', 'Linode', 'Vultr', 'OpenStack', 'Cloud Foundry']:
            return 'Cloud Platforms'
        
        # DevOps & Infrastructure
        elif tech_name in ['Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins', 'GitLab', 
                          'GitHub', 'Git', 'CircleCI', 'Travis', 'Chef', 'Puppet', 'Bamboo', 
                          'Azure DevOps', 'Bitbucket', 'GitHub Actions', 'GitLab CI', 'Helm', 
                          'Rancher', 'Nomad', 'Consul', 'Vault', 'Pulumi', 'CI/CD']:
            return 'DevOps & Infrastructure'
        
        # Data Engineering & Analytics
        elif tech_name in ['Databricks', 'Apache Spark', 'Hadoop', 'Apache Kafka', 'Apache Airflow', 'Prefect', 'dbt', 
                          'Talend', 'Informatica', 'Fivetran', 'Stitch', 'Segment', 'Kubeflow', 
                          'Luigi', 'Dagster', 'Apache Flink', 'Apache Beam', 'Apache NiFi', 
                          'Apache Storm', 'Apache Hive', 'Presto', 'Trino', 'Apache Drill', 
                          'Apache Pig', 'Apache Kylin', 'Great Expectations', 'Dataflow', 'Glue', 
                          'Data Factory', 'Matillion']:
            return 'Data Engineering & Analytics'
        
        # Data Architecture
        elif tech_name in ['Data Warehouse', 'Data Lake', 'Data Mesh', 'Blockchain Ledger', 'Data Marts', 'Spreadmarts']:
            return 'Data Architecture'
        
        # Business Intelligence
        elif tech_name in ['Tableau', 'Power BI', 'Qlik', 'Looker', 'Metabase', 'Sisense', 
                          'Business Objects', 'Cognos', 'Crystal Reports', 'Domo', 'Mode', 
                          'Superset', 'Redash', 'Chartio', 'Preset', 'Google Data Studio', 
                          'MicroStrategy', 'ThoughtSpot', 'Alteryx', 'Spotfire', 'Pentaho', 'Yellowfin']:
            return 'Business Intelligence'
        
        # Monitoring & Observability
        elif tech_name in ['Grafana', 'DataDog', 'Datatrace', 'New Relic', 'Kibana', 'Splunk', 
                          'Prometheus', 'ELK Stack', 'Logstash', 'Sentry', 'AppDynamics', 
                          'Dynatrace', 'Sumo Logic', 'CloudWatch', 'Azure Monitor', 'Stackdriver']:
            return 'Monitoring & Observability'
        
        # Web Frameworks
        elif tech_name in ['React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Express', 
                          'Next.js', 'Nuxt.js', 'Svelte', 'Gatsby', 'Ember', 'Backbone', 
                          'ASP.NET', 'Rails', 'Laravel', 'Phoenix', 'Koa', 'Fastify', 'NestJS', 
                          'FastAPI', 'Gin', 'Echo', 'Fiber']:
            return 'Web Frameworks'
        
        # Machine Learning & AI
        elif tech_name in ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Keras', 'MLflow', 
                          'Hugging Face', 'LangChain', 'OpenAI', 'Anthropic', 'LLM', 'XGBoost', 
                          'LightGBM', 'CatBoost', 'SageMaker', 'Vertex AI', 'Azure ML', 'H2O', 
                          'RAPIDS', 'Optuna', 'Weights & Biases', 'Comet ML', 'Ray', 'Dask', 'MXNet', 'Caffe', 
                          'ONNX', 'TensorRT']:
            return 'Machine Learning & AI'
        
        # Data Sources & Integration
        elif tech_name in ['Salesforce', 'Segment', 'Pendo', 'Tatari', 'Braze', 'Quicken', 'ERPs', 'NetSuite', 'Zapier', 'SAP']:
            return 'Data Sources & Integration'
        
        # Data Modeling & Design
        elif tech_name in ['ERwin', 'LucidArt']:
            return 'Data Modeling & Design'
        
        # Other Tools
        elif tech_name in ['Excel', 'MS Access', 'Jupyter', 'Pandas', 'NumPy', 'Google Sheets', 'Airtable', 
                          'DVC', 'MLOps', 'DataOps', 'Cursor AI', 'PowerPoint', 'Word', 'Outlook']:
            return 'Other Tools'
        
        else:
            return 'Other'

