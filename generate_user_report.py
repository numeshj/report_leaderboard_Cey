import csv
import io
import sys
from typing import Dict, List, Any

def load_email_map(map_file: str) -> Dict[str, str]:
    """
    Loads the UserID-to-Email mapping from user_emails.txt.
    """
    user_id_to_email_map = {}
    print(f"Loading User IDs and Emails from map file: {map_file}...")
    try:
        # Assuming user_emails.txt is space/tab-separated
        with io.open(map_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Split by any whitespace
                parts = line.strip().split()
                if len(parts) >= 2:
                    email = parts[0].strip()   # Email is the first column (index 0)
                    user_id = parts[1].strip() # UserID is the second column (index 1)
                    
                    # Store as: {UserID: Email}
                    user_id_to_email_map[user_id] = email
                    
        print(f"   -> Found {len(user_id_to_email_map)} unique email mappings.")
    except FileNotFoundError:
        print(f"Error: Map file '{map_file}' not found.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred reading map file: {e}", file=sys.stderr)
        
    return user_id_to_email_map

def merge_data_and_create_report(csv_file: str, map_file: str, output_file: str):
    """
    Merges user data from a CSV file (users_data.csv) with email addresses
    from a text map file (user_emails.txt) and creates the final report.
    """
    
    # 1. Load the UserID -> Email map
    user_id_to_email_map = load_email_map(map_file)
    if not user_id_to_email_map:
        return

    # 2. Read and merge data from the DynamoDB CSV
    final_report_data: List[List[Any]] = []
    header: List[str] = []
    
    try:
        with io.open(csv_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            # Get the header
            header = next(reader, None)
            if header is None or 'userId' not in header:
                print(f"Error: CSV file '{csv_file}' must contain a 'userId' column.", file=sys.stderr)
                return

            # Add 'Email' as the new first column in the header
            email_column_index = 0
            header.insert(email_column_index, "Email")
            
            # Find the index of 'userId' in the original columns
            user_id_index = header.index("userId", email_column_index + 1)
            
            # Process data rows
            for row in reader:
                if not row: continue
                
                user_id = row[user_id_index - 1].strip() # -1 because we shifted the index when inserting 'Email'
                
                # Get the email, defaulting to a placeholder if not found
                email = user_id_to_email_map.get(user_id, "EMAIL_NOT_FOUND")
                
                # Insert the email into the row at the beginning
                new_row = row[:]
                new_row.insert(email_column_index, email)
                
                final_report_data.append(new_row)

    except FileNotFoundError:
        print(f"Error: Input file '{csv_file}' not found.", file=sys.stderr)
        return
    except Exception as e:
        print(f"An error occurred reading or processing CSV file: {e}", file=sys.stderr)
        return

    # 3. Write the final report CSV
    try:
        with io.open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            csv_writer = csv.writer(outfile)

            # Write the new header
            csv_writer.writerow(header)

            # Write the data rows
            csv_writer.writerows(final_report_data)

        print(f"\n✅ Success! User Report created as '{output_file}'.")
        print(f"Total user records in report: {len(final_report_data)}")

    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)

# --- Configuration ---
DYNAMO_CSV_FILE = "users_data.csv"     # Output from process_dynamo_users.py
COGNITO_MAP_FILE = "user_emails.txt"   # Your Cognito data source
OUTPUT_FILE = "user_report.csv"        # The final report file

# --- Execution ---
if __name__ == "__main__":
    # --- RUN THE PROCESSOR ---
    merge_data_and_create_report(DYNAMO_CSV_FILE, COGNITO_MAP_FILE, OUTPUT_FILE)
