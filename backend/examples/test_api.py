"""
Example script for testing the API.
Usage: python examples/test_api.py
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def create_user(email: str, name: str):
    """Create a new user."""
    url = f"{BASE_URL}/users"
    data = {
        "email": email,
        "name": name
    }
    response = requests.post(url, json=data)
    print(f"POST {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json() if response.status_code == 201 else None

def analyze_files(user_id: int, resume_path: str, jd_path: str):
    """Analyze resume and job description."""
    url = f"{BASE_URL}/analyze"
    
    with open(resume_path, 'rb') as f_resume, \
         open(jd_path, 'rb') as f_jd:
        files = {
            'resume_file': f_resume,
            'jd_file': f_jd,
        }
        data = {
            'user_id': user_id,
        }
        response = requests.post(url, files=files, data=data)
    
    print(f"\nPOST {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json() if response.status_code == 200 else None

def get_analysis(analysis_id: int):
    """Retrieve a stored analysis."""
    url = f"{BASE_URL}/analysis/{analysis_id}"
    response = requests.get(url)
    print(f"\nGET {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def get_user_analyses(user_id: int):
    """Get all analyses for a user."""
    url = f"{BASE_URL}/users/{user_id}/analyses"
    response = requests.get(url)
    print(f"\nGET {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def health_check():
    """Check API health."""
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print(f"GET {url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("AI Adaptive Onboarding Engine - API Test Script")
    print("=" * 60)
    
    # Test health check
    print("\n1. Testing Health Check...")
    if not health_check():
        print("ERROR: API is not running. Start it with:")
        print("  python -m uvicorn app.main:app --reload")
        exit(1)
    
    # Create user
    print("\n2. Creating User...")
    user = create_user("test@example.com", "Test User")
    if not user:
        print("ERROR: Failed to create user")
        exit(1)
    user_id = user['id']
    
    # Create sample resume and JD files for testing
    print("\n3. Creating Sample Files...")
    resume_path = "examples/sample_resume.txt"
    jd_path = "examples/sample_jd.txt"
    
    Path("examples").mkdir(exist_ok=True)
    
    # Sample resume
    with open(resume_path, 'w') as f:
        f.write("""
John Doe
Senior Backend Developer

SKILLS
Python, FastAPI, SQL, Docker, Git, AWS

EXPERIENCE
Senior Backend Developer at TechCorp (2021-Present)
- Led microservices architecture using FastAPI
- Managed PostgreSQL databases
- Implemented CI/CD pipelines with Docker

Backend Developer at StartupXYZ (2019-2021)
- Developed REST APIs using Python
- Database optimization

EDUCATION
BS Computer Science - State University
""")
    
    # Sample job description
    with open(jd_path, 'w') as f:
        f.write("""
Senior Backend Engineer

REQUIRED SKILLS
Python (5+ years), FastAPI, SQL, PostgreSQL, Docker, Kubernetes, AWS, React

RESPONSIBILITIES
- Design backend systems
- Optimize databases
- Mentor junior developers

ABOUT YOU
- Strong problem solving
- Experience with microservices
- Good communication
""")
    
    # Analyze files
    print("\n4. Analyzing Resume and Job Description...")
    analysis = analyze_files(user_id, resume_path, jd_path)
    if not analysis:
        print("ERROR: Failed to analyze files")
        exit(1)
    analysis_id = analysis.get('analysis_id')
    
    # Get analysis
    if analysis_id:
        print("\n5. Retrieving Stored Analysis...")
        get_analysis(analysis_id)
    
    # Get user analyses
    print("\n6. Listing User's Analyses...")
    get_user_analyses(user_id)
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)
