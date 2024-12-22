import json
import os

# Load the JSON file
input_file = 'data/full_data.json'  # Replace with your file path

# Create an output directory if not exists
output_dir = 'data'
os.makedirs(output_dir, exist_ok=True)

with open(input_file, 'r') as file:
    data = json.load(file)

# Iterate through the years in the JSON and create individual files
for year, content in data.items():
    output_file = os.path.join(output_dir, f'ifsc_{year}.json')
    with open(output_file, 'w') as year_file:
        json.dump(content, year_file, indent=4)

print(f"JSON files have been split and saved in the '{output_dir}' directory.")