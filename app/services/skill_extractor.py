import re
from typing import Dict, List, Tuple

from app.utils.skill_knowledge_base import SKILL_KEYWORDS


class SkillExtractor:
    """Extract skills from text using rule-based matching and optional LLM."""

    def extract_skills(self, text: str) -> List[str]:
        """Return a deduplicated list of skills found in the text."""
        return self._extract_skills_rule_based(text)

    def _extract_skills_rule_based(self, text: str) -> List[str]:
        """Scan text for each known skill keyword and collect matches."""
        found: List[str] = []
        lower_text = text.lower()
        for skill, aliases in SKILL_KEYWORDS.items():
            if self._is_skill_present(lower_text, aliases):
                found.append(skill)
        return found

    def _is_skill_present(self, lower_text: str, aliases: List[str]) -> bool:
        """Return True if any alias appears as a whole word/phrase in the text."""
        for alias in aliases:
            # Use word-boundary matching for short tokens to reduce false positives
            pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
            if re.search(pattern, lower_text):
                return True
        return False

    def extract_skills_with_llm(self, text: str, llm_client=None) -> List[str]:
        """Placeholder for LLM-based skill extraction.

        When a real LLM client is provided this method should call the model
        and parse the response.  Falls back to rule-based extraction.
        """
        if llm_client is not None:
            # TODO: integrate with an actual LLM endpoint
            pass
        return self.extract_skills(text)

    def extract_with_confidence(self, text: str) -> List[Tuple[str, float]]:
        """Return skills with a naive confidence score (1.0 for rule-based hits)."""
        skills = self.extract_skills(text)
        return [(skill, 1.0) for skill in skills]
