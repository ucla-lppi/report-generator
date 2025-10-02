# UCLA LPPI Report Generator API Reference

This document provides detailed API documentation for the ReportGenerator class and related functions.

## ReportGenerator Class

The main interface for generating environmental health disparity reports.

### Constructor

```python
ReportGenerator(config: Optional[Dict] = None)
```

**Parameters:**
- `config` (Dict, optional): Configuration dictionary. If None, uses default settings.

**Default Configuration:**
```python
{
    'output_dir': 'output',
    'geojson_path': 'inputs/geojson/ca_counties_simplified.geojson',
    'population_csv_url': 'https://docs.google.com/spreadsheets/d/...',
    'text_csv_url': 'https://docs.google.com/spreadsheets/d/...',
    'census_tracts_geojson': 'inputs/geojson/ca_census_tracts.geojson',
    'heat_data_csv': 'inputs/heat_data.csv',
    'air_pollution_csv': 'inputs/pm25_binned_data.csv',
    'tract_level_data': 'inputs/tract_level_data.csv',
    'roads_geojson': 'inputs/geojson/ca_primary_secondary_roads.geojson'
}
```

### Methods

#### load_data(offline_mode: bool = False) -> 'ReportGenerator'

Load population and geographic data.

**Parameters:**
- `offline_mode` (bool): If True, skip loading data from Google Sheets URLs

**Returns:**
- Self for method chaining

**Example:**
```python
generator = ReportGenerator()
generator.load_data(offline_mode=False)
```

#### generate_population_charts(counties: Optional[List[str]] = None) -> 'ReportGenerator'

Generate population donut charts for specified counties.

**Parameters:**
- `counties` (List[str], optional): List of county names. If None, generates for all counties.

**Returns:**
- Self for method chaining

**Example:**
```python
generator.generate_population_charts(['Los Angeles', 'San Diego'])
```

#### generate_heat_maps(counties: Optional[List[str]] = None) -> 'ReportGenerator'

Generate extreme heat vulnerability maps.

**Parameters:**
- `counties` (List[str], optional): List of county names. If None, generates for all counties.

**Returns:**
- Self for method chaining

**Example:**
```python
generator.generate_heat_maps(['Los Angeles'])
```

#### generate_air_pollution_maps(counties: Optional[List[str]] = None) -> 'ReportGenerator'

Generate air pollution exposure maps.

**Parameters:**
- `counties` (List[str], optional): List of county names. If None, generates for all counties.

**Returns:**
- Self for method chaining

**Example:**
```python
generator.generate_air_pollution_maps(['San Diego'])
```

#### generate_html_reports(report_type: str = 'all', counties: Optional[List[str]] = None) -> 'ReportGenerator'

Generate HTML reports using Flask templating.

**Parameters:**
- `report_type` (str): Type of report ('extremeheat', 'airpollution', or 'all')
- `counties` (List[str], optional): List of county names. If None, generates for all counties.

**Returns:**
- Self for method chaining

**Example:**
```python
generator.generate_html_reports('extremeheat', ['Los Angeles'])
```

#### generate_pdfs(report_type: str = 'all', counties: Optional[List[str]] = None) -> 'ReportGenerator'

Generate PDF reports from HTML.

**Parameters:**
- `report_type` (str): Type of report ('extremeheat', 'airpollution', or 'all')
- `counties` (List[str], optional): List of county names. If None, generates for all counties.

**Returns:**
- Self for method chaining

**Requirements:**
- wkhtmltopdf must be installed
- geckodriver must be in PATH

**Example:**
```python
generator.generate_pdfs('all', ['Los Angeles'])
```

#### generate_full_report(counties: Optional[List[str]] = None, include_pdfs: bool = True, offline_mode: bool = False) -> Dict

Generate complete reports for specified counties.

**Parameters:**
- `counties` (List[str], optional): List of county names. If None, generates for all available counties.
- `include_pdfs` (bool): Whether to generate PDF outputs (requires additional dependencies)
- `offline_mode` (bool): Whether to run without fetching online data

**Returns:**
- Dictionary with generation results and file paths

**Return Structure:**
```python
{
    'counties_processed': ['Los Angeles', 'San Diego'],
    'output_directory': 'output',
    'files_generated': ['path/to/file1.html', 'path/to/file2.png', ...],
    'error': 'error message if any'  # Optional
}
```

**Example:**
```python
results = generator.generate_full_report(
    counties=['Los Angeles'],
    include_pdfs=False,
    offline_mode=True
)
print(f"Generated {len(results['files_generated'])} files")
```

#### list_available_counties() -> List[str]

Get list of available counties for report generation.

**Returns:**
- List of county names

**Example:**
```python
counties = generator.list_available_counties()
print(f"Available counties: {counties}")
```

#### get_county_summary(county_name: str) -> Dict

Get summary statistics for a specific county.

**Parameters:**
- `county_name` (str): Name of the county

**Returns:**
- Dictionary with county summary data

**Return Structure:**
```python
{
    'county_name': 'Los Angeles',
    'total_population': '10.0M',
    'latino_population': '4.9M',
    'nl_white_population': '2.7M',
    'pct_latino': '49%',
    'pct_nl_white': '27%'
}
```

**Example:**
```python
summary = generator.get_county_summary('Los Angeles')
print(f"Total population: {summary['total_population']}")
```

## Convenience Functions

### generate_reports_for_counties(counties: List[str], output_dir: str = 'output', include_pdfs: bool = True) -> Dict

Convenience function to generate reports for specific counties.

**Parameters:**
- `counties` (List[str]): List of county names
- `output_dir` (str): Output directory path
- `include_pdfs` (bool): Whether to generate PDF outputs

**Returns:**
- Dictionary with generation results

**Example:**
```python
from report_generator import generate_reports_for_counties

results = generate_reports_for_counties(
    counties=['Los Angeles', 'San Diego'],
    output_dir='my_reports',
    include_pdfs=False
)
```

### quick_demo(offline_mode: bool = True) -> Dict

Generate a quick demo report for testing.

**Parameters:**
- `offline_mode` (bool): Run without internet dependencies

**Returns:**
- Dictionary with generation results

**Example:**
```python
from report_generator import quick_demo

demo_results = quick_demo(offline_mode=True)
print(f"Demo generated {len(demo_results['files_generated'])} files")
```

## Method Chaining

The ReportGenerator class supports method chaining for efficient workflows:

```python
results = (ReportGenerator()
    .load_data(offline_mode=False)
    .generate_population_charts(['Los Angeles'])
    .generate_heat_maps(['Los Angeles'])
    .generate_html_reports('extremeheat', ['Los Angeles'])
    .generate_pdfs('extremeheat', ['Los Angeles']))
```

## Error Handling

All methods include comprehensive error handling:

- Network connectivity issues are handled gracefully with offline fallbacks
- Missing data files result in warning messages rather than crashes
- Invalid county names are filtered out automatically
- Dependencies that aren't installed are detected and reported

**Common Error Patterns:**

```python
# Check for errors in results
results = generator.generate_full_report(['Invalid County'])
if 'error' in results:
    print(f"Error occurred: {results['error']}")

# Validate county names
available = generator.list_available_counties()
requested = ['Los Angeles', 'Invalid County']
valid_counties = [c for c in requested if c in available]
```

## Configuration Examples

### Custom Output Directory

```python
config = {
    'output_dir': '/path/to/custom/output',
    'geojson_path': 'custom/path/to/counties.geojson'
}
generator = ReportGenerator(config=config)
```

### Production Configuration

```python
config = {
    'output_dir': '/var/www/reports',
    'population_csv_url': 'https://your-custom-data-source.com/data.csv',
    'census_tracts_geojson': '/data/census_tracts_2020.geojson'
}
generator = ReportGenerator(config=config)
```

### Development/Testing Configuration

```python
config = {
    'output_dir': 'test_output',
    'geojson_path': 'test_data/sample_counties.geojson'
}
generator = ReportGenerator(config=config)
```

## Performance Considerations

### Memory Usage

- Each county report requires approximately 50-100MB of memory during generation
- Process counties in batches of 5-10 for large-scale operations
- Use offline mode when possible to reduce network overhead

### Disk Space

- Each complete county report generates 10-50 files (HTML, PNG, SVG)
- Maps are typically 1-5MB each
- Plan for 50-100MB per county for complete reports

### Processing Time

- Population charts: ~1-2 seconds per county
- Maps: ~30-60 seconds per county (depending on complexity)
- HTML reports: ~5-10 seconds per county
- PDF generation: ~10-30 seconds per county

## Dependencies

### Required Python Packages

See `requirements.txt` for complete list:
- geopandas
- matplotlib  
- pandas
- flask
- jinja2
- contextily
- selenium
- pillow

### System Dependencies (Optional)

For PDF generation:
- wkhtmltopdf
- geckodriver (Firefox WebDriver)

### Data Dependencies

- Input GeoJSON files for geographic boundaries
- CSV files with population and environmental data
- Access to Google Sheets for real-time data (optional)

## Troubleshooting

### Common Issues

**Import Errors:**
```python
# Check dependencies
try:
    from report_generator import ReportGenerator
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("Run: pip install -r requirements.txt")
```

**Data Loading Issues:**
```python
# Test data loading
generator = ReportGenerator()
try:
    generator.load_data(offline_mode=False)
    print("✅ Data loaded successfully")
except Exception as e:
    print(f"❌ Data loading failed: {e}")
    print("Try offline_mode=True for testing")
```

**PDF Generation Issues:**
```python
# Check system dependencies
import shutil
if shutil.which('wkhtmltopdf'):
    print("✅ wkhtmltopdf found")
else:
    print("❌ wkhtmltopdf not found - install from https://wkhtmltopdf.org/")

if shutil.which('geckodriver'):
    print("✅ geckodriver found")
else:
    print("❌ geckodriver not found - download from Mozilla GitHub")
```

### Debugging Tools

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check system diagnostics
generator = ReportGenerator()
print(f"Output directory: {generator.output_dir}")
print(f"Configuration: {generator.config}")

# Validate files exist
import os
required_files = [
    'inputs/geojson/ca_counties_simplified.geojson',
    'templates',
    'static'
]
for file_path in required_files:
    if os.path.exists(file_path):
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path} - Missing required file")
```

## Version History

- **v1.0.0**: Initial refactored version with unified ReportGenerator class
- **v0.x.x**: Original scattered script-based implementation

For more information, see the main README.md and methodology documentation.