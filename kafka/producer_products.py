import json
import time
import random
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Toys']

def generate_product(product_id):
    price = round(random.uniform(10.0, 500.0), 2)
    stock_level = random.randint(10, 100)  # random stock level
    return {
        'product_id': product_id,
        'name': f'Product_{product_id}',
        'category': random.choice(categories),
        'price': price,
        'stock_level': stock_level
    }

product_id = 1

while True:
    product = generate_product(product_id)
    producer.send('products_topic', product)
    print(f"Produced product: {product}")
    product_id += 1
    time.sleep(3)  # Every 3 seconds
