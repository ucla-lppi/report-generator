# FILE: data_utils.py
import geopandas as gpd
import pandas as pd
import os
# from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv()

# Use the Agg backend for matplotlib
import matplotlib.pyplot as plt
plt.switch_backend('Agg')

def load_geojson(geojson_path):
    return gpd.read_file(geojson_path)

def format_as_thousands(value):
    if value >= 1000:
        return f"{int(value // 1000)}k"
    return str(int(value))

def format_population(number):
    if number >= 1_000_000:
        return f"{round(number / 1_000_000, 1)}M"
    elif number >= 1_000:
        return f"{int(round(number / 1_000, 0))}K"
    else:
        return f"{int(number)}"

def ensure_directories(output_dir):
    map_dir = os.path.join(output_dir, 'maps')
    img_dir = os.path.join(output_dir, 'imgs')
    os.makedirs(map_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    return map_dir, img_dir

def fetch_population_data(csv_url, nrows=None):
    pop_data = pd.read_csv(csv_url, nrows=nrows, dtype={'County': str})

    required_columns = [
        'County', 'comparison_group', 'factsheet_language',
        'neigh_50pct_lat', 'neigh_50pct_nlw',
        'neigh_70pct_lat', 'neigh_70pct_nlw', 'total_tracts', 'pop_county_lat', 'pop_county_nlw',
        'pop_county_other', 'pop_county_total', 'pct_nlw', 'pct_lat', 'pct_other',
        'med_age_nlw', 'med_age_lat', 'med_age_tot', 'pct_non_cit_nlw', 'pct_non_cit_lat',
        'pct_non_cit_tot', 'pct_lep_nlw', 'pct_lep_lat',
        'pct_lep_tot', 'med_inc_nlw', 'med_inc_lat', 'med_inc_tot', 'pct_pov_nlw',
        'pct_pov_lat', 'pct_pov_tot', 'pct_no_ins_tot', 'pct_no_ins_nlw',
        'pct_no_ins_lat', 'pct_rent_nlw', 'pct_rent_lat', 'pct_rent_tot',
        'pct_snap_nlw', 'pct_snap_lat', 'pct_snap_tot', 'pct_food_insecure_lat',
        'pct_food_insecure_nlw', 'pct_food_insecure_tot', 'pct_health_stat_lat',
        'pct_health_stat_nlw', 'pct_health_stat_tot', 'life_exp_tot',
        'life_exp_lat', 'life_exp_nlw', 'pct_no_vehicle_comp',
        'pct_no_vehicle_lat', 'pct_out_lat', 'pct_broad_lat', 'pct_under_18_lat',
        'pct_over_65_lat', 'pct_under_5_lat', 'pct_old_house_lat', 'pct_out_comp',
        'pct_broad_comp', 'pct_under_18_comp', 'pct_over_65_comp',
        'pct_under_5_comp', 'pct_old_house_comp', 'avgDays90F_lat',
        'avgDays90F_comp', 'avgDays_90F_county', 'avgDays_90F_state',
        'avgDays95F_lat', 'avgDays95F_comp', 'avgDays100F_lat',
        'avgDays100F_comp', 'avgDays105F_lat', 'avgDays105F_comp',
        'avgLong90F_lat', 'avgLong90F_comp', 'pct_imp_surf_lat',
        'pct_imp_surf_comp', 'mid_cent_90F_lat', 'mid_cent_90F_comp',
        'end_cent_90F_lat', 'end_cent_90F_comp', 'mid_cent_100F_lat',
        'mid_cent_100F_comp', 'end_cent_100F_lat', 'end_cent_100F_comp',
        'pct_tree_lat', 'pct_tree_comp', 'pct_diabetes_lat',
        'pct_diabetes_comp', 'pct_obesity_lat', 'pct_obesity_comp',
        'rate_asthma_ed_lat', 'rate_asthma_ed_comp', 'rate_cvd_ed_lat',
        'rate_cvd_ed_comp', 'rate_heat_ed_lat', 'rate_heat_ed_comp',
        'pct_lowBirthWght_lat', 'pct_lowBirthWght_comp', 'avgPM25_lat',
        'avgPM25_comp', 'dieselPM_lat', 'dieselPM_comp', 'tox_conc_lat',
        'tox_conc_comp', 'trafficDens_lat', 'trafficDens_comp',
        'cleanupSites_lat', 'cleanupSites_comp', 'hazFacilites_lat',
        'hazFacilites_comp',
        'prox_rmp_lat', 'prox_rmp_comp', 'pct_poverty_lat', 'pct_poverty_comp',
        'pct_walk_lat', 'pct_walk_comp', 'pct_pub_lat', 'pct_pub_comp',
        'pct_dac_lat', 'pct_dac_comp', 'pct_clean_veh_lat', 'pct_clean_veh_comp',
        'pct_veh_20yrs_lat', 'pct_veh_20yrs_comp'
    ]
    # Check if all required columns are present
    missing_columns = [col for col in required_columns if col not in pop_data.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns in population data: {', '.join(missing_columns)}")

    # Ensure the County column is treated as a string
    pop_data['County'] = pop_data['County'].astype(str)

    # Debugging: Print the unique values in the County column
    print("Unique values in the 'County' column before dropping NaNs:", pop_data['County'].unique())

    # Filter out rows with NaN values in the County column
    pop_data = pop_data.dropna(subset=['County'])

    # Debugging: Print the unique values in the County column after dropping NaNs
    print("Unique values in the 'County' column after dropping NaNs:", pop_data['County'].unique())

    return pop_data

def create_county_name_mapping(pop_data):
    return {str(name): str(name).replace(' ', '_') for name in pop_data['County'].unique()}