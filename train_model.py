import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

print("Starting model training...")

# --- 1. Load the Preprocessed Data ---
try:
    data = pd.read_csv('daily_user_features.csv')
    print("Loaded daily_user_features.csv successfully.")
except FileNotFoundError:
    print("Error: 'daily_user_features.csv' not found. Please run preprocess_data.py first.")
    exit()

# --- 2. Prepare Data for the Model ---
# The model needs only the numerical features. We exclude identifiers.
features = data.drop(columns=['username', 'date'])
print(f"Training model on {len(features.columns)} features: {list(features.columns)}")

# --- 3. Initialize and Train the Isolation Forest Model ---
# The 'contamination' parameter is the expected proportion of anomalies in the dataset.
# 'auto' is a good starting point. You can also set it to a small float, e.g., 0.01 (1%).
# A lower value makes the model more sensitive to anomalies.
model = IsolationForest(
    n_estimators=100,      # The number of trees in the forest.
    contamination='auto',  # The proportion of outliers in the data set.
    random_state=42,       # For reproducibility.
    n_jobs=-1              # Use all available CPU cores.
)

print("Training Isolation Forest model...")
model.fit(features)
print("Model training complete.")

# --- 4. Get Predictions ---
# The model gives us two things:
# 1. Anomaly Score: A score where lower values are more anomalous.
# 2. Prediction: -1 for anomalies (outliers) and 1 for inliers (normal points).
data['anomaly_score'] = model.decision_function(features)
data['is_anomaly'] = model.predict(features)

# --- 5. Analyze and Display Results ---
print("\n--- Anomaly Detection Results ---")

# Find all records that the model flagged as anomalies
anomalies = data[data['is_anomaly'] == -1]

if anomalies.empty:
    print("No anomalies were detected.")
else:
    print(f"Total anomalies detected: {len(anomalies)}")
    print("Top 10 most anomalous activities (lower score is more anomalous):")
    # Using .to_string() to ensure all columns are displayed in the terminal
    print(anomalies.sort_values(by='anomaly_score').head(10).to_string())

    # Specifically check if our known insider's activity was caught
    insider_username = 'alex.doe'
    insider_anomalies = anomalies[anomalies['username'] == insider_username]

    if not insider_anomalies.empty:
        print(f"\n✅ SUCCESS: Malicious activity for '{insider_username}' was correctly identified as an anomaly.")
    else:
        print(f"\n⚠️ NOTE: Malicious activity for '{insider_username}' was NOT flagged. You might need to tune the 'contamination' parameter.")

# --- 6. Save the Trained Model ---
# We save the model to a file so our dashboard can use it later without retraining.
model_filename = 'insider_threat_model.pkl'
joblib.dump(model, model_filename)
print(f"\nTrained model saved successfully to '{model_filename}'")