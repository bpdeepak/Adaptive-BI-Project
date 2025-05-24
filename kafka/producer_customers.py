import json
import time
import random
import uuid
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']

def generate_customer():
    customer_id = str(uuid.uuid4())
    name = f"Customer_{customer_id[:8]}"  # short UUID part for readable name
    email = f"{name.lower()}@example.com"
    location = random.choice(locations)
    signup_date = datetime.utcnow().isoformat()
    return {
        'customer_id': customer_id,
        'name': name,
        'email': email,
        'location': location,
        'signup_date': signup_date
    }

while True:
    customer = generate_customer()
    producer.send('customers_topic', customer)
    print(f"Produced customer: {customer}")
    time.sleep(2)  # Every 2 seconds
