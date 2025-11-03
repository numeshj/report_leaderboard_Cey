import pandas as pd

# Read the CSV files
df_current = pd.read_csv('user_report.csv')
df_old = pd.read_csv('user_report_old.csv')

# Strip whitespace from column names
df_current.columns = df_current.columns.str.strip()
df_old.columns = df_old.columns.str.strip()

# Find new users by comparing userId
# Users in current report but not in old report
new_users = df_current[~df_current['userId'].isin(df_old['userId'])]

# Save to new CSV file
new_users.to_csv('user_report_new.csv', index=False)

print(f"Total users in current report: {len(df_current)}")
print(f"Total users in old report: {len(df_old)}")
print(f"New users found: {len(new_users)}")
print(f"\nNew users saved to 'user_report_new.csv'")

# Display the new users
# if len(new_users) > 0:
#     print("\nNew users:")
#     print(new_users[['Email', 'userId', 'firstname', 'lastname']].to_string(index=False))
# else:
#     print("\nNo new users found.")
