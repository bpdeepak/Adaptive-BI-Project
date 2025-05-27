# anomaly_detection.py

import pymongo
import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest

def fetch_orders(mongo_uri="mongodb://localhost:27017/", db_name="kafka_streaming", collection_name="orders"):
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    orders_cursor = collection.find()
    orders_df = pd.DataFrame(list(orders_cursor))
    return orders_df

def detect_anomalies(orders_df):
    orders_df['timestamp'] = pd.to_datetime(orders_df['timestamp'])
    orders_df['date'] = pd.to_datetime(orders_df['timestamp'].dt.date)  # Ensures datetime format for MongoDB
    daily_sales = orders_df.groupby('date').agg({'price': 'sum'}).reset_index()
    daily_sales.rename(columns={'price': 'daily_total'}, inplace=True)

    iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    daily_sales['anomaly'] = iso_forest.fit_predict(daily_sales[['daily_total']])
    daily_sales['anomaly_label'] = daily_sales['anomaly'].map({1: 'Normal', -1: 'Anomaly'})

    return daily_sales, iso_forest

def save_anomalies(daily_sales, mongo_uri="mongodb://localhost:27017/", db_name="kafka_streaming", collection_name="sales_anomalies"):
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    anomaly_collection = db[collection_name]
    anomaly_collection.delete_many({})  # Clear old data
    records = daily_sales.to_dict('records')
    anomaly_collection.insert_many(records)
    print(f"✅ Saved {len(records)} anomaly records to MongoDB collection '{collection_name}'")

def save_model_and_data(model, daily_sales):
    # Ensure directories exist
    os.makedirs("models", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # Save model
    model_path = "models/anomaly_model.pkl"
    joblib.dump(model, model_path)

    # Save dataset
    data_path = "data/anomoly_data.csv"
    daily_sales.to_csv(data_path, index=False)

    print(f"✅ Model saved to '{model_path}'")
    print(f"✅ Feature data saved to '{data_path}'")

if __name__ == "__main__":
    print("🚀 Starting anomaly detection process...")
    orders_df = fetch_orders()
    print(f"Loaded {len(orders_df)} orders from MongoDB.")

    daily_sales, model = detect_anomalies(orders_df)
    num_anomalies = (daily_sales['anomaly_label'] == 'Anomaly').sum()
    print(f"Detected {num_anomalies} anomalies out of {len(daily_sales)} days.")

    save_anomalies(daily_sales)
    save_model_and_data(model, daily_sales)
    print("✅ Anomaly detection process complete!")
