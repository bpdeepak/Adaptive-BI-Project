import pymongo
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def load_data():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["kafka_streaming"]
    orders_collection = db["orders"]
    orders_cursor = orders_collection.find()
    orders_df = pd.DataFrame(list(orders_cursor))
    print(f"✅ Loaded {len(orders_df)} orders")
    return orders_df

def preprocess_data(orders_df, active_window_days=30):
    orders_df['timestamp'] = pd.to_datetime(orders_df['timestamp'])
    latest_date = orders_df['timestamp'].max()
    customer_last_order = orders_df.groupby('customer_id')['timestamp'].max().reset_index()
    customer_last_order['days_since_last_order'] = (latest_date - customer_last_order['timestamp']).dt.days
    customer_last_order['churned'] = np.where(customer_last_order['days_since_last_order'] > active_window_days, 1, 0)

    customer_features = orders_df.groupby('customer_id').agg({
        'order_id': 'count',
        'price': ['sum', 'mean']
    }).reset_index()
    customer_features.columns = ['customer_id', 'total_orders', 'total_spend', 'avg_order_value']

    churn_data = pd.merge(customer_features, customer_last_order[['customer_id', 'churned']], on='customer_id')
    return churn_data

def train_model(churn_data):
    X = churn_data[['total_orders', 'total_spend', 'avg_order_value']]
    y = churn_data['churned']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

    # Feature importance
    importance = model.coef_[0]
    for i, col in enumerate(X.columns):
        print(f"Feature: {col}, Importance: {importance[i]:.4f}")

    return model, churn_data, X

def save_predictions(model, churn_data, X):
    churn_data['prediction'] = model.predict(X)
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["kafka_streaming"]
    churn_collection = db["customer_churn_predictions"]
    churn_collection.delete_many({})
    churn_collection.insert_many(churn_data.to_dict('records'))
    print("✅ Predictions saved to MongoDB 'customer_churn_predictions' collection.")

def save_model_and_data(model, X):
    joblib.dump(model, 'models/churn_model.pkl')
    pd.DataFrame(X, columns=['total_orders', 'total_spend', 'avg_order_value']).to_csv('data/churn_data.csv', index=False)
    print("✅ Model saved as 'models/churn_model.pkl'")
    print("✅ Feature data saved as 'data/churn_data.csv'")

if __name__ == "__main__":
    orders_df = load_data()
    churn_data = preprocess_data(orders_df)
    model, churn_data, X = train_model(churn_data)
    save_predictions(model, churn_data, X)
    save_model_and_data(model, X)
    print("✅ Churn prediction pipeline complete!")
