#!/usr/bin/env python3
"""
Debug script to identify the exact cause of the 400 Bad Request error.
"""

import requests
from io import BytesIO
from PIL import Image, ImageDraw
import json

def create_simple_image():
    """Create a very simple, small test image."""
    img = Image.new('RGB', (200, 150), 'white')
    draw = ImageDraw.Draw(img)
    
    # Simple rectangle
    draw.rectangle([10, 10, 190, 140], outline='black', width=2)
    draw.text((20, 20), "TEST", fill='black')
    
    return img

def test_endpoints_step_by_step():
    """Test each step to identify where the issue occurs."""
    print("🔍 Debugging Canvas Smith API - Step by Step")
    print("=" * 60)
    
    # Step 1: Test basic health endpoint
    print("1️⃣ Testing basic health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"   ✅ Health endpoint: {response.status_code}")
        if response.status_code != 200:
            print(f"   ❌ Health check failed: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Health endpoint failed: {e}")
        return
    
    # Step 2: Test AI health endpoint
    print("2️⃣ Testing AI health endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/ai/health", timeout=10)
        print(f"   ✅ AI Health endpoint: {response.status_code}")
        if response.status_code != 200:
            print(f"   ❌ AI health check failed: {response.text}")
            return
        else:
            result = response.json()
            print(f"   📊 AI Status: {result.get('ai_service_status')}")
            print(f"   🔧 Endpoints configured: {result.get('endpoints_configured')}")
    except Exception as e:
        print(f"   ❌ AI health endpoint failed: {e}")
        return
    
    # Step 3: Test supported frameworks
    print("3️⃣ Testing supported frameworks...")
    try:
        response = requests.get("http://localhost:8000/api/ai/supported-frameworks", timeout=10)
        print(f"   ✅ Frameworks endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            frameworks = [f['id'] for f in result.get('frameworks', [])]
            print(f"   📋 Available frameworks: {frameworks}")
    except Exception as e:
        print(f"   ❌ Frameworks endpoint failed: {e}")
    
    # Step 4: Create and validate test image
    print("4️⃣ Creating test image...")
    try:
        test_image = create_simple_image()
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        image_size = img_buffer.tell()
        img_buffer.seek(0)
        print(f"   ✅ Image created: {image_size} bytes")
        
        # Validate the image can be reopened
        img_buffer.seek(0)
        with Image.open(img_buffer) as img:
            print(f"   ✅ Image validation: {img.format}, {img.size}, {img.mode}")
        img_buffer.seek(0)
        
    except Exception as e:
        print(f"   ❌ Image creation failed: {e}")
        return
    
    # Step 5: Test the generate-code endpoint with detailed error handling
    print("5️⃣ Testing generate-code endpoint...")
    
    url = "http://localhost:8000/api/ai/generate-code"
    
    # Test with minimal data first
    files = {
        'image': ('test.png', img_buffer, 'image/png')
    }
    data = {
        'framework': 'html'
    }
    
    print(f"   📡 URL: {url}")
    print(f"   📝 Data: {data}")
    print(f"   📎 Files: image file ({image_size} bytes)")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=120)
        
        print(f"   📊 Response Status: {response.status_code}")
        print(f"   📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS! Generate-code endpoint working")
            result = response.json()
            print(f"   🎯 Framework: {result.get('framework')}")
            print(f"   ⏱️ Processing time: {result.get('processing_time_ms')}ms")
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            print(f"   📄 Response Text: {response.text}")
            
            # Try to parse as JSON for better error details
            try:
                error_detail = response.json()
                print(f"   🔍 Error Details: {json.dumps(error_detail, indent=2)}")
            except:
                print("   🔍 Raw response (not JSON)")
                
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out")
    except requests.exceptions.ConnectionError:
        print("   🔌 Connection error - server may not be running")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    # Step 6: Test with Vue framework specifically
    print("6️⃣ Testing with Vue framework...")
    try:
        img_buffer.seek(0)  # Reset buffer
        files = {
            'image': ('test.png', img_buffer, 'image/png')
        }
        data = {
            'framework': 'vue',
            'additional_instructions': 'Simple Vue component'
        }
        
        response = requests.post(url, files=files, data=data, timeout=120)
        print(f"   📊 Vue test status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Vue test failed: {response.text}")
        else:
            print("   ✅ Vue framework test successful")
            
    except Exception as e:
        print(f"   ❌ Vue test error: {e}")

if __name__ == "__main__":
    test_endpoints_step_by_step()
    print("\n🎉 Debugging completed!")