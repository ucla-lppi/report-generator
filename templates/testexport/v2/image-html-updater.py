import os
import requests
from bs4 import BeautifulSoup

# File paths
html_file = 'index.html'
images_dir = 'images'

# Create images directory if it doesn't exist
os.makedirs(images_dir, exist_ok=True)

# Read the HTML file
with open(html_file, 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find all img tags with src starting with the specified URL
img_tags = soup.find_all('img', src=lambda x: x and x.startswith('https://c.animaapp.com/'))

for img in img_tags:
    img_url = img['src']
    img_name = os.path.basename(img_url.split('?')[0])  # Remove query params if any
    local_path = os.path.join(images_dir, img_name)
    
    # Download the image
    response = requests.get(img_url)
    if response.status_code == 200:
        with open(local_path, 'wb') as img_file:
            img_file.write(response.content)
        # Update the src attribute to the local path
        img['src'] = os.path.join(images_dir, img_name).replace('\\', '/')
    else:
        print(f'Failed to download {img_url}')

# Write the updated HTML back to the file
with open(html_file, 'w', encoding='utf-8') as file:
    file.write(str(soup))

print('All images downloaded and index.html updated.')