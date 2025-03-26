import os
import random
import shutil

def split_dataset():
    # Define source and destination directories
    source_dir = "dataset"
    train_dir = "train"
    test_dir = "test"
    
    # Create train and test directories if they don't exist
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: Directory '{source_dir}' not found")
        return
    
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
    
    # Process test subdirs and flatten into test_dir
    test_image_count = 0
    for subdir in test_subdirs:
        source_subdir = os.path.join(source_dir, subdir)
        images = [f for f in os.listdir(source_subdir) 
                 if os.path.isfile(os.path.join(source_subdir, f)) 
                 and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        for img in images:
            src_path = os.path.join(source_subdir, img)
            ext = os.path.splitext(img)[1]
            test_image_count += 1
            dest_path = os.path.join(test_dir, f"{test_image_count}{ext}")
            shutil.copy2(src_path, dest_path)
    
    # Process train subdirs and flatten into train_dir
    train_image_count = 0
    for subdir in train_subdirs:
        source_subdir = os.path.join(source_dir, subdir)
        images = [f for f in os.listdir(source_subdir) 
                 if os.path.isfile(os.path.join(source_subdir, f)) 
                 and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        for img in images:
            src_path = os.path.join(source_subdir, img)
            ext = os.path.splitext(img)[1]
            train_image_count += 1
            dest_path = os.path.join(train_dir, f"{train_image_count}{ext}")
            shutil.copy2(src_path, dest_path)
    
    print(f"Processed {len(subdirs)} total folder groups:")
    print(f"  {len(train_subdirs)} folder groups ({train_image_count} images) moved to train")
    print(f"  {len(test_subdirs)} folder groups ({test_image_count} images) moved to test")

if __name__ == "__main__":
    split_dataset()