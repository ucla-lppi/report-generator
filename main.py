import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import pdfkit
import os
from flask import Flask, render_template, send_from_directory

# Use the Agg backend for matplotlib
plt.switch_backend('Agg')

# Step 1: Read the GeoJSON file
geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
gdf = gpd.read_file(geojson_path)

# Ensure the directories exist
output_dir = 'output'
map_dir = os.path.join(output_dir, 'maps')
img_dir = os.path.join(output_dir, 'imgs')
os.makedirs(map_dir, exist_ok=True)
os.makedirs(img_dir, exist_ok=True)

# Step 5: Fetch and parse population data from Google Spreadsheet
csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?output=csv'
pop_data = pd.read_csv(csv_url)

# Remove commas from relevant columns
pop_data['pop'] = pop_data['pop'].str.replace(',', '')
pop_data['latino'] = pop_data['latino'].str.replace(',', '')
pop_data['nlw'] = pop_data['nlw'].str.replace(',', '')

# Convert relevant columns to numeric types
pop_data['pop'] = pd.to_numeric(pop_data['pop'], errors='coerce')
pop_data['latino'] = pd.to_numeric(pop_data['latino'], errors='coerce')
pop_data['nlw'] = pd.to_numeric(pop_data['nlw'], errors='coerce')
pop_data['pct_latino'] = pd.to_numeric(pop_data['pct_latino'], errors='coerce')
pop_data['pct_nlw'] = pd.to_numeric(pop_data['pct_nlw'], errors='coerce')

# Create a mapping of standardized county names to original names
county_name_mapping = {name: name.replace(' ', '_') for name in pop_data['county_name'].unique()}

# Step 6: Serve the HTML file using Flask
app = Flask(__name__, template_folder='template')

@app.route('/county_report/<standardized_county_name>.html')
def county_report(standardized_county_name):
    original_county_name = next(key for key, value in county_name_mapping.items() if value == standardized_county_name)
    county_gdf = gdf[gdf['name'] == original_county_name]
    
    # Generate the map highlighting the specific county
    fig, ax = plt.subplots(1, 1, figsize=(6, 6))  # Adjust the size as needed
    gdf.plot(ax=ax, color='white', edgecolor='gray', linewidth=0.5)
    county_gdf.plot(ax=ax, color='#005587')  # UCLA blue
    ax.set_axis_off()  # Remove the axis
    map_img_path = os.path.join(map_dir, f'{standardized_county_name}_map.png')
    plt.savefig(map_img_path, bbox_inches='tight', pad_inches=0)
    plt.close()
    
    # Generate infographics
    # Example: Create a simple bar chart
    data = {'Category': ['A', 'B', 'C'], 'Values': [10, 20, 30]}
    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 6))
    plt.bar(df['Category'], df['Values'], color='skyblue')
    plt.title(f'{original_county_name} County Data')
    plt.xlabel('Category')
    plt.ylabel('Values')
    plt_path = os.path.join(img_dir, f'{standardized_county_name}_infographic.png')
    plt.savefig(plt_path)
    plt.close()
    
    county_pop_data = pop_data[pop_data['county_name'] == original_county_name].iloc[0]
    
    total_pop = round(county_pop_data['pop'] / 1_000_000, 1)
    latino_pop = round(county_pop_data['latino'] / 1_000_000, 1)
    nlw_pop = round(county_pop_data['nlw'] / 1_000_000, 1)
    pct_latino = int(county_pop_data['pct_latino'] * 100)
    pct_nlw = int(county_pop_data['pct_nlw'] * 100)
    ranking_by_latino_county = county_pop_data['ranking_by_latino_county']
    
    # Extract county statistics
    county_statistics = {
        'Median Age': {
            'Latino': county_pop_data['median_age_hispanic'],
            'NL White': county_pop_data['median_age_white'],
            'Total': county_pop_data['median_age_total']
        },
        'Non-U.S. Citizen Population': {
            'Latino': f"{county_pop_data['percent_hispanic_non_citizens']}%",
            'NL White': f"{county_pop_data['percent_white_non_citizens']}%",
            'Total': f"{county_pop_data['percent_total_non_citizens']}%"
        },
        'Limited English Proficiency': {
            'Latino': f"{county_pop_data['percent_hispanic_less_english']}%",
            'NL White': f"{county_pop_data['percent_white_less_english']}%",
            'Total': f"{county_pop_data['percent_total_less_english']}%"
        },
        'Median Household Income': {
            'Latino': f"${county_pop_data['median_income_hispanic']:,}",
            'NL White': f"${county_pop_data['median_income_white']:,}",
            'Total': f"${county_pop_data['median_income_total']:,}"
        },
        'Poverty Rate': {
            'Latino': f"{county_pop_data['percent_hispanic_poverty']}%",
            'NL White': f"{county_pop_data['percent_white_poverty']}%",
            'Total': f"{county_pop_data['percent_total_poverty']}%"
        },
        'No Health Insurance': {
            'Latino': f"{county_pop_data['percent_hispanic_no_insurance']}%",
            'NL White': f"{county_pop_data['percent_white_no_insurance']}%",
            'Total': f"{county_pop_data['percent_total_county_no_insurance']}%"
        },
        'Renter Occupied Households': {
            'Latino': f"{county_pop_data['percent_hispanic_renter']}%",
            'NL White': f"{county_pop_data['percent_white_renter']}%",
            'Total': f"{county_pop_data['percent_total_renter']}%"
        },
        'SNAP benefits': {
            'Latino': f"{county_pop_data['percent_hispanic_snap']}%",
            'NL White': f"{county_pop_data['percent_white_snap']}%",
            'Total': f"{county_pop_data['percent_total_snap']}%"
        },
        'Food Insecurity': {
            'Latino': f"{county_pop_data['latino_food_insecure']}%",
            'NL White': f"{county_pop_data['nl_white_food_insecure']}%",
            'Total': f"{county_pop_data['all_food_insecure']}%"
        },
        'Self-Reported Health Status (Fair or Poor)': {
            'Latino': f"{county_pop_data['latino_fair_poor']}%",
            'NL White': f"{county_pop_data['nl_white_fair_or_poor']}%",
            'Total': f"{county_pop_data['all_fair_or_poor']}%"
        }
    }
    
    return render_template(
        'template.html',
        county_name=original_county_name,
        map_path=f'/output/maps/{standardized_county_name}_map.png',
        plt_path=f'/output/imgs/{standardized_county_name}_infographic.png',
        total_pop=total_pop,
        latino_pop=latino_pop,
        nlw_pop=nlw_pop,
        pct_latino=pct_latino,
        pct_nlw=pct_nlw,
        ranking_by_latino_county=ranking_by_latino_county,
        county_statistics=county_statistics
    )

@app.route('/output/<path:filename>')
def serve_output_file(filename):
    return send_from_directory('output', filename)

if __name__ == '__main__':
    from threading import Timer

    def generate_pdfs():
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
            pdf_path = os.path.join(output_dir, f'{standardized_county_name}_extreme_heat.pdf')
            pdfkit.from_url(f'http://127.0.0.1:5000/county_report/{standardized_county_name}.html', pdf_path, configuration=config, options=options)
            print(f"PDF report generated and saved as '{pdf_path}'")
        
        os._exit(0)
    
    Timer(1, generate_pdfs).start()
    app.run()