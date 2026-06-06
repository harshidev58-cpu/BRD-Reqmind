#!/usr/bin/env python3
"""Test script to demonstrate dataset-based BRD generation features."""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_dataset_status():
    """Test dataset configuration status."""
    print("🔍 Testing dataset status...")
    response = requests.get(f"{BASE_URL}/dataset/dataset_status")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_regular_brd_generation():
    """Test regular BRD generation."""
    print("📝 Testing regular BRD generation...")
    data = {
        "projectName": "Regular API Test",
        "emailText": "We need a simple web application with user authentication"
    }
    response = requests.post(f"{BASE_URL}/generate_brd", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Project: {result['projectName']}")
        print(f"Requirements: {len(result['requirements'])}")
        print(f"Stakeholders: {len(result['stakeholders'])}")
    else:
        print(response.text)
    print()

def test_dataset_brd_generation():
    """Test dataset-based BRD generation."""
    print("📊 Testing dataset-based BRD generation...")
    data = {
        "projectName": "Trading System from Dataset",
        "keywords": ["trading", "system", "security"],
        "sampleSize": 15
    }
    response = requests.post(f"{BASE_URL}/dataset/generate_brd_from_dataset", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Project: {result['projectName']}")
        print(f"Requirements: {len(result['requirements'])}")
        print(f"Stakeholders: {len(result['stakeholders'])}")
        print(f"Email count: {result['metadata']['email_count']}")
        print(f"Meeting count: {result['metadata']['meeting_count']}")
        print(f"Conflicts detected: {len(result['conflicts'])}")
        
        # Show first few requirements
        print("\nSample Requirements:")
        for req in result['requirements'][:3]:
            print(f"  - {req['id']}: {req['description']} ({req['priority']})")
    else:
        print(response.text)
    print()

def test_keyword_filtering():
    """Test keyword filtering."""
    print("🔍 Testing keyword filtering...")
    data = {
        "projectName": "Security Focused Project",
        "keywords": ["security", "authentication", "encryption"],
        "sampleSize": 10
    }
    response = requests.post(f"{BASE_URL}/dataset/generate_brd_from_dataset", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Filtered emails: {result['metadata']['email_count']}")
        print(f"Keywords used: {result['metadata']['keywords_used']}")
    else:
        print(response.text)
    print()

if __name__ == "__main__":
    print("🚀 BRD Generator Dataset Features Test\n")
    
    try:
        test_dataset_status()
        test_regular_brd_generation()
        test_dataset_brd_generation()
        test_keyword_filtering()
        print("✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure it's running on http://127.0.0.1:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)