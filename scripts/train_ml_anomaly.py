import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from pathlib import Path

print("1. Generating Synthetic Network Traffic Dataset (10,000 packets)...")
# We simulate features: [packet_size, destination_port, connection_duration, failed_logins, bytes_transferred]
np.random.seed(42)

# Generate 8,000 Normal Traffic packets (e.g., standard web browsing on port 80/443)
normal_data = np.random.normal(loc=[500, 80, 1.5, 0, 1000], scale=[100, 10, 0.5, 0.1, 200], size=(8000, 5))
normal_labels = np.zeros(8000)

# Generate 2,000 Attack Traffic packets (e.g., SSH Brute Force on port 22, massive payloads)
attack_data = np.random.normal(loc=[1500, 22, 5.0, 5, 5000], scale=[300, 2, 2.0, 2, 1000], size=(2000, 5))
attack_labels = np.ones(2000)

# Combine and shuffle the dataset
X = np.vstack([normal_data, attack_data])
y = np.concatenate([normal_labels, attack_labels])
columns = ['packet_size', 'destination_port', 'connection_duration', 'failed_logins', 'bytes_transferred']
df = pd.DataFrame(X, columns=columns)

print("2. Splitting data into 80% Training and 20% Testing sets...")
X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)

print("3. Training Random Forest Intrusion Detection Model...")
# A Random Forest builds 100 decision trees and averages their votes to prevent overfitting
clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

print("4. Evaluating Model Performance on Unseen Test Data...")
y_pred = clf.predict(X_test)

print("\n================ CLASSIFICATION REPORT ================")
print(classification_report(y_test, y_pred, target_names=['Normal Traffic', 'Malicious Attack']))
print("=======================================================\n")

output_path = 'model/ml_engine/network_rf_model.pkl'
joblib.dump(clf, output_path)
print(f"5. ✅ Traditional ML Engine successfully trained and saved to {output_path}!")
