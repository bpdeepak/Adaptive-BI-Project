# ai_module/explainability.py

import pandas as pd
import shap
import lime
import lime.lime_tabular
import joblib
import tensorflow as tf
import warnings
warnings.filterwarnings("ignore")

# ---------- Utility: Run SHAP + LIME ----------

def run_shap_lime(model, data, model_name, mode='classification'):
    print(f"\n=== {model_name.upper()} ===")

    # ---- SHAP ----
    print(f"Generating SHAP summary plot for {model_name}...")

    if hasattr(model, 'predict_proba'):
        pred_fn = model.predict_proba
    elif hasattr(model, 'decision_function'):
        pred_fn = model.decision_function
    else:
        pred_fn = model.predict

    explainer = shap.Explainer(pred_fn, data)
    shap_values = explainer(data)
    shap.summary_plot(shap_values, data)

    # ---- LIME ----
    if hasattr(model, 'predict_proba'):
        print(f"Generating LIME explanation for {model_name} (first sample)...")
        feature_names = list(data.columns)
        X = data.values

        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X,
            feature_names=feature_names,
            class_names=['Normal', 'Anomaly'] if mode == 'classification' else None,
            mode=mode
        )

        sample_idx = 0
        exp = lime_explainer.explain_instance(X[sample_idx], pred_fn, num_features=5)
        exp.show_in_notebook(show_table=True)
    else:
        print(f"⚠️ Skipping LIME for {model_name} (no predict_proba support)")


# ---------- Churn Prediction ----------

churn_model = joblib.load('models/churn_model.pkl')
churn_data = pd.read_csv('data/churn_data.csv').drop(columns=['churned'], errors='ignore')
run_shap_lime(churn_model, churn_data, 'churn prediction', mode='classification')


# ---------- Anomaly Detection ----------

anomaly_model = joblib.load('models/anomaly_model.pkl')
anomaly_data = pd.read_csv('data/anomaly_data.csv').drop(columns=['anomaly', 'anomaly_label', 'date'], errors='ignore')
run_shap_lime(anomaly_model, anomaly_data, 'anomaly detection', mode='classification')


# ---------- Sales Forecast ----------

sales_model = tf.keras.models.load_model('models/sales_forecast_model.h5', compile=False)
sales_model.compile(optimizer='adam', loss='mean_squared_error')
sales_data = pd.read_csv('data/sales_forecast.csv')
features = sales_data[['predicted_sales']]  # Use the actual column present
run_shap_lime(sales_model, features, 'sales forecast', mode='regression')
