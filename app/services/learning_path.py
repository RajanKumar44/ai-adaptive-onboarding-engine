from typing import Dict, List, Optional

from app.utils.learning_knowledge_base import PROFICIENCY_LEVELS, SKILL_LEARNING_PATHS
from app.utils.skill_knowledge_base import SKILL_KEYWORDS


class LearningPathGenerator:
    """Generate a personalized, prioritized learning path for missing skills."""

    RELATED_SKILL_GROUPS = [
        {"javascript", "typescript", "react", "angular", "vue", "nextjs", "nuxtjs"},
        {"python", "django", "flask", "fastapi"},
        {"java", "spring", "kotlin"},
        {"docker", "kubernetes"},
        {"aws", "gcp", "azure"},
        {"postgresql", "mysql", "sqlite"},
        {"machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn"},
    ]

    def generate_path(
        self,
        missing_skills: List[str],
        resume_skills: List[str],
    ) -> List[Dict]:
        """Build a learning path list ordered by priority."""
        paths = []
        for skill in missing_skills:
            level = self._detect_user_level(skill, resume_skills)
            target = self._determine_target_level(level)
            steps = self._get_learning_steps(skill, level)
            paths.append(
                {
                    "skill": skill,
                    "current_level": level,
                    "target_level": target,
                    "priority": self._assign_priority(skill),
                    "steps": steps,
                    "total_hours": self._calculate_total_hours(steps),
                }
            )
        # Sort: high priority first, then by total hours ascending
        priority_order = {"high": 0, "medium": 1, "low": 2}
        paths.sort(key=lambda p: (priority_order.get(p["priority"], 1), p["total_hours"]))
        return paths

    def _detect_user_level(self, skill: str, resume_skills: List[str]) -> str:
        """Infer the user's current level for a skill they are missing."""
        if self._has_related_skill(skill, resume_skills):
            return "beginner"
        return "beginner"

    def _has_related_skill(self, skill: str, resume_skills: List[str]) -> bool:
        """Check whether the user has any skill in the same technology family."""
        skill_lower = skill.lower()
        resume_lower = {s.lower() for s in resume_skills}
        for group in self.RELATED_SKILL_GROUPS:
            if skill_lower in group:
                if group & resume_lower:
                    return True
        return False

    def _determine_target_level(self, current_level: str) -> str:
        """Set a realistic target one level above the current."""
        level_order = ["beginner", "intermediate", "advanced", "expert"]
        idx = level_order.index(current_level) if current_level in level_order else 0
        return level_order[min(idx + 2, len(level_order) - 1)]

    def _get_learning_steps(self, skill: str, current_level: str) -> List[Dict]:
        """Retrieve structured learning steps from the knowledge base."""
        skill_lower = skill.lower()
        if skill_lower in SKILL_LEARNING_PATHS:
            path_data = SKILL_LEARNING_PATHS[skill_lower]
            if current_level in path_data:
                return path_data[current_level]
            # Fall back to the first available level
            first_key = next(iter(path_data))
            return path_data[first_key]
        return self._generate_generic_steps(skill)

    def _calculate_total_hours(self, steps: List[Dict]) -> int:
        """Sum estimated hours across all steps."""
        return sum(step.get("estimated_hours", 0) for step in steps)

    def _assign_priority(self, skill: str) -> str:
        """Assign priority based on broad skill category."""
        from app.utils.skill_knowledge_base import SKILL_CATEGORIES

        skill_lower = skill.lower()
        high_priority_categories = {"languages", "backend", "databases", "devops"}
        for category, skills in SKILL_CATEGORIES.items():
            if skill_lower in skills and category in high_priority_categories:
                return "high"
        if skill_lower in SKILL_CATEGORIES.get("data_ml", []):
            return "medium"
        return "low"

    def _generate_generic_path(self, skill: str) -> Dict:
        """Fallback path when the skill has no knowledge-base entry."""
        steps = self._generate_generic_steps(skill)
        return {
            "skill": skill,
            "current_level": "beginner",
            "target_level": "intermediate",
            "priority": "medium",
            "steps": steps,
            "total_hours": self._calculate_total_hours(steps),
        }

    def _generate_generic_steps(self, skill: str) -> List[Dict]:
        """Produce three generic learning steps for any skill."""
        return [
            {
                "step": 1,
                "title": f"Introduction to {skill.title()}",
                "description": f"Learn the core concepts and basics of {skill.title()}.",
                "resources": [
                    f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial",
                    "https://www.udemy.com/",
                ],
                "estimated_hours": 15,
            },
            {
                "step": 2,
                "title": f"Intermediate {skill.title()} Skills",
                "description": f"Build practical projects and deepen your {skill.title()} knowledge.",
                "resources": [
                    f"https://github.com/topics/{skill.lower().replace(' ', '-')}",
                ],
                "estimated_hours": 20,
            },
            {
                "step": 3,
                "title": f"Advanced {skill.title()} Patterns",
                "description": f"Apply best practices and advanced patterns for {skill.title()}.",
                "resources": [
                    "https://roadmap.sh/",
                ],
                "estimated_hours": 20,
            },
        ]

    def generate_reasoning(
        self,
        resume_skills: List[str],
        jd_skills: List[str],
        matched_skills: List[str],
        missing_skills: List[str],
        learning_path: List[Dict],
        match_percentage: float,
    ) -> str:
        """Produce a human-readable reasoning trace for the analysis."""
        lines = [
            "=== AI Adaptive Onboarding Analysis ===",
            "",
            f"Resume Skills Detected ({len(resume_skills)}): {', '.join(resume_skills) or 'None'}",
            f"JD Skills Required ({len(jd_skills)}): {', '.join(jd_skills) or 'None'}",
            "",
            f"Match Rate: {match_percentage:.1f}%",
            f"Matched Skills ({len(matched_skills)}): {', '.join(matched_skills) or 'None'}",
            f"Missing Skills ({len(missing_skills)}): {', '.join(missing_skills) or 'None'}",
            "",
            "=== Learning Path Rationale ===",
        ]

        if not learning_path:
            lines.append("No skill gaps identified. Candidate is well-qualified for this role.")
        else:
            for path in learning_path:
                lines.append(
                    f"- {path['skill'].title()} [{path['priority']} priority]"
                    f" — ~{path['total_hours']}h to reach {path['target_level']} level"
                )

        lines += [
            "",
            "=== Recommendation ===",
            (
                "Focus on high-priority skills first to maximize your employability, "
                "then build breadth with medium and low-priority items."
            ),
        ]
        return "\n".join(lines)
