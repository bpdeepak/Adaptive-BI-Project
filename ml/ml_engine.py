import psycopg2
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="adaptive_bi",
    user="bi_user",
    password="bi_pass"
)

# Load data from 'orders' table
query = """
SELECT quantity, price AS unit_price, price * quantity AS total_value
FROM orders;
"""
df = pd.read_sql(query, conn)
print("✅ Data loaded:", df.shape)

# Preprocessing
X = df[['quantity', 'unit_price']]
y = df['total_value']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train model (Random Forest)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

# Evaluate
y_pred = model.predict(X_scaled)
rmse = np.sqrt(mean_squared_error(y, y_pred))
r2 = r2_score(y, y_pred)

print(f"✅ Model trained. RMSE: {rmse:.2f}, R²: {r2:.2f}")

# Save model + scaler
joblib.dump(model, 'models/order_value_rf_model.pkl')
joblib.dump(scaler, 'models/order_value_scaler.pkl')
print("✅ Model and scaler saved to disk.")
# Save feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values(by='importance', ascending=False)
feature_importance.to_csv('models/feature_importance.csv', index=False)
print("✅ Feature importance saved to models/feature_importance.csv")
# Close database connection
conn.close()