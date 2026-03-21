#!/usr/bin/env python3
"""
Comprehensive API Test - Tests all fixed endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def test_endpoints():
    """Test all endpoints and generate report"""
    
    results = {
        "passed": [],
        "failed": [],
        "errors": []
    }
    
    print("\n" + "="*80)
    print("COMPREHENSIVE API ENDPOINT TEST")
    print("="*80)
    print(f"Server: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ============ HEALTH ENDPOINTS ============
    print("[1] Testing Health Endpoints...")
    try:
        # Root
        r = requests.get(f"{BASE_URL}/", timeout=5)
        status = "PASS" if r.status_code == 200 else "FAIL"
        results["passed" if r.status_code == 200 else "failed"].append(f"[GET /] → {r.status_code}")
        print(f"  [GET /] → {r.status_code} [{status}]")
        
        # Health
        r = requests.get(f"{BASE_URL}{API_PREFIX}/health", timeout=5)
        status = "PASS" if r.status_code == 200 else "FAIL"
        results["passed" if r.status_code == 200 else "failed"].append(f"[GET {API_PREFIX}/health] → {r.status_code}")
        print(f"  [GET {API_PREFIX}/health] → {r.status_code} [{status}]")
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        results["errors"].append(f"Health endpoints: {str(e)}")
    
    # ============ AUTHENTICATION ENDPOINTS ============
    print("\n[2] Testing Authentication Endpoints...")
    access_token = None
    try:
        # Register
        register_data = {
            "email": f"test_{int(datetime.now().timestamp())}@example.com",
            "name": "Test User",
            "password": "TestPassword@123456",
            "confirm_password": "TestPassword@123456"
        }
        r = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=register_data, timeout=5)
        status = "PASS" if r.status_code == 201 else "FAIL"
        results["passed" if r.status_code == 201 else "failed"].append(f"[POST {API_PREFIX}/auth/register] → {r.status_code}")
        print(f"  [POST {API_PREFIX}/auth/register] → {r.status_code} [{status}]")
        
        if r.status_code == 201:
            access_token = r.json().get("access_token")
            print(f"    → Token obtained: {access_token[:30]}...")
        
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        r = requests.post(f"{BASE_URL}{API_PREFIX}/auth/login", json=login_data, timeout=5)
        status = "PASS" if r.status_code == 200 else "FAIL"
        results["passed" if r.status_code == 200 else "failed"].append(f"[POST {API_PREFIX}/auth/login] → {r.status_code}")
        print(f"  [POST {API_PREFIX}/auth/login] → {r.status_code} [{status}]")
        
        if r.status_code == 200 and not access_token:
            access_token = r.json().get("access_token")
        
        # Protected endpoints (if we have a token)
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get current user
            r = requests.get(f"{BASE_URL}{API_PREFIX}/auth/me", headers=headers, timeout=5)
            status = "PASS" if r.status_code == 200 else "FAIL"
            results["passed" if r.status_code == 200 else "failed"].append(f"[GET {API_PREFIX}/auth/me] → {r.status_code}")
            print(f"  [GET {API_PREFIX}/auth/me] → {r.status_code} [{status}]")
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        results["errors"].append(f"Auth endpoints: {str(e)}")
    
    # ============ ANALYSIS ENDPOINTS ============
    print("\n[3] Testing Analysis Endpoints...")
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            # Create analysis
            analysis_data = {
                "resume_text": "John Doe - Python Engineer with 5 years experience",
                "job_description": "Senior Python Engineer needed - FastAPI, PostgreSQL required"
            }
            r = requests.post(f"{BASE_URL}{API_PREFIX}/analyze", json=analysis_data, headers=headers, timeout=5)
            status = "PASS" if r.status_code == 201 else "FAIL"
            results["passed" if r.status_code == 201 else "failed"].append(f"[POST {API_PREFIX}/analyze] → {r.status_code}")
            print(f"  [POST {API_PREFIX}/analyze] → {r.status_code} [{status}]")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results["errors"].append(f"Analysis endpoints: {str(e)}")
    else:
        print("  SKIPPED (no authentication token)")
    
    # ============ BULK OPERATIONS ============
    print("\n[4] Testing Bulk Operations Endpoints...")
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            bulk_data = {
                "analyses": [
                    {
                        "resume_text": "Jane Doe - Data Scientist",
                        "job_description": "Data Scientist needed - ML, Python required"
                    }
                ],
                "fail_mode": "partial"
            }
            r = requests.post(f"{BASE_URL}{API_PREFIX}/bulk/analyses/create", json=bulk_data, headers=headers, timeout=5)
            status = "PASS" if r.status_code in [200, 201] else "FAIL"
            results["passed" if r.status_code in [200, 201] else "failed"].append(f"[POST {API_PREFIX}/bulk/analyses/create] → {r.status_code}")
            print(f"  [POST {API_PREFIX}/bulk/analyses/create] → {r.status_code} [{status}]")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results["errors"].append(f"Bulk endpoints: {str(e)}")
    else:
        print("  SKIPPED (no authentication token)")
    
    # ============ METRICS ENDPOINTS ============
    print("\n[5] Testing Metrics Endpoints...")
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            r = requests.get(f"{BASE_URL}{API_PREFIX}/metrics/system", headers=headers, timeout=5)
            status = "PASS" if r.status_code == 200 else "FAIL"
            results["passed" if r.status_code == 200 else "failed"].append(f"[GET {API_PREFIX}/metrics/system] → {r.status_code}")
            print(f"  [GET {API_PREFIX}/metrics/system] → {r.status_code} [{status}]")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results["errors"].append(f"Metrics endpoints: {str(e)}")
    else:
        print("  SKIPPED (no authentication token)")
    
    # ============ LLM ENDPOINTS ============
    print("\n[6] Testing LLM Endpoints...")
    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            llm_data = {
                "analysis_id": 1,
                "skill_gap": "Docker",
                "current_level": "beginner",
                "target_level": "intermediate"
            }
            r = requests.post(f"{BASE_URL}{API_PREFIX}/llm/generate-learning-path", json=llm_data, headers=headers, timeout=5)
            status = "PASS" if r.status_code in [200, 201] else "FAIL"
            results["passed" if r.status_code in [200, 201] else "failed"].append(f"[POST {API_PREFIX}/llm/generate-learning-path] → {r.status_code}")
            print(f"  [POST {API_PREFIX}/llm/generate-learning-path] → {r.status_code} [{status}]")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results["errors"].append(f"LLM endpoints: {str(e)}")
    else:
        print("  SKIPPED (no authentication token)")
    
    # ============ SUMMARY ============
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed_count = len(results["passed"])
    failed_count = len(results["failed"])
    total = passed_count + failed_count
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed_count} ✓")
    print(f"Failed: {failed_count} ✗")
    if results["errors"]:
        print(f"Errors: {len(results['errors'])}")
    
    if total > 0:
        percentage = (passed_count / total) * 100
        print(f"Pass Rate: {percentage:.1f}%")
    
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)
    
    if results["passed"]:
        print("\n✓ PASSED:")
        for item in results["passed"]:
            print(f"  {item}")
    
    if results["failed"]:
        print("\n✗ FAILED:")
        for item in results["failed"]:
            print(f"  {item}")
    
    if results["errors"]:
        print("\n⚠ ERRORS:")
        for item in results["errors"]:
            print(f"  {item}")
    
    print("\n" + "="*80 + "\n")
    
    return results

if __name__ == "__main__":
    try:
        results = test_endpoints()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
