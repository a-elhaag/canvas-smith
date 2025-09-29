#!/usr/bin/env python3
"""
Test script for Canvas Smith image conversion service.
This script tests the AI image-to-code conversion functionality.
"""

import requests
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json

def create_test_sketch():
    """Create a simple test sketch image."""
    # Create a simple sketch of a webpage layout
    width, height = 600, 400
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple webpage layout with thicker lines
    # Header
    draw.rectangle([30, 30, 570, 80], outline='black', width=3)
    draw.text((40, 50), "HEADER SECTION", fill='black')
    
    # Navigation
    draw.rectangle([30, 100, 570, 140], outline='black', width=2)
    draw.text((40, 115), "Home | About | Services | Contact", fill='black')
    
    # Main content area
    draw.rectangle([30, 160, 380, 320], outline='black', width=2)
    draw.text((40, 180), "Main Content Area", fill='black')
    draw.text((40, 200), "Lorem ipsum dolor sit amet", fill='black')
    draw.text((40, 220), "consectetur adipiscing elit", fill='black')
    
    # Add a button placeholder
    draw.rectangle([40, 250, 140, 280], outline='black', width=2)
    draw.text((50, 260), "Button", fill='black')
    
    # Sidebar
    draw.rectangle([400, 160, 570, 320], outline='black', width=2)
    draw.text((410, 180), "Sidebar", fill='black')
    draw.text((410, 200), "• Menu Item 1", fill='black')
    draw.text((410, 220), "• Menu Item 2", fill='black')
    draw.text((410, 240), "• Menu Item 3", fill='black')
    
    # Footer
    draw.rectangle([30, 340, 570, 370], outline='black', width=2)
    draw.text((40, 350), "Footer - Copyright © 2025", fill='black')
    
    print(f"📐 Created test image: {width}x{height} pixels")
    return img

def test_image_conversion():
    """Test the image conversion service."""
    print("🎨 Testing Canvas Smith Image Conversion Service")
    print("=" * 50)
    
    # Create test image
    print("📝 Creating test sketch...")
    test_image = create_test_sketch()
    
    # Convert to bytes and validate
    img_buffer = BytesIO()
    test_image.save(img_buffer, format='PNG')
    image_size = img_buffer.tell()
    img_buffer.seek(0)
    
    print(f"📊 Image size: {image_size} bytes ({image_size / 1024:.1f} KB)")
    
    # Prepare the request
    url = "http://localhost:8000/api/ai/generate-code"
    files = {
        'image': ('test_sketch.png', img_buffer, 'image/png')
    }
    data = {
        'framework': 'vue',
        'additional_instructions': 'Create a Vue.js single file component (.vue) with template, script, and style sections. Use modern Vue 3 composition API and make it responsive with clean CSS styling.'
    }
    
    print(f"📡 Request URL: {url}")
    print(f"🎯 Framework: {data['framework']}")
    print(f"📝 Content-Type: image/png")
    
    print("🚀 Sending request to AI service...")
    try:
        response = requests.post(url, files=files, data=data, timeout=120)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! AI conversion completed")
            print(f"📊 Framework: {result.get('framework', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time_ms', 'N/A')}ms")
            
            # DETAILED DEBUGGING OF RESPONSE
            print("\n� DETAILED RESPONSE ANALYSIS:")
            print("=" * 50)
            print(f"Response keys: {list(result.keys())}")
            
            generated_code = result.get('generated_code', None)
            print(f"Generated code type: {type(generated_code)}")
            print(f"Generated code is None: {generated_code is None}")
            print(f"Generated code length: {len(generated_code) if generated_code else 'N/A'}")
            
            # Print the ENTIRE response for debugging
            print(f"\n📄 FULL RESPONSE:")
            print(json.dumps(result, indent=2))
            
            print(f"\n📈 Metadata: {json.dumps(result.get('metadata', {}), indent=2)}")
            
            # Save generated code to file
            if generated_code and generated_code.strip():
                with open('generated_website.vue', 'w', encoding='utf-8') as f:
                    f.write(generated_code)
                print("💾 Generated Vue component saved to 'generated_website.vue'")
                print("\n🔍 Generated Code Preview (first 500 chars):")
                print("-" * 50)
                print(generated_code[:500] + "..." if len(generated_code) > 500 else generated_code)
            else:
                print("⚠️  No code was generated or code is empty!")
                print(f"   Raw generated_code value: {repr(generated_code)}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - AI processing may take longer")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - make sure the server is running")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_chat_service():
    """Test the chat assistance service."""
    print("\n💬 Testing Chat Service")
    print("=" * 50)
    
    url = "http://localhost:8000/api/ai/chat"
    data = {
        "message": "How can I improve my Vue.js component? Can you suggest best practices for Vue 3 composition API?",
        "context": {"framework": "vue", "topic": "vue_component_optimization"}
    }
    
    print("🚀 Sending chat request...")
    try:
        response = requests.post(url, json=data, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Chat response received")
            print(f"🤖 AI Response:")
            print("-" * 50)
            print(result.get('response', 'No response'))
            print("-" * 50)
            print(f"📊 Metadata: {json.dumps(result.get('metadata', {}), indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def debug_image_validation():
    """Debug function to test image creation and validation."""
    print("🔍 Debug: Testing image creation and validation")
    print("=" * 50)
    
    try:
        # Create and save test image
        test_image = create_test_sketch()
        test_image.save('debug_test_image.png', 'PNG')
        print("✅ Image created and saved successfully")
        
        # Test opening the image
        with open('debug_test_image.png', 'rb') as f:
            image_data = f.read()
        
        # Validate with PIL
        with Image.open(BytesIO(image_data)) as img:
            print(f"📊 Image format: {img.format}")
            print(f"📐 Image size: {img.size}")
            print(f"🎨 Image mode: {img.mode}")
            
        print("✅ Image validation successful")
        
    except Exception as e:
        print(f"❌ Image validation failed: {e}")

if __name__ == "__main__":
    # Debug image validation first
    debug_image_validation()
    
    # Test image conversion
    test_image_conversion()
    
    # Test chat service  
    test_chat_service()
    
    print("\n🎉 Testing completed!")