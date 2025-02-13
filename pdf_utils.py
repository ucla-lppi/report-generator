import os
import time
import pdfkit
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from PIL import Image, ImageChops
import requests

def trim(im):
    bg = Image.new(im.mode, im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def check_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"URL {url} is accessible.")
            return True, None
        else:
            error_msg = f"URL {url} returned status code {response.status_code}."
            print(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"Error accessing URL {url}: {e}"
        print(error_msg)
        return False, error_msg

def generate_pdfs(county_name_mapping, output_dir):
    reports_dir = os.path.join(output_dir, "heatreports")
    pdf_output_dir = os.path.join(output_dir, "pdf_reports")
    os.makedirs(pdf_output_dir, exist_ok=True)

    # Set up Firefox options for headless mode.
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.set_preference("layout.css.devPixelsPerPx", "2.0")
    driver = webdriver.Firefox(options=firefox_options)  # Ensure geckodriver is in your PATH
    driver.set_window_size(2550, 3300)
    
    # Options for wkhtmltopdf via pdfkit
    pdfkit_options = {
        'page-size': 'Letter',
        'margin-top': '0in',
        'margin-right': '0in',
        'margin-bottom': '0in',
        'margin-left': '0in',
        'encoding': "UTF-8",
        'disable-smart-shrinking': '',
		'enable-local-file-access': '',
        'zoom': '1.3'
    }
    
    for original_county_name, standardized_county_name in county_name_mapping.items():
        screenshot_paths = []
        for page in [1, 2]:
            html_file = os.path.join(reports_dir, f'{standardized_county_name}_page{page}.html')
            if not os.path.exists(html_file):
                print(f"HTML file not found: {html_file}")
                continue

            file_url = f'http://127.0.0.1:5000/county_report/extremeheat/{standardized_county_name}.html?page={page}'
            driver.get(file_url)
            time.sleep(2)  # Wait for page to load; adjust delay if needed

            # Optionally set window size to capture the full page.
            driver.set_window_size(1200, 1600)
            screenshot_path = os.path.join(pdf_output_dir, f'{standardized_county_name}_page{page}.png')
            driver.save_screenshot(screenshot_path)
            print(f"Saved screenshot: {screenshot_path}")
            screenshot_paths.append(screenshot_path)

        if len(screenshot_paths) < 2:
            print(f"Not all screenshots found for {standardized_county_name}; skipping PDF generation.")
            continue

        # Process each screenshot with Pillow (optionally trim white space)
        processed_image_paths = []
        for idx, img_path in enumerate(screenshot_paths, start=1):
            img = Image.open(img_path).convert('RGB')
            img = trim(img)  # Trim extra white space from the image
            processed_path = os.path.join(pdf_output_dir, f'{standardized_county_name}_trimmed_page{idx}.png')
            img.save(processed_path)
            processed_image_paths.append(processed_path)
            print(f"Saved processed image: {processed_path}")

        # Create an HTML string that embeds each image.
        # The style "page-break-after: always" ensures each image is on its own PDF page.
        html_string = """
<html>
<head>
  <style>
    body { margin: 0; padding: 0; }
    img { width: 100%; display: block; }
    .page-break { page-break-after: always; }
  </style>
</head>
<body>
"""
        for image_path in processed_image_paths:
            # Use file URI scheme (ensure forward slashes)
            file_uri = "file:///" + os.path.abspath(image_path).replace("\\", "/")
            html_string += f'<img src="{file_uri}"><div class="page-break"></div>'
        html_string += "</body></html>"

        final_pdf_path = os.path.join(pdf_output_dir, f'{standardized_county_name}_extreme_heat.pdf')
        try:
            pdfkit.from_string(html_string, final_pdf_path, options=pdfkit_options)
            print(f"Saved merged PDF for county {standardized_county_name}: {final_pdf_path}")
        except Exception as e:
            print(f"Error generating PDF for {standardized_county_name}: {e}")

    driver.quit()