import os
from PIL import Image

def generate_icons(source_path, android_res_dir, web_public_dir):
    try:
        img = Image.open(source_path).convert("RGBA")
        
        # Android mipmap sizes
        android_sizes = {
            "mipmap-mdpi": 48,
            "mipmap-hdpi": 72,
            "mipmap-xhdpi": 96,
            "mipmap-xxhdpi": 144,
            "mipmap-xxxhdpi": 192,
        }
        
        # Generate Android icons
        for folder, size in android_sizes.items():
            folder_path = os.path.join(android_res_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            resized_img.save(os.path.join(folder_path, "ic_launcher.png"))
            resized_img.save(os.path.join(folder_path, "ic_launcher_round.png"))
            
        # Web sizes
        web_sizes = {
            "favicon.ico": [(16, 16), (32, 32), (48, 48)], # ico can contain multiple sizes
            "logo192.png": (192, 192),
            "logo512.png": (512, 512),
            "apple-touch-icon.png": (180, 180)
        }
        
        for filename, size_info in web_sizes.items():
            if filename.endswith(".ico"):
                # Save as ico with multiple sizes
                img.save(os.path.join(web_public_dir, filename), sizes=size_info)
            else:
                resized_img = img.resize(size_info, Image.Resampling.LANCZOS)
                resized_img.save(os.path.join(web_public_dir, filename))
                
        print("Icons generated successfully.")
    except Exception as e:
        print(f"Error generating icons: {e}")

if __name__ == "__main__":
    src_img = "/Users/shauryatiwari/SIH-Navigators/logo-nav.png"
    android_res = "/Users/shauryatiwari/SIH-Navigators/android/app/src/main/res"
    web_public = "/Users/shauryatiwari/SIH-Navigators/web/public"
    
    generate_icons(src_img, android_res, web_public)
