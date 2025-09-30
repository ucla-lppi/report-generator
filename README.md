# UCLA LPPI Report Generator

This repository contains tools for generating comprehensive environmental health disparity reports that compare conditions between Latino and Non-Latino White populations across California counties. The reports analyze extreme heat exposure, air pollution, and related health outcomes.

## What This Tool Does

The UCLA LPPI Report Generator creates comprehensive reports that include:

- **Population Demographics**: Donut charts showing population composition by ethnicity
- **Environmental Heat Maps**: Geographic visualization of extreme heat exposure disparities  
- **Air Pollution Maps**: Geographic visualization of air quality disparities
- **Statistical Comparisons**: Detailed analysis of health and environmental indicators
- **Multi-format Outputs**: HTML reports and PDF exports for sharing and publication

## Quick Start

### Requirements

- Python 3.8+
- Jupyter Notebook
- Required Python packages (see `requirements.txt`)

### Jupyter Notebooks

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch Jupyter and open the Quick Start Guide:**
   ```bash
   jupyter notebook notebooks/01_Quick_Start_Guide.ipynb
   ```

3. **Follow the step-by-step instructions** in the notebook to generate your first reports.

### For Developers and Researchers

Use the unified `ReportGenerator` class for programmatic access:

```python
from report_generator import ReportGenerator

# Initialize the generator
generator = ReportGenerator()

# Load data
generator.load_data(offline_mode=False)  # Set to True for demo mode

# Generate complete reports for specific counties
results = generator.generate_full_report(
    counties=['Los Angeles', 'San Diego'],
    include_pdfs=True,
    offline_mode=False
)

print(f"Generated {len(results['files_generated'])} files")
```

## Prerequisites

### Required Software
- **Python 3.8+**
- **Git** (for cloning the repository)

### For PDF Generation (Optional)
- **wkhtmltopdf**: [Download here](https://wkhtmltopdf.org/downloads.html)
- **geckodriver**: [Download here](https://github.com/mozilla/geckodriver/releases) and add to PATH

### System Requirements
- **Memory**: 4GB+ RAM recommended for processing multiple counties
- **Storage**: 1GB+ free space for generated reports and maps
- **Network**: Internet connectivity for real data (offline mode available for testing)

## Installation

### Standard Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ucla-lppi/report-generator.git
   cd report-generator
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies (optional, for PDF generation):**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install wkhtmltopdf firefox-geckodriver
   ```
   
   **macOS:**
   ```bash
   brew install wkhtmltopdf geckodriver
   ```
   
   **Windows:**
   - Download and install wkhtmltopdf from [official website](https://wkhtmltopdf.org/downloads.html)
   - Download geckodriver and add to PATH
   - Restart terminal after installation

### Verification

Test your installation:
```bash
python -c "from report_generator import quick_demo; quick_demo(offline_mode=True)"
```

## Usage Guide

### Command Line Interface

Generate reports using the original interface:

```bash
# Generate all report types for all counties
python main.py build

# Generate specific report type
python main.py build -t extremeheat
python main.py build -t airpollution

# Serve reports locally for preview
python main.py serve
```

### New Unified Interface

Use the simplified ReportGenerator class:

```python
from report_generator import ReportGenerator

# Quick demo (offline mode)
from report_generator import quick_demo
results = quick_demo(offline_mode=True)

# Full workflow
generator = ReportGenerator()
generator.load_data()

# Generate step by step
generator.generate_population_charts(['Los Angeles'])
generator.generate_heat_maps(['Los Angeles']) 
generator.generate_air_pollution_maps(['Los Angeles'])
generator.generate_html_reports('all', ['Los Angeles'])
generator.generate_pdfs('all', ['Los Angeles'])

# Or generate everything at once
results = generator.generate_full_report(
    counties=['Los Angeles', 'San Diego'],
    include_pdfs=True
)
```

### Jupyter Notebooks

Two notebooks are provided for different skill levels:

1. **`notebooks/01_Quick_Start_Guide.ipynb`**: For beginners and non-technical users
2. **`notebooks/02_Advanced_Usage.ipynb`**: For researchers and power users

Launch Jupyter:
```bash
jupyter notebook
```

Then navigate to the `notebooks/` folder and open the appropriate guide.

## Project Structure

```
report-generator/
├── 📄 report_generator.py          # Main unified interface (NEW)
├── 📁 notebooks/                   # Jupyter notebooks for easy use (NEW)
│   ├── 01_Quick_Start_Guide.ipynb
│   └── 02_Advanced_Usage.ipynb
├── 📄 main.py                      # Original command-line interface
├── 📄 flask_app.py                 # Web interface for report generation
├── 📄 data_utils.py                # Data loading and processing utilities
├── 📄 map_utils.py                 # Geographic map generation
├── 📄 pdf_utils.py                 # PDF export functionality
├── 📄 generate_donuts.py           # Population chart generation
├── 📁 inputs/                      # Input data files
│   ├── 📁 geojson/                # Geographic boundary files
│   └── 📄 *.csv                   # Statistical data files
├── 📁 output/                      # Generated reports and files
├── 📁 templates/                   # HTML templates for reports
├── 📁 static/                      # CSS, fonts, and assets
├── 📁 tests/                       # Test files
│   ├── test_pdf_utils.py
│   ├── test_heat_maps.py
│   └── test_air_pollution_maps.py
└── 📄 requirements.txt             # Python dependencies
```

## Workflow Overview

The report generation follows this process:

1. **Data Loading**: 
   - Population demographics from Google Sheets
   - Geographic boundaries from GeoJSON files
   - Environmental data from CSV files

2. **Chart Generation**:
   - Population donut charts showing ethnic composition
   - Statistical summaries for each county

3. **Map Generation**:
   - Heat exposure maps showing geographic disparities
   - Air pollution exposure maps
   - Neighborhood-level analysis comparing Latino and Non-Latino White areas

4. **Report Assembly**:
   - HTML reports using Flask/Jinja2 templates
   - Multi-page layouts with embedded charts and maps
   - Statistical narratives generated from data

5. **Export**:
   - Static HTML files for web deployment
   - PDF exports for printing and sharing

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Test PDF generation
python -m unittest test_pdf_utils.py

# Test heat map generation  
python -m unittest test_heat_maps.py

# Test air pollution map generation
python -m unittest test_air_pollution_maps.py

# Run all tests
python -m unittest discover -s . -p "test_*.py"
```

## Configuration

### Environment Variables

Set these for production use:

```bash
# For GitHub Pages deployment
export GITHUB_PAGES=true

# Custom data URLs
export POPULATION_DATA_URL="your-google-sheets-url"
export HEAT_DATA_URL="your-heat-data-url"
```

### Custom Configuration

```python
custom_config = {
    'output_dir': 'custom_output',
    'population_csv_url': 'your-custom-url',
    'geojson_path': 'path/to/your/boundaries.geojson'
}

generator = ReportGenerator(config=custom_config)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for any API changes
- Use meaningful commit messages

## Additional Documentation

- **[Methodology Guide](docs/methodology.md)**: Detailed explanation of the analysis approach for researchers and policymakers
- **[API Reference](docs/api.md)**: Complete documentation of the ReportGenerator class
- **[Data Sources](docs/data-sources.md)**: Information about input data requirements and formats

## Troubleshooting

### Common Issues

**Import Error**: Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

**PDF Generation Fails**: Install wkhtmltopdf and geckodriver, ensure they're in PATH

**Map Generation Errors**: Verify input GeoJSON and CSV files exist and are properly formatted

**Memory Issues**: Process counties in smaller batches, especially for large datasets

**Network Errors**: Use `offline_mode=True` for testing without internet connectivity

### Getting Help

1. Check the [Issues page](https://github.com/ucla-lppi/report-generator/issues) for known problems
2. Review the Jupyter notebooks for step-by-step guidance
3. Run the diagnostic tools in the Advanced Usage notebook
4. Contact the development team for persistent issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **UCLA Latino Policy and Politics Institute (LPPI)**: Primary funding and research guidance
- **Data Sources**: California government agencies, U.S. Census Bureau, environmental monitoring networks
- **Technical Contributors**: Research staff and graduate students at UCLA LPPI

## Citation

If you use this tool in research or policy work, please cite:

```
UCLA Latino Policy and Politics Institute. (2024). Environmental Health Report Generator. 
GitHub. https://github.com/ucla-lppi/report-generator
```

---

**For technical support or collaboration inquiries, please contact the UCLA LPPI research team.**