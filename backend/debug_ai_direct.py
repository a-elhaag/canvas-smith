#!/usr/bin/env python3
"""
Specific debug for the AI service generate_code_from_image method.
"""

import asyncio
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import json
import sys
import os

# Add the parent directory to sys.path to import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

from app.services.ai_service import AIService
from app.core.config import settings

async def debug_ai_service_directly():
    """Test the AI service directly without going through the API."""
    print("🔍 Testing AI Service Directly")
    print("=" * 50)
    
    # Create a simple test image
    img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(img)
    
    # Simple layout
    draw.rectangle([20, 20, 380, 60], outline='black', width=2)
    draw.text((30, 35), "HEADER", fill='black')
    
    draw.rectangle([20, 80, 380, 120], outline='black', width=1)
    draw.text((30, 95), "Navigation: Home | About | Contact", fill='black')
    
    draw.rectangle([20, 140, 250, 220], outline='black', width=1)
    draw.text((30, 155), "Main Content", fill='black')
    
    draw.rectangle([270, 140, 380, 220], outline='black', width=1)
    draw.text((280, 155), "Sidebar", fill='black')
    
    draw.rectangle([20, 240, 380, 270], outline='black', width=1)
    draw.text((30, 250), "Footer", fill='black')
    
    # Convert to bytes
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    image_data = img_buffer.getvalue()
    
    print(f"📊 Created test image: {len(image_data)} bytes")
    
    # Test AI service configuration
    print("🔧 Testing AI Service Configuration...")
    ai_service = AIService()
    
    print(f"   API Key configured: {bool(ai_service.api_key)}")
    print(f"   Endpoint: {ai_service.endpoint}")
    print(f"   Deployment: {ai_service.deployment_name}")
    print(f"   API Version: {ai_service.api_version}")
    print(f"   Max Tokens: {ai_service.max_tokens}")
    
    try:
        # Test the generate_code_from_image method directly
        print("\n🚀 Calling AI service generate_code_from_image...")
        
        result = await ai_service.generate_code_from_image(
            image_data=image_data,
            image_format="png",
            framework="vue",
            additional_instructions="Create a simple Vue component"
        )
        
        print("✅ AI service call successful!")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            code = result.get("code", None)
            print(f"📝 Generated code type: {type(code)}")
            print(f"📝 Generated code length: {len(code) if code else 'None/0'}")
            print(f"📝 Generated code is empty: {not code or code.strip() == ''}")
            
            if code and code.strip():
                print(f"\n✅ GENERATED CODE (first 300 chars):")
                print("-" * 50)
                print(code[:300] + "..." if len(code) > 300 else code)
                
                # Save to file
                with open('direct_ai_test.vue', 'w', encoding='utf-8') as f:
                    f.write(code)
                print(f"💾 Code saved to 'direct_ai_test.vue'")
            else:
                print("❌ NO CODE GENERATED!")
                print(f"Raw code value: {repr(code)}")
        
            print(f"\n📊 Full Result:")
            print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ AI service call failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ai_service_directly())