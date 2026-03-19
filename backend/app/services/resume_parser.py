"""
Resume parser service for extracting information from resume text.
"""

import re
from typing import List, Dict


class ResumeParser:
    """
    Parser for extracting structured information from resume text.
    """
    
    @staticmethod
    def extract_education(text: str) -> List[str]:
        """
        Extract education information from resume.
        
        Args:
            text: Resume text content
            
        Returns:
            List of education entries
        """
        education_keywords = [
            "bachelor", "master", "phd", "degree", "diploma",
            "certification", "bs", "ms", "associate", "bootcamp"
        ]
        
        lines = text.split("\n")
        education = []
        
        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in education_keywords):
                education.append(line.strip())
        
        return education
    
    @staticmethod
    def extract_experience_years(text: str) -> int:
        """
        Estimate years of experience from resume.
        
        Args:
            text: Resume text content
            
        Returns:
            Estimated years of experience
        """
        # Look for date patterns
        years_pattern = r"(19|20)\d{2}|(\d+)\s*(?:years?|yrs?)"
        matches = re.findall(years_pattern, text, re.IGNORECASE)
        
        if matches:
            return len(matches) // 2  # Rough estimation
        return 0
    
    @staticmethod
    def extract_projects(text: str) -> List[str]:
        """
        Extract project information from resume.
        
        Args:
            text: Resume text content
            
        Returns:
            List of projects
        """
        project_keywords = [
            "project", "developed", "built", "created",
            "implemented", "designed", "led"
        ]
        
        lines = text.split("\n")
        projects = []
        
        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in project_keywords):
                projects.append(line.strip())
        
        return projects
    
    @staticmethod
    def infer_experience_level(text: str) -> str:
        """
        Infer experience level (beginner, intermediate, advanced) from resume.
        
        Args:
            text: Resume text content
            
        Returns:
            Experience level string
        """
        text_lower = text.lower()
        years = ResumeParser.extract_experience_years(text)
        
        # Count mentions of senior/expert/lead roles
        senior_keywords = ["senior", "lead", "architect", "expert", "principal"]
        senior_mentions = sum(1 for keyword in senior_keywords if keyword in text_lower)
        
        # Heuristic logic
        if senior_mentions >= 2 or years >= 7:
            return "advanced"
        elif years >= 3 or senior_mentions >= 1:
            return "intermediate"
        else:
            return "beginner"
    
    @staticmethod
    def parse_resume(text: str) -> Dict[str, any]:
        """
        Parse complete resume and extract structured information.
        
        Args:
            text: Resume text content
            
        Returns:
            Dictionary with parsed resume information
        """
        return {
            "education": ResumeParser.extract_education(text),
            "experience_years": ResumeParser.extract_experience_years(text),
            "projects": ResumeParser.extract_projects(text),
            "experience_level": ResumeParser.infer_experience_level(text),
            "text_length": len(text),
        }
