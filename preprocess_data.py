import pandas as pd
import numpy as np

print("Starting data preprocessing and feature engineering...")

# --- 1. Load the Datasets ---
try:
    login_df = pd.read_csv('login_logs.csv')
    file_df = pd.read_csv('file_access_logs.csv')
    usb_df = pd.read_csv('usb_logs.csv')
    email_df = pd.read_csv('email_logs.csv')
    print("All log files loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading files: {e}. Make sure all log CSV files are in the same directory.")
    exit()

# --- 2. Convert Timestamps ---
# Convert the 'timestamp' column in each dataframe to datetime objects
login_df['timestamp'] = pd.to_datetime(login_df['timestamp'])
file_df['timestamp'] = pd.to_datetime(file_df['timestamp'])
usb_df['timestamp'] = pd.to_datetime(usb_df['timestamp'])
email_df['timestamp'] = pd.to_datetime(email_df['timestamp'])
print("Timestamp columns converted to datetime objects.")

# --- 3. Feature Engineering from Login Data ---
print("Engineering features from login data...")

# Extract date from timestamp for daily aggregation
login_df['date'] = login_df['timestamp'].dt.date

# Feature 1: Count of logins per day
daily_logins = login_df[login_df['action'] == 'login'].groupby(['username', 'date']).size().reset_index(name='login_count')

# Feature 2: Count of failed logins per day
failed_logins = login_df[login_df['success'] == False].groupby(['username', 'date']).size().reset_index(name='failed_login_count')

# Feature 3: Count of after-hours logins (e.g., before 8 AM or after 7 PM)
login_df['hour'] = login_df['timestamp'].dt.hour
after_hours_logins = login_df[(login_df['hour'] < 8) | (login_df['hour'] > 19)].groupby(['username', 'date']).size().reset_index(name='after_hours_login_count')

# --- 4. Merge Login Features ---
# Start building our main feature dataframe
daily_features = pd.merge(daily_logins, failed_logins, on=['username', 'date'], how='left')
daily_features = pd.merge(daily_features, after_hours_logins, on=['username', 'date'], how='left')

# Fill NaN values with 0 (for days with no failed or after-hours logins)
daily_features = daily_features.fillna(0)

# (Code from Part 1 should be above this)

# --- 5. Feature Engineering from File Access Data ---
print("Engineering features from file access data...")
file_df['date'] = file_df['timestamp'].dt.date

# Feature 4: Count of file accesses per day
daily_file_access = file_df.groupby(['username', 'date']).size().reset_index(name='file_access_count')

# Feature 5: Count of access to unusual directories (e.g., a developer in sales folder)
# In our scenario, we'll hardcode this as access to the '/sales/' directory
unusual_dir_access = file_df[file_df['filepath'].str.contains('/sales/', na=False)].groupby(['username', 'date']).size().reset_index(name='unusual_dir_access_count')

# Feature 6: Count of file write actions (to detect the ZIP creation)
file_writes = file_df[file_df['action'] == 'file_write'].groupby(['username', 'date']).size().reset_index(name='file_write_count')

# --- 6. Feature Engineering from USB Data ---
print("Engineering features from USB data...")

# (Code from previous parts should be above this)

# --- 8. Feature Engineering from Email Data ---
print("Engineering features from email data...")
email_df['date'] = email_df['timestamp'].dt.date

# Helper function to parse attachment size
def parse_attachment_size_mb(size):
    if pd.isna(size):
        return 0
    size = str(size).upper()
    if 'MB' in size:
        return float(size.replace('MB', ''))
    elif 'KB' in size:
        return float(size.replace('KB', '')) / 1024
    else:
        return 0

email_df['attachment_mb'] = email_df['attachment'].apply(parse_attachment_size_mb)

# Feature 8: Count of emails sent per day
emails_sent = email_df.groupby(['username', 'date']).size().reset_index(name='emails_sent_count')

# Feature 9: Count of emails to personal domains (a strong indicator)
personal_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'protonmail.com']
personal_emails = email_df[email_df['recipient'].str.contains('|'.join(personal_domains), na=False)]
personal_emails_sent = personal_emails.groupby(['username', 'date']).size().reset_index(name='personal_emails_sent_count')

# Feature 10: Count of emails with large attachments (e.g., > 5 MB)
large_attachment_emails = email_df[email_df['attachment_mb'] > 5]
large_attachments_sent = large_attachment_emails.groupby(['username', 'date']).size().reset_index(name='large_attachments_sent_count')
usb_df['date'] = usb_df['timestamp'].dt.date

# Feature 7: Count of USB connections per day (a very strong indicator)
usb_connections = usb_df[usb_df['action'] == 'usb_connect'].groupby(['username', 'date']).size().reset_index(name='usb_connection_count')

# (This replaces the old section 7 and the final "Save and Display" section)

# --- 9. Merge All Features into Final Dataset ---
print("Merging all engineered features...")
# Merge File and USB features
daily_features = pd.merge(daily_features, daily_file_access, on=['username', 'date'], how='left')
daily_features = pd.merge(daily_features, unusual_dir_access, on=['username', 'date'], how='left')
daily_features = pd.merge(daily_features, file_writes, on=['username', 'date'], how='left')
daily_features = pd.merge(daily_features, usb_connections, on=['username', 'date'], how='left')

# Merge Email features
daily_features = pd.merge(daily_features, emails_sent, on=['username', 'date'], how='left')
daily_features = pd.merge(daily_features, personal_emails_sent, on=['username', 'date'], how='left')
daily_features = pd.merge(daily_features, large_attachments_sent, on=['username', 'date'], how='left')


# Fill all NaN values that resulted from left merges with 0
daily_features = daily_features.fillna(0)

# Convert all feature columns to integer types for cleanliness
feature_columns = [
    'login_count', 'failed_login_count', 'after_hours_login_count', 
    'file_access_count', 'unusual_dir_access_count', 'file_write_count', 
    'usb_connection_count', 'emails_sent_count', 'personal_emails_sent_count', 
    'large_attachments_sent_count'
]
for col in feature_columns:
    daily_features[col] = daily_features[col].astype(int)

# --- 10. Save Final Dataset ---
daily_features.to_csv('daily_user_features.csv', index=False)

print("\n--- Preprocessing and Feature Engineering Complete ---")
print("Final dataset saved to 'daily_user_features.csv'")
print(f"The dataset contains {len(daily_features)} records and {len(daily_features.columns)} columns.")

print("\nFull anomalous activity profile for insider 'alex.doe':")
insider_activity = daily_features[daily_features['username'] == 'alex.doe']
anomaly_day = insider_activity[
    (insider_activity['after_hours_login_count'] > 0) |
    (insider_activity['unusual_dir_access_count'] > 0) |
    (insider_activity['usb_connection_count'] > 0) |
    (insider_activity['personal_emails_sent_count'] > 0)
]
print(anomaly_day)