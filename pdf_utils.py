import pdfkit
import os
import requests
import openai

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

def generate_openai_content(prompt):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OpenAI API key is not set.")
        return None

    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating text with OpenAI: {e}")
        return None

def generate_pdfs(county_name_mapping, output_dir, use_openai=False):
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'enable-local-file-access': None,
        'no-outline': None,
        'print-media-type': None,
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'quiet': '',
        'footer-right': '[page]',  # Add page numbers to the footer
        'footer-font-size': '12'
    }

    for original_county_name, standardized_county_name in county_name_mapping.items():
        url = f'http://127.0.0.1:5000/county_report/{standardized_county_name}.html'
        if check_url(url):
            pdf_path = os.path.join(output_dir, f'{standardized_county_name}_extreme_heat.pdf')
            
            if use_openai:
                prompt = f"Generate a report for {original_county_name} county."
                openai_content = generate_openai_content(prompt)
                if openai_content:
                    # Save the OpenAI content to a temporary HTML file
                    temp_html_path = os.path.join(output_dir, f'{standardized_county_name}_temp.html')
                    with open(temp_html_path, 'w', encoding='utf-8') as temp_html_file:
                        temp_html_file.write(openai_content)
                    pdfkit.from_file(temp_html_path, pdf_path, configuration=config, options=options)
                    os.remove(temp_html_path)
                else:
                    print(f"Skipping PDF generation for {standardized_county_name} due to OpenAI content generation issue.")
            else:
                pdfkit.from_url(url, pdf_path, configuration=config, options=options)
            
            print(f"PDF report generated and saved as '{pdf_path}'")
        else:
            print(f"Skipping PDF generation for {standardized_county_name} due to URL access issue.")