import json
import csv
import sys
import io
from typing import List, Dict, Any

def process_dynamo_json(input_files: List[str], output_file: str):
    """
    Extracts user data from multiple DynamoDB JSON output files, removes duplicates
    by keeping the last record encountered (using userId as the key), and saves the unique data to a CSV.
    Only processes records where PK starts with 'USER#'.
    """
    # Use a dictionary to store records by userId (PK). Keys are unique, solving the duplication issue.
    unique_users_map: Dict[str, List[Any]] = {}
    total_records_processed = 0
    
    # Define the fields and their extraction logic
    FIELD_MAPPINGS = [
        ('PK', 'userId', lambda x: x['S'].replace('USER#', '') if 'S' in x and x['S'].startswith('USER#') else None),
        ('UserDetails', 'preferred_username', lambda x: x.get('M', {}).get('preferred_username', {}).get('S')),
        ('UserDetails', 'picture', lambda x: x.get('M', {}).get('picture', {}).get('S')),
        ('UserInsights', 'firstname', lambda x: x.get('M', {}).get('firstname', {}).get('S')),
        ('UserInsights', 'lastname', lambda x: x.get('M', {}).get('lastname', {}).get('S')),
        ('UserInsights', 'mobile', lambda x: x.get('M', {}).get('mobile', {}).get('S')),
        ('UserInsights', 'nic', lambda x: x.get('M', {}).get('nic', {}).get('S')),
        ('UserInsights', 'district', lambda x: x.get('M', {}).get('district', {}).get('S')),
        ('UserInsights', 'nearest_branch', lambda x: x.get('M', {}).get('nearest_branch', {}).get('S')),
    ]
    
    HEADER = [field[1] for field in FIELD_MAPPINGS]

    # Iterate over all provided input files
    for input_file in input_files:
        print(f"Processing file: {input_file}...")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    total_records_processed += 1
                    try:
                        record = json.loads(line.strip())
                        
                        pk_data = record.get('Item', {}).get('PK', {})
                        pk_value = pk_data.get('S', '')
                        
                        # --- CORE FILTERING LOGIC ---
                        if not pk_value.startswith('USER#'):
                            # This correctly skips SESSIONS# and STATES# records
                            continue 
                        
                        # Extract the userId (PK without 'USER#')
                        user_id = pk_value.replace('USER#', '')
                        if not user_id:
                            continue 
                            
                        row = []
                        # Extract all fields for the row
                        for parent_key, _, extractor in FIELD_MAPPINGS:
                            if parent_key == 'PK':
                                value = extractor(pk_data)
                            else:
                                parent_data = record.get('Item', {}).get(parent_key, {})
                                value = extractor(parent_data)
                            
                            row.append(value if value is not None else '')
                        
                        # Store in the map (handles duplication by overwriting)
                        unique_users_map[user_id] = row

                    except json.JSONDecodeError as e:
                        print(f"Skipping line in {input_file} due to JSON error: {e}", file=sys.stderr)
                    except Exception as e:
                        print(f"An unexpected error occurred while processing a record in {input_file}: {e}", file=sys.stderr)

        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found. Skipping.", file=sys.stderr)
            continue 

    # Prepare final list of unique records from the map
    csv_data = list(unique_users_map.values())
    
    # Calculate skipped records
    total_unique_records = len(csv_data)
    
    # Write the data to CSV
    try:
        with io.open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(HEADER)
            csv_writer.writerows(csv_data)

        print(f"\n✅ Success! DynamoDB user data from {len(input_files)} files extracted to '{output_file}'.")
        print(f"Total input records read: {total_records_processed}")
        print(f"Total unique user records saved: {total_unique_records}")
        print(f"Records skipped (likely non-user items like SESSIONS# or STATES#): {total_records_processed - total_unique_records}")

    except Exception as e:
        print(f"Error writing CSV file: {e}", file=sys.stderr)

# --- Configuration ---
DYNAMO_INPUT_FILENAMES = [
    "1.json",
    "2.json",
    "3.json",
    "4.json"
]
OUTPUT_USERS_FILENAME = "users_data.csv"

# --- Execution ---
if __name__ == "__main__":
    # Ensure your 4 dynamo_part_X.json files are correctly named and located.
    # The dummy creation lines from the previous example are removed here.
    # If you run this file, it will use the actual files you have created.
    process_dynamo_json(DYNAMO_INPUT_FILENAMES, OUTPUT_USERS_FILENAME)