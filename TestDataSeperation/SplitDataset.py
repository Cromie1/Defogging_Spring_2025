import os
import random
import shutil
from PIL import Image

def split_and_process_dataset():
    # Define source and destination directories
    source_dir = "dataset"
    train_dir = "train"  # Combined foggy + non-foggy images
    test_dir = "test"    # Combined foggy + non-foggy images
    
    # Create train and test directories if they don't exist
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Directory '{source_dir}' not found")
        return
    
    # Set target combined size: "512x256" or "256x256"
    target_combined_size = "512x256"  # Change to "256x256" if desired
    
    # Get all subdirectories (folder groups)
    subdirs = [d for d in os.listdir(source_dir) 
               if os.path.isdir(os.path.join(source_dir, d))]
    
    # Shuffle the subdirectories randomly
    random.shuffle(subdirs)
    
    # Calculate split point (25% of subdirs for test)
    split_point = int(len(subdirs) * 0.25)
    
    # Split subdirs into test and train sets
    test_subdirs = subdirs[:split_point]
    train_subdirs = subdirs[split_point:]
    
    # Process test subdirs
    test_image_count = 0
    for subdir in test_subdirs:
        source_subdir = os.path.join(source_dir, subdir)
        images = [f for f in os.listdir(source_subdir) 
                  if os.path.isfile(os.path.join(source_subdir, f)) 
                  and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        for img in images:
            src_path = os.path.join(source_subdir, img)
            test_image_count += 1
            process_and_recombine_image(src_path, test_dir, test_image_count, target_combined_size)
    
    # Process train subdirs
    train_image_count = 0
    for subdir in train_subdirs:
        source_subdir = os.path.join(source_dir, subdir)
        images = [f for f in os.listdir(source_subdir) 
                  if os.path.isfile(os.path.join(source_subdir, f)) 
                  and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        for img in images:
            src_path = os.path.join(source_subdir, img)
            train_image_count += 1
            process_and_recombine_image(src_path, train_dir, train_image_count, target_combined_size)
    
    print(f"Processed {len(subdirs)} total folder groups:")
    print(f"  {len(train_subdirs)} folder groups ({train_image_count} images) moved to train")
    print(f"  {len(test_subdirs)} folder groups ({test_image_count} images) moved to test")

def process_and_recombine_image(src_path, dest_dir, image_count, target_combined_size):
    """Split, crop, resize, and recombine a 3840x1080 image into a target combined size."""
    # Open the image
    img = Image.open(src_path)
    width, height = img.size
    assert width == 3840 and height == 1080, f"Unexpected size: {width}x{height}"

    # Split into foggy (left) and non-foggy (right)
    foggy = img.crop((0, 0, 1920, 1080))
    clear = img.crop((1920, 0, 3840, 1080))

    # Crop to square 1080x1080 (center of 1920x1080)
    left_crop = (1920 - 1080) // 2
    foggy_square = foggy.crop((left_crop, 0, left_crop + 1080, 1080))
    clear_square = clear.crop((left_crop, 0, left_crop + 1080, 1080))

    # Set resize dimensions based on target combined size
    if target_combined_size == "512x256":
        half_width = 256  # 256x256 per half, combined to 512x256
        combined_width = 512
    elif target_combined_size == "256x256":
        half_width = 128  # 128x256 per half, combined to 256x256
        combined_width = 256
    else:
        raise ValueError("target_combined_size must be '512x256' or '256x256'")
    half_height = 256

    # Resize to half dimensions
    foggy_resized = foggy_square.resize((half_width, half_height), Image.Resampling.LANCZOS)
    clear_resized = clear_square.resize((half_width, half_height), Image.Resampling.LANCZOS)

    # Recombine into a single image
    combined = Image.new("RGB", (combined_width, half_height))
    combined.paste(foggy_resized, (0, 0))           # Foggy on right
    combined.paste(clear_resized, (half_width, 0))  # Non-foggy on left

    # Save with consistent naming
    ext = os.path.splitext(src_path)[1]
    dest_path = os.path.join(dest_dir, f"{image_count}{ext}")
    combined.save(dest_path)

if __name__ == "__main__":
    split_and_process_dataset()