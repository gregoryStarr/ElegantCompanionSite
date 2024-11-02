from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(width, height, text, output_path):
    # Create a new image with a dark background
    image = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(image)
    
    # Draw a border
    border_width = 2
    draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                  outline='#ffffff', width=border_width)
    
    # Add text
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    # Center the text
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill='#ffffff', font=font)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the image
    image.save(output_path, quality=95)

def generate_gallery_images():
    # Create featured image
    create_placeholder_image(800, 1200, "Featured Image", "static/images/featured.jpg")
    
    # Create gallery images
    for gallery_id in range(1, 5):
        gallery_path = f"static/images/gallery{gallery_id}"
        os.makedirs(gallery_path, exist_ok=True)
        
        for image_id in range(1, 7):
            image_path = f"{gallery_path}/image{image_id}.jpg"
            create_placeholder_image(600, 800, f"Gallery {gallery_id}\nImage {image_id}", image_path)

if __name__ == "__main__":
    generate_gallery_images()
