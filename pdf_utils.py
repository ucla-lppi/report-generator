import pdfkit
import os
import requests

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
    for original_county_name, standardized_county_name in county_name_mapping.items():
        url = f'http://127.0.0.1:5000/county_report/{standardized_county_name}.html'
        accessible, err = check_url(url)
        if accessible:
            pdf_path = os.path.join(output_dir, f'{standardized_county_name}_extreme_heat.pdf')
            try:
                pdfkit.from_url(url, pdf_path)
                print(f"PDF report generated and saved as '{pdf_path}'")
            except Exception as e:
                print(f"Failed to generate PDF for {standardized_county_name}: {e}")
        else:
            print(f"Skipping PDF generation for {standardized_county_name} due to URL access issue.")