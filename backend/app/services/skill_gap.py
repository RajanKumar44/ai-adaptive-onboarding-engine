"""
Skill gap analysis service.
Identifies missing and matched skills between resume and job description.
"""

from typing import List, Dict, Tuple


class SkillGapAnalyzer:
    """
    Analyzes skill gaps between resume and job description.
    """
    
    @staticmethod
    def normalize_skill(skill: str) -> str:
        """
        Normalize skill name for comparison.
        
        Args:
            skill: Skill name
            
        Returns:
            Normalized skill name
        """
        return skill.lower().strip()
    
    @staticmethod
    def analyze_gaps(
        resume_skills: List[str],
        jd_skills: List[str]
    ) -> Dict[str, List[str]]:
        """
        Analyze skill gaps between resume and job description.
        
        Args:
            resume_skills: List of skills found in resume
            jd_skills: List of skills found in job description
            
        Returns:
            Dictionary containing matched and missing skills
        """
        # Normalize all skills for comparison
        normalized_resume = {
            SkillGapAnalyzer.normalize_skill(skill): skill
            for skill in resume_skills
        }
        
        normalized_jd = {
            SkillGapAnalyzer.normalize_skill(skill): skill
            for skill in jd_skills
        }
        
        # Find matched skills
        matched_skills = list(set(normalized_resume.keys()) & set(normalized_jd.keys()))
        
        # Find missing skills (in JD but not in resume)
        missing_skills = list(set(normalized_jd.keys()) - set(normalized_resume.keys()))
        
        # Find extra skills (in resume but not in JD)
        extra_skills = list(set(normalized_resume.keys()) - set(normalized_jd.keys()))
        
        return {
            "matched_skills": sorted(matched_skills),
            "missing_skills": sorted(missing_skills),
            "extra_skills": sorted(extra_skills),
            "match_percentage": (
                len(matched_skills) / len(normalized_jd) * 100
                if normalized_jd else 0
            )
        }
    
    @staticmethod
    def categorize_skills_by_priority(
        missing_skills: List[str],
        jd_text: str
    ) -> Dict[str, List[str]]:
        """
        Categorize missing skills by priority based on JD mentions.
        
        Args:
            missing_skills: List of missing skills
            jd_text: Full job description text
            
        Returns:
            Dictionary with skills categorized by priority
        """
        jd_text_lower = jd_text.lower()
        
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for skill in missing_skills:
            skill_lower = skill.lower()
            
            # Count frequency of skill mention
            mention_count = jd_text_lower.count(skill_lower)
            
            # High priority keywords
            high_keywords = ["required", "must have", "essential", "critical", "key"]
            high_context = any(
                f"{keyword} {skill_lower}" in jd_text_lower or
                f"{skill_lower} {keyword}" in jd_text_lower
                for keyword in high_keywords
            )
            
            if mention_count >= 3 or high_context:
                high_priority.append(skill)
            elif mention_count >= 2:
                medium_priority.append(skill)
            else:
                low_priority.append(skill)
        
        return {
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
        }
    
    @staticmethod
    def generate_gap_report(
        resume_skills: List[str],
        jd_skills: List[str],
        jd_text: str
    ) -> Dict:
        """
        Generate comprehensive skill gap report.
        
        Args:
            resume_skills: Skills found in resume
            jd_skills: Skills found in job description
            jd_text: Full job description text
            
        Returns:
            Comprehensive gap analysis report
        """
        gaps = SkillGapAnalyzer.analyze_gaps(resume_skills, jd_skills)
        categories = SkillGapAnalyzer.categorize_skills_by_priority(
            gaps["missing_skills"],
            jd_text
        )
        
        return {
            "summary": {
                "total_jd_skills": len(jd_skills),
                "matched_skills_count": len(gaps["matched_skills"]),
                "missing_skills_count": len(gaps["missing_skills"]),
                "match_percentage": gaps["match_percentage"],
            },
            "matched_skills": gaps["matched_skills"],
            "missing_skills": {
                "high_priority": categories["high_priority"],
                "medium_priority": categories["medium_priority"],
                "low_priority": categories["low_priority"],
            },
            "extra_skills": gaps["extra_skills"],
        }
