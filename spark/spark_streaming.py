from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType, TimestampType

# MongoDB connection configs
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "kafka_streaming"

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("KafkaSparkMongoStreaming") \
    .config("spark.mongodb.write.connection.uri", f"{MONGO_URI}/{DB_NAME}") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define schemas for each topic
customer_schema = StructType() \
    .add("customer_id", StringType()) \
    .add("name", StringType()) \
    .add("email", StringType()) \
    .add("location", StringType()) \
    .add("signup_date", StringType())

order_schema = StructType() \
    .add("order_id", StringType()) \
    .add("customer_id", StringType()) \
    .add("product_id", IntegerType()) \
    .add("quantity", IntegerType()) \
    .add("price", DoubleType()) \
    .add("timestamp", StringType())

product_schema = StructType() \
    .add("product_id", IntegerType()) \
    .add("name", StringType()) \
    .add("category", StringType()) \
    .add("price", DoubleType()) \
    .add("stock_level", IntegerType())

# Read from Kafka
def read_kafka_topic(topic):
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", topic) \
        .option("startingOffsets", "latest") \
        .load() \
        .selectExpr("CAST(value AS STRING) as json_str")

# Process and write to MongoDB
def process_and_write(df, schema, collection):
    parsed_df = df.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

    query = parsed_df.writeStream \
        .format("mongodb") \
        .option("checkpointLocation", f"/tmp/spark_checkpoint/{collection}") \
        .option("collection", collection) \
        .outputMode("append") \
        .start()
    
    return query

# Set up streams
customers_df = read_kafka_topic("customers_topic")
orders_df = read_kafka_topic("orders_topic")
products_df = read_kafka_topic("products_topic")

# Write to MongoDB collections
customers_query = process_and_write(customers_df, customer_schema, "customers")
orders_query = process_and_write(orders_df, order_schema, "orders")
products_query = process_and_write(products_df, product_schema, "products")

# Wait for termination
spark.streams.awaitAnyTermination()
