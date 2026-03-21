#!/usr/bin/env python3
"""
Simple API Endpoint Testing Script - Tests all endpoints without code modifications
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import time

BASE_URL = "http://localhost:8000"
API_VERSION = "/api/v1"

class TestRunner:
    def __init__(self):
        self.results = []
        self.access_token = None
        self.user_id = None
        self.analysis_id = None
        
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                     headers: Dict = None, expected_status: int = 200) -> Dict:
        """Test a single endpoint"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                response = requests.request(method, url, json=data, headers=headers, timeout=10)
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "expected": expected_status,
                "success": response.status_code == expected_status,
                "response": str(response_data)[:200] if response_data else "",
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            status_symbol = "[PASS]" if result["success"] else "[FAIL]"
            print(f"{status_symbol} [{method:6s}] {endpoint:50s} | Status: {response.status_code} (expected {expected_status})")
            
            return result
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": None,
                "expected": expected_status,
                "success": False,
                "response": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            print(f"[FAIL] [{method:6s}] {endpoint:50s} | ERROR: {str(e)[:50]}")
        if result["success"] and "access_token" in str(result["response"]):
            try:
                resp = requests.post(f"{BASE_URL}{API_VERSION}/auth/register", 
                                    json=register_data, timeout=10)
                self.access_token = resp.json().get("access_token")
                print(f"✓ Token obtained: {self.access_token[:30]}...")
            except:
                pass
        
        # Login
        if register_data["email"]:
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            result = self.test_endpoint("POST", f"{API_VERSION}/auth/login",
                                       data=login_data, expected_status=200)
            if result["success"]:
                try:
                    resp = requests.post(f"{BASE_URL}{API_VERSION}/auth/login",
                                        json=login_data, timeout=10)
                    self.access_token = resp.json().get("access_token")
                except:
                    pass
        
        # Get current user
        self.test_endpoint("GET", f"{API_VERSION}/auth/me",
                         headers=self.get_auth_headers(), expected_status=200)
        
        # Refresh token (may fail without valid token)
        refresh_data = {"refresh_token": "dummy"}
        self.test_endpoint("POST", f"{API_VERSION}/auth/refresh",
                         data=refresh_data, headers=self.get_auth_headers())
        
        # Change password
        pwd_data = {
            "old_password": register_data["password"],
            "new_password": "NewPwd@456",
            "confirm_password": "NewPwd@456"
        }
        self.test_endpoint("POST", f"{API_VERSION}/auth/change-password",
                         data=pwd_data, headers=self.get_auth_headers())
        
        # Update profile
        profile_data = {"name": "Updated User"}
        self.test_endpoint("PUT", f"{API_VERSION}/auth/me",
                         data=profile_data, headers=self.get_auth_headers())
    
    def run_analysis_tests(self):
        """Test analysis endpoints"""
        print("\n" + "="*90)
        print("ANALYSIS ENDPOINTS")
        print("="*90)
        
        # Create analysis
        analysis_data = {
            "resume_text": "John Doe - Python Engineer with 5 years experience",
            "job_description": "Senior Python Engineer needed - FastAPI, PostgreSQL required"
        }
        result = self.test_endpoint("POST", f"{API_VERSION}/analyze",
                                  data=analysis_data, 
                                  headers=self.get_auth_headers(), expected_status=201)
        
        if result["success"]:
            try:
                resp = requests.post(f"{BASE_URL}{API_VERSION}/analyze",
                                    json=analysis_data,
                                    headers=self.get_auth_headers(), timeout=10)
                self.analysis_id = resp.json().get("id", 1)
            except:
                self.analysis_id = 1
        
        # Get analysis
        if self.analysis_id:
            self.test_endpoint("GET", f"{API_VERSION}/analysis/{self.analysis_id}",
                             headers=self.get_auth_headers(), expected_status=200)
        
        # List user analyses
        self.test_endpoint("GET", f"{API_VERSION}/users/1/analyses",
                         headers=self.get_auth_headers(), expected_status=200)
    
    def run_admin_tests(self):
        """Test admin endpoints"""
        print("\n" + "="*90)
        print("ADMIN ENDPOINTS")
        print("="*90)
        
        # List users
        self.test_endpoint("GET", f"{API_VERSION}/admin/users",
                         headers=self.get_auth_headers(), expected_status=200)
        
        # Get user details
        self.test_endpoint("GET", f"{API_VERSION}/admin/users/1",
                         headers=self.get_auth_headers(), expected_status=200)
        
        # Update user role (may fail)
        role_data = {"role": "analyst"}
        self.test_endpoint("PUT", f"{API_VERSION}/admin/users/2/role",
                         data=role_data, headers=self.get_auth_headers())
        
        # Deactivate user (may fail)
        self.test_endpoint("PUT", f"{API_VERSION}/admin/users/2/deactivate",
                         data={}, headers=self.get_auth_headers())
        
        # Activate user (may fail)
        self.test_endpoint("PUT", f"{API_VERSION}/admin/users/2/activate",
                         data={}, headers=self.get_auth_headers())
        
        # Delete user (may fail)
        self.test_endpoint("DELETE", f"{API_VERSION}/admin/users/3",
                         headers=self.get_auth_headers())
    
    def run_bulk_tests(self):
        """Test bulk operation endpoints"""
        print("\n" + "="*90)
        print("BULK OPERATION ENDPOINTS")
        print("="*90)
        
        # Bulk create analyses
        bulk_data = {
            "analyses": [
                {
                    "resume_text": "Jane Doe - Data Scientist",
                    "job_description": "Data Scientist needed - ML, Python required"
                }
            ],
            "fail_mode": "partial"
        }
        self.test_endpoint("POST", f"{API_VERSION}/bulk/analyses/create",
                         data=bulk_data, headers=self.get_auth_headers(), expected_status=200)
        
        # Bulk update analyses
        self.test_endpoint("POST", f"{API_VERSION}/bulk/analyses/update",
                         data={"updates": [], "fail_mode": "partial"},
                         headers=self.get_auth_headers(), expected_status=200)
        
        # Bulk delete analyses
        self.test_endpoint("POST", f"{API_VERSION}/bulk/analyses/delete",
                         data={"ids": [1], "fail_mode": "partial"},
                         headers=self.get_auth_headers(), expected_status=200)
    
    def run_metrics_tests(self):
        """Test metrics endpoints"""
        print("\n" + "="*90)
        print("METRICS ENDPOINTS")
        print("="*90)
        
        # User metrics
        self.test_endpoint("GET", f"{API_VERSION}/metrics/user/1",
                         headers=self.get_auth_headers(), expected_status=200)
        
        # System metrics
        self.test_endpoint("GET", f"{API_VERSION}/metrics/system",
                         headers=self.get_auth_headers(), expected_status=200)
    
    def run_llm_tests(self):
        """Test LLM endpoints"""
        print("\n" + "="*90)
        print("LLM ENDPOINTS")
        print("="*90)
        
        llm_data = {
            "analysis_id": 1,
            "skill_gap": "Docker",
            "current_level": "beginner",
            "target_level": "intermediate"
        }
        self.test_endpoint("POST", f"{API_VERSION}/llm/generate-learning-path",
                         data=llm_data, headers=self.get_auth_headers())
    
    def generate_report(self):
        """Generate HTML report"""
        passed = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - passed
        
        html = f"""
<html>
<head>
    <title>API Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        * {{ font-family: Segoe UI, Arial, sans-serif; }}
        body {{ margin: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .summary-card .value {{ font-size: 2.5em; font-weight: bold; }}
        .pass {{ color: #27ae60; }}
        .fail {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; background: white; margin-bottom: 30px; }}
        thead {{ background: #2c3e50; color: white; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f8f9fa; }}
        .pass-row {{ border-left: 4px solid #27ae60; }}
        .fail-row {{ border-left: 4px solid #e74c3c; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ API Endpoint Test Report</h1>
        <p>AI Adaptive Onboarding Engine - Backend Testing</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>Total Tests</h3>
            <div class="value">{len(self.results)}</div>
        </div>
        <div class="summary-card">
            <h3>Passed ✓</h3>
            <div class="value pass">{passed}</div>
        </div>
        <div class="summary-card">
            <h3>Failed ✗</h3>
            <div class="value fail">{failed}</div>
        </div>
        <div class="summary-card">
            <h3>Pass Rate</h3>
            <div class="value">{(passed/len(self.results)*100 if self.results else 0):.1f}%</div>
        </div>
    </div>
    
    <h2 style="color: #2c3e50; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px;">Detailed Results</h2>
    <table>
        <thead>
            <tr>
                <th style="width: 5%;">Status</th>
                <th style="width: 10%;">Method</th>
                <th style="width: 40%;">Endpoint</th>
                <th style="width: 10%;">Status Code</th>
                <th style="width: 35%;">Response</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for result in self.results:
            row_class = "pass-row" if result["success"] else "fail-row"
            status_symbol = "✓" if result["success"] else "✗"
            html += f"""
            <tr class="{row_class}">
                <td><strong>{status_symbol}</strong></td>
                <td><code>{result['method']}</code></td>
                <td><code>{result['endpoint']}</code></td>
                <td>{result['status_code'] or 'ERROR'}</td>
                <td><small>{result['response']}</small></td>
            </tr>
"""
        
        html += """
        </tbody>
    </table>
    
    <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 30px;">
        <h3>Test Coverage</h3>
        <ul>
            <li>✓ Health & Root Endpoints (2 tests)</li>
            <li>✓ Authentication Endpoints (7 tests)</li>
            <li>✓ Analysis Endpoints (3 tests)</li>
            <li>✓ Admin Endpoints (6 tests)</li>
            <li>✓ Bulk Operations (3 tests)</li>
            <li>✓ Metrics Endpoints (2 tests)</li>
            <li>✓ LLM Endpoints (1 test)</li>
        </ul>
    </div>
</body>
</html>
"""
        return html
    
    def run_all(self):
        """Run all tests"""
        print("\n" + "="*90)
        print("STARTING COMPREHENSIVE API ENDPOINT TESTING")
        print("="*90)
        print(f"Server: {BASE_URL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.run_health_tests()
        self.run_auth_tests()
        self.run_analysis_tests()
        self.run_admin_tests()
        self.run_bulk_tests()
        self.run_metrics_tests()
        self.run_llm_tests()
        
        # Generate report
        html = self.generate_report()
        
        # Save report
        with open("api_test_report.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # Print summary
        passed = sum(1 for r in self.results if r["success"])
        print("\n" + "="*90)
        print(f"TEST COMPLETE: {passed}/{len(self.results)} tests passed")
        print("="*90)
        print(f"✓ Report saved to: api_test_report.html\n")

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all()
