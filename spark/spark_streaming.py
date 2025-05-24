from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, to_timestamp
from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType, TimestampType
import uuid

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaSparkToPostgres") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# -------------------------------
# Define schemas to match PostgreSQL
# -------------------------------
order_schema = StructType() \
    .add("order_id", StringType()) \
    .add("customer_id", StringType()) \
    .add("product_id", IntegerType()) \
    .add("quantity", IntegerType()) \
    .add("price", DoubleType()) \
    .add("timestamp", StringType())

customer_schema = StructType() \
    .add("customer_id", StringType()) \
    .add("name", StringType()) \
    .add("email", StringType()) \
    .add("location", StringType()) \
    .add("signup_date", StringType())

product_schema = StructType() \
    .add("product_id", IntegerType()) \
    .add("name", StringType()) \
    .add("category", StringType()) \
    .add("price", DoubleType()) \
    .add("stock_level", IntegerType())

# -------------------------------
# UUID validator/converter UDF
# -------------------------------
def to_uuid_str(s):
    if s:
        try:
            return str(uuid.UUID(s))
        except Exception:
            return None
    return None

uuid_udf = udf(to_uuid_str, StringType())

# -------------------------------
# Write to PostgreSQL function
# -------------------------------
def write_to_postgres(batch_df, epoch_id, table_name):
    print(f"\n--- Batch {epoch_id} for {table_name} ---")
    batch_df.printSchema()

    try:
        batch_df.limit(5).show(truncate=False)
    except Exception as e:
        print(f"Error previewing data: {e}")

    if batch_df.rdd.isEmpty():
        print(f"Skipping Batch {epoch_id} for {table_name}: Empty DataFrame.")
        return

    jdbc_url = "jdbc:postgresql://localhost:5432/adaptive_bi?stringtype=unspecified"

    try:
        batch_df.write \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", table_name) \
            .option("user", "bi_user") \
            .option("password", "bi_pass") \
            .option("driver", "org.postgresql.Driver") \
            .option("batchsize", "1000") \
            .option("isolationLevel", "NONE") \
            .mode("append") \
            .save()
        print(f"Batch {epoch_id} for {table_name} successfully written.")
    except Exception as e:
        print(f"Write error for {table_name} in Batch {epoch_id}: {e}")

# -------------------------------
# Process orders stream
# -------------------------------
orders_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "orders_topic") \
    .option("startingOffsets", "latest") \
    .load()

orders_df = orders_df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), order_schema).alias("data")) \
    .select(
        col("data.order_id"),
        col("data.customer_id"),
        col("data.product_id"),
        col("data.quantity"),
        col("data.price"),
        to_timestamp(col("data.timestamp")).alias("timestamp")
    )

orders_query = orders_df.writeStream \
    .foreachBatch(
        lambda df, epoch_id: write_to_postgres(
            df
            .withColumn("order_id", uuid_udf(col("order_id")))
            .withColumn("customer_id", uuid_udf(col("customer_id"))),
            epoch_id,
            "orders"
        )
    ) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoints/orders") \
    .start()

# -------------------------------
# Process customers stream
# -------------------------------
customers_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "customers_topic") \
    .option("startingOffsets", "latest") \
    .load()

customers_df = customers_df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), customer_schema).alias("data")) \
    .select(
        col("data.customer_id"),
        col("data.name"),
        col("data.email"),
        col("data.location"),
        to_timestamp(col("data.signup_date")).alias("signup_date")
    )

customers_query = customers_df.writeStream \
    .foreachBatch(
        lambda df, epoch_id: write_to_postgres(
            df.withColumn("customer_id", uuid_udf(col("customer_id"))),
            epoch_id,
            "customers"
        )
    ) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoints/customers") \
    .start()

# -------------------------------
# Process products stream
# -------------------------------
products_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "products_topic") \
    .option("startingOffsets", "latest") \
    .load()

products_df = products_df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), product_schema).alias("data")) \
    .select(
        col("data.product_id"),
        col("data.name"),
        col("data.category"),
        col("data.price"),
        col("data.stock_level")
    )

products_query = products_df.writeStream \
    .foreachBatch(lambda df, epoch_id: write_to_postgres(df, epoch_id, "products")) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoints/products") \
    .start()

# -------------------------------
# Keep streams running
# -------------------------------
spark.streams.awaitAnyTermination()
