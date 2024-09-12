from bs4 import BeautifulSoup

# Step 1: Read the HTML file
with open('LACountyExtremeHeatFactsheet_CONCEPTUALDRAFT.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Step 2: Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Step 3: Prettify the HTML
prettified_html = soup.prettify()

# Step 4: Write the prettified HTML to a new file
with open('Prettified_LACountyExtremeHeatFactsheet.html', 'w', encoding='utf-8') as file:
    file.write(prettified_html)

print("HTML file prettified and saved as 'Prettified_LACountyExtremeHeatFactsheet.html'")