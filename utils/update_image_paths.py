import os
import shutil
from bs4 import BeautifulSoup

def update_img_src_paths(html_file_path, static_subdir='extremeheat'):
    """
    Updates the src attributes of all <img> tags in the given HTML file
    to use Flask's url_for for static file referencing.

    Args:
        html_file_path (str): Path to the HTML file to be updated.
        static_subdir (str): Subdirectory under 'static/' where images are stored.
                             Default is 'extremeheat'.
    """
    # Ensure the HTML file exists
    if not os.path.isfile(html_file_path):
        print(f"Error: The file {html_file_path} does not exist.")
        return

    # Create a backup of the original HTML file
    backup_path = f"{html_file_path}.backup"
    shutil.copy(html_file_path, backup_path)
    print(f"Backup created at {backup_path}")

    # Read the original HTML content
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find all <img> tags
    img_tags = soup.find_all('img')

    # Counter for tracking updates
    updated_count = 0

    for img in img_tags:
        src = img.get('src', '')
        # Check if src starts with 'images/' or './images/' or similar
        if src.startswith('images/') or src.startswith('./images/') or src.startswith('../images/'):
            # Extract the image file name
            image_filename = os.path.basename(src)
            # Construct the new src using url_for
            new_src = "{{ url_for('static', filename='"
            # Adjust the path based on the static_subdir
            # If original src had subdirectories, preserve them
            relative_path = os.path.relpath(src, 'images')
            if relative_path == '.':
                relative_path = image_filename
            new_src += f"{static_subdir}/images/{relative_path}"
            new_src += "') }}"
            # Update the src attribute
            img['src'] = new_src
            updated_count += 1
            print(f"Updated <img> tag: {src} -> {new_src}")

    # Write the updated HTML back to the file
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup.prettify()))

    print(f"Total <img> tags updated: {updated_count}")

if __name__ == "__main__":
    # Define the path to your index.html file
    html_file = os.path.join('..','templates', 'extremeheat', 'index.html')

    # Call the function to update image src paths
    update_img_src_paths(html_file, static_subdir='extremeheat')