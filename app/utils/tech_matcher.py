"""Technology matching utility - uses string matching instead of AI to avoid hallucination"""
import re
from typing import Dict, List, Set, Tuple
from difflib import SequenceMatcher


class TechnologyMatcher:
    """Matches technologies between job descriptions and resumes using direct string comparison"""
    
    # Comprehensive technology dictionary with variations
    TECHNOLOGIES = {
        # Programming Languages
        'python': ['python', 'py'],
        'java': ['java'],
        'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'node js'],
        'typescript': ['typescript', 'ts'],
        'r': [r'\br\b', r'\br programming\b'],  # regex pattern to avoid matching "r" in words
        'scala': ['scala'],
        'go': ['golang', r'\bgo\b'],
        'rust': ['rust'],
        'c++': ['c++', 'cpp', 'c plus plus'],
        'c#': ['c#', 'csharp', 'c sharp'],
        'php': ['php'],
        'ruby': ['ruby'],
        'swift': ['swift'],
        'kotlin': ['kotlin'],
        'perl': ['perl'],
        'lua': ['lua'],
        'dart': ['dart', 'flutter'],
        'elixir': ['elixir'],
        'haskell': ['haskell'],
        'objective-c': ['objective-c', 'objective c', 'objc'],
        'powershell': ['powershell', 'pwsh'],
        'bash': ['bash', 'shell', 'shell script', 'sh'],
        'matlab': ['matlab'],
        'julia': ['julia'],
        'groovy': ['groovy'],
        
        # Databases
        'sql': ['sql', 'structured query language'],
        'mysql': ['mysql'],
        'postgresql': ['postgresql', 'postgres'],
        'oracle': ['oracle', 'oracle database'],
        'mongodb': ['mongodb', 'mongo'],
        'redis': ['redis'],
        'cassandra': ['cassandra'],
        'dynamodb': ['dynamodb', 'dynamo db'],
        'redshift': ['redshift', 'aws redshift', 'amazon redshift'],
        'bigquery': ['bigquery', 'big query', 'google bigquery'],
        'snowflake': ['snowflake'],
        'sqlite': ['sqlite'],
        'db2': ['db2', 'ibm db2'],
        'mariadb': ['mariadb'],
        'neo4j': ['neo4j'],
        'couchdb': ['couchdb', 'couch db'],
        'elasticsearch': ['elasticsearch', 'elastic search'],
        'influxdb': ['influxdb', 'influx db'],
        'couchbase': ['couchbase'],
        'hbase': ['hbase', 'apache hbase'],
        'teradata': ['teradata'],
        'memsql': ['memsql', 'singlestore'],
        'sql server': ['sql server', 'microsoft sql server', 'mssql', 'ms sql'],
        'clickhouse': ['clickhouse'],
        'timescaledb': ['timescaledb', 'timescale'],
        
        # Cloud Platforms
        'aws': ['aws', 'amazon web services'],
        'azure': ['azure', 'microsoft azure'],
        'gcp': ['gcp', 'google cloud', 'google cloud platform'],
        'ibm cloud': ['ibm cloud'],
        'oracle cloud': ['oracle cloud'],
        'alibaba cloud': ['alibaba cloud', 'aliyun'],
        'digitalocean': ['digitalocean', 'digital ocean'],
        'heroku': ['heroku'],
        'linode': ['linode'],
        'vultr': ['vultr'],
        'openstack': ['openstack'],
        'cloud foundry': ['cloud foundry', 'cloudfoundry'],
        
        # DevOps & Infrastructure
        'docker': ['docker'],
        'kubernetes': ['kubernetes', 'k8s'],
        'terraform': ['terraform'],
        'ansible': ['ansible'],
        'jenkins': ['jenkins'],
        'gitlab': ['gitlab', 'git lab'],
        'github': ['github', 'git hub'],
        'git': ['git', 'version control'],
        'circleci': ['circleci', 'circle ci'],
        'travis': ['travis', 'travis ci'],
        'chef': ['chef'],
        'puppet': ['puppet'],
        'bamboo': ['bamboo', 'atlassian bamboo'],
        'azure devops': ['azure devops', 'azure pipelines'],
        'bitbucket': ['bitbucket'],
        'github actions': ['github actions'],
        'gitlab ci': ['gitlab ci', 'gitlab ci/cd'],
        'helm': ['helm'],
        'rancher': ['rancher'],
        'nomad': ['nomad', 'hashicorp nomad'],
        'consul': ['consul', 'hashicorp consul'],
        'vault': ['vault', 'hashicorp vault'],
        'pulumi': ['pulumi'],
        
        # Data Engineering & Analytics
        'databricks': ['databricks'],
        'spark': ['spark', 'apache spark', 'pyspark'],
        'hadoop': ['hadoop', 'hdfs', 'hadoop distributed file system'],
        'kafka': ['kafka', 'apache kafka'],
        'airflow': ['airflow', 'apache airflow'],
        'prefect': ['prefect'],
        'dbt': ['dbt', 'data build tool'],
        'talend': ['talend'],
        'informatica': ['informatica'],
        'fivetran': ['fivetran'],
        'stitch': ['stitch'],
        'segment': ['segment'],
        'kubeflow': ['kubeflow'],
        'luigi': ['luigi'],
        'dagster': ['dagster'],
        'apache flink': ['flink', 'apache flink'],
        'apache beam': ['beam', 'apache beam'],
        'apache nifi': ['nifi', 'apache nifi'],
        'apache storm': ['storm', 'apache storm'],
        'apache hive': ['hive', 'apache hive'],
        'presto': ['presto', 'prestodb'],
        'trino': ['trino', 'trino db'],
        'apache drill': ['drill', 'apache drill'],
        'apache pig': ['pig', 'apache pig'],
        'apache kylin': ['kylin', 'apache kylin'],
        'great expectations': ['great expectations'],
        'dataflow': ['dataflow', 'google dataflow'],
        'glue': ['glue', 'aws glue'],
        'data factory': ['data factory', 'azure data factory'],
        'matillion': ['matillion'],
        
        # BI Tools
        'tableau': ['tableau'],
        'power bi': ['power bi', 'powerbi'],
        'qlik': ['qlik', 'qlikview', 'qlik sense'],
        'looker': ['looker'],
        'metabase': ['metabase'],
        'sisense': ['sisense'],
        'business objects': ['business objects', 'sap business objects'],
        'cognos': ['cognos', 'ibm cognos'],
        'crystal reports': ['crystal reports'],
        'domo': ['domo'],
        'mode': ['mode', 'mode analytics'],
        'superset': ['superset', 'apache superset'],
        'redash': ['redash'],
        'chartio': ['chartio'],
        'preset': ['preset'],
        'google data studio': ['google data studio', 'data studio', 'looker studio'],
        'microstrategy': ['microstrategy'],
        'thoughtspot': ['thoughtspot'],
        'alteryx': ['alteryx'],
        'spotfire': ['spotfire', 'tibco spotfire'],
        'pentaho': ['pentaho'],
        'yellowfin': ['yellowfin'],
        
        # Monitoring & Observability
        'grafana': ['grafana'],
        'datadog': ['datadog', 'data dog'],
        'new relic': ['new relic', 'newrelic'],
        'kibana': ['kibana'],
        'splunk': ['splunk'],
        'datatrace': ['datatrace'],
        'prometheus': ['prometheus'],
        'elk stack': ['elk', 'elk stack', 'elasticsearch logstash kibana'],
        'logstash': ['logstash'],
        'sentry': ['sentry'],
        'appdynamics': ['appdynamics'],
        'dynatrace': ['dynatrace'],
        'sumologic': ['sumologic', 'sumo logic'],
        'cloudwatch': ['cloudwatch', 'aws cloudwatch'],
        'azure monitor': ['azure monitor'],
        'stackdriver': ['stackdriver', 'google cloud operations'],
        
        # Web Frameworks
        'react': ['react', 'reactjs', 'react.js'],
        'angular': ['angular', 'angularjs'],
        'vue': ['vue', 'vuejs', 'vue.js'],
        'django': ['django'],
        'flask': ['flask'],
        'spring': ['spring', 'spring boot', 'spring framework'],
        'express': ['express', 'expressjs', 'express.js'],
        'next.js': ['next.js', 'nextjs', 'next js'],
        'nuxt.js': ['nuxt.js', 'nuxtjs', 'nuxt js'],
        'svelte': ['svelte', 'sveltejs'],
        'gatsby': ['gatsby', 'gatsbyjs'],
        'ember': ['ember', 'ember.js', 'emberjs'],
        'backbone': ['backbone', 'backbone.js', 'backbonejs'],
        'asp.net': ['asp.net', 'aspnet', 'asp net'],
        'rails': ['rails', 'ruby on rails'],
        'laravel': ['laravel'],
        'phoenix': ['phoenix', 'phoenix framework'],
        'koa': ['koa', 'koa.js', 'koajs'],
        'fastify': ['fastify'],
        'nestjs': ['nestjs', 'nest.js', 'nest js'],
        'fastapi': ['fastapi', 'fast api'],
        'gin': ['gin', 'gin framework'],
        'echo': ['echo', 'echo framework'],
        'fiber': ['fiber', 'fiber framework'],
        
        # Project Management & Collaboration
        'jira': ['jira', 'atlassian jira'],
        'confluence': ['confluence', 'atlassian confluence'],
        'slack': ['slack'],
        'teams': ['microsoft teams', 'ms teams'],
        'asana': ['asana'],
        'monday': ['monday', 'monday.com'],
        'trello': ['trello'],
        'notion': ['notion'],
        'clickup': ['clickup'],
        'basecamp': ['basecamp'],
        'airtable': ['airtable'],
        
        # CRM & Marketing
        'salesforce': ['salesforce', 'sales force'],
        'hubspot': ['hubspot'],
        'marketo': ['marketo'],
        'pendo': ['pendo'],
        'braze': ['braze'],
        
        # ERP & Business Systems
        'sap': ['sap'],
        'netsuite': ['netsuite'],
        'erp': ['erp', 'enterprise resource planning'],
        'quicken': ['quicken'],
        'zapier': ['zapier'],
        
        # Machine Learning & AI
        'tensorflow': ['tensorflow', 'tensor flow'],
        'pytorch': ['pytorch', 'py torch'],
        'scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
        'keras': ['keras'],
        'mlflow': ['mlflow'],
        'hugging face': ['hugging face', 'huggingface', 'transformers'],
        'langchain': ['langchain', 'lang chain'],
        'openai': ['openai', 'open ai', 'gpt'],
        'anthropic': ['anthropic', 'claude'],
        'llm': ['llm', 'large language model', 'llms'],
        'xgboost': ['xgboost'],
        'lightgbm': ['lightgbm', 'light gbm'],
        'catboost': ['catboost'],
        'sagemaker': ['sagemaker', 'aws sagemaker'],
        'vertex ai': ['vertex ai', 'vertex', 'google vertex'],
        'azure ml': ['azure ml', 'azure machine learning'],
        'h2o': ['h2o', 'h2o.ai'],
        'rapids': ['rapids', 'nvidia rapids'],
        'optuna': ['optuna'],
        'wandb': ['wandb', 'weights and biases'],
        'comet': ['comet', 'comet ml'],
        'ray': ['ray', 'ray.io'],
        'dask': ['dask'],
        'mxnet': ['mxnet', 'apache mxnet'],
        'caffe': ['caffe', 'caffe2'],
        'onnx': ['onnx'],
        'tensorrt': ['tensorrt', 'tensor rt'],
        
        # Testing Frameworks
        'jest': ['jest'],
        'mocha': ['mocha'],
        'pytest': ['pytest', 'py.test'],
        'junit': ['junit'],
        'testng': ['testng'],
        'selenium': ['selenium'],
        'cypress': ['cypress'],
        'playwright': ['playwright'],
        'puppeteer': ['puppeteer'],
        'jasmine': ['jasmine'],
        'karma': ['karma'],
        'cucumber': ['cucumber', 'gherkin'],
        'rspec': ['rspec'],
        'postman': ['postman'],
        'newman': ['newman'],
        
        # Package Managers
        'npm': ['npm'],
        'yarn': ['yarn'],
        'pnpm': ['pnpm'],
        'pip': ['pip'],
        'conda': ['conda', 'anaconda', 'miniconda'],
        'poetry': ['poetry'],
        'pipenv': ['pipenv'],
        'maven': ['maven', 'apache maven'],
        'gradle': ['gradle'],
        'composer': ['composer'],
        'bundler': ['bundler'],
        'cargo': ['cargo'],
        'go modules': ['go modules', 'go mod'],
        'nuget': ['nuget'],
        
        # IDEs & Editors
        'vscode': ['vscode', 'vs code', 'visual studio code'],
        'intellij': ['intellij', 'intellij idea'],
        'pycharm': ['pycharm'],
        'eclipse': ['eclipse'],
        'rstudio': ['rstudio', 'r studio'],
        'sublime': ['sublime', 'sublime text'],
        'atom': ['atom'],
        'vim': ['vim', 'vi'],
        'emacs': ['emacs'],
        'netbeans': ['netbeans'],
        'webstorm': ['webstorm'],
        'android studio': ['android studio'],
        'xcode': ['xcode'],
        'visual studio': ['visual studio'],
        
        # API & Integration Tools
        'rest': ['rest', 'rest api', 'restful'],
        'graphql': ['graphql', 'graph ql'],
        'grpc': ['grpc', 'g rpc'],
        'soap': ['soap', 'soap api'],
        'postman': ['postman'],
        'insomnia': ['insomnia'],
        'swagger': ['swagger', 'openapi'],
        'apigee': ['apigee'],
        'kong': ['kong', 'kong gateway'],
        'mulesoft': ['mulesoft'],
        
        # Data Visualization Libraries
        'd3.js': ['d3.js', 'd3', 'data driven documents'],
        'plotly': ['plotly'],
        'matplotlib': ['matplotlib'],
        'seaborn': ['seaborn'],
        'ggplot2': ['ggplot2', 'ggplot'],
        'bokeh': ['bokeh'],
        'altair': ['altair'],
        'chart.js': ['chart.js', 'chartjs'],
        'highcharts': ['highcharts'],
        'recharts': ['recharts'],
        'victory': ['victory', 'victory charts'],
        'vega': ['vega', 'vega-lite'],
        
        # Other Tools
        'excel': ['excel', 'microsoft excel', 'ms excel'],
        'jupyter': ['jupyter', 'jupyter notebook', 'jupyterlab'],
        'pandas': ['pandas'],
        'numpy': ['numpy'],
        'google sheets': ['google sheets'],
        'airtable': ['airtable'],
        'dvc': ['dvc', 'data version control'],
        'mlops': ['mlops', 'ml ops'],
        'dataops': ['dataops', 'data ops'],
    }
    
    def __init__(self):
        """Initialize the technology matcher"""
        self.fuzzy_threshold = 0.85  # Threshold for fuzzy string matching
    
    def extract_technologies(self, text: str) -> Dict[str, List[str]]:
        """
        Extract technologies from text using string matching.
        
        Returns:
            Dict with technology names as keys and list of matched variations as values
        """
        text_lower = text.lower()
        found_technologies = {}
        
        for tech_name, variations in self.TECHNOLOGIES.items():
            matches = []
            for variation in variations:
                # Check if variation is a regex pattern
                if variation.startswith(r'\b'):
                    if re.search(variation, text_lower, re.IGNORECASE):
                        matches.append(variation)
                else:
                    # Simple substring search
                    if variation in text_lower:
                        matches.append(variation)
            
            if matches:
                found_technologies[tech_name] = matches
        
        return found_technologies
    
    def compare_technologies(self, job_description: str, resume: str) -> Dict[str, any]:
        """
        Compare technologies between job description and resume.
        
        Returns:
            Dict with matched, missing, and additional technologies
        """
        job_techs = self.extract_technologies(job_description)
        resume_techs = self.extract_technologies(resume)
        
        job_tech_names = set(job_techs.keys())
        resume_tech_names = set(resume_techs.keys())
        
        matched = job_tech_names & resume_tech_names
        missing = job_tech_names - resume_tech_names
        additional = resume_tech_names - job_tech_names
        
        return {
            'matched': sorted(list(matched)),
            'missing': sorted(list(missing)),
            'additional': sorted(list(additional)),
            'job_technologies': job_techs,
            'resume_technologies': resume_techs,
            'match_count': len(matched),
            'missing_count': len(missing),
            'total_required': len(job_tech_names)
        }
    
    def get_technology_display_name(self, tech_key: str) -> str:
        """Get a human-readable display name for a technology"""
        # Capitalize properly
        display_names = {
            # Programming Languages
            'sql': 'SQL',
            'nosql': 'NoSQL',
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'c++': 'C++',
            'c#': 'C#',
            'php': 'PHP',
            'objective-c': 'Objective-C',
            'powershell': 'PowerShell',
            'bash': 'Bash',
            'matlab': 'MATLAB',
            
            # Databases
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'dynamodb': 'DynamoDB',
            'bigquery': 'BigQuery',
            'sqlite': 'SQLite',
            'db2': 'DB2',
            'mariadb': 'MariaDB',
            'neo4j': 'Neo4j',
            'couchdb': 'CouchDB',
            'elasticsearch': 'Elasticsearch',
            'influxdb': 'InfluxDB',
            'hbase': 'HBase',
            'memsql': 'MemSQL',
            'sql server': 'SQL Server',
            'clickhouse': 'ClickHouse',
            'timescaledb': 'TimescaleDB',
            
            # Cloud
            'aws': 'AWS',
            'gcp': 'GCP',
            'azure': 'Azure',
            'ibm cloud': 'IBM Cloud',
            'digitalocean': 'DigitalOcean',
            'openstack': 'OpenStack',
            
            # DevOps
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'circleci': 'CircleCI',
            'azure devops': 'Azure DevOps',
            'github actions': 'GitHub Actions',
            'gitlab ci': 'GitLab CI',
            
            # Data Engineering
            'apache flink': 'Apache Flink',
            'apache beam': 'Apache Beam',
            'apache nifi': 'Apache NiFi',
            'apache storm': 'Apache Storm',
            'apache hive': 'Apache Hive',
            'apache drill': 'Apache Drill',
            'apache pig': 'Apache Pig',
            'apache kylin': 'Apache Kylin',
            'dbt': 'dbt',
            'fivetran': 'Fivetran',
            'dataflow': 'Dataflow',
            'glue': 'AWS Glue',
            'data factory': 'Azure Data Factory',
            
            # BI Tools
            'power bi': 'Power BI',
            'qlik': 'Qlik',
            'metabase': 'Metabase',
            'sisense': 'Sisense',
            'business objects': 'Business Objects',
            'cognos': 'Cognos',
            'crystal reports': 'Crystal Reports',
            'google data studio': 'Google Data Studio',
            'microstrategy': 'MicroStrategy',
            'thoughtspot': 'ThoughtSpot',
            'spotfire': 'Spotfire',
            
            # Monitoring
            'datadog': 'DataDog',
            'new relic': 'New Relic',
            'elk stack': 'ELK Stack',
            'appdynamics': 'AppDynamics',
            'sumologic': 'Sumo Logic',
            'cloudwatch': 'CloudWatch',
            'azure monitor': 'Azure Monitor',
            
            # Web Frameworks
            'next.js': 'Next.js',
            'nuxt.js': 'Nuxt.js',
            'gatsby': 'Gatsby',
            'asp.net': 'ASP.NET',
            'fastapi': 'FastAPI',
            'nestjs': 'NestJS',
            
            # ML/AI
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'scikit-learn': 'Scikit-learn',
            'mlflow': 'MLflow',
            'hugging face': 'Hugging Face',
            'langchain': 'LangChain',
            'openai': 'OpenAI',
            'llm': 'LLM',
            'xgboost': 'XGBoost',
            'lightgbm': 'LightGBM',
            'catboost': 'CatBoost',
            'sagemaker': 'SageMaker',
            'vertex ai': 'Vertex AI',
            'azure ml': 'Azure ML',
            'h2o': 'H2O.ai',
            'rapids': 'RAPIDS',
            'wandb': 'Weights & Biases',
            'comet': 'Comet ML',
            'mxnet': 'MXNet',
            'onnx': 'ONNX',
            'tensorrt': 'TensorRT',
            
            # Testing
            'pytest': 'pytest',
            'junit': 'JUnit',
            'testng': 'TestNG',
            
            # Package Managers
            'npm': 'npm',
            'pnpm': 'pnpm',
            'pip': 'pip',
            'pipenv': 'pipenv',
            'nuget': 'NuGet',
            
            # IDEs
            'vscode': 'VS Code',
            'intellij': 'IntelliJ IDEA',
            'pycharm': 'PyCharm',
            'rstudio': 'RStudio',
            'webstorm': 'WebStorm',
            'android studio': 'Android Studio',
            'xcode': 'Xcode',
            
            # API Tools
            'rest': 'REST',
            'graphql': 'GraphQL',
            'grpc': 'gRPC',
            'soap': 'SOAP',
            'openapi': 'OpenAPI',
            
            # Viz Libraries
            'd3.js': 'D3.js',
            'matplotlib': 'Matplotlib',
            'ggplot2': 'ggplot2',
            'chart.js': 'Chart.js',
            
            # Other
            'jupyter': 'Jupyter',
            'pandas': 'pandas',
            'numpy': 'NumPy',
            'dvc': 'DVC',
            'mlops': 'MLOps',
            'dataops': 'DataOps',
        }
        
        return display_names.get(tech_key, tech_key.title())
    
    def format_technology_table(self, comparison: Dict[str, any]) -> str:
        """
        Format the technology comparison as a markdown table.
        
        Returns:
            Markdown formatted table string
        """
        lines = []
        lines.append("| Technology | Job Description | Resume Evidence | Match Level |")
        lines.append("| --- | --- | --- | --- |")
        
        # Add matched technologies
        for tech in comparison['matched']:
            display_name = self.get_technology_display_name(tech)
            lines.append(f"| {display_name} | Required | ✓ MATCHED | Strong Match |")
        
        # Add missing technologies
        for tech in comparison['missing']:
            display_name = self.get_technology_display_name(tech)
            lines.append(f"| {display_name} | Required | ✗ NOT FOUND | Missing |")
        
        return "\n".join(lines)
    
    def get_summary_statistics(self, comparison: Dict[str, any]) -> str:
        """
        Get summary statistics about technology matching.
        
        Returns:
            Formatted summary string
        """
        total = comparison['total_required']
        matched = comparison['match_count']
        missing = comparison['missing_count']
        
        if total == 0:
            match_percentage = 0
        else:
            match_percentage = int((matched / total) * 100)
        
        return f"""**Technologies Compared:** {total}
**Technologies Matched:** {matched} ({match_percentage}%)
**Technologies Missing:** {missing}"""


def extract_technologies_from_text(text: str) -> List[str]:
    """
    Convenience function to extract technologies from text.
    
    Returns:
        List of technology names found
    """
    matcher = TechnologyMatcher()
    techs = matcher.extract_technologies(text)
    return sorted(list(techs.keys()))


def compare_job_and_resume_technologies(job_description: str, resume: str) -> Dict[str, any]:
    """
    Convenience function to compare technologies.
    
    Returns:
        Comparison dictionary
    """
    matcher = TechnologyMatcher()
    return matcher.compare_technologies(job_description, resume)

