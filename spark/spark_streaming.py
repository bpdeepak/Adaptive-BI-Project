from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, regexp_replace
from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType, TimestampType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkToPostgres") \
    .getOrCreate()

# Define schema for incoming data from Kafka
json_schema = StructType() \
    .add("order_id", StringType()) \
    .add("customer_id", StringType()) \
    .add("product_id", IntegerType()) \
    .add("quantity", IntegerType()) \
    .add("price", DoubleType()) \
    .add("timestamp", StringType())

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "orders_topic") \
    .load()

# Parse JSON and apply necessary casts to match PostgreSQL table types
orders_df = df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), json_schema).alias("data")) \
    .select(
        col("data.order_id").cast(StringType()).alias("order_id"),
        col("data.customer_id").cast(StringType()).alias("customer_id"),
        col("data.product_id").cast(IntegerType()).alias("product_id"),
        col("data.quantity").cast(IntegerType()).alias("quantity"),
        col("data.price").cast(DoubleType()).alias("price"),
        col("data.timestamp").cast(TimestampType()).alias("timestamp")
    )

# Write stream to PostgreSQL using foreachBatch
def write_to_postgres(batch_df, epoch_id):
    print(f"--- Batch {epoch_id} Schema Before Write ---")
    batch_df.printSchema()
    print(f"--- Sample Data for Batch {epoch_id} (first 5 rows) Before Write ---")
    # This time, let's force the show to complete by collecting a small sample
    # Note: collecting data to driver can be problematic for large DFs,
    # but for debugging small batches, it's fine.
    try:
        sample_data = batch_df.limit(5).collect()
        for row in sample_data:
            print(row)
    except Exception as e:
        print(f"Could not show sample data: {e}")

    try:
        batch_df.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://localhost:5432/adaptive_bi") \
            .option("dbtable", "orders") \
            .option("user", "bi_user") \
            .option("password", "bi_pass") \
            .option("driver", "org.postgresql.Driver") \
            .option("stringtype", "unspecified") \
            .mode("append") \
            .save()
        print(f"Batch {epoch_id} successfully written to PostgreSQL.")
    except Exception as e:
        print(f"Error writing batch {epoch_id} to PostgreSQL: {e}")

query = orders_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .start()

query.awaitTermination()