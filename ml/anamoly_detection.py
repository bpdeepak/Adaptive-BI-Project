import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["kafka_streaming"]
sales_collection = db["daily_sales"]

# Load data
sales_data = pd.DataFrame(list(sales_collection.find()))
sales_data['date'] = pd.to_datetime(sales_data['date'])
sales_data = sales_data.sort_values('date')

# Prepare features
X = sales_data[['total_sales']]

# Fit Isolation Forest
model = IsolationForest(contamination=0.05, random_state=42)
sales_data['anomaly'] = model.fit_predict(X)

# Flag anomalies
sales_data['anomaly'] = sales_data['anomaly'].apply(lambda x: 1 if x == -1 else 0)

# Save anomalies to MongoDB
anomalies = sales_data[sales_data['anomaly'] == 1][['date', 'total_sales']]
anomalies_collection = db["sales_anomalies"]
anomalies_collection.insert_many(anomalies.to_dict('records'))

print(f"Detected {len(anomalies)} anomalies and saved to 'sales_anomalies' collection.")
