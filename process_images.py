import os
import re
import shutil
import configparser

# Path to the configuration file
config_file = os.path.expanduser("~/.obsidian_to_hugo_config")
if not os.path.exists(config_file):
    print("Error: Config file not found. Please set up paths first.")
    exit(1)

# Read and fix the config file content if necessary
with open(config_file, "r", encoding="utf-8") as f:
    config_content = f.read()
if not config_content.strip().startswith("["):
    config_content = "[Paths]\n" + config_content

config = configparser.ConfigParser()
config.read_string(config_content)

# Retrieve paths from the config
posts_dir = config.get("Paths", "destinationPath", fallback=None)
attachments_dir = config.get("Paths", "sourcePath", fallback=None)
if not posts_dir or not attachments_dir:
    print("Error: Required paths not found in the config file.")
    exit(1)

# Determine the static images directory
static_images_dir = os.path.join(os.path.dirname(posts_dir), "static/images")
os.makedirs(static_images_dir, exist_ok=True)

# Process each markdown file in the posts directory
for filename in os.listdir(posts_dir):
    if filename.endswith(".md"):
        file_path = os.path.join(posts_dir, filename)
        with open(file_path, "r", encoding="utf-8") as md_file:
            content = md_file.read()

        # Find and replace Obsidian-style image links ([[image.png]]) with Hugo Markdown
        images = re.findall(r'\[\[([^]]*\.(?:png|jpg|jpeg|gif|svg))\]\]', content)
        for image in images:
            image_name = os.path.basename(image)
            markdown_link = f"![{image_name}](/images/{image_name.replace(' ', '%20')})"
            content = content.replace(f"[[{image}]]", markdown_link)

            # Copy the image to the static images directory if it exists
            image_source = os.path.join(attachments_dir, image)
            if os.path.exists(image_source):
                shutil.copy(image_source, os.path.join(static_images_dir, image_name))
            else:
                print(f"Warning: Image not found at {image_source}")

        with open(file_path, "w", encoding="utf-8") as md_file:
            md_file.write(content)

print("Markdown files processed and images copied successfully.")
