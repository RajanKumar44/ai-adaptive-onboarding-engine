"""
Rule-based skill extraction fallback.
Used when LLM is unavailable or as a lightweight alternative.
"""

import re
import logging
from typing import List, Set, Dict, Optional
from app.utils.skill_knowledge_base import get_all_skills

logger = logging.getLogger(__name__)


class FallbackExtractor:
    """
    Rule-based skill extraction used as fallback when LLM is unavailable.
    Provides consistent results without external API dependencies.
    """
    
    # Predefined skill list
    COMMON_SKILLS = get_all_skills()
    
    # Extended skill variations and aliases
    SKILL_ALIASES = {
        "javascript": ["js", "node", "nodejs", "node.js", "es6", "es5"],
        "typescript": ["ts", "types"],
        "python": ["py", "django", "flask", "pip"],
        "fastapi": ["fast api", "fastapi"],
        "react": ["reactjs", "react.js", "jsx"],
        "vue": ["vuejs", "vue.js"],
        "angular": ["angularjs", "angular.js"],
        "sql": ["mysql", "postgresql", "postgres", "sqlite", "database", "plsql", "t-sql"],
        "mongodb": ["mongo"],
        "docker": ["containerization", "containers", "docker"],
        "kubernetes": ["k8s", "orchestration"],
        "aws": ["amazon web services", "amazon", "ec2", "s3", "lambda"],
        "git": ["github", "gitlab", "bitbucket", "version control"],
        "html": ["markup", "html5"],
        "css": ["styling", "stylesheets", "scss", "sass"],
        "redis": ["cache"],
        "elasticsearch": ["search engine", "elastic"],
        "ci/cd": ["continuous integration", "continuous deployment", "cicd", "devops", "github actions", "gitlab ci"],
        "rest": ["restful", "rest api", "http"],
        "graphql": ["graph ql"],
        "json": ["json"],
        "xml": ["xml"],
        "api": ["apis", "api design"],
        "testing": ["unit test", "pytest", "jest", "unittest", "test automation", "tdd"],
        "linux": ["unix", "operating system", "os"],
        "vim": ["text editor"],
        "bash": ["shell scripting", "shell", "zsh"],
        "agile": ["scrum", "kanban", "sprint"],
        "microservices": ["micro services"],
        "architecture": ["system design", "design patterns"],
    }
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """
        Extract skills from text using rule-based matching.
        
        Args:
            text: Document text to extract skills from
            
        Returns:
            List of extracted skills
        """
        extracted_skills: Set[str] = set()
        text_lower = text.lower()
        
        # Check for exact skill matches
        for skill in FallbackExtractor.COMMON_SKILLS:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                extracted_skills.add(skill)
        
        # Check for skill aliases
        for main_skill, aliases in FallbackExtractor.SKILL_ALIASES.items():
            if main_skill in extracted_skills:
                continue
            
            for alias in aliases:
                if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
                    extracted_skills.add(main_skill)
                    break
        
        # Check for technologies with regex patterns
        technology_patterns = {
            "django": r"\bdjango\b",
            "flask": r"\bflask\b",
            "spring": r"\bspring\b",
            "maven": r"\bmaven\b",
            "gradle": r"\bgradle\b",
            "ant": r"\bant\b",
            "junit": r"\bjunit\b",
            "jenkins": r"\bjenkins\b",
            "travis": r"\b(travis|travis ci)\b",
            "circleci": r"\b(circleci|circle ci)\b",
            "nginx": r"\bnginx\b",
            "apache": r"\bapache\b",
            "kafka": r"\bkafka\b",
            "rabbitmq": r"\brabbitmq\b",
            "oauth": r"\boauth\b",
            "jwt": r"\bjwt\b",
            "ssl": r"\b(ssl|tls)\b",
            "https": r"\bhttps\b",
        }
        
        for skill, pattern in technology_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                extracted_skills.add(skill)
        
        # Check for cloud providers
        cloud_providers = {
            "aws": [r"\bamazon web services\b", r"\bamazon\b", r"\baws\b", r"\bedge\b"],
            "azure": [r"\bazure\b", r"\bmicrosoft azure\b"],
            "gcp": [r"\bgoogle cloud\b", r"\bgcp\b"],
        }
        
        for provider, patterns in cloud_providers.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    extracted_skills.add(provider)
        
        # Check for databases
        databases = {
            "postgresql": [r"\bpostgres\b", r"\bpostgresql\b"],
            "mysql": [r"\bmysql\b"],
            "mongodb": [r"\bmongo\b", r"\bmongodb\b"],
            "cassandra": [r"\bcassandra\b"],
            "dynamodb": [r"\bdynamodb\b"],
            "oracle": [r"\boracle\b"],
        }
        
        for db, patterns in databases.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    extracted_skills.add(db)
        
        # Check for frontend frameworks
        frontend = {
            "react": [r"\breact\b", r"\breactjs\b"],
            "vue": [r"\bvue\b", r"\bvuejs\b"],
            "angular": [r"\bangular\b"],
            "svelte": [r"\bsvelte\b"],
        }
        
        for fw, patterns in frontend.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    extracted_skills.add(fw)
        
        # Check for backend frameworks
        backend = {
            "node.js": [r"\bnode\b", r"\bnodejs\b", r"\bnode\.js\b"],
            "django": [r"\bdjango\b"],
            "flask": [r"\bflask\b"],
            "fastapi": [r"\bfastapi\b", r"\bfast api\b"],
            "spring": [r"\bspring\b", r"\bspring boot\b"],
            "laravel": [r"\blaravel\b"],
            "rails": [r"\brails\b", r"\bruby on rails\b"],
        }
        
        for fw, patterns in backend.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    extracted_skills.add(fw)
        
        # Sort and return
        result = sorted(list(extracted_skills))
        logger.info(
            f"Rule-based extraction: {len(result)} skills extracted",
            extra={"skills": result}
        )
        
        return result
    
    @staticmethod
    def extract_skills_with_confidence(text: str) -> Dict[str, float]:
        """
        Extract skills with confidence scores (frequency-based).
        
        Args:
            text: Document text
            
        Returns:
            Dictionary mapping skill to confidence (0-1)
        """
        text_lower = text.lower()
        word_count = len(text_lower.split())
        
        skill_frequencies: Dict[str, int] = {}
        
        # Count skill occurrences
        for skill in FallbackExtractor.COMMON_SKILLS:
            matches = len(re.findall(r'\b' + re.escape(skill) + r'\b', text_lower))
            if matches > 0:
                skill_frequencies[skill] = matches
        
        # Also check aliases
        for main_skill, aliases in FallbackExtractor.SKILL_ALIASES.items():
            current_count = skill_frequencies.get(main_skill, 0)
            for alias in aliases:
                matches = len(re.findall(r'\b' + re.escape(alias) + r'\b', text_lower))
                if matches > 0:
                    current_count += matches
            
            if current_count > 0:
                skill_frequencies[main_skill] = current_count
        
        # Calculate confidence (frequency / document length, capped at 1.0)
        skills_with_confidence = {}
        for skill, frequency in skill_frequencies.items():
            confidence = min(1.0, frequency / (word_count / 100) if word_count > 0 else 0)
            skills_with_confidence[skill] = round(confidence, 3)
        
        # Sort by confidence
        sorted_skills = dict(sorted(
            skills_with_confidence.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        return sorted_skills
    
    @staticmethod
    def extract_skills_by_category(text: str) -> Dict[str, List[str]]:
        """
        Extract skills and categorize them.
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with skills grouped by category
        """
        all_skills = FallbackExtractor.extract_skills(text)
        
        categories = {
            "programming_languages": [],
            "frameworks": [],
            "databases": [],
            "cloud_providers": [],
            "tools": [],
            "methodologies": [],
            "other": [],
        }
        
        # Map skills to categories
        skill_categories = {
            # Programming languages
            "python": "programming_languages",
            "javascript": "programming_languages",
            "typescript": "programming_languages",
            "java": "programming_languages",
            "cpp": "programming_languages",
            "csharp": "programming_languages",
            "go": "programming_languages",
            "rust": "programming_languages",
            "php": "programming_languages",
            "ruby": "programming_languages",
            "swift": "programming_languages",
            "kotlin": "programming_languages",
            
            # Frameworks
            "react": "frameworks",
            "angular": "frameworks",
            "vue": "frameworks",
            "django": "frameworks",
            "flask": "frameworks",
            "fastapi": "frameworks",
            "spring": "frameworks",
            "laravel": "frameworks",
            "rails": "frameworks",
            "express": "frameworks",
            
            # Databases
            "postgresql": "databases",
            "mysql": "databases",
            "mongodb": "databases",
            "redis": "databases",
            "elasticsearch": "databases",
            "sql": "databases",
            
            # Cloud providers
            "aws": "cloud_providers",
            "azure": "cloud_providers",
            "gcp": "cloud_providers",
            
            # Tools
            "git": "tools",
            "docker": "tools",
            "kubernetes": "tools",
            "jenkins": "tools",
            "travis": "tools",
            
            # Methodologies
            "agile": "methodologies",
            "scrum": "methodologies",
            "testing": "methodologies",
        }
        
        for skill in all_skills:
            category = skill_categories.get(skill, "other")
            categories[category].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
