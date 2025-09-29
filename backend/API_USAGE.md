# Canvas Smith API - Simplified Usage

## Generate Vue.js Code from Sketch

### Simple Image Upload

```bash
# Upload any image format and get Vue.js code
curl -X POST "http://localhost:8000/api/ai/generate-code" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@your_sketch.png"
```

### Supported Image Formats

- ✅ **JPG/JPEG** - Photos and compressed images
- ✅ **PNG** - Sketches and drawings (recommended)
- ✅ **WebP** - Modern web format
- ✅ **GIF** - Animated or static images
- ✅ **BMP** - Bitmap images
- ✅ **TIFF** - High-quality images
- ✅ **SVG** - Vector graphics (converted to PNG for AI)

### Response Format

```json
{
  "success": true,
  "generated_code": "<template>\n  <div class=\"component\">...</div>\n</template>\n\n<script setup>...</script>\n\n<style scoped>...</style>",
  "finish_reason": "stop",
  "token_usage": {
    "prompt_tokens": 1250,
    "completion_tokens": 800,
    "total_tokens": 2050,
    "estimated_cost_usd": 0.0615
  },
  "component_analysis": {
    "component_type": "vue",
    "has_script_setup": true,
    "has_typescript": false,
    "interactive_elements": {
      "buttons": 3,
      "forms": 1,
      "inputs": 2,
      "links": 1
    },
    "animations": {
      "vue_transitions": 2,
      "css_animations": 1,
      "hover_effects": 5
    },
    "vue_features": {
      "reactive_data": true,
      "computed_properties": false,
      "watchers": false,
      "lifecycle_hooks": true
    }
  },
  "metadata": {
    "framework": "vue",
    "image_size_bytes": 245760,
    "image_format": "png",
    "has_animations": true,
    "has_hover_effects": true
  },
  "timestamp": "2025-09-30T10:30:45.123Z",
  "processing_time_ms": 3250
}
```

### Features

🎯 **Vue.js 3 Only** - Optimized for Vue.js with Composition API  
📸 **All Image Formats** - Upload any common image format  
🧠 **Smart Predictions** - AI predicts button functionality and interactions  
🎨 **Animations Included** - Smooth transitions and hover effects  
📊 **Token Tracking** - Detailed usage and cost information  
🚀 **Production Ready** - Complete Vue.js components with TypeScript support

### Health Check

```bash
# Check service status
curl http://localhost:8000/api/ai/health-detailed
```

### Framework Information

```bash
# Get Vue.js capabilities info
curl http://localhost:8000/api/ai/supported-frameworks
```
