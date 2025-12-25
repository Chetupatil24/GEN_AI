#!/usr/bin/env python3
"""Complete system test to verify all components are working."""

import requests
import json
import sys

def test_system():
    """Run comprehensive system tests."""
    base_url = "http://localhost:8000"
    print("🧪 Running Complete System Tests\n")
    print("=" * 60)

    tests_passed = 0
    tests_total = 0

    # Test 1: Health Check
    tests_total += 1
    print("\n1. Testing Health Check...")
    try:
        r = requests.get(f"{base_url}/healthz", timeout=5)
        if r.status_code == 200 and r.json().get("status") == "ok":
            print("   ✅ Health check passed")
            tests_passed += 1
        else:
            print(f"   ❌ Health check failed: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")

    # Test 2: Banuba Filters
    tests_total += 1
    print("\n2. Testing Banuba Filters Endpoint...")
    try:
        r = requests.get(f"{base_url}/api/banuba-filters", timeout=5)
        if r.status_code == 200:
            data = r.json()
            filters = data.get("filters", [])
            print(f"   ✅ Banuba filters working ({len(filters)} filters available)")
            for f in filters:
                print(f"      - {f['name']}: {f['description'][:50]}...")
            tests_passed += 1
        else:
            print(f"   ❌ Banuba filters failed: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Banuba filters error: {e}")

    # Test 3: API Documentation
    tests_total += 1
    print("\n3. Testing API Documentation...")
    try:
        r = requests.get(f"{base_url}/docs", timeout=5)
        if r.status_code == 200:
            print("   ✅ API docs accessible")
            tests_passed += 1
        else:
            print(f"   ❌ API docs failed: {r.status_code}")
    except Exception as e:
        print(f"   ❌ API docs error: {e}")

    # Test 4: OpenAPI Schema
    tests_total += 1
    print("\n4. Testing OpenAPI Schema...")
    try:
        r = requests.get(f"{base_url}/openapi.json", timeout=5)
        if r.status_code == 200:
            schema = r.json()
            endpoints = list(schema.get("paths", {}).keys())
            print(f"   ✅ OpenAPI schema valid ({len(endpoints)} endpoints)")
            tests_passed += 1
        else:
            print(f"   ❌ OpenAPI schema failed: {r.status_code}")
    except Exception as e:
        print(f"   ❌ OpenAPI schema error: {e}")

    # Test 5: Backend Connection Test
    tests_total += 1
    print("\n5. Testing Backend Connection Endpoint...")
    try:
        r = requests.get(f"{base_url}/api/test-backend-connection", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"   ✅ Backend connection test working")
            print(f"      Status: {data.get('status')}")
            print(f"      Message: {data.get('message')}")
            tests_passed += 1
        else:
            print(f"   ❌ Backend connection test failed: {r.status_code}")
    except Exception as e:
        print(f"   ❌ Backend connection test error: {e}")

    # Test 6: Check Dependencies
    tests_total += 1
    print("\n6. Testing Python Dependencies...")
    try:
        import torch
        import torchvision
        import cv2
        import redis
        print(f"   ✅ All ML dependencies installed")
        print(f"      PyTorch: {torch.__version__}")
        print(f"      Torchvision: {torchvision.__version__}")
        print(f"      OpenCV: {cv2.__version__}")
        tests_passed += 1
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")

    # Test 7: Redis Connection
    tests_total += 1
    print("\n7. Testing Redis Connection...")
    try:
        import redis as redis_lib
        r = redis_lib.Redis.from_url("redis://localhost:6379/0")
        if r.ping():
            print("   ✅ Redis connection successful")
            info = r.info("server")
            print(f"      Redis version: {info.get('redis_version')}")
            tests_passed += 1
        else:
            print("   ❌ Redis ping failed")
    except Exception as e:
        print(f"   ❌ Redis connection error: {e}")

    # Summary
    print("\n" + "=" * 60)
    print(f"\n📊 Test Summary: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n🎉 All tests passed! System is fully operational!")
        return 0
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(test_system())
