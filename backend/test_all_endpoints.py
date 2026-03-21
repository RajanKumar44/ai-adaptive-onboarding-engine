"""
Comprehensive API Testing Script for AI Adaptive Onboarding Engine
Tests all endpoints with dummy data and generates detailed report
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any
import base64
from io import BytesIO

BASE_URL = "http://localhost:8000"
API_VERSION = "/api/v1"

# Test credentials and data
DUMMY_USERS = [
    {
        "email": "testuser1@example.com",
        "name": "Test User 1",
        "password": "TestPassword123!@#",
        "confirm_password": "TestPassword123!@#"
    },
    {
        "email": "testuser2@example.com",
        "name": "Test User 2", 
        "password": "TestPassword456!@#",
        "confirm_password": "TestPassword456!@#"
    }
]

# Sample resume and JD text
SAMPLE_RESUME = """
John Doe
Email: john@example.com | Phone: (555) 123-4567

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in web development and cloud technologies.

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, Java, SQL
- Frameworks: FastAPI, React, Spring Boot
- Databases: PostgreSQL, MongoDB, Redis
- Cloud: AWS, Docker, Kubernetes
- Tools: Git, Jenkins, GitHub Actions

EXPERIENCE
Senior Software Engineer | Tech Corp (2020-Present)
- Developed microservices using FastAPI and Python
- Implemented CI/CD pipelines with Jenkins
- Managed cloud infrastructure on AWS

Software Engineer | StartUp Inc (2018-2020)
- Built React applications
- Worked with PostgreSQL databases
- Implemented REST APIs

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2018

CERTIFICATIONS
- AWS Certified Solutions Architect
- Docker Certified Associate
"""

SAMPLE_JD = """
Senior Full Stack Developer - Immediate Hire

We are looking for a talented Full Stack Developer to join our growing team.

REQUIRED SKILLS
- Strong proficiency in Python and JavaScript/TypeScript
- Experience with React and FastAPI
- PostgreSQL database design and optimization
- Docker and container orchestration (Kubernetes)
- AWS cloud services (EC2, S3, RDS)
- RESTful API design and implementation
- Git version control
- Microservices architecture

NICE TO HAVE
- Experience with Machine Learning frameworks (TensorFlow, PyTorch)
- GraphQL experience
- CI/CD pipeline implementation
- Agile/Scrum methodology
- Terraform for Infrastructure as Code

RESPONSIBILITIES
- Develop and maintain full-stack applications
- Design scalable database schemas
- Implement automated testing
- Collaborate with cross-functional teams
- Participate in code reviews

QUALIFICATIONS
- 5+ years of software development experience
- Strong problem-solving skills
- Communication and teamwork abilities
"""


class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []
        self.tokens: Dict[str, str] = {}
        self.analysis_ids: List[int] = []
        self.user_ids: List[int] = []
        self.session = requests.Session()
        
    def log_test(self, endpoint: str, method: str, status: str, response_code: int, 
                 details: str = "", time_ms: float = 0):
        """Log test result"""
        self.results.append({
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "response_code": response_code,
            "details": details,
            "time_ms": time_ms
        })
        
    def test_health_check(self) -> bool:
        """Test GET /api/v1/health"""
        print("\n📋 Testing Health Check Endpoint...")
        try:
            response = requests.get(f"{self.base_url}{API_VERSION}/health")
            self.log_test("/health", "GET", "✓ PASS" if response.status_code == 200 else "✗ FAIL", 
                         response.status_code, json.dumps(response.json(), indent=2))
            print(f"  ✓ Health Check: {response.status_code}")
            print(f"    Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            self.log_test("/health", "GET", "✗ FAIL", 0, str(e))
            print(f"  ✗ Health Check failed: {e}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test GET / (root)"""
        print("\n📋 Testing Root Endpoint...")
        try:
            response = requests.get(f"{self.base_url}/")
            self.log_test("/", "GET", "✓ PASS" if response.status_code == 200 else "✗ FAIL",
                         response.status_code, json.dumps(response.json(), indent=2))
            print(f"  ✓ Root Endpoint: {response.status_code}")
            print(f"    Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            self.log_test("/", "GET", "✗ FAIL", 0, str(e))
            print(f"  ✗ Root Endpoint failed: {e}")
            return False
    
    def test_user_registration(self) -> bool:
        """Test POST /api/v1/auth/register"""
        print("\n📋 Testing User Registration...")
        results = []
        for user_data in DUMMY_USERS:
            try:
                response = requests.post(
                    f"{self.base_url}{API_VERSION}/auth/register",
                    json={
                        "email": user_data["email"],
                        "name": user_data["name"],
                        "password": user_data["password"],
                        "password_confirm": user_data["confirm_password"]
                    }
                )
                
                status_text = "✓ PASS" if response.status_code in [200, 201] else "✗ FAIL"
                self.log_test("/auth/register", "POST", status_text, response.status_code,
                             f"User: {user_data['email']}")
                
                if response.status_code in [200, 201]:
                    token_data = response.json()
                    self.tokens[user_data['email']] = token_data.get('access_token')
                    print(f"  ✓ Registered: {user_data['email']} - {response.status_code}")
                    results.append(True)
                else:
                    print(f"  ✗ Registration failed: {user_data['email']} - {response.status_code}")
                    print(f"    Error: {response.text}")
                    results.append(False)
            except Exception as e:
                self.log_test("/auth/register", "POST", "✗ FAIL", 0, f"User: {user_data['email']} - {str(e)}")
                print(f"  ✗ Registration failed: {user_data['email']} - {e}")
                results.append(False)
        
        return all(results)
    
    def test_user_login(self) -> bool:
        """Test POST /api/v1/auth/login"""
        print("\n📋 Testing User Login...")
        results = []
        for user_data in DUMMY_USERS:
            try:
                response = requests.post(
                    f"{self.base_url}{API_VERSION}/auth/login",
                    json={
                        "email": user_data["email"],
                        "password": user_data["password"]
                    }
                )
                
                status_text = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
                self.log_test("/auth/login", "POST", status_text, response.status_code,
                             f"User: {user_data['email']}")
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.tokens[user_data['email']] = token_data.get('access_token')
                    print(f"  ✓ Login: {user_data['email']} - {response.status_code}")
                    results.append(True)
                else:
                    print(f"  ✗ Login failed: {user_data['email']} - {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test("/auth/login", "POST", "✗ FAIL", 0, f"User: {user_data['email']} - {str(e)}")
                print(f"  ✗ Login failed: {user_data['email']} - {e}")
                results.append(False)
        
        return all(results)
    
    def create_test_files(self) -> Tuple[BytesIO, BytesIO]:
        """Create test resume and JD files"""
        resume_file = BytesIO(SAMPLE_RESUME.encode())
        resume_file.name = "test_resume.txt"
        
        jd_file = BytesIO(SAMPLE_JD.encode())
        jd_file.name = "test_jd.txt"
        
        return resume_file, jd_file
    
    def test_analyze_endpoint(self) -> bool:
        """Test POST /api/v1/analyze"""
        print("\n📋 Testing Analysis Endpoint...")
        results = []
        
        for email, token in list(self.tokens.items())[:1]:  # Test with first user
            try:
                resume_file, jd_file = self.create_test_files()
                
                files = {
                    'resume_file': ('test_resume.txt', resume_file, 'text/plain'),
                    'jd_file': ('test_jd.txt', jd_file, 'text/plain')
                }
                
                headers = {'Authorization': f'Bearer {token}'}
                
                response = requests.post(
                    f"{self.base_url}{API_VERSION}/analyze",
                    files=files,
                    headers=headers
                )
                
                status_text = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
                self.log_test("/analyze", "POST", status_text, response.status_code,
                             f"User: {email}")
                
                if response.status_code == 200:
                    analysis_data = response.json()
                    analysis_id = analysis_data.get('analysis_id')
                    if analysis_id:
                        self.analysis_ids.append(analysis_id)
                    print(f"  ✓ Analysis: {email} - {response.status_code}")
                    print(f"    Analysis ID: {analysis_id}")
                    results.append(True)
                else:
                    print(f"  ✗ Analysis failed: {email} - {response.status_code}")
                    print(f"    Response: {response.text[:500]}")
                    results.append(False)
            except Exception as e:
                self.log_test("/analyze", "POST", "✗ FAIL", 0, f"User: {email} - {str(e)}")
                print(f"  ✗ Analysis failed: {email} - {e}")
                results.append(False)
        
        return len(self.analysis_ids) > 0
    
    def test_get_analysis(self) -> bool:
        """Test GET /api/v1/analysis/{id}"""
        print("\n📋 Testing Get Analysis Endpoint...")
        results = []
        
        if not self.analysis_ids:
            print("  ⚠ No analysis IDs available to test")
            return False
        
        for email, token in list(self.tokens.items())[:1]:
            for analysis_id in self.analysis_ids:
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    response = requests.get(
                        f"{self.base_url}{API_VERSION}/analysis/{analysis_id}",
                        headers=headers
                    )
                    
                    status_text = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
                    self.log_test(f"/analysis/{analysis_id}", "GET", status_text, 
                                 response.status_code, f"User: {email}")
                    
                    if response.status_code == 200:
                        print(f"  ✓ Get Analysis ID {analysis_id}: {response.status_code}")
                        results.append(True)
                    else:
                        print(f"  ✗ Get Analysis ID {analysis_id} failed: {response.status_code}")
                        results.append(False)
                except Exception as e:
                    self.log_test(f"/analysis/{analysis_id}", "GET", "✗ FAIL", 0, 
                                 f"User: {email} - {str(e)}")
                    print(f"  ✗ Get Analysis ID {analysis_id} failed: {e}")
                    results.append(False)
        
        return len(results) > 0 and any(results)
    
    def test_get_user_analyses(self) -> bool:
        """Test GET /api/v1/users/{user_id}/analyses"""
        print("\n📋 Testing Get User Analyses Endpoint...")
        results = []
        
        # Note: We need user IDs, which we'll have to extract from responses
        # For now, we'll test with a dummy ID
        test_user_id = 1
        
        for email, token in list(self.tokens.items())[:1]:
            try:
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(
                    f"{self.base_url}{API_VERSION}/users/{test_user_id}/analyses",
                    headers=headers,
                    params={"skip": 0, "limit": 10}
                )
                
                status_text = "✓ PASS" if response.status_code == 200 else "✗ FAIL"
                self.log_test(f"/users/{test_user_id}/analyses", "GET", status_text,
                             response.status_code, f"User: {email}")
                
                if response.status_code == 200:
                    analyses_data = response.json()
                    print(f"  ✓ Get User Analyses: {response.status_code}")
                    print(f"    Total analyses: {analyses_data.get('total', 0)}")
                    results.append(True)
                else:
                    print(f"  ✗ Get User Analyses failed: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log_test(f"/users/{test_user_id}/analyses", "GET", "✗ FAIL", 0,
                             f"User: {email} - {str(e)}")
                print(f"  ✗ Get User Analyses failed: {e}")
                results.append(False)
        
        return len(results) > 0
    
    def run_all_tests(self) -> None:
        """Run all API tests"""
        print("\n" + "="*60)
        print("🚀 STARTING COMPREHENSIVE API TESTING")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test basic endpoints
        self.test_root_endpoint()
        self.test_health_check()
        
        # Test authentication
        self.test_user_registration()
        self.test_user_login()
        
        # Test main endpoints
        self.test_analyze_endpoint()
        self.test_get_analysis()
        self.test_get_user_analyses()
        
        print("\n" + "="*60)
        print("✅ TESTING COMPLETE")
        print("="*60)
        
    def generate_html_report(self, filename: str = "api_test_report.html") -> str:
        """Generate HTML report of all tests"""
        
        passed = len([r for r in self.results if "PASS" in r['status']])
        failed = len([r for r in self.results if "FAIL" in r['status']])
        total = len(self.results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Test Report - AI Adaptive Onboarding Engine</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .summary-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .summary-card.pass .value {{
            color: #28a745;
        }}
        
        .summary-card.fail .value {{
            color: #dc3545;
        }}
        
        .summary-card.rate .value {{
            color: #007bff;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        
        table thead {{
            background: #f8f9fa;
        }}
        
        table th {{
            padding: 15px;
            text-align: left;
            color: #333;
            font-weight: 600;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        table tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-pass {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .method-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: 600;
        }}
        
        .method-get {{
            background: #cfe9ff;
            color: #004085;
        }}
        
        .method-post {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .method-put {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .method-delete {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .endpoint {{
            font-family: 'Courier New', monospace;
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 4px;
            color: #d63384;
        }}
        
        .time {{
            color: #999;
            font-size: 0.85em;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
            color: #666;
        }}
        
        .test-details {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }}
        
        .test-details pre {{
            background: white;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.85em;
            line-height: 1.4;
        }}
        
        .chart-container {{
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            flex-wrap: wrap;
        }}
        
        .chart {{
            text-align: center;
            flex: 1;
            min-width: 200px;
            padding: 20px;
        }}
        
        .pie {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            margin: 0 auto 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 API Test Report</h1>
            <p>AI Adaptive Onboarding Engine Backend</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="value">{total}</div>
            </div>
            <div class="summary-card pass">
                <h3>Passed</h3>
                <div class="value">{passed}</div>
            </div>
            <div class="summary-card fail">
                <h3>Failed</h3>
                <div class="value">{failed}</div>
            </div>
            <div class="summary-card rate">
                <h3>Pass Rate</h3>
                <div class="value">{pass_rate:.1f}%</div>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">📊 Test Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Endpoint</th>
                        <th>Method</th>
                        <th>Status</th>
                        <th>Response Code</th>
                        <th>Details</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for result in self.results:
            status_class = "status-pass" if "PASS" in result['status'] else "status-fail"
            method_class = f"method-{result['method'].lower()}"
            
            html_content += f"""
                    <tr>
                        <td><span class="endpoint">{result['endpoint']}</span></td>
                        <td><span class="method-badge {method_class}">{result['method']}</span></td>
                        <td><span class="status-badge {status_class}">{result['status']}</span></td>
                        <td>{result['response_code']}</td>
                        <td>{result['details']}</td>
                        <td class="time">{result['time_ms']}ms</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
            
            <div class="test-details">
                <h3>📋 Summary</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
"""
        
        # Add summary information
        if passed == total and total > 0:
            html_content += f"<li>✅ All {total} tests passed successfully!</li>"
        else:
            html_content += f"<li>⚠️ {failed} out of {total} tests failed</li>"
        
        html_content += f"""
                    <li>Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                    <li>Base URL: {self.base_url}</li>
                    <li>API Version: /api/v1</li>
"""
        
        html_content += """
                </ul>
            </div>
            
            <div class="test-details">
                <h3>🔍 Endpoints Tested</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><code>GET /</code> - Root endpoint</li>
                    <li><code>GET /api/v1/health</code> - Health check</li>
                    <li><code>POST /api/v1/auth/register</code> - User registration</li>
                    <li><code>POST /api/v1/auth/login</code> - User login</li>
                    <li><code>POST /api/v1/analyze</code> - Resume & JD analysis</li>
                    <li><code>GET /api/v1/analysis/{id}</code> - Get analysis</li>
                    <li><code>GET /api/v1/users/{user_id}/analyses</code> - List user analyses</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>AI Adaptive Onboarding Engine | Backend Testing Suite</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Write to file
        filepath = f"{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath


def main():
    """Main execution function"""
    tester = APITester(BASE_URL)
    
    # Run all tests
    tester.run_all_tests()
    
    # Generate report
    report_file = tester.generate_html_report(
        "api_test_report.html"
    )
    print(f"\n📄 Report generated: {report_file}")
    
    # Print summary
    passed = len([r for r in tester.results if "PASS" in r['status']])
    failed = len([r for r in tester.results if "FAIL" in r['status']])
    total = len(tester.results)
    
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Pass Rate: {(passed/total*100):.1f}%")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
