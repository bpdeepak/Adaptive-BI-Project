import random
import json
import time
from faker import Faker
from kafka import KafkaProducer

fake = Faker()

customers = [fake.uuid4() for _ in range(10)]  # List of fake customer IDs

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_order():
    return {
        'order_id': fake.uuid4(),
        'customer_id': random.choice(customers),
        'product_id': random.randint(1, 21),  # Assuming product IDs from 1 to 21
        'quantity': random.randint(1, 5),
        'price': round(random.uniform(100, 1000), 2),
        'timestamp': fake.iso8601()
    }

while True:
    order = generate_order()
    producer.send('orders_topic', order)
    print(f"Sent: {order}")
    time.sleep(1)
