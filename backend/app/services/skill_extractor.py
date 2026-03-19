"""
Skill extraction service with rule-based and LLM-based approaches.
"""

import re
from typing import List, Set
from app.utils.skill_knowledge_base import get_all_skills


class SkillExtractor:
    """
    Extracts technical skills from resume and job description text.
    Implements both rule-based matching and LLM-ready interface.
    """
    
    # Predefined skill list for rule-based extraction
    COMMON_SKILLS = get_all_skills()
    
    # Extended skill variations and aliases
    SKILL_ALIASES = {
        "javascript": ["js", "node", "nodejs", "node.js"],
        "typescript": ["ts"],
        "python": ["py", "django", "flask"],
        "fastapi": ["fast api"],
        "react": ["reactjs", "react.js"],
        "sql": ["mysql", "postgresql", "postgres", "sqlite", "database"],
        "docker": ["containerization", "containers"],
        "kubernetes": ["k8s", "k8s", "orchestration"],
        "aws": ["amazon web services", "amazon"],
        "git": ["github", "gitlab", "bitbucket", "version control"],
        "html": ["markup"],
        "css": ["styling", "stylesheets"],
        "mongodb": ["mongo"],
        "redis": [],
        "elasticsearch": ["search engine"],
        "ci/cd": ["continuous integration", "continuous deployment", "cicd", "devops"],
        "rest": ["restful", "rest api"],
        "graphql": ["graph ql"],
        "json": [],
        "xml": [],
        "api": ["apis"],
        "testing": ["unit test", "pytest", "jest", "unittest", "test automation"],
        "linux": ["unix", "operating system"],
        "vim": ["text editor"],
        "bash": ["shell scripting", "shell"],
        "agile": ["scrum", "kanban"],
    }
    
    @staticmethod
    def rule_based_extraction(text: str) -> List[str]:
        """
        Extract skills using rule-based pattern matching.
        
        Args:
            text: Document text to extract skills from
            
        Returns:
            List of extracted skills
        """
        extracted_skills: Set[str] = set()
        text_lower = text.lower()
        
        # Check for exact skill matches
        for skill in SkillExtractor.COMMON_SKILLS:
            if skill in text_lower:
                extracted_skills.add(skill)
        
        # Check for skill aliases
        for main_skill, aliases in SkillExtractor.SKILL_ALIASES.items():
            if main_skill in extracted_skills:
                # Already found via main skill name
                continue
            
            for alias in aliases:
                if alias in text_lower:
                    extracted_skills.add(main_skill)
                    break
        
        # Check for common frameworks and technologies
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
            "rest": r"\brest\b",
            "graphql": r"\bgraphql\b",
        }
        
        for tech, pattern in technology_patterns.items():
            if re.search(pattern, text_lower):
                extracted_skills.add(tech)
        
        return sorted(list(extracted_skills))
    
    @staticmethod
    async def extract_skills_with_llm(text: str, api_key: str = None) -> List[str]:
        """
        Extract skills using LLM-based approach.
        
        Currently implements a placeholder that can be easily swapped with actual LLM API calls.
        Supports OpenAI, Claude, or any other LLM provider.
        
        Args:
            text: Document text to extract skills from
            api_key: API key for LLM provider
            
        Returns:
            List of extracted skills
            
        Note:
            To integrate with real LLM:
            1. Install provider SDK: pip install openai (or anthropic, etc.)
            2. Uncomment actual API calls below
            3. Add API key to environment variables
            4. Update LLM_PROVIDER in config.py
        """
        
        # Placeholder implementation - demonstrates structure
        # Replace with actual LLM API calls
        
        # Example structure for OpenAI integration:
        # if api_key:
        #     from openai import OpenAI
        #     client = OpenAI(api_key=api_key)
        #     response = client.chat.completions.create(
        #         model="gpt-4",
        #         messages=[{
        #             "role": "user",
        #             "content": f"""Extract all technical skills from this text.
        #             Return as JSON list.
        #             Text: {text[:2000]}"""
        #         }]
        #     )
        #     # Parse and return skills
        
        # For now, use rule-based as fallback
        return SkillExtractor.rule_based_extraction(text)
    
    @staticmethod
    async def extract_skills(text: str, use_llm: bool = False, api_key: str = None) -> List[str]:
        """
        Extract skills using specified method.
        
        Args:
            text: Document text to extract skills from
            use_llm: Whether to use LLM-based extraction
            api_key: API key for LLM provider
            
        Returns:
            List of extracted skills
        """
        if use_llm and api_key:
            return await SkillExtractor.extract_skills_with_llm(text, api_key)
        else:
            return SkillExtractor.rule_based_extraction(text)
    
    @staticmethod
    def normalize_skills(skills: List[str]) -> List[str]:
        """
        Normalize skill names for consistent comparison.
        
        Args:
            skills: List of skill names
            
        Returns:
            Normalized skills list
        """
        normalized = set()
        
        for skill in skills:
            # Convert to lowercase and strip whitespace
            normalized_skill = skill.lower().strip()
            
            # Remove common suffixes
            normalized_skill = re.sub(r"\s*(framework|library|tool|language|database)$", "", normalized_skill)
            
            if normalized_skill:
                normalized.add(normalized_skill)
        
        return sorted(list(normalized))
