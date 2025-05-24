import pandas as pd
import numpy as np
import psycopg2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="adaptive_bi",
    user="bi_user",
    password="bi_pass"
)

# Load data
query = """
SELECT quantity, price AS unit_price, price * quantity AS total_value
FROM orders;
"""
df = pd.read_sql(query, conn)

print("✅ Data loaded:", df.shape)

# Check for nulls
if df.isnull().sum().sum() > 0:
    print("⚠️ Null values detected, dropping rows.")
    df = df.dropna()

# Feature selection
X = df[['quantity', 'unit_price']]
y = df['total_value']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Predictions
y_pred = model.predict(X_test_scaled)

# Evaluation
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"✅ Model trained. RMSE: {rmse:.2f}, R²: {r2:.2f}")

# Feature importance
importances = model.feature_importances_
for name, importance in zip(['quantity', 'unit_price'], importances):
    print(f"Feature: {name}, Importance: {importance:.4f}")

# Save model and scaler
joblib.dump(model, 'order_value_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("✅ Model and scaler saved to disk.")
