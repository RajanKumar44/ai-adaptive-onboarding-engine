"""
File handling utilities for processing resume and job description files.
Supports PDF and text file extraction.
"""

import os
import pdfplumber
from typing import Tuple
from fastapi import UploadFile, HTTPException


async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        Extracted text from PDF
        
    Raises:
        HTTPException: If PDF processing fails
    """
    try:
        # Read file content
        content = await file.read()
        
        # Write to temporary file
        temp_path = f"/tmp/{file.filename}"
        os.makedirs("/tmp", exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Extract text using pdfplumber
        text = ""
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return text
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text from uploaded file (PDF or TXT).
    
    Args:
        file: Uploaded file
        
    Returns:
        Extracted text content
        
    Raises:
        HTTPException: If file type is not supported
    """
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension == "pdf":
        return await extract_text_from_pdf(file)
    elif file_extension == "txt":
        content = await file.read()
        return content.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(
            status_code=400,
            detail="File must be PDF or TXT format"
        )


def validate_file_size(file: UploadFile, max_size: int = 10 * 1024 * 1024) -> None:
    """
    Validate file size before processing.
    
    Args:
        file: Upload file to validate
        max_size: Maximum file size in bytes (default 10MB)
        
    Raises:
        HTTPException: If file exceeds max size
    """
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum limit of {max_size / 1024 / 1024}MB"
        )


def validate_file_type(file: UploadFile, allowed_extensions: list = None) -> None:
    """
    Validate file type/extension.
    
    Args:
        file: Upload file to validate
        allowed_extensions: List of allowed extensions (default: ['pdf', 'txt'])
        
    Raises:
        HTTPException: If file type is not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = ["pdf", "txt"]
    
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{file_extension}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )


async def process_and_validate_file(file: UploadFile, allowed_extensions: list = None) -> str:
    """
    Complete file validation and text extraction pipeline.
    
    Args:
        file: Upload file to process
        allowed_extensions: List of allowed extensions
        
    Returns:
        Extracted text content
        
    Raises:
        HTTPException: If validation or extraction fails
    """
    # Validate file type
    validate_file_type(file, allowed_extensions)
    
    # Validate file size
    validate_file_size(file)
    
    # Extract text
    return await extract_text_from_file(file)
