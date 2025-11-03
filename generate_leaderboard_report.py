import json
import csv
import sys
import io
from typing import Dict, List, Any

def load_leaderboard_scores(lb_file: str) -> Dict[str, str]:
    """
    Reads the leaderboard JSON file (lb1.txt) and creates a dictionary 
    mapping UserID to Score.
    """
    score_map = {}
    print(f"Loading leaderboard scores from: {lb_file}...")
    try:
        with open(lb_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Leaderboard file '{lb_file}' not found.", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Leaderboard file '{lb_file}' is not valid JSON. Detail: {e}", file=sys.stderr)
        return None

    leader_board = data.get("leaderBoard")

    if not leader_board or not isinstance(leader_board, list):
        print("Error: 'leaderBoard' array not found or is not a list in the JSON data.", file=sys.stderr)
        return score_map 

    # Array is [UserID_1, Score_1, UserID_2, Score_2, ...]
    for i in range(0, len(leader_board), 2):
        user_id = str(leader_board[i])
        if i + 1 < len(leader_board):
            score = str(leader_board[i+1])
            score_map[user_id] = score
            
    print(f"   -> Found {len(score_map)} unique User IDs with scores in the leaderboard.")
    return score_map

def generate_leaderboard_user_report(lb_file: str, report_file: str, output_file: str):
    """
    Merges detailed user data from user_report.csv with scores from lb1.txt,
    sorts by score in descending order, and creates the final comprehensive report.
    """
    
    # 1. Load the UserID -> Score map from lb1.txt
    user_id_to_score_map = load_leaderboard_scores(lb_file)
    if user_id_to_score_map is None:
        return

    # 2. Read user_report.csv and perform the merge
    final_report_data: List[List[Any]] = []
    header: List[str] = []
    
    processed_lb_ids = set()

    try:
        with io.open(report_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            # Get the header
            header = next(reader, None)
            if header is None or 'userId' not in header:
                print(f"Error: User Report file '{report_file}' must contain a 'userId' column.", file=sys.stderr)
                return

            user_id_index = header.index("userId")
            header.append("Score") # Add 'Score' to the header
            score_index_final = len(header) - 1 # This will be the index of the Score column in the final data
            
            # Process data rows from user_report.csv
            for row in reader:
                if not row: continue
                
                # Get the UserID from the profile data
                user_id = row[user_id_index].strip()
                
                # Check if this user is in the leaderboard
                score = user_id_to_score_map.get(user_id)
                
                if score is not None:
                    # If the user is in the leaderboard, add their details + score
                    new_row = row[:]
                    new_row.append(score)
                    final_report_data.append(new_row)
                    processed_lb_ids.add(user_id)

    except FileNotFoundError:
        print(f"Error: User Report file '{report_file}' not found.", file=sys.stderr)
        return
    except ValueError:
        print(f"Error: 'userId' column not found in '{report_file}'. Check your header.", file=sys.stderr)
        return
    except Exception as e:
        print(f"An error occurred reading or processing report CSV file: {e}", file=sys.stderr)
        return

    # 3. Handle users in lb1.txt but NOT in user_report.csv
    missing_user_profiles = user_id_to_score_map.keys() - processed_lb_ids
    
    if missing_user_profiles:
        # Create a blank row template based on the final header structure
        blank_row_template = [""] * len(header)
        
        for user_id in missing_user_profiles:
            score = user_id_to_score_map[user_id]
            
            sparse_row = blank_row_template[:]
            
            # Set known fields: Email, UserID, Score
            # Assuming 'Email' is the first column as set in previous step
            email_idx = header.index("Email")
            userid_idx = header.index("userId")
            
            sparse_row[email_idx] = "EMAIL_FROM_LB_ONLY"
            sparse_row[userid_idx] = user_id
            sparse_row[score_index_final] = score # Use the correct final score index

            final_report_data.append(sparse_row)
            print(f"Warning: Added user {user_id} with score {score} but no profile details found.", file=sys.stderr)


    # 4. SORT the data by Score in DESCENDING order (highest score first)
    try:
        # Use int() to ensure numerical sorting, not alphabetical ("1000" > "900")
        final_report_data.sort(key=lambda row: int(row[score_index_final]), reverse=True)
        print("Data successfully sorted by Score (Descending).")
    except Exception as e:
        print(f"Error during sorting by score: {e}. Outputting unsorted data.", file=sys.stderr)


    # 5. Write the final report CSV
    try:
        with io.open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(header)
            csv_writer.writerows(final_report_data)

        # Verification of the requirement
        expected_count = len(user_id_to_score_map)
        actual_count = len(final_report_data)

        print(f"\n✅ Success! Sorted Leaderboard Report created as '{output_file}'.")
        print(f"   Total expected user records (from {lb_file}): {expected_count}")
        print(f"   Total records saved in report: {actual_count}")
        if expected_count == actual_count:
             print("   -> The counts match, fulfilling the row count requirement.")
        else:
             print("   -> WARNING: The row counts do NOT match. Check for data inconsistencies.")


    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)

# --- Configuration ---
LEADERBOARD_FILE = "lb1.txt"          
USER_REPORT_FILE = "user_report.csv"  
OUTPUT_FINAL_REPORT = "leaderboard_user_report.csv" 

# --- Execution ---
if __name__ == "__main__":
    # --- RUN THE PROCESSOR ---
    generate_leaderboard_user_report(LEADERBOARD_FILE, USER_REPORT_FILE, OUTPUT_FINAL_REPORT)
