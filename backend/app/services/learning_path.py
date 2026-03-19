"""
Adaptive learning path generation service.
Creates personalized learning roadmaps based on skill gaps and user level.
"""

from typing import List, Dict, Any
from app.utils.skill_knowledge_base import get_skill_info, SKILL_KNOWLEDGE_BASE
from app.services.resume_parser import ResumeParser


class LearningPathGenerator:
    """
    Generates adaptive, personalized learning paths for skill acquisition.
    """
    
    @staticmethod
    def detect_user_skill_level(skill: str, resume_text: str) -> str:
        """
        Detect user's current proficiency level for a specific skill.
        
        Args:
            skill: The skill name
            resume_text: Resume text content
            
        Returns:
            Proficiency level: 'beginner', 'intermediate', or 'advanced'
        """
        resume_lower = resume_text.lower()
        skill_lower = skill.lower()
        
        # Check if skill is mentioned at all
        if skill_lower not in resume_lower:
            return "beginner"  # Not mentioned, so beginner
        
        # Heuristic: look for experience indicators
        advanced_patterns = [
            f"senior {skill_lower}",
            f"lead {skill_lower}",
            f"{skill_lower} architect",
            f"expert {skill_lower}",
            f"{skill_lower} expert",
            f"{skill_lower} specialist",
        ]
        
        for pattern in advanced_patterns:
            if pattern in resume_lower:
                return "advanced"
        
        # Check for intermediate indicators
        intermediate_patterns = [
            f"experienced {skill_lower}",
            f"proficient {skill_lower}",
            f"{skill_lower} developer",
            f"{skill_lower} engineer",
        ]
        
        for pattern in intermediate_patterns:
            if pattern in resume_lower:
                return "intermediate"
        
        # Default to intermediate if skill is mentioned
        return "intermediate"
    
    @staticmethod
    def generate_learning_path_for_skill(
        skill: str,
        user_level: str,
        resume_text: str
    ) -> Dict[str, Any]:
        """
        Generate personalized learning path for a single skill.
        
        Args:
            skill: The skill name
            user_level: User's current proficiency level
            resume_text: Resume text for context
            
        Returns:
            Personalized learning path for the skill
        """
        skill_info = get_skill_info(skill)
        
        if not skill_info:
            # Fallback for unknown skills
            return {
                "skill": skill,
                "level": user_level,
                "steps": [
                    f"Research {skill} fundamentals",
                    f"Start with official {skill} documentation",
                    f"Complete beginner tutorials",
                    f"Build simple projects to practice",
                ],
                "resources": [
                    {
                        "title": f"Learn {skill}",
                        "url": "https://google.com",
                        "type": "search"
                    }
                ],
                "estimated_hours": 40,
                "next_level": "intermediate" if user_level == "beginner" else "advanced",
                "reasoning": f"No structured learning path available. {skill} is important for the role."
            }
        
        # Determine next level to learn
        if user_level == "beginner":
            next_level = "intermediate"
            current_steps = skill_info.get("beginner", [])
        elif user_level == "intermediate":
            next_level = "advanced"
            current_steps = skill_info.get("intermediate", [])
        else:
            next_level = "advanced"
            current_steps = skill_info.get("advanced", [])
        
        # Get resources for the next level
        resources = skill_info.get("resources", {}).get(next_level.lower(), [])
        
        # Get estimated hours
        estimated_hours = skill_info.get("estimated_hours", {}).get(next_level.lower(), 50)
        
        return {
            "skill": skill,
            "current_level": user_level,
            "target_level": next_level,
            "steps": current_steps,
            "resources": resources,
            "estimated_hours": estimated_hours,
            "difficulty": next_level,
            "prerequisites": [],
        }
    
    @staticmethod
    def generate_complete_roadmap(
        missing_skills: List[str],
        prioritized_skills: Dict[str, List[str]],
        resume_text: str,
        experience_level: str = "intermediate"
    ) -> List[Dict[str, Any]]:
        """
        Generate complete adaptive learning roadmap.
        
        Args:
            missing_skills: List of skills to learn
            prioritized_skills: Skills grouped by priority
            resume_text: Resume text for user context
            experience_level: Overall experience level
            
        Returns:
            Ordered list of learning steps with reasoning
        """
        roadmap = []
        
        # Process high priority skills first
        for skill in prioritized_skills.get("high_priority", []):
            user_level = LearningPathGenerator.detect_user_skill_level(skill, resume_text)
            path = LearningPathGenerator.generate_learning_path_for_skill(
                skill,
                user_level,
                resume_text
            )
            path["priority"] = "high"
            roadmap.append(path)
        
        # Process medium priority skills
        for skill in prioritized_skills.get("medium_priority", []):
            user_level = LearningPathGenerator.detect_user_skill_level(skill, resume_text)
            path = LearningPathGenerator.generate_learning_path_for_skill(
                skill,
                user_level,
                resume_text
            )
            path["priority"] = "medium"
            roadmap.append(path)
        
        # Process low priority skills
        for skill in prioritized_skills.get("low_priority", []):
            user_level = LearningPathGenerator.detect_user_skill_level(skill, resume_text)
            path = LearningPathGenerator.generate_learning_path_for_skill(
                skill,
                user_level,
                resume_text
            )
            path["priority"] = "low"
            roadmap.append(path)
        
        return roadmap
    
    @staticmethod
    def estimate_total_learning_time(roadmap: List[Dict[str, Any]]) -> int:
        """
        Calculate total estimated learning time for complete roadmap.
        
        Args:
            roadmap: Learning path roadmap
            
        Returns:
            Total estimated hours
        """
        total_hours = sum(item.get("estimated_hours", 0) for item in roadmap)
        return total_hours
    
    @staticmethod
    def generate_reasoning_trace(
        missing_skills: List[str],
        jd_text: str,
        matched_skills: List[str]
    ) -> List[Dict[str, str]]:
        """
        Generate reasoning explanation for each skill recommendation.
        
        Args:
            missing_skills: Skills that are missing
            jd_text: Job description text
            matched_skills: Skills that matched
            
        Returns:
            List of reasoning entries for each skill
        """
        reasoning_trace = []
        
        for skill in missing_skills:
            skill_lower = skill.lower()
            mention_count = jd_text.lower().count(skill_lower)
            
            # Build reasoning message
            reason = f"{skill} is required in the job description"
            
            if mention_count > 1:
                reason += f" (mentioned {mention_count} times)"
            
            reason += f", but was not found in your resume."
            
            reasoning_trace.append({
                "skill": skill,
                "reason": reason,
                "missing": True,
            })
        
        # Add positive reasoning for matched skills
        for skill in matched_skills[:5]:  # Show top 5 matched
            reasoning_trace.append({
                "skill": skill,
                "reason": f"{skill} matches between your resume and job description.",
                "missing": False,
            })
        
        return reasoning_trace
