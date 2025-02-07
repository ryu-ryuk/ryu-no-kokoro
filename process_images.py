import os
import re
import shutil

# Define paths
posts_dir = "/home/ryu/obsidian/ryu-no-kokoro/content/blog/"
attachments_dir = "/home/ryu/obsidian/vault/"
static_images_dir = "/home/ryu/obsidian/ryu-no-kokoro/static/images/"

# Make sure the static images directory exists
os.makedirs(static_images_dir, exist_ok=True)

def find_image_file(image_name, base_dir):
    """
    Try to locate the image file in base_dir.
    First check for a direct match; if not found, search recursively.
    """
    direct_path = os.path.join(base_dir, image_name)
    if os.path.exists(direct_path):
        return direct_path
    for root, _, files in os.walk(base_dir):
        if image_name in files:
            return os.path.join(root, image_name)
    return None

# Process each markdown file in the posts directory
for filename in os.listdir(posts_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(posts_dir, filename)
        
        # Read file content
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
        
        # Find all image links in Obsidian-style format [[image.png]]
        images = re.findall(r'\[\[([^]]*\.png)\]\]', content)
        
        # Process each found image link
        for image in images:
            # Use the basename to ensure matching the filename only
            image_basename = os.path.basename(image)
            # Generate a Hugo Markdown image link (spaces replaced with %20)
            markdown_image = f"![{image_basename}](/images/{image_basename.replace(' ', '%20')})"
            # Replace the original link in the markdown content
            content = content.replace(f"[[{image}]]", markdown_image)
            
            # Locate the original image file (searches recursively if necessary)
            image_file = find_image_file(image_basename, attachments_dir)
            if image_file:
                try:
                    shutil.copy(image_file, os.path.join(static_images_dir, image_basename))
                    print(f"Copied {image_file} to {static_images_dir}")
                except Exception as e:
                    print(f"Failed to copy {image_file}: {e}")
            else:
                print(f"Warning: Could not locate image file: {image_basename}")
        
        # Write the updated content back to the markdown file
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

print("Markdown files processed and images copied successfully.")
