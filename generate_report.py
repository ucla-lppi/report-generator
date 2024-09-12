import geopandas as gpd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import pdfkit
import os
from flask import Flask, send_from_directory

# Use the Agg backend for matplotlib
plt.switch_backend('Agg')

# Step 1: Read the GeoJSON file
geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
gdf = gpd.read_file(geojson_path)

# Step 2: Filter the county data
county_name = 'Siskiyou'  # Change this to the desired county name
county_gdf = gdf[gdf['name'] == county_name]

# Ensure the directory exists
output_dir = 'output_images'
os.makedirs(output_dir, exist_ok=True)

# Step 3: Generate the map highlighting the specific county
fig, ax = plt.subplots(1, 1, figsize=(6, 6))  # Adjust the size as needed
gdf.plot(ax=ax, color='white', edgecolor='black')
county_gdf.plot(ax=ax, color='orange')
ax.set_title(f'{county_name} County Map')
ax.set_axis_off()  # Remove the axis
map_img_path = os.path.join(output_dir, 'county_map.png')
plt.savefig(map_img_path, bbox_inches='tight', pad_inches=0)
plt.close()

# Step 4: Generate infographics
# Example: Create a simple bar chart
data = {'Category': ['A', 'B', 'C'], 'Values': [10, 20, 30]}
df = pd.DataFrame(data)
plt.figure(figsize=(10, 6))
plt.bar(df['Category'], df['Values'], color='skyblue')
plt.title(f'{county_name} County Data')
plt.xlabel('Category')
plt.ylabel('Values')
plt_path = os.path.join(output_dir, 'infographic.png')
plt.savefig(plt_path)
plt.close()

# Step 5: Combine everything into an HTML report
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('report_template.html')

html_content = template.render(
    county_name=county_name,
    map_path=map_img_path,
    plt_path=plt_path
)

report_path = 'county_report.html'
with open(report_path, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"HTML report generated and saved as '{report_path}'")

# Step 6: Serve the HTML file using Flask
app = Flask(__name__)

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    from threading import Timer

    def open_pdf():
        pdf_path = 'county_report.pdf'
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_url('http://127.0.0.1:5000/county_report.html', pdf_path, configuration=config)
        print(f"PDF report generated and saved as '{pdf_path}'")
        os._exit(0)

    Timer(1, open_pdf).start()
    app.run()