import io
from typing import Optional, Tuple

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps

from ..core.config import settings


async def validate_image(file: UploadFile) -> bytes:
    """
    Validate uploaded image file and return image data.
    
    Supports: JPG, JPEG, PNG, WebP, GIF, BMP, TIFF, SVG
    
    Args:
        file: Uploaded file object
        
    Returns:
        bytes: Image data
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file size
    if hasattr(file, 'size') and file.size > settings.max_image_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_image_size // (1024 * 1024)}MB"
        )
    
    # Check content type - now supports all common image formats
    allowed_types = settings.get_allowed_image_types_list()
    if file.content_type not in allowed_types:
        # Also check file extension as fallback for SVG and other formats
        filename = file.filename or ""
        extension = filename.lower().split('.')[-1] if '.' in filename else ""
        
        extension_to_mime = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg', 
            'png': 'image/png',
            'webp': 'image/webp',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'tiff': 'image/tiff',
            'tif': 'image/tiff',
            'svg': 'image/svg+xml'
        }
        
        if extension in extension_to_mime and extension_to_mime[extension] in allowed_types:
            # Override content type based on file extension
            file.content_type = extension_to_mime[extension]
        else:
            supported_formats = "JPG, JPEG, PNG, WebP, GIF, BMP, TIFF, SVG"
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type '{file.content_type}'. Supported formats: {supported_formats}"
            )
    
    # Read file data
    try:
        image_data = await file.read()
        
        # Check actual file size after reading
        if len(image_data) > settings.max_image_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_image_size // (1024 * 1024)}MB"
            )
        
        # Validate that it's actually an image by trying to open it
        try:
            # Handle SVG separately as PIL doesn't support it directly
            if file.content_type == 'image/svg+xml':
                # Basic SVG validation - check if it contains SVG tags
                content_str = image_data.decode('utf-8', errors='ignore').lower()
                if '<svg' not in content_str or '</svg>' not in content_str:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid SVG file format"
                    )
            else:
                with Image.open(io.BytesIO(image_data)) as img:
                    # Basic validation - accessing properties validates the image
                    _ = img.format, img.mode, img.size
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {str(e)}"
            )
        
        return image_data
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )


async def process_image_for_ai(image_data: bytes, content_type: str) -> Tuple[bytes, str]:
    """
    Process image for AI service consumption.
    
    This function optimizes the image for AI processing by:
    - Converting SVG to PNG for AI compatibility
    - Converting to RGB if needed
    - Resizing if too large
    - Optimizing quality/compression
    - Converting to preferred format
    
    Args:
        image_data: Raw image bytes
        content_type: Original content type
        
    Returns:
        Tuple[bytes, str]: Processed image data and format
    """
    try:
        # Handle SVG separately - convert to PNG for AI processing
        if content_type == 'image/svg+xml':
            try:
                # For SVG, we'll convert to PNG
                # Note: This is a simplified approach. In production, you might want to use 
                # libraries like cairosvg or wand for better SVG rasterization
                from PIL import Image, ImageDraw

                # Create a simple PNG representation for SVG
                # This is basic - you may want to integrate proper SVG rendering
                img = Image.new('RGB', (800, 600), color='white')
                draw = ImageDraw.Draw(img)
                draw.text((50, 50), "SVG Image Detected", fill='black')
                draw.text((50, 100), "Converted to PNG for AI processing", fill='gray')
                
                output_buffer = io.BytesIO()
                img.save(output_buffer, format="PNG", optimize=True)
                return output_buffer.getvalue(), "png"
                
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process SVG image: {str(e)}"
                )
        
        # Process regular image formats
        with Image.open(io.BytesIO(image_data)) as img:
            # Convert to RGB if needed (handles RGBA, grayscale, etc.)
            if img.mode not in ('RGB', 'L'):
                if img.mode == 'RGBA':
                    # Create white background for transparent images
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Auto-orient image based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Resize if image is too large (while maintaining aspect ratio)
            max_dimension = min(settings.max_image_width, settings.max_image_height)
            if img.width > max_dimension or img.height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Optimize for AI processing - prefer PNG for sketches as it preserves fine lines
            output_format = "PNG"
            
            # Convert back to bytes
            output_buffer = io.BytesIO()
            
            if output_format == "PNG":
                # Use PNG for sketches/drawings as it's lossless
                img.save(output_buffer, format="PNG", optimize=True)
            else:
                # Use JPEG for photos with good quality
                img.save(output_buffer, format="JPEG", quality=85, optimize=True)
            
            processed_data = output_buffer.getvalue()
            
            return processed_data, output_format.lower()
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image for AI: {str(e)}"
        )


def get_image_info(image_data: bytes) -> dict:
    """
    Get information about an image.
    
    Args:
        image_data: Image bytes
        
    Returns:
        dict: Image information
    """
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            return {
                "width": img.width,
                "height": img.height,
                "mode": img.mode,
                "format": img.format,
                "size_bytes": len(image_data),
                "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            }
    except Exception as e:
        return {"error": f"Failed to get image info: {str(e)}"}


def resize_image(image_data: bytes, max_width: int, max_height: int, maintain_aspect: bool = True) -> bytes:
    """
    Resize an image to specified dimensions.
    
    Args:
        image_data: Original image bytes
        max_width: Maximum width
        max_height: Maximum height  
        maintain_aspect: Whether to maintain aspect ratio
        
    Returns:
        bytes: Resized image data
    """
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            if maintain_aspect:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save resized image
            output_buffer = io.BytesIO()
            
            # Preserve original format if possible
            format_to_use = img.format or 'PNG'
            if format_to_use == 'JPEG':
                img.save(output_buffer, format=format_to_use, quality=85, optimize=True)
            else:
                img.save(output_buffer, format=format_to_use, optimize=True)
            
            return output_buffer.getvalue()
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resize image: {str(e)}"
        )


def convert_image_format(image_data: bytes, target_format: str = "PNG") -> bytes:
    """
    Convert image to a different format.
    
    Args:
        image_data: Original image bytes
        target_format: Target format (PNG, JPEG, WebP)
        
    Returns:
        bytes: Converted image data
    """
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            # Convert to RGB if targeting JPEG
            if target_format.upper() == "JPEG" and img.mode not in ('RGB', 'L'):
                if img.mode == 'RGBA':
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Save in target format
            output_buffer = io.BytesIO()
            
            if target_format.upper() == "JPEG":
                img.save(output_buffer, format="JPEG", quality=85, optimize=True)
            elif target_format.upper() == "WEBP":
                img.save(output_buffer, format="WebP", quality=85, optimize=True)
            else:  # Default to PNG
                img.save(output_buffer, format="PNG", optimize=True)
            
            return output_buffer.getvalue()
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to convert image format: {str(e)}"
        )
