from typing import Dict, List

from app.utils.skill_knowledge_base import SKILL_KEYWORDS


class SkillGapAnalyzer:
    """Compare resume skills against JD skills and identify gaps."""

    def analyze(
        self, resume_skills: List[str], jd_skills: List[str]
    ) -> Dict[str, object]:
        """Return matched skills, missing skills, and match percentage."""
        resume_normalized = {s.lower() for s in resume_skills}
        jd_normalized = {s.lower() for s in jd_skills}

        matched = [
            self._restore_case(skill)
            for skill in jd_normalized
            if skill in resume_normalized
        ]
        missing = [
            self._restore_case(skill)
            for skill in jd_normalized
            if skill not in resume_normalized
        ]

        return {
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
            "match_percentage": self._calculate_match_percentage(matched, jd_skills),
        }

    def _restore_case(self, skill: str) -> str:
        """Prefer the canonical casing from SKILL_KEYWORDS, else title-case."""
        for canonical in SKILL_KEYWORDS:
            if canonical.lower() == skill.lower():
                return canonical
        return skill.title()

    def _calculate_match_percentage(
        self, matched: List[str], jd_skills: List[str]
    ) -> float:
        """Return the proportion of JD skills that are already present."""
        if not jd_skills:
            return 0.0
        return round(len(matched) / len(jd_skills) * 100, 2)
