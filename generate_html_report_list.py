import os

def generate_html_report(directory, output_file):
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
    
    # Write the HTML content to the output file
    with open(output_file, 'w') as f:
        f.write(html_content)

# Define the directory and output file
directory = 'output/heatreports'
output_file = os.path.join(directory, 'index.html')

# Generate the HTML report
generate_html_report(directory, output_file)