#!/usr/bin/env python3
"""
Create a simple app icon for Dino Tamagotchi
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a 1024x1024 image (highest resolution for macOS icons)
    size = 1024
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background gradient (purple to blue)
    for y in range(size):
        r = int(102 + (118 - 102) * y / size)  # 102 -> 118
        g = int(126 + (78 - 126) * y / size)   # 126 -> 78
        b = int(234 + (162 - 234) * y / size)  # 234 -> 162
        color = (r, g, b, 255)
        draw.line([(0, y), (size, y)], fill=color)
    
    # Draw dinosaur emoji (simplified)
    try:
        # Try to use system font that has emoji
        font = ImageFont.truetype('/System/Library/Fonts/Apple Color Emoji.ttc', 600)
        emoji_pos = (size//2 - 300, size//2 - 350)
        draw.text(emoji_pos, "🦕", font=font, embedded_color=True)
    except:
        # Fallback: draw a simple circle
        circle_size = 400
        circle_pos = (size//2 - circle_size//2, size//2 - circle_size//2)
        draw.ellipse([circle_pos[0], circle_pos[1], 
                     circle_pos[0] + circle_size, circle_pos[1] + circle_size], 
                    fill=(76, 175, 80, 255))
        
        # Add eyes
        eye_size = 40
        left_eye = (size//2 - 80, size//2 - 80)
        right_eye = (size//2 + 40, size//2 - 80)
        draw.ellipse([left_eye[0], left_eye[1], left_eye[0] + eye_size, left_eye[1] + eye_size], 
                    fill=(33, 33, 33, 255))
        draw.ellipse([right_eye[0], right_eye[1], right_eye[0] + eye_size, right_eye[1] + eye_size], 
                    fill=(33, 33, 33, 255))
    
    # Save as PNG first
    img.save('icon.png', 'PNG')
    
    # Create iconset directory for macOS
    iconset_dir = 'DinoTamagotchi.iconset'
    os.makedirs(iconset_dir, exist_ok=True)
    
    # Generate different sizes for macOS iconset
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size_px in sizes:
        # Standard resolution
        resized = img.resize((size_px, size_px), Image.Resampling.LANCZOS)
        resized.save(f'{iconset_dir}/icon_{size_px}x{size_px}.png')
        
        # High resolution (@2x)
        if size_px <= 512:  # Don't create @2x for 1024
            resized_2x = img.resize((size_px * 2, size_px * 2), Image.Resampling.LANCZOS)
            resized_2x.save(f'{iconset_dir}/icon_{size_px}x{size_px}@2x.png')
    
    print(f"✅ Icon created: icon.png")
    print(f"✅ Iconset created: {iconset_dir}/")
    
    # Convert to .icns using system tools
    try:
        os.system(f'iconutil -c icns {iconset_dir}')
        print(f"✅ macOS icon created: DinoTamagotchi.icns")
    except:
        print("⚠️ Could not create .icns file (iconutil not available)")

if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("⚠️ PIL/Pillow not installed. Install with: pip3 install Pillow")
        print("📝 Creating simple text icon instead...")
        
        # Create a simple text-based icon
        with open('icon.txt', 'w') as f:
            f.write('🦕')
        print("✅ Simple icon created: icon.txt")