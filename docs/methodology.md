# Environmental Health Disparities Analysis Methodology

## Overview

This document explains the methodology used by the UCLA Latino Policy and Politics Institute (LPPI) to analyze environmental health disparities between Latino and Non-Latino White populations across California counties. The analysis focuses on two primary environmental hazards: extreme heat exposure and air pollution.

## Background and Purpose

Environmental health disparities refer to differences in environmental exposures and related health outcomes between different population groups. Research consistently shows that communities of color, including Latino populations, often face disproportionate exposure to environmental hazards due to historical patterns of residential segregation, discriminatory housing policies, and unequal distribution of industrial facilities.

This analysis tool was developed to:
- **Quantify disparities** in environmental exposures between Latino and Non-Latino White populations
- **Visualize geographic patterns** of environmental hazards at the neighborhood level
- **Support policy development** with data-driven evidence of environmental justice issues
- **Inform community advocacy** with accessible reports and visualizations

## Data Sources and Geographic Scope

### Geographic Units
The analysis uses **census tracts** as the primary geographic unit. Census tracts are small, relatively permanent statistical subdivisions of counties containing approximately 2,500 to 8,000 residents. This fine-grained geographic resolution allows for neighborhood-level analysis while maintaining statistical reliability.

### Population Data
Population demographics come from the **American Community Survey (ACS)**, which provides detailed demographic information including:
- Total population by race and ethnicity
- Age distributions
- Income and poverty statistics
- Housing characteristics
- Health insurance coverage

### Environmental Data Sources

**Extreme Heat Data:**
- Historical temperature records from meteorological stations
- Climate projections from downscaled global climate models
- Urban heat island intensity measurements
- Land surface temperature data from satellite imagery

**Air Pollution Data:**
- PM2.5 (fine particulate matter) concentrations from monitoring networks
- Diesel particulate matter estimates
- Traffic density measurements
- Proximity to pollution sources (highways, industrial facilities)

### Health Outcome Data
Health indicators come from:
- California Department of Public Health databases
- Hospital discharge records
- Emergency department visit records
- Community health surveys

## Analytical Framework

### Neighborhood Classification

Census tracts are classified into demographic categories based on population composition:

- **Latino Neighborhoods**: Areas where Latino residents comprise 50% or more of the population
- **Majority Latino Neighborhoods**: Areas where Latino residents comprise 70% or more of the population  
- **Non-Latino White Neighborhoods**: Areas where Non-Latino White residents comprise 50% or more of the population
- **Mixed/Other Neighborhoods**: Areas not meeting the above criteria

This classification allows for direct comparison of environmental conditions between predominantly Latino and predominantly Non-Latino White communities.

### Environmental Exposure Assessment

**Heat Exposure Metrics:**
1. **Historical Heat Days**: Average annual days with maximum temperature ≥ 90°F
2. **Heat Wave Duration**: Average length of consecutive days ≥ 90°F
3. **Future Projections**: Projected heat days under mid-century (2035-2064) and end-century (2070-2099) climate scenarios
4. **Extreme Heat Events**: Days exceeding 100°F, which pose severe health risks

**Air Pollution Metrics:**
1. **PM2.5 Concentrations**: Annual average fine particulate matter levels
2. **Diesel Pollution**: Estimated diesel particulate matter exposure
3. **Traffic Proximity**: Distance to major roadways and traffic density
4. **Industrial Sources**: Proximity to refineries, power plants, and other emission sources

### Statistical Analysis

The analysis employs several statistical approaches:

1. **Descriptive Statistics**: Mean, median, and range calculations for each exposure metric by demographic group
2. **Comparative Analysis**: Direct comparison of exposure levels between Latino and Non-Latino White neighborhoods
3. **Spatial Analysis**: Geographic clustering and hotspot identification
4. **Vulnerability Assessment**: Integration of exposure data with demographic factors that increase susceptibility (age, poverty, health status)

### Health Impact Assessment

The methodology incorporates health outcome data to demonstrate the connection between environmental exposures and health disparities:

**Heat-Related Health Impacts:**
- Emergency department visits for heat-related illness
- Cardiovascular disease hospitalizations during heat waves
- Respiratory disease exacerbations
- Mortality during extreme heat events

**Air Pollution Health Impacts:**
- Asthma hospitalization rates
- Cardiovascular disease incidence
- Respiratory symptoms and lung function
- Birth outcomes (low birth weight, preterm birth)

## Visualization and Mapping Approach

### Geographic Mapping
Maps are created using Geographic Information Systems (GIS) to show:
- **Neighborhood Boundaries**: Census tract outlines with demographic classification
- **Exposure Gradients**: Color-coded representation of environmental hazard levels
- **Latino Community Overlay**: Special marking to highlight predominantly Latino areas
- **Transportation Networks**: Major highways and roads that contribute to pollution
- **Landmark References**: Cities and recognizable geographic features for orientation

### Statistical Charts
Population and exposure data are presented through:
- **Donut Charts**: Showing demographic composition of each county
- **Bar Charts**: Comparing exposure levels between demographic groups
- **Time Series**: Showing trends and future projections
- **Summary Statistics Tables**: Detailed numerical comparisons

## Quality Assurance and Limitations

### Data Quality Measures
- **Validation**: Cross-checking against multiple data sources where possible
- **Uncertainty Analysis**: Acknowledging margins of error in estimates
- **Temporal Consistency**: Using data from consistent time periods
- **Geographic Accuracy**: Ensuring proper alignment of different data layers

### Known Limitations
1. **Data Resolution**: Some environmental data may not be available at the census tract level
2. **Temporal Mismatch**: Different datasets may come from slightly different time periods
3. **Population Dynamics**: Demographic composition changes over time between census updates
4. **Exposure Modeling**: Some environmental exposures are modeled rather than directly measured
5. **Individual Variation**: Neighborhood-level analysis cannot capture individual exposure differences

## Interpretation Guidelines

### Understanding Disparities
When interpreting results, consider:
- **Magnitude**: How large are the differences between groups?
- **Consistency**: Do disparities appear across multiple indicators?
- **Geographic Patterns**: Are disparities concentrated in specific regions?
- **Vulnerability Factors**: Do exposed populations have additional risk factors?

### Policy Implications
Results can inform:
- **Environmental Justice Policy**: Targeting resources to disproportionately affected communities
- **Climate Adaptation Planning**: Prioritizing heat mitigation in vulnerable neighborhoods
- **Air Quality Regulation**: Strengthening pollution controls in overburdened areas
- **Public Health Preparedness**: Developing early warning systems and response plans

## Technical Implementation

### Computational Workflow
1. **Data Integration**: Combining demographic, environmental, and health datasets
2. **Spatial Processing**: Aligning geographic boundaries and calculating spatial statistics
3. **Statistical Analysis**: Computing exposure metrics and comparative statistics
4. **Visualization Generation**: Creating maps, charts, and summary reports
5. **Report Assembly**: Combining visualizations with narrative text into final reports

### Software and Tools
The analysis uses open-source tools to ensure reproducibility and accessibility:
- **Python**: Primary programming language for data analysis
- **GeoPandas**: Geographic data processing and spatial analysis
- **Matplotlib**: Statistical visualization and mapping
- **Flask**: Web framework for report generation interface
- **Jupyter Notebooks**: Interactive analysis and documentation

### Reproducibility
All analysis code is version-controlled and documented to ensure:
- **Transparency**: Methods can be reviewed and verified
- **Replicability**: Analysis can be repeated with updated data
- **Adaptability**: Methodology can be applied to other regions or time periods
- **Continuous Improvement**: Methods can be refined based on user feedback and new research

## Applications and Impact

### Research Applications
- Academic studies of environmental justice
- Climate vulnerability assessments
- Health disparities research
- Urban planning and development studies

### Policy Applications
- Environmental impact assessments
- Community benefit agreement negotiations
- Climate adaptation and resilience planning
- Public health emergency preparedness

### Community Applications
- Advocacy for environmental justice
- Grant applications for community programs
- Public education and awareness campaigns
- Coalition building across affected communities

## Conclusion

This methodology provides a systematic approach to documenting and analyzing environmental health disparities. By combining rigorous data analysis with accessible visualization tools, it supports evidence-based advocacy and policy development while maintaining scientific credibility and transparency.

The approach recognizes that environmental justice is fundamentally about ensuring that all communities have equal protection from environmental hazards and equal access to environmental benefits, regardless of race, ethnicity, or socioeconomic status. Through careful documentation of existing disparities, this analysis contributes to efforts to achieve environmental equity across California's diverse communities.

---

*This methodology document was developed by the UCLA Latino Policy and Politics Institute in collaboration with environmental health researchers, community advocates, and policy experts. For questions about the methodology or technical implementation, please contact the UCLA LPPI research team.*