import pandas as pd

# Read the CSV file
input_file = '../inputs/tract_level_data.csv'
data = pd.read_csv(input_file)

# Group by County and Neighborhood_type and count occurrences
grouped_data = data.groupby(['county', 'Neighborhood_type']).size().reset_index(name='Count')

# Write the result to a new CSV file
output_file = '../outputs/neighborhood_type_count_by_county.csv'
grouped_data.to_csv(output_file, index=False)

print(f"Counts of Neighborhood_type by county have been written to {output_file}")