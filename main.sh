#!/bin/bash
set -euo pipefail

# Configuration file to store paths
CONFIG_FILE="$HOME/.obsidian_to_hugo_config"

# Sets up the Path Variables for the first time and saves it to a config file
setup_config() {
    echo "Nyan! First time running the script? Let's set up the Path variables for you ~"
    echo "Please provide the following paths:"

    read -p "Enter the full path to your Obsidian vault's Blog folder: " sourcePath
    read -p "Enter the full path to your Hugo content/posts folder: " destinationPath
    read -p "Enter the Git repository URL (e.g., https://github.com/your-username/your-repo.git): " myrepo
    echo "Saving the paths for you cutie~~~"

    # Save paths and Git repo to the config file in INI format
    {
        echo "[Paths]"
        echo "sourcePath=$sourcePath"
        echo "destinationPath=$destinationPath"
        echo ""
        echo "[Git]"
        echo "myrepo=$myrepo"
    } > "$CONFIG_FILE"

    echo "Paths has been saved to $CONFIG_FILE , continuing..."
}

# Load paths from the config file
if [ -f "$CONFIG_FILE" ]; then
    source <(grep '=' "$CONFIG_FILE")  # Load key-value pairs into the shell environment
else
    setup_config
fi


# Check for required commands
for cmd in git rsync python3 hugo; do
    if ! command -v $cmd &> /dev/null; then
        echo "$cmd is not installed or not in PATH."
        exit 1
    fi
done

# Step 1: Check if Git is initialized, and initialize if necessary
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    git remote add origin $myrepo
else
    echo "Git repository already initialized."
    if ! git remote | grep -q 'origin'; then
        echo "Adding remote origin..."
        git remote add origin $myrepo
    fi
fi

sleep 1

# Step 2: Sync posts from Obsidian to Hugo content folder using rsync
echo "Syncing posts from Obsidian..."

if [ ! -d "$sourcePath" ]; then
    echo "Source path does not exist: $sourcePath"
    exit 1
fi

if [ ! -d "$destinationPath" ]; then
    echo "Destination path does not exist: $destinationPath"
    exit 1
fi


rsync -av --delete "$sourcePath" "$destinationPath"
sleep 2 

# Step 3: Process Markdown files with Python script to handle image links
echo "Processing image links in Markdown files..."
if [ ! -f "process_images.py" ]; then
    echo "Python script process_images.py not found."
    exit 1
fi
sleep 1 

if ! python3 process_images.py; then
    echo "Failed to process image links."
    exit 1
fi

# Step 4: Build the Hugo site
echo "Building the Hugo site..."
if ! hugo; then
    echo "Hugo build failed."
    exit 1
fi

# Step 5: Add changes to Git
echo "Staging changes for Git..."
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes to stage."
else
    git add .
fi

# Step 6: Commit changes with a dynamic message
commit_message="Posting new blog on $(date +'%Y-%m-%d %H:%M:%S')"
if git diff --cached --quiet; then
    echo "No changes to commit."
else
    echo "Committing..."
    git commit -m "$commit_message"
fi

# Step 7: Push all changes to the main branch
echo "Deploying to GitHub Main..."
if ! git push origin master; then
    echo "Failed to push to main branch."
    exit 1
fi

# Step 8: Deploy to Netlify
echo "Deploying to Netlify..."
if ! netlify deploy --prod; then
    echo "Failed to deploy to Netlify."
    exit 1
fi

echo "All done! Site synced, processed, committed, built, and deployed."