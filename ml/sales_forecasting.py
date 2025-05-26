# ml/sales_forecasting.py

import pandas as pd
import numpy as np
from pymongo import MongoClient
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import pickle
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
print("Loading order data from MongoDB...")
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
series = (series - np.min(series)) / (np.max(series) - np.min(series))  # normalize
X, y = create_sequences(series, time_steps)
X = np.expand_dims(X, axis=-1)

# 3️⃣ Build LSTM model
model = Sequential([
    LSTM(50, activation='relu', input_shape=(time_steps, 1)),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')

# 4️⃣ Train model
print("Training LSTM model...")
model.fit(X, y, epochs=20, verbose=1)

# 5️⃣ Save model
os.makedirs('models', exist_ok=True)
model.save('models/sales_forecast_model.h5')
print("Model saved to models/sales_forecast_model.h5")

# 6️⃣ Generate forecast
last_sequence = series[-time_steps:]
forecast_input = np.expand_dims(last_sequence, axis=(0, -1))
forecast = []
for _ in range(forecast_horizon):
    pred = model.predict(forecast_input)[0, 0]
    forecast.append(pred)
    last_sequence = np.append(last_sequence[1:], pred)
    forecast_input = np.expand_dims(last_sequence, axis=(0, -1))

forecast = np.array(forecast) * (np.max(df['sales']) - np.min(df['sales'])) + np.min(df['sales'])

# 7️⃣ Write forecast to MongoDB
forecast_dates = pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=forecast_horizon)
for date, value in zip(forecast_dates, forecast):
    forecast_col.insert_one({'date': date.strftime('%Y-%m-%d'), 'predicted_sales': float(value)})

print(f"Inserted {forecast_horizon} forecast entries into MongoDB collection 'sales_forecast'")
