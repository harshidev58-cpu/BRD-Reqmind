#!/usr/bin/env python3
"""Test script for Alignment Intelligence Engine."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_low_risk_scenario():
    """Test scenario with good alignment (LOW risk)."""
    print_section("TEST 1: LOW RISK - Good Alignment")
    
    data = {
        "projectName": "Well-Aligned Project",
        "emailText": "We need a web application with user authentication by June 15.",
        "slackText": "Agreed on the web app with auth. June 15 deadline works for everyone.",
        "meetingText": "Team consensus: web application, authentication module, June 15 delivery."
    }
    
    response = requests.post(f"{BASE_URL}/generate_brd_with_alignment", json=data)
    result = response.json()
    
    alignment = result['alignment_analysis']
    print(f"✅ Alignment Score: {alignment['alignment_score']}")
    print(f"✅ Risk Level: {alignment['risk_level']}")
    print(f"✅ Alert: {alignment['alert']}")
    print(f"\nComponent Scores:")
    for key, value in alignment['component_scores'].items():
        print(f"  - {key}: {value}")

def test_medium_risk_scenario():
    """Test scenario with some misalignment (MEDIUM risk)."""
    print_section("TEST 2: MEDIUM RISK - Some Misalignment")
    
    data = {
        "projectName": "Partially Aligned Project",
        "emailText": "We need delivery by March 30 for Q1 release.",
        "slackText": "The team thinks April 10 is more realistic given the scope.",
        "meetingText": "Let's target early April for delivery to be safe."
    }
    
    response = requests.post(f"{BASE_URL}/generate_brd_with_alignment", json=data)
    result = response.json()
    
    alignment = result['alignment_analysis']
    print(f"⚠️  Alignment Score: {alignment['alignment_score']}")
    print(f"⚠️  Risk Level: {alignment['risk_level']}")
    print(f"⚠️  Alert: {alignment['alert']}")
    print(f"\nTimeline Mismatches: {len(alignment['timeline_mismatches'])}")
    for mismatch in alignment['timeline_mismatches']:
        print(f"  - {mismatch['description']}")

def test_high_risk_scenario():
    """Test scenario with major conflicts (HIGH risk)."""
    print_section("TEST 3: HIGH RISK - Major Conflicts")
    
    data = {
        "projectName": "Conflicting Requirements",
        "emailText": "URGENT: Need simple, basic MVP by March 1. Keep it minimal and low priority for now.",
        "slackText": "I disagree - we need a complex, advanced system with all features. This is not urgent, let's take time and deliver by June.",
        "meetingText": "Client changed their mind again. Now they want immediate delivery but keep adding features. Scope changes every week. Actually, let's revert to the original plan."
    }
    
    response = requests.post(f"{BASE_URL}/generate_brd_with_alignment", json=data)
    result = response.json()
    
    alignment = result['alignment_analysis']
    print(f"🚨 Alignment Score: {alignment['alignment_score']}")
    print(f"🚨 Risk Level: {alignment['risk_level']}")
    print(f"🚨 Alert: {alignment['alert']}")
    
    print(f"\nConflicts Detected: {len(alignment['conflicts'])}")
    for conflict in alignment['conflicts']:
        print(f"\n  Type: {conflict['type']}")
        print(f"  Severity: {conflict['severity']}")
        print(f"  Description: {conflict['description']}")
        print(f"  Sources: {', '.join(conflict['sources'])}")
        print(f"  Recommendation: {conflict['recommendation']}")
    
    print(f"\nTimeline Mismatches: {len(alignment['timeline_mismatches'])}")
    for mismatch in alignment['timeline_mismatches']:
        print(f"  - {mismatch['description']}")
    
    print(f"\nRequirement Volatility:")
    vol = alignment['requirement_volatility']
    print(f"  - Changes: {vol['change_count']}")
    print(f"  - Stability: {vol['stability_percentage']}%")
    print(f"  - Change Sources: {', '.join(vol['change_sources'])}")

def test_reqmind_example():
    """Test the exact example from ReqMind AI requirements."""
    print_section("TEST 4: ReqMind AI Example - PM vs Client Timeline")
    
    data = {
        "projectName": "ReqMind AI - Alignment Intelligence Pipeline",
        "slackText": "PM: Delivery by March 30. This is critical for Q1 release.",
        "emailText": "Client: Need delivery by April 10. We have internal reviews that week."
    }
    
    response = requests.post(f"{BASE_URL}/generate_brd_with_alignment", json=data)
    result = response.json()
    
    alignment = result['alignment_analysis']
    print(f"Alignment Score: {alignment['alignment_score']}")
    print(f"Risk Level: {alignment['risk_level']}")
    print(f"Alert: {alignment['alert']}")
    
    print(f"\nTimeline Mismatch Detected:")
    for mismatch in alignment['timeline_mismatches']:
        print(f"  Source 1 ({mismatch['source1']}): {', '.join(mismatch['dates1'])}")
        print(f"  Source 2 ({mismatch['source2']}): {', '.join(mismatch['dates2'])}")
        print(f"  Description: {mismatch['description']}")
    
    print(f"\nComponent Scores:")
    for key, value in alignment['component_scores'].items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  ReqMind AI - Alignment Intelligence Engine Test Suite")
    print("="*80)
    
    try:
        test_low_risk_scenario()
        test_medium_risk_scenario()
        test_high_risk_scenario()
        test_reqmind_example()
        
        print("\n" + "="*80)
        print("  ✅ All Tests Completed Successfully!")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server at http://127.0.0.1:8000")
        print("Make sure the server is running with: uvicorn app.main:app --reload\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")