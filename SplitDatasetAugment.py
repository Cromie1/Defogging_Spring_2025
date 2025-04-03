import os
import random
from PIL import Image

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
    
    # Process test subdirs
    print(f"Processing test set...")
    for subdir in test_subdirs:
        source_subdir = os.path.join(source_dir, subdir)
        images = [f for f in os.listdir(source_subdir) 
                  if os.path.isfile(os.path.join(source_subdir, f)) 
                  and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        for img in images:
            src_path = os.path.join(source_subdir, img)
            global_image_count = process_and_augment_image(src_path, test_dir, global_image_count)
    print(f"Test set processing complete. Generated images up to {global_image_count - 1}")
    
    # Process train subdirs
    print(f"Processing train set...")
    for subdir in train_subdirs:
        source_subdir = os.path.join(source_dir, subdir)
        images = [f for f in os.listdir(source_subdir) 
                  if os.path.isfile(os.path.join(source_subdir, f)) 
                  and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        for img in images:
            src_path = os.path.join(source_subdir, img)
            global_image_count = process_and_augment_image(src_path, train_dir, global_image_count)
    print(f"Train set processing complete. Generated images up to {global_image_count - 1}")
    
    print(f"\nProcessing complete!")
    print(f"Total subdirs processed: {len(subdirs)}")
    print(f"Total output images: {global_image_count - 1}")

def process_and_augment_image(src_path, dest_dir, image_count):
    """Extract multiple 256x256 pairs, combine with clear on left and foggy on right."""
    img = Image.open(src_path)
    width, height = img.size
    assert width == 3840 and height == 1080, f"Unexpected size: {width}x{height}"

    # Split into clear (left) and foggy (right)
    clear = img.crop((0, 0, 1920, 1080))      # Left half is clear
    foggy = img.crop((1920, 0, 3840, 1080))   # Right half is foggy

    # Parameters for augmentation
    patch_size = 256
    stride = 128

    # Calculate number of patches
    width_patches = (1920 - patch_size) // stride + 1  # 14 with stride 128
    height_patches = (1080 - patch_size) // stride + 1  # 7 with stride 128

    for y in range(0, 1080 - patch_size + 1, stride):
        for x in range(0, 1920 - patch_size + 1, stride):
            # Extract patches
            clear_patch = clear.crop((x, y, x + patch_size, y + patch_size))
            foggy_patch = foggy.crop((x, y, x + patch_size, y + patch_size))

            # Combine patches: clear on left, foggy on right
            combined = Image.new("RGB", (512, 256))
            combined.paste(clear_patch, (0, 0))      # Clear on left
            combined.paste(foggy_patch, (256, 0))    # Foggy on right

            # Save with simple numbering
            ext = os.path.splitext(src_path)[1]
            dest_path = os.path.join(dest_dir, f"{image_count}{ext}")
            combined.save(dest_path)
            image_count += 1

    return image_count

if __name__ == "__main__":
    split_and_process_dataset()