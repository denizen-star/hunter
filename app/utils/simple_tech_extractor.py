"""Simplified technology extraction and comparison system"""

import re
from typing import Dict, List, Set, Tuple


class SimpleTechExtractor:
    """Simple, clean technology extraction and comparison"""
    
    # Comprehensive but clean technology list
    TECHNOLOGIES = {
        # Cloud Platforms
        'AWS': ['aws', 'amazon web services', 'amazon aws'],
        'Azure': ['azure', 'microsoft azure'],
        'GCP': ['gcp', 'google cloud', 'google cloud platform'],
        'Amazon Kinesis': ['amazon kinesis', 'kinesis'],
        'AWS Lake Formation': ['aws lake formation', 'lake formation'],
        'Microsoft Purview': ['microsoft purview', 'purview'],
        
        # Data Engineering
        'Apache Kafka': ['apache kafka', 'kafka'],
        'Apache Flink': ['apache flink', 'flink'],
        'Apache Spark': ['apache spark', 'spark'],
        'Apache Hudi': ['apache hudi', 'hudi'],
        'Apache Iceberg': ['apache iceberg', 'iceberg'],
        'Apache NiFi': ['apache nifi', 'nifi'],
        'Apache Airflow': ['apache airflow', 'airflow'],
        'dbt': ['dbt', 'data build tool'],
        'Fivetran': ['fivetran'],
        'Databricks': ['databricks'],
        'Talend': ['talend'],
        'Kubeflow': ['kubeflow'],
        'Informatica': ['informatica'],
        
        # Query Engines & Databases
        'Presto': ['presto', 'prestodb'],
        'Trino': ['trino'],
        'StarRocks': ['starrocks', 'star rocks'],
        'BigQuery': ['bigquery', 'big query', 'google bigquery'],
        'Snowflake': ['snowflake'],
        'Redshift': ['redshift', 'aws redshift'],
        'PostgreSQL': ['postgresql', 'postgres'],
        'MySQL': ['mysql'],
        'Oracle': ['oracle', 'oracle database'],
        'MongoDB': ['mongodb', 'mongo'],
        'Redis': ['redis'],
        'Cassandra': ['cassandra'],
        'DynamoDB': ['dynamodb', 'dynamo db'],
        'Aurora': ['aurora', 'aws aurora', 'amazon aurora'],
        'RDS': ['rds', 'aws rds', 'amazon rds'],
        'DocumentDB': ['documentdb', 'aws documentdb', 'amazon documentdb'],
        'Neptune': ['neptune', 'aws neptune', 'amazon neptune'],
        'Timestream': ['timestream', 'aws timestream', 'amazon timestream'],
        'DB2': ['db2', 'ibm db2'],
        'Sybase': ['sybase'],
        'ASE': ['ase', 'adaptive server enterprise', 'sybase ase', 'sybase adaptive server enterprise'],
        'ASA': ['asa', 'adaptive server anywhere', 'sybase asa', 'sybase adaptive server anywhere'],
        'Elasticsearch': ['elasticsearch', 'elastic search'],
        
        # BI Tools
        'Tableau': ['tableau'],
        'Power BI': ['power bi', 'powerbi'],
        'Looker': ['looker'],
        'Qlik': ['qlik', 'qlikview', 'qlik sense'],
        'Metabase': ['metabase'],
        'Superset': ['superset', 'apache superset'],
        'Business Objects': ['business objects', 'sap business objects'],
        'Crystal Reports': ['crystal reports'],
        'Cognos': ['cognos', 'ibm cognos'],
        'Sisense': ['sisense'],
        
        # Programming Languages
        'Python': ['python', 'py'],
        'Java': ['java'],
        'SQL': ['sql', 'structured query language'],
        'PL/SQL': ['pl/sql', 'plsql', 'pl sql'],
        'JavaScript': ['javascript', 'js', 'node.js', 'nodejs'],
        'TypeScript': ['typescript', 'ts'],
        'Go': ['golang', r'\bgo\b'],
        'Rust': ['rust'],
        'C++': ['c++', 'cpp', 'c plus plus'],
        'C#': ['c#', 'csharp', 'c sharp'],
        
        # DevOps & Infrastructure
        'Kubernetes': ['kubernetes', 'k8s'],
        'Docker': ['docker'],
        'Terraform': ['terraform'],
        'CloudFormation': ['cloudformation', 'cloud formation'],
        'Jenkins': ['jenkins'],
        'Git': ['git', 'version control'],
        'GitHub': ['github', 'git hub'],
        'GitLab': ['gitlab', 'git lab'],
        'CI/CD': ['ci/cd', 'continuous integration', 'continuous delivery'],
        
        # Monitoring & Observability
        'Grafana': ['grafana'],
        'Prometheus': ['prometheus'],
        'DataDog': ['datadog', 'data dog'],
        'Datatrace': ['datatrace'],
        'New Relic': ['new relic', 'newrelic'],
        'Splunk': ['splunk'],
        'ELK Stack': ['elk', 'elk stack', 'elasticsearch logstash kibana'],
        
        # Machine Learning & AI
        'TensorFlow': ['tensorflow', 'tensor flow'],
        'PyTorch': ['pytorch', 'py torch'],
        'Scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
        'MLflow': ['mlflow'],
        'SageMaker': ['sagemaker', 'aws sagemaker'],
        'Vertex AI': ['vertex ai', 'vertex', 'google vertex'],
        'Azure ML': ['azure ml', 'azure machine learning'],
        
        # Web Frameworks
        'React': ['react', 'reactjs', 'react.js'],
        'Angular': ['angular', 'angularjs'],
        'Vue': ['vue', 'vuejs', 'vue.js'],
        'Django': ['django'],
        'Flask': ['flask'],
        'Spring': ['spring', 'spring boot', 'spring framework'],
        'Express': ['express', 'expressjs', 'express.js'],
        'FastAPI': ['fastapi', 'fast api'],
        
        # Data Architecture
        'Data Warehouse': ['data warehouse', 'datawarehouse'],
        'Data Lake': ['data lake', 'datalake'],
        'Data Mesh': ['data mesh', 'datamesh'],
        'Blockchain Ledger': ['blockchain ledger', 'blockchain'],
        'Data Marts': ['data marts', 'datamarts'],
        'Spreadmarts': ['spreadmarts'],
        
        # Data Sources & Integration
        'Salesforce': ['salesforce', 'sales force'],
        'Segment': ['segment'],
        'Pendo': ['pendo'],
        'Tatari': ['tatari'],
        'Braze': ['braze'],
        'Quicken': ['quicken'],
        'ERPs': ['erp', 'erps', 'enterprise resource planning'],
        'NetSuite': ['netsuite'],
        'Zapier': ['zapier'],
        'SAP': ['sap'],
        
        # Data Modeling & Design
        'ERwin': ['erwin'],
        'LucidArt': ['lucidart', 'lucid art'],
        
        # Other Tools
        'Jupyter': ['jupyter', 'jupyter notebook', 'jupyterlab'],
        'Pandas': ['pandas'],
        'NumPy': ['numpy'],
        'Excel': ['excel', 'microsoft excel', 'ms excel'],
        'MS Access': ['ms access', 'microsoft access', 'access'],
        'PowerPoint': ['powerpoint', 'power point', 'microsoft powerpoint'],
        'Word': ['word', 'microsoft word', 'ms word'],
        'Outlook': ['outlook', 'microsoft outlook'],
        'Cursor AI': ['cursor ai', 'cursor'],
    }
    
    def __init__(self):
        """Initialize the simple tech extractor"""
        pass
    
    def extract_technologies(self, text: str) -> List[str]:
        """
        Extract technologies from text using simple string matching.
        
        Returns:
            List of technology names found in the text
        """
        text_lower = text.lower()
        found_technologies = []
        
        for tech_name, variations in self.TECHNOLOGIES.items():
            for variation in variations:
                # Check if variation is a regex pattern
                if variation.startswith(r'\b'):
                    if re.search(variation, text_lower, re.IGNORECASE):
                        found_technologies.append(tech_name)
                        break
                else:
                    # Simple substring search
                    if variation in text_lower:
                        found_technologies.append(tech_name)
                        break
        
        return sorted(list(set(found_technologies)))  # Remove duplicates and sort
    
    def compare_technologies(self, job_description: str, resume: str) -> Dict[str, any]:
        """
        Compare technologies between job description and resume.
        
        Returns:
            Simple comparison dictionary
        """
        job_techs = set(self.extract_technologies(job_description))
        resume_techs = set(self.extract_technologies(resume))
        
        matched = job_techs & resume_techs
        missing = job_techs - resume_techs
        additional = resume_techs - job_techs
        
        # Calculate simple score
        total_required = len(job_techs)
        match_count = len(matched)
        score = int((match_count / total_required * 100)) if total_required > 0 else 0
        
        return {
            'job_technologies': sorted(list(job_techs)),
            'resume_technologies': sorted(list(resume_techs)),
            'matched': sorted(list(matched)),
            'missing': sorted(list(missing)),
            'additional': sorted(list(additional)),
            'total_required': total_required,
            'match_count': match_count,
            'missing_count': len(missing),
            'score': score
        }
    
    def format_simple_comparison(self, comparison: Dict[str, any]) -> str:
        """
        Format a simple, clean comparison report.
        
        Returns:
            Clean markdown formatted comparison
        """
        lines = []
        
        # Summary
        lines.append("## Technology Comparison")
        lines.append("")
        lines.append(f"**Match Score: {comparison['score']}%**")
        lines.append(f"**Technologies Required: {comparison['total_required']}**")
        lines.append(f"**Technologies Matched: {comparison['match_count']}**")
        lines.append(f"**Technologies Missing: {comparison['missing_count']}**")
        lines.append("")
        
        # Matched Technologies
        if comparison['matched']:
            lines.append("### ✅ Matched Technologies")
            for tech in comparison['matched']:
                lines.append(f"- {tech}")
            lines.append("")
        
        # Missing Technologies
        if comparison['missing']:
            lines.append("### ❌ Missing Technologies")
            for tech in comparison['missing']:
                lines.append(f"- {tech}")
            lines.append("")
        
        # Additional Technologies (bonus points)
        if comparison['additional']:
            lines.append("### ➕ Additional Technologies (Bonus)")
            for tech in comparison['additional']:
                lines.append(f"- {tech}")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_technology_list_from_job(self, job_description: str) -> str:
        """
        Get a clean list of technologies from job description.
        
        Returns:
            Formatted technology list
        """
        technologies = self.extract_technologies(job_description)
        
        if not technologies:
            return "No specific technologies identified in job description."
        
        # Group by category for better organization
        categories = {
            'Cloud Platforms': [],
            'Data Engineering': [],
            'Databases & Query Engines': [],
            'BI Tools': [],
            'Programming Languages': [],
            'DevOps & Infrastructure': [],
            'Other': []
        }
        
        # Categorize technologies
        for tech in technologies:
            tech_lower = tech.lower()
            if any(keyword in tech_lower for keyword in ['aws', 'azure', 'gcp', 'kinesis', 'purview']):
                categories['Cloud Platforms'].append(tech)
            elif any(keyword in tech_lower for keyword in ['apache', 'kafka', 'spark', 'flink', 'hudi', 'iceberg', 'airflow', 'dbt', 'databricks']):
                categories['Data Engineering'].append(tech)
            elif any(keyword in tech_lower for keyword in ['presto', 'trino', 'bigquery', 'snowflake', 'redshift', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'starrocks']):
                categories['Databases & Query Engines'].append(tech)
            elif any(keyword in tech_lower for keyword in ['tableau', 'power bi', 'looker', 'qlik', 'metabase', 'superset']):
                categories['BI Tools'].append(tech)
            elif any(keyword in tech_lower for keyword in ['python', 'java', 'sql', 'javascript', 'typescript', 'r', 'go', 'rust', 'c++', 'c#']):
                categories['Programming Languages'].append(tech)
            elif any(keyword in tech_lower for keyword in ['kubernetes', 'docker', 'terraform', 'jenkins', 'git', 'ci/cd', 'cloudformation']):
                categories['DevOps & Infrastructure'].append(tech)
            else:
                categories['Other'].append(tech)
        
        # Format output
        lines = []
        lines.append("## Technologies Found in Job Description")
        lines.append("")
        
        for category, techs in categories.items():
            if techs:
                lines.append(f"**{category}:**")
                for tech in sorted(techs):
                    lines.append(f"- {tech}")
                lines.append("")
        
        return "\n".join(lines)


def extract_technologies_simple(text: str) -> List[str]:
    """
    Simple convenience function to extract technologies from text.
    
    Returns:
        List of technology names found
    """
    extractor = SimpleTechExtractor()
    return extractor.extract_technologies(text)


def compare_technologies_simple(job_description: str, resume: str) -> Dict[str, any]:
    """
    Simple convenience function to compare technologies.
    
    Returns:
        Comparison dictionary
    """
    extractor = SimpleTechExtractor()
    return extractor.compare_technologies(job_description, resume)
