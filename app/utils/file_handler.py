import os
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.core.config import settings


class FileHandler:
    """Utilities for reading, saving, and validating uploaded files."""

    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx"}

    def read_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file using pdfplumber."""
        try:
            import pdfplumber
        except ImportError as exc:
            raise RuntimeError("pdfplumber is required for PDF parsing.") from exc

        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    def read_text_file(self, file_path: str) -> str:
        """Read plain text from a file."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()

    def save_file(self, upload_file: UploadFile, destination: Optional[str] = None) -> str:
        """Persist an uploaded file and return its absolute path."""
        upload_dir = Path(destination or settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(upload_file.filename).name  # strip directory traversal
        file_path = upload_dir / safe_name
        with open(file_path, "wb") as fh:
            fh.write(upload_file.file.read())
        return str(file_path)

    def validate_file(self, upload_file: UploadFile) -> bool:
        """Return True if the file extension is allowed and size is within limit."""
        suffix = Path(upload_file.filename).suffix.lower()
        if suffix not in self.ALLOWED_EXTENSIONS:
            return False
        # Check size if readable
        try:
            upload_file.file.seek(0, 2)
            size = upload_file.file.tell()
            upload_file.file.seek(0)
            if size > settings.MAX_FILE_SIZE:
                return False
        except Exception:
            pass
        return True
