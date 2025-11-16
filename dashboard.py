import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# Use caching to load model and data only once for efficiency
@st.cache_resource
def load_model():
    """Loads the saved insider threat detection model."""
    try:
        model = joblib.load('insider_threat_model.pkl')
        return model
    except FileNotFoundError:
        st.error("Model file 'insider_threat_model.pkl' not found. Please run train_model.py first.")
        return None

@st.cache_data
def load_data():
    """Loads the preprocessed user features dataset."""
    try:
        data = pd.read_csv('daily_user_features.csv')
        return data
    except FileNotFoundError:
        st.error("Data file 'daily_user_features.csv' not found. Please run preprocess_data.py first.")
        return None

# --- Page Configuration ---
st.set_page_config(page_title="Insider Threat Detection Dashboard", layout="wide")
st.title("🚨 AI-Powered Insider Threat Detection Dashboard")

# --- Initialize Session State ---
# This is used to store information that persists between user interactions.
if 'action_log' not in st.session_state:
    st.session_state.action_log = {}

# --- Load Model and Data ---
model = load_model()
data = load_data()

if model is None or data is None:
    st.stop()

# --- Apply Model to Data ---
features = data.drop(columns=['username', 'date'])
data['anomaly_score'] = model.decision_function(features)
data['is_anomaly'] = model.predict(features)
data['date'] = pd.to_datetime(data['date'])
anomalies = data[data['is_anomaly'] == -1].sort_values(by='anomaly_score')


# --- Main Dashboard Display ---
st.header("Anomalous Activity Alerts")
st.info("This table lists all user activities flagged as potential threats. Lower scores are more anomalous.")

# Add a status column to the anomalies dataframe
anomalies['status'] = [st.session_state.action_log.get(idx, "Pending Review") for idx in anomalies.index]
st.dataframe(anomalies[['username', 'date', 'anomaly_score', 'status'] + features.columns.tolist()])


# --- Sidebar for User-Specific Analysis ---
st.sidebar.header("User Behavior Deep Dive")
all_users = data['username'].unique()
selected_user = st.sidebar.selectbox("Select a User to Investigate", all_users)


# --- Display Data for Selected User ---
st.header(f"Behavioral Analysis for: {selected_user}")
user_data = data[data['username'] == selected_user].set_index('date')

# --- NEW: Alerting and Response Section ---
# Check if the selected user has any anomalies
user_anomalies = anomalies[anomalies['username'] == selected_user]
if not user_anomalies.empty:
    st.warning(f"⚠️ This user has been flagged for anomalous activity.")
    
    anomaly_to_action = user_anomalies.iloc[0] # Focus on their most severe anomaly
    anomaly_index = anomaly_to_action.name

    # Check if action has already been taken for this anomaly
    if st.session_state.action_log.get(anomaly_index) == "Action Taken":
        st.success(f"Action was already taken for this user on {anomaly_to_action['date'].strftime('%Y-%m-%d')}. Account is under review.")
    else:
        if st.button(f"🚨 Trigger Alert & Auto-Response for {selected_user}"):
            # 1. Simulate Alert (prints to terminal)
            print("\n" + "="*50)
            print(f"ALERT TRIGGERED: High-Risk Anomaly Detected")
            print(f"Timestamp: {datetime.now().isoformat()}")
            print(f"User: {selected_user}")
            print("Anomaly Details:")
            print(anomaly_to_action[features.columns].to_string())
            print("="*50 + "\n")

            # 2. Simulate Auto-Response (updates dashboard)
            st.session_state.action_log[anomaly_index] = "Action Taken"
            st.success("Action Taken: User account flagged for manual review. Alert sent to Security Team.")
            st.rerun() # Rerun the script to update the main anomalies table status

# Display chart and full log
st.subheader("Key Activity Timeline")
features_to_plot = ['after_hours_login_count', 'unusual_dir_access_count', 'usb_connection_count', 'personal_emails_sent_count']
st.line_chart(user_data[features_to_plot])
st.subheader("Full Daily Activity Log")
st.dataframe(user_data)