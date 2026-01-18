import os
import io
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_image_with_gemini(prompt, size=1024):
    """
    Generates an image using Gemini Imagen (if available).
    Falls back to a placeholder if not supported.
    """
    if not GEMINI_API_KEY:
        return None
    
    try:
        # Note: As of current API, imagen might not be available via standard SDK
        # This is a placeholder for when the feature becomes available
        # For now, we'll use a fallback approach
        
        # Attempt to generate (this may not work with current API)
        model = genai.GenerativeModel('gemini-2.0-flash-exp-image-generation')
        response = model.generate_content(prompt)
        
        # If successful, return image data
        # This is speculative based on future API support
        return None  # Placeholder for now
        
    except Exception as e:
        print(f"Gemini image generation error: {e}")
        return None

def download_image(image_url):
    """Downloads an image from URL and returns PIL Image object."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))
        return img.convert('RGB')
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def create_gradient_overlay(size, gradient_height_ratio=0.4):
    """Creates a gradient overlay (black to transparent) for text background."""
    width, height = size
    gradient_height = int(height * gradient_height_ratio)
    
    # Create gradient from transparent to black
    gradient = Image.new('RGBA', (width, gradient_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    
    for y in range(gradient_height):
        alpha = int((y / gradient_height) * 200)  # Max 200 for semi-transparency
        draw.rectangle([(0, y), (width, y + 1)], fill=(0, 0, 0, alpha))
    
    return gradient

def add_headline_to_image(image_url, headline_text, output_path=None):
    """
    Downloads image, adds gradient overlay, and overlays Thai headline text.
    Returns path to the processed image.
    """
    # Download image
    img = download_image(image_url)
    if not img:
        return None
    
    # Resize to 1024x1024 if needed
    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    
    # Create RGBA version for overlay
    img = img.convert('RGBA')
    
    # Create gradient overlay
    gradient = create_gradient_overlay((1024, 1024), gradient_height_ratio=0.35)
    
    # Position gradient at bottom
    gradient_position = (0, 1024 - gradient.size[1])
    img.paste(gradient, gradient_position, gradient)
    
    # Add text
    draw = ImageDraw.Draw(img)
    
    # Try to load a Thai font
    font_size = 48
    try:
        # Try common Thai fonts
        font_paths = [
            "/System/Library/Fonts/Supplemental/Thonburi.ttc",  # macOS
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",  # Linux
            "C:\\Windows\\Fonts\\leelawad.ttf",  # Windows
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
        
        if not font:
            # Fallback to default
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (center bottom)
    # Wrap text if too long
    max_width = 900
    lines = []
    words = headline_text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    # Draw each line
    y_position = 1024 - 120 - (len(lines) * 60)
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_position = (1024 - text_width) // 2
        
        # Draw text with shadow for better readability
        draw.text((x_position + 2, y_position + 2), line, font=font, fill=(0, 0, 0, 255))
        draw.text((x_position, y_position), line, font=font, fill=(255, 255, 255, 255))
        
        y_position += 60
    
    # Convert back to RGB
    final_img = Image.new('RGB', img.size, (255, 255, 255))
    final_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
    
    # Save image
    if not output_path:
        output_path = f"generated_images/news_{hash(headline_text)}.jpg"
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "generated_images", exist_ok=True)
    final_img.save(output_path, "JPEG", quality=90)
    
    return output_path

if __name__ == "__main__":
    # Test
    test_url = "https://images.cointelegraph.com/cdn-cgi/image/format=auto,onerror=redirect,quality=90,width=1024/https://s3.cointelegraph.com/uploads/2025-01/d25ce3e4-7bc5-4e4f-92bc-e05c37b10da3"
    test_headline = "บิตคอยน์พุ่งทะลุ 100,000 ดอลลาร์สหรัฐ!"
    
    result = add_headline_to_image(test_url, test_headline, "test_output.jpg")
    print(f"Generated: {result}")
