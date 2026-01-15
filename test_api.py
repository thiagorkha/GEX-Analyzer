#!/usr/bin/env python
"""
Simple API Test Script for GEX Analyzer
"""

import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Test imports
try:
    from app import app, create_app
    print("✅ App imported successfully")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    sys.exit(1)

# Create test client
app_instance = create_app() if callable(create_app) else app
client = app_instance.test_client()

print("\n" + "="*60)
print("Testing GEX Analyzer API")
print("="*60)

# Test 1: Health check
print("\n1️⃣  Testing /api/health...")
try:
    response = client.get('/api/health')
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Examples
print("\n2️⃣  Testing /api/examples...")
try:
    response = client.get('/api/examples')
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Received {len(data)} examples")
    if data:
        print(f"   First example keys: {list(data[0].keys())}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Analysis
print("\n3️⃣  Testing /api/analyze...")
try:
    test_payload = {
        "current_price": 100.0,
        "expiration_date": "2024-02-16",
        "options": [
            {"ticker": "SPY", "tipo": "CALL", "strike": 100.0, "gamma": 0.28, "oi": 12000},
            {"ticker": "SPY", "tipo": "PUT", "strike": 100.0, "gamma": 0.15, "oi": 4000},
            {"ticker": "SPY", "tipo": "CALL", "strike": 102.0, "gamma": 0.20, "oi": 8000},
            {"ticker": "SPY", "tipo": "PUT", "strike": 98.0, "gamma": 0.18, "oi": 6000}
        ]
    }
    
    print(f"   Payload: {json.dumps(test_payload, indent=2)[:200]}...")
    
    response = client.post(
        '/api/analyze',
        data=json.dumps(test_payload),
        content_type='application/json'
    )
    
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    
    if response.status_code == 200:
        print(f"   ✅ Success!")
        print(f"   Keys in response: {list(data.keys())}")
        if 'total_gex' in data:
            print(f"   Total GEX: {data['total_gex']}")
        if 'strikes' in data:
            print(f"   Strikes analyzed: {len(data['strikes'])}")
    else:
        print(f"   ❌ Error: {data}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test Complete")
print("="*60)
