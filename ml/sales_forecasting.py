# ml/sales_forecasting.py

import pandas as pd
import numpy as np
from pymongo import MongoClient
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client.kafka_streaming
orders_col = db.orders
forecast_col = db.sales_forecast

# Parameters
time_steps = 10
forecast_horizon = 7

# 1️⃣ Load data from MongoDB
print("📦 Loading order data from MongoDB...")
orders = list(orders_col.find({}, {'_id': 0, 'timestamp': 1, 'price': 1, 'quantity': 1}))
df = pd.DataFrame(orders)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['sales'] = df['price'] * df['quantity']
df = df.set_index('timestamp').resample('D').sum().fillna(0)

# 2️⃣ Prepare data for LSTM
def create_sequences(data, time_steps):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:(i + time_steps)])
        y.append(data[i + time_steps])
    return np.array(X), np.array(y)

series = df['sales'].values
series_min, series_max = np.min(series), np.max(series)
series = (series - series_min) / (series_max - series_min)  # normalize
X, y = create_sequences(series, time_steps)
X = np.expand_dims(X, axis=-1)

# 3️⃣ Build LSTM model
model = Sequential([
    LSTM(50, activation='relu', input_shape=(time_steps, 1)),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')

# 4️⃣ Train model
print("🧠 Training LSTM model...")
model.fit(X, y, epochs=20, verbose=1)

# 5️⃣ Save model
os.makedirs('models', exist_ok=True)
model_path = 'models/sales_forecast_model.h5'
model.save(model_path)
print(f"✅ Model saved to {model_path}")

# 6️⃣ Generate forecast
last_sequence = series[-time_steps:]
forecast_input = np.expand_dims(last_sequence, axis=(0, -1))
forecast = []
for _ in range(forecast_horizon):
    pred = model.predict(forecast_input, verbose=0)[0, 0]
    forecast.append(pred)
    last_sequence = np.append(last_sequence[1:], pred)
    forecast_input = np.expand_dims(last_sequence, axis=(0, -1))

# Denormalize forecast
forecast = np.array(forecast) * (series_max - series_min) + series_min

# 7️⃣ Save forecast to MongoDB and CSV
forecast_dates = pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=forecast_horizon)
forecast_df = pd.DataFrame({
    'date': forecast_dates,
    'predicted_sales': forecast
})

# Insert into MongoDB
forecast_col.delete_many({})  # Optional: clear old forecasts
forecast_col.insert_many(forecast_df.to_dict('records'))
print(f"✅ Inserted {forecast_horizon} forecast entries into MongoDB collection 'sales_forecast'")

# Save to CSV
os.makedirs('data', exist_ok=True)
csv_path = 'data/sales_forecast.csv'
forecast_df.to_csv(csv_path, index=False)
print(f"✅ Forecast data saved to {csv_path}")
