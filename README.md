# Report Generator

This project generates a PDF report for a specified county using GeoJSON data and infographics. The report includes a map highlighting the county and a bar chart with sample data.

## Features

- Generates a map highlighting a specific county.
- Creates a bar chart with sample data.
- Combines the map and bar chart into an HTML report.
- Converts the HTML report to a PDF.

## Requirements

- Python 3.6+
- `geopandas`
- `matplotlib`
- `jinja2`
- `pandas`
- `pdfkit`
- `flask`
- `wkhtmltopdf`

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/report-generator.git
   cd report-generator
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Install `wkhtmltopdf`:
   - For Ubuntu:
	 ```sh
	 sudo apt-get install wkhtmltopdf
	 ```
   - For macOS:
	 ```sh
	 brew install wkhtmltopdf
	 ```
   - For Windows:
	 - Download the installer from the [wkhtmltopdf website](https://wkhtmltopdf.org/downloads.html).
	 - Add the installation directory to the system PATH.
	 - Restart the terminal.
	 - Verify the installation by running `wkhtmltopdf --version`.
	- If the installation was successful, you should see the version number.

## Usage

Run the script:
```sh
python python main.py build
```

• `python main.py build -t extremeheat`  
• `python main.py build -t airpollution`  
• `python main.py build`  (or `-t all`) to generate both.

Make sure geckodriver is up to date and in your PATH. You can download it from [here](https://github.com/mozilla/geckodriver/releases).