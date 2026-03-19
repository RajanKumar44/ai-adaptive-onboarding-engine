import re
from typing import Dict, List


class ResumeParser:
    """Parse and clean resume text, extracting structured sections."""

    SECTION_HEADERS = [
        "experience",
        "education",
        "skills",
        "projects",
        "certifications",
        "summary",
        "objective",
        "awards",
        "publications",
        "languages",
        "interests",
    ]

    def parse_text(self, text: str) -> Dict[str, str]:
        """Parse raw resume text and return a dict of sections."""
        cleaned = self._clean_text(text)
        sections = self.extract_sections(cleaned)
        return sections

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Split text into labelled sections based on common headers."""
        sections: Dict[str, str] = {"full_text": text}
        pattern = re.compile(
            r"(?i)^(" + "|".join(self.SECTION_HEADERS) + r")\s*[:\-]?\s*$",
            re.MULTILINE,
        )
        matches = list(pattern.finditer(text))
        if not matches:
            return sections

        for i, match in enumerate(matches):
            header = match.group(1).lower()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections[header] = text[start:end].strip()

        return sections

    def _clean_text(self, text: str) -> str:
        """Normalize whitespace and remove non-printable characters."""
        text = re.sub(r"[^\x20-\x7E\n]", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
