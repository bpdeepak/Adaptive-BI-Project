import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["kafka_streaming"]
customers_collection = db["customers"]

# Load data
customers = pd.DataFrame(list(customers_collection.find()))

# Example feature engineering (replace with real features later)
customers['churned'] = np.random.choice([0, 1], size=len(customers))  # mock churn labels

features = customers[['signup_days', 'num_orders', 'avg_order_value']]
labels = customers['churned']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Predict on all customers
customers['churn_probability'] = model.predict_proba(features)[:, 1]

# Save predictions to MongoDB
churn_collection = db["churn_predictions"]
churn_collection.insert_many(customers[['customer_id', 'churn_probability']].to_dict('records'))

print(f"Churn predictions saved to 'churn_predictions' collection.")
