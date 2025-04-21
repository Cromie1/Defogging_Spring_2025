import os
import random
from PIL import Image
import re

varianceThreshold = 50

def split_and_process_dataset():
    source_dir = "dataset"
    train_dir = "train"
    test_dir = "test"
    
    print(f"Starting dataset processing...")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    print(f"Directories created: {train_dir}, {test_dir}")
    
    if not os.path.exists(source_dir):
        print(f"Error: Directory '{source_dir}' not found")
        return
    
    subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    print(f"Found {len(subdirs)} subdirectories")
    
    random.shuffle(subdirs)
    split_point = int(len(subdirs) * 0.25)
    test_subdirs = subdirs[:split_point]
    train_subdirs = subdirs[split_point:]
    print(f"Dataset split: {len(train_subdirs)} train, {len(test_subdirs)} test subdirs")
    
    # Global counter for output images
    global_image_count = 1
    temp_count = 0
    
    # Process test subdirs
    print(f"Processing test set...")
    for subdir in test_subdirs:
        source_subdir = os.path.join(source_dir, subdir)
        images = [f for f in os.listdir(source_subdir) 
                  if os.path.isfile(os.path.join(source_subdir, f)) 
                  and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        for img in images:
            variance = extract_variance(img)
            if variance is not None and variance < varianceThreshold:
                src_path = os.path.join(source_subdir, img)
                global_image_count = process_and_augment_image(src_path, test_dir, global_image_count)
    print(f"Test set processing complete. Generated images up to {global_image_count - 1}")
    
    temp_count = global_image_count
    global_image_count = 1
    # Process train subdirs
    print(f"Processing train set...")
    for subdir in train_subdirs:
        source_subdir = os.path.join(source_dir, subdir)
        images = [f for f in os.listdir(source_subdir) 
                  if os.path.isfile(os.path.join(source_subdir, f)) 
                  and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        for img in images:
            variance = extract_variance(img)
            if variance is not None and variance < varianceThreshold:
                src_path = os.path.join(source_subdir, img)
                global_image_count = process_and_augment_image(src_path, train_dir, global_image_count)
    print(f"Train set processing complete. Generated images up to {global_image_count - 1}")
    
    global_image_count += temp_count
    print(f"\nProcessing complete!")
    print(f"Total subdirs processed: {len(subdirs)}")
    print(f"Total output images: {global_image_count - 1}")

def process_and_augment_image(src_path, dest_dir, image_count):
    """Extract exactly four 256x256 pairs from centered positions, combine with clear on left and foggy on right."""
    img = Image.open(src_path)
    width, height = img.size
    assert width == 3840 and height == 1080, f"Unexpected size: {width}x{height}"

    # Split into clear (left) and foggy (right)
    clear = img.crop((0, 0, 1920, 1080))      # Left half is clear
    foggy = img.crop((1920, 0, 3840, 1080))   # Right half is foggy

    # Define four centered positions (around center at 960, 540)
    patch_size = 256
    center_x, center_y = 960, 540  # Center of 1920x1080
    half_patch = patch_size // 2   # 128
    positions = [
        (center_x - half_patch, center_y - patch_size),  # Above center
        (center_x - half_patch, center_y),               # Below center (starts where above ends)
        (center_x - patch_size, center_y - half_patch),  # Left of center
        (center_x, center_y - half_patch)                # Right of center
    ]

    # Extract and process exactly four pairs
    for (x, y) in positions:
        # Extract patches
        clear_patch = clear.crop((x, y, x + patch_size, y + patch_size))
        foggy_patch = foggy.crop((x, y, x + patch_size, y + patch_size))

        # Combine patches: clear on left, foggy on right
        combined = Image.new("RGB", (512, 256))
        combined.paste(clear_patch, (0, 0))      # Clear on left
        combined.paste(foggy_patch, (256, 0))    # Foggy on right

        # Save with sequential numbering and .jpg extension
        dest_path = os.path.join(dest_dir, f"{image_count}.jpg")
        combined.save(dest_path, "JPEG")
        image_count += 1

    return image_count
def extract_variance(filename):
    """Extract variance value from filename like 'frame92var56.65916.jpg'"""
    try:
        pattern = r'var(\d+\.\d+|\d+)\.jpg'
        match = re.search(pattern, filename)
        if match:
            return float(match.group(1))
        return None
    except (ValueError, AttributeError):
        return None

if __name__ == "__main__":
    split_and_process_dataset()