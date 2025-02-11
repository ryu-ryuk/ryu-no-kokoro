import os
import re
import shutil
import configparser
import logging

# Setting up logging function

logging.basicConfig(filename="image_processing.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration from INI file ~ from the bash script
CONFIG_FILE = os.path.expanduser("~/.obsidian_to_hugo_config")

if not os.path.exists(CONFIG_FILE):
  logging.error(f"Config files don't exist! Please run the main.sh script first")
  exit 1

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Create the images directory for hugo to retrieve

# mkdir -p static/images

# Parse the config
try:
    posts_dir = config.get("Paths", "sourcePath")
    attachments_dir = config.get("Paths", "sourcePath")  # Assuming attachments are in the same folder
    static_images_dir = os.path.join(config.get("Paths", "destinationPath"), "static/images/")

except configparser.NoOptionError as e:
    logging.error(f"Missing configuration option: {e}")
    exit(1)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

# Ensuring static images directory exists
os.makedirs(static_images_dir, exist_ok=True)

# Ensure Validity of the image
def is_valid_image(filename):
    """Check if the file has a valid image extension."""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def find_image_file(image_name, base_dir, max_depth=3):
    """Find an image file in the attachments directory, limiting depth of the search"""
    
    if not is_valid_image(image_name):
      logger.warning(f"Blocked invalid image file")
      return None

    direct_path = os.path.join(base_dir, image_name)
    if os.path exists(direct_path):
      return direct_path

# Using 'os.sep' for seamless integration among different systems
    for root, _, files in os.walk(base_dir):
        if root.count(os.sep) - base_dir.count(os.sep) >= max_depth:
          continue # Preventing deep recursion


        if image_name in files:
            return os.path.join(root, image_name)
    
    return None

# Process Markdown files in the blog directory
for filename in os.listdir(posts_dir):

    # Scanning posts directory for markdown files
    if filename.endswith(".md"):
        filepath = os.path.join(posts_dir, filename)

        try:
            # Reads the entire markdown file
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            logging.error(f"Failed to read {filepath}: {e}")
            continue
        # Searches for Obsidian style formatted image links in the markdown files

        images = re.findall(r'([^]]*\.(?:png|jpg|jpeg|gif|webp))', content, re.IGNORECASE)

        # Converting those Obsidian formatted image links for Hugo Compatibility

        for image in images:
            image_basename = os.path.basename(image)
            markdown_image = f"![{image_basename}](/images/{image_basename.replace(' ', '%20')})"
            content = content.replace(f"[[{image}]]", markdown_image)

            # Locating image files and copying it over to Static/Images folder

            image_file = find_image_file(image_basename, attachments_dir)

            if image_file:
                try:

                    # Usinf shutil.copy 2 to preserve metadata
                    shutil.copy2(image_file, os.path.join(static_images_dir, image_basename))
                    logging.info(f"Copied {image_file} to {static_images_dir}")
                except PermissionError:
                    logging.error(f"Permission denied when copying {image_file}")
                except Exception as e:
                    logging.error(f"Failed to copy {image_file}: {e}")
            else:
                logging.warning(f"Could not locate image file: {image_basename}")

        # Writing the modified image link to the markdown file and updating content
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
        except Exception as e:
            logging.error(f"Failed to write to {filepath}: {e}")

logging.info("Markdown files processed and images copied successfully.")

