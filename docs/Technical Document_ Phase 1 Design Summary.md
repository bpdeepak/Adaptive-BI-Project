## **Technical Document: Phase 1 Design Summary**

---

### **Project Title**

**Adaptive Business Intelligence in the Era of Data Deluge: A Cognitive AI Framework for Sustainable Decision-Making**

---

### **Phase 1 Objective**

Design and implement the foundational components of the Adaptive BI system, focusing on synthetic data generation, real-time ingestion, big data processing, ML model integration, and visualization.

---

### **Core Components**

| Layer | Description |
| ----- | ----- |
| **Data Simulation** | Python script using Faker to generate synthetic e-commerce orders |
| **Streaming Layer** | Kafka setup to ingest real-time messages |
| **Processing Layer** | Spark Streaming jobs to consume, transform, and store incoming data |
| **Storage Layer** | PostgreSQL to hold processed data |
| **ML Layer** | Scikit-learn models for forecasting and adaptive decision-making |
| **Visualization Layer** | Streamlit dashboard to visualize insights and monitor system status |

---

### **Data Schemas**

1️⃣ **Orders**

* `order_id` (UUID)  
* `customer_id` (UUID)  
* `product_id` (UUID)  
* `quantity` (int)  
* `price` (float)  
* `timestamp` (ISO 8601\)

2️⃣ **Customers**

* `customer_id` (UUID)  
* `name` (string)  
* `email` (string)  
* `location` (string)  
* `signup_date` (ISO 8601\)

3️⃣ **Products**

* `product_id` (UUID)  
* `name` (string)  
* `category` (string)  
* `price` (float)  
* `stock_level` (int)

---

### **Technology Stack**

| Component | Tool / Library |
| ----- | ----- |
| Language | Python 3.10+ |
| Streaming | Apache Kafka |
| Processing | Apache Spark (with PySpark) |
| Storage | PostgreSQL 14+ |
| ML Framework | Scikit-learn (initial) |
| Dashboard | Streamlit |

