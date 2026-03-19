# AI Adaptive Onboarding Engine

A production-ready FastAPI backend system that analyzes resumes and job descriptions to generate personalized adaptive learning roadmaps.

## Features

- Resume & JD Analysis: Extract text from PDF and text documents
- Dual Skill Extraction: Rule-based matching + LLM-ready placeholders
- Skill Gap Analysis: Identify missing skills and proficiency gaps
- Personalized Learning Paths: Generate customized roadmaps with estimated hours
- Reasoning Trace: Detailed explanations for each recommendation
- PostgreSQL Storage: Persist analysis results for future reference
- Scalable Architecture: Modular service-based design
- Production-Ready: Error handling, validation, and best practices

## Technology Stack

- Framework: FastAPI (Python)
- Database: PostgreSQL
- ORM: SQLAlchemy
- Validation: Pydantic
- PDF Processing: pdfplumber

## Quick Start

See INSTALLATION.md for complete setup instructions.

## API Endpoints

- POST /api/v1/analyze - Analyze resume and job description
- GET /api/v1/analysis/{id} - Get analysis by ID
- GET /api/v1/analyses/user/{email} - Get user analyses

## Documentation

Complete documentation available in README_FULL.md