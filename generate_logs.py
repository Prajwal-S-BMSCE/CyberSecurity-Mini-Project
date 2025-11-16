import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker for generating realistic names
fake = Faker()

# --- Configuration ---
NUM_EMPLOYEES = 50
START_DATE = datetime(2025, 7, 1)
END_DATE = datetime(2025, 9, 30)
INSIDER_USERNAME = "alex.doe" # Our malicious actor

# --- Generate Employee List ---
def generate_employees(num_employees):
    employees = []
    for _ in range(num_employees - 1):
        name = fake.name()
        username = name.lower().replace(" ", ".")
        employees.append({'username': username, 'name': name, 'role': 'developer'})
    
    # Manually add our insider
    employees.append({'username': INSIDER_USERNAME, 'name': 'Alex Doe', 'role': 'senior_developer'})
    return employees

employees = generate_employees(NUM_EMPLOYEES)
employee_usernames = [e['username'] for e in employees]

# --- Log Generation ---
def generate_login_logs(employees, start_date, end_date):
    logs = []
    current_date = start_date
    
    while current_date <= end_date:
        # Only generate logs for weekdays
        if current_date.weekday() < 5:
            for emp in employees:
                # Normal login behavior
                if np.random.rand() > 0.1: # 90% chance of logging in
                    login_time = current_date.replace(hour=np.random.randint(8, 11), minute=np.random.randint(0, 59))
                    logout_time = login_time + timedelta(hours=np.random.randint(8, 10), minutes=np.random.randint(0, 59))
                    logs.append({'timestamp': login_time, 'username': emp['username'], 'action': 'login', 'success': True})
                    logs.append({'timestamp': logout_time, 'username': emp['username'], 'action': 'logout', 'success': True})

                # Simulate occasional failed logins
                if np.random.rand() > 0.95:
                    failed_login_time = current_date.replace(hour=np.random.randint(0, 23), minute=np.random.randint(0, 59))
                    logs.append({'timestamp': failed_login_time, 'username': emp['username'], 'action': 'login', 'success': False})

        current_date += timedelta(days=1)
        
    # --- Inject Anomalies for the Insider ---
    # Alex Doe starts logging in at odd hours in the last week
    anomaly_start_date = end_date - timedelta(days=7)
    for i in range(5): # Five late-night logins
        anomaly_date = anomaly_start_date + timedelta(days=i)
        if anomaly_date.weekday() < 5: # Only on weekdays
            anomaly_time = anomaly_date.replace(hour=np.random.randint(2, 5), minute=np.random.randint(0, 59))
            logs.append({'timestamp': anomaly_time, 'username': INSIDER_USERNAME, 'action': 'login', 'success': True})
            # And logs out a few hours later
            anomaly_logout_time = anomaly_time + timedelta(hours=np.random.randint(1, 3))
            logs.append({'timestamp': anomaly_logout_time, 'username': INSIDER_USERNAME, 'action': 'logout', 'success': True})
            
    return pd.DataFrame(logs)

# (Keep all the code from Part 1 above this)

# --- Define File System Structure (for simulation) ---
FILE_PATHS = {
    'developer': ['/src/project-phoenix/', '/docs/api-specs/', '/tests/project-phoenix/'],
    'senior_developer': ['/src/project-phoenix/', '/src/project-valhalla/', '/docs/api-specs/', '/design/database-schemas/'],
    'sales': ['/sales/client-prospects/', '/marketing/campaigns/']
}
CRITICAL_FILES = ['/sales/client-prospects/q3_targets.csv', '/design/database-schemas/main_schema.sql']

def generate_file_access_logs(employees, start_date, end_date):
    logs = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5: # Weekdays only
            for emp in employees:
                # Normal file access based on role
                if np.random.rand() > 0.3: # 70% chance of accessing files
                    role = emp['role'] if emp['role'] in FILE_PATHS else 'developer'
                    num_accesses = np.random.randint(5, 20)
                    for _ in range(num_accesses):
                        folder = np.random.choice(FILE_PATHS[role])
                        filename = f"{fake.word()}.{np.random.choice(['py', 'md', 'txt', 'sql'])}"
                        access_time = current_date.replace(hour=np.random.randint(9, 18), minute=np.random.randint(0, 59))
                        logs.append({
                            'timestamp': access_time,
                            'username': emp['username'],
                            'action': 'file_read',
                            'filepath': f"{folder}{filename}"
                        })

        current_date += timedelta(days=1)

    # --- Inject Anomalies for the Insider (Alex Doe) ---
    anomaly_date = end_date - timedelta(days=3)
    anomaly_time_base = anomaly_date.replace(hour=3, minute=15) # Correlate with late-night login

    # 1. Accessing unauthorized sales folder
    for i in range(10):
        logs.append({
            'timestamp': anomaly_time_base + timedelta(minutes=i*2),
            'username': INSIDER_USERNAME,
            'action': 'file_read',
            'filepath': f"/sales/client-prospects/client_{i}.csv"
        })
    
    # 2. Compressing source code into a single large file (simulated by a file_write)
    logs.append({
        'timestamp': anomaly_time_base + timedelta(minutes=30),
        'username': INSIDER_USERNAME,
        'action': 'file_write',
        'filepath': '/home/alex.doe/documents/all_source.zip'
    })

    return pd.DataFrame(logs)

def generate_usb_logs(employees, end_date):
    logs = []
    
    # Normal behavior: Very few (or no) USB events
    # For simplicity in our simulation, we'll assume no one else uses USBs.

    # --- Inject Anomaly for the Insider (Alex Doe) ---
    # Alex connects a USB drive shortly after creating the ZIP file
    anomaly_time = end_date - timedelta(days=3)
    anomaly_time = anomaly_time.replace(hour=3, minute=45) # 15 mins after zipping
    
    logs.append({
        'timestamp': anomaly_time,
        'username': INSIDER_USERNAME,
        'action': 'usb_connect',
        'device_id': 'Personal_USB_0A5B'
    })
    
    # And disconnects it after some time
    logs.append({
        'timestamp': anomaly_time + timedelta(minutes=np.random.randint(15, 45)),
        'username': INSIDER_USERNAME,
        'action': 'usb_disconnect',
        'device_id': 'Personal_USB_0A5B'
    })

    return pd.DataFrame(logs)

# (Keep all the code from Part 1 & 2 above this)

def generate_email_logs(employees, start_date, end_date):
    logs = []
    current_date = start_date
    company_domain = "acme-corp.com"
    partners = ["partner-a.com", "consulting-b.org", "supplier-c.net"]

    while current_date <= end_date:
        if current_date.weekday() < 5:
            for emp in employees:
                # Normal email activity
                if np.random.rand() > 0.4: # 60% chance of sending emails
                    num_emails = np.random.randint(1, 10)
                    for _ in range(num_emails):
                        # 80% chance of internal email, 20% external
                        if np.random.rand() > 0.2:
                            recipient = f"{np.random.choice(employee_usernames)}@{company_domain}"
                        else:
                            recipient = f"{fake.user_name()}@{np.random.choice(partners)}"
                        
                        has_attachment = np.random.rand() > 0.7 # 30% chance of attachment
                        attachment_size = f"{np.random.randint(10, 1024)}KB" if has_attachment else None
                        
                        email_time = current_date.replace(hour=np.random.randint(9, 18), minute=np.random.randint(0, 59))
                        logs.append({
                            'timestamp': email_time,
                            'username': emp['username'],
                            'sender': f"{emp['username']}@{company_domain}",
                            'recipient': recipient,
                            'subject': fake.sentence(nb_words=4),
                            'attachment': attachment_size
                        })
        current_date += timedelta(days=1)
    
    # --- Inject Anomaly for the Insider (Alex Doe) ---
    # Alex sends the zipped file to a personal email address.
    # This happens after the USB event.
    anomaly_date = end_date - timedelta(days=3)
    anomaly_time = anomaly_date.replace(hour=4, minute=30) # After USB disconnect
    
    logs.append({
        'timestamp': anomaly_time,
        'username': INSIDER_USERNAME,
        'sender': f"{INSIDER_USERNAME}@{company_domain}",
        'recipient': "alex.doe.private@gmail.com", # Personal email
        'subject': "Vacation Photos", # Deceptive subject
        'attachment': "25.6MB" # Large, suspicious attachment size
    })
    
    return pd.DataFrame(logs)

# --- Main Execution ---
if __name__ == "__main__":
    employees = generate_employees(NUM_EMPLOYEES)
    employee_usernames = [e['username'] for e in employees] # Make sure this is defined for the email function

    print("Generating synthetic logs...")

    # Generate Login Logs
    login_df = generate_login_logs(employees, START_DATE, END_DATE)
    login_df = login_df.sort_values(by='timestamp').reset_index(drop=True)
    login_df.to_csv('login_logs.csv', index=False)
    print(f"Generated {len(login_df)} login records. Saved to login_logs.csv.")

    # Generate File Access Logs
    file_df = generate_file_access_logs(employees, START_DATE, END_DATE)
    file_df = file_df.sort_values(by='timestamp').reset_index(drop=True)
    file_df.to_csv('file_access_logs.csv', index=False)
    print(f"Generated {len(file_df)} file access records. Saved to file_access_logs.csv.")

    # Generate USB Logs
    usb_df = generate_usb_logs(employees, END_DATE)
    usb_df = usb_df.sort_values(by='timestamp').reset_index(drop=True)
    usb_df.to_csv('usb_logs.csv', index=False)
    print(f"Generated {len(usb_df)} USB records. Saved to usb_logs.csv.")
    
    # Generate Email Logs
    email_df = generate_email_logs(employees, START_DATE, END_DATE)
    email_df = email_df.sort_values(by='timestamp').reset_index(drop=True)
    email_df.to_csv('email_logs.csv', index=False)
    print(f"Generated {len(email_df)} email records. Saved to email_logs.csv.")

    print("\nLog generation complete. All datasets created.")
    print("\nSample Anomalous Email Data:")
    print(email_df[email_df['recipient'] == "alex.doe.private@gmail.com"])