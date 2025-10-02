import os

def generate_html_report(directory):
    # Get the list of files in the directory
    files = os.listdir(directory)
    
    # Start the HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Heat Reports</title>
    </head>
    <body>
        <h1>Heat Reports</h1>
        <ul>
    """
    
    # Add each file as a list item
    for file in files:
        if file.endswith('.html'):
            html_content += f'<li><a href="{file}">{file}</a></li>\n'
    
    # Close the HTML content
    html_content += """
        </ul>
    </body>
    </html>
    """
    output_file = os.path.join(directory, 'index.html')
    # Write the HTML content to the output file
    with open(output_file, 'w') as f:
        f.write(html_content)

# Define the directory and output file
extremeheat_2025_reports_directory = '../output/heatreports'
airpollution_2025_reports_directory = '../output/airpollution'


# Generate the HTML reports
generate_html_report(extremeheat_2025_reports_directory)
generate_html_report(airpollution_2025_reports_directory)

