# Ceylinco Run For Savari - Leaderboard Report Scripts

This repository contains Python scripts for generating leaderboard and user reports for the Ceylinco Run For Savari Game.

## Scripts

### 1. `generate_leaderboard_report.py`
Generates leaderboard reports from the game data.

### 2. `generate_new_user_report.py`
Compares current user data with previous reports to identify new users.
- Reads `user_report.csv` (current users)
- Reads `user_report_old.csv` (previous users)
- Generates `user_report_new.csv` (new users only)

### 3. `generate_user_report.py`
Generates comprehensive user reports from the data.

### 4. `process_dynamo_users.py`
Processes user data from DynamoDB sources.

## Data Files

- `*.json` - Raw game data files
- `*.csv` - Generated reports
- `*.txt` - Text-based reports and user lists
- `old/` - Archive folder containing historical data organized by date

## Setup

1. Ensure Python 3.x is installed
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```bash
   # Windows
   .\.venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```
4. Install required dependencies:
   ```bash
   pip install pandas
   ```

## Usage

Run the scripts directly:
```bash
python generate_new_user_report.py
python generate_leaderboard_report.py
python generate_user_report.py
```

## Output

The scripts generate various CSV and text files containing:
- User registration data
- Leaderboard rankings
- New user identification
- Historical data comparisons

## Data Structure

The repository maintains historical data in the `old/` directory, organized by date folders (e.g., `20-10-2025/`, `23-10-2025/`, etc.).