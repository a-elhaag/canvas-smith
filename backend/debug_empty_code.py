#!/usr/bin/env python3
"""
Debug script to check why generated_code is empty.
"""

import requests
from io import BytesIO
from PIL import Image, ImageDraw
import json

def create_test_image():
    """Create a simple test image."""
    img = Image.new('RGB', (300, 200), 'white')
    draw = ImageDraw.Draw(img)
    
    # Simple layout
    draw.rectangle([20, 20, 280, 50], outline='black', width=2)
    draw.text((30, 30), "Header", fill='black')
    
    draw.rectangle([20, 70, 280, 120], outline='black', width=1)
    draw.text((30, 85), "Content Area", fill='black')
    
    draw.rectangle([20, 140, 280, 180], outline='black', width=1)
    draw.text((30, 155), "Footer", fill='black')
    
    return img

def debug_ai_response():
    """Debug the AI response to see what's being returned."""
    print("🔍 Debugging AI Response - Detailed Analysis")
    print("=" * 60)
    
    # Create test image
    test_image = create_test_image()
    img_buffer = BytesIO()
    test_image.save(img_buffer, format='PNG')
    image_size = img_buffer.tell()
    img_buffer.seek(0)
    
    print(f"📊 Test image size: {image_size} bytes")
    
    # Test the endpoint
    url = "http://localhost:8000/api/ai/generate-code"
    files = {
        'image': ('debug_test.png', img_buffer, 'image/png')
    }
    data = {
        'framework': 'vue',
        'additional_instructions': 'Create a simple Vue component'
    }
    
    try:
        print("🚀 Sending request to AI service...")
        response = requests.post(url, files=files, data=data, timeout=180)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n🔍 FULL RESPONSE ANALYSIS:")
            print("=" * 50)
            print(f"Success: {result.get('success', 'NOT FOUND')}")
            print(f"Framework: {result.get('framework', 'NOT FOUND')}")
            print(f"Timestamp: {result.get('timestamp', 'NOT FOUND')}")
            print(f"Processing Time: {result.get('processing_time_ms', 'NOT FOUND')}ms")
            
            # Check generated_code specifically
            generated_code = result.get('generated_code', None)
            print(f"\n📝 Generated Code Status:")
            print(f"   Type: {type(generated_code)}")
            print(f"   Length: {len(generated_code) if generated_code else 'None/0'}")
            print(f"   Is Empty: {generated_code == '' if generated_code is not None else 'N/A'}")
            print(f"   Is None: {generated_code is None}")
            
            if generated_code:
                print(f"\n✅ GENERATED CODE (first 200 chars):")
                print("-" * 40)
                print(generated_code[:200] + "..." if len(generated_code) > 200 else generated_code)
            else:
                print(f"\n❌ NO GENERATED CODE FOUND!")
                
            # Check metadata
            metadata = result.get('metadata', {})
            print(f"\n📈 Metadata Analysis:")
            print(json.dumps(metadata, indent=2))
            
            # Check if there are any other fields that might contain the code
            print(f"\n🔍 All Response Keys:")
            for key, value in result.items():
                if key != 'generated_code':
                    print(f"   {key}: {type(value)} - {str(value)[:100]}...")
            
        else:
            print(f"❌ ERROR Response: {response.status_code}")
            print(f"📄 Error Details: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_ai_service_directly():
    """Test if the AI service itself is returning code."""
    print("\n🤖 Testing AI Service Health...")
    
    try:
        # Check AI service health with details
        response = requests.get("http://localhost:8000/api/ai/health", timeout=30)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ AI Service Status: {health_data.get('ai_service_status')}")
            print(f"🔧 Endpoints Configured: {health_data.get('endpoints_configured')}")
            
            details = health_data.get('details', {})
            print(f"📡 Endpoint: {details.get('endpoint', 'Unknown')}")
            print(f"⏱️ Response Time: {details.get('response_time_ms', 'Unknown')}ms")
            print(f"📊 Status Code: {details.get('status_code', 'Unknown')}")
            
            if details.get('error'):
                print(f"⚠️ AI Service Error: {details.get('error')}")
        else:
            print(f"❌ AI Health Check Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ AI Health Check Error: {e}")

if __name__ == "__main__":
    debug_ai_response()
    test_ai_service_directly()
    print("\n🎉 Debug analysis completed!")