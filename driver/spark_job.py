from pyspark.sql import SparkSession
from pyspark.sql.functions import window, sum
from pyspark.sql.types import IntegerType, StringType, StructType, StructField, TimestampType

# Create a Spark session
spark = SparkSession.builder.appName("RealTimeTopProducts").getOrCreate()

# Define the Kafka configuration
kafka_bootstrap_servers = "kafka:9092"
kafka_topic = "products-sold"

# Define the schema for the Kafka message value
kafka_message_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("timestamp", TimestampType(), True)  # Assuming timestamp is already present in data
])

# Read data from Kafka topic
kafka_stream_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .load()

# Parse the JSON value from the Kafka message
parsed_data_df = kafka_stream_df \
    .selectExpr("CAST(value AS STRING)") \
    .selectExpr("from_json(value, '{}') AS data") \
    .selectExpr("data.*")

# Perform windowed processing
windowed_df = parsed_data_df \
    .withWatermark("timestamp", "2 seconds") \
    .groupBy(window("timestamp", "2 seconds", "1 second")) \
    .agg(sum("quantity").alias("totalQuantity")) \
    .orderBy("totalQuantity", ascending=False) \
    .limit(10)

# Define the query to output the top products in real-time
query = windowed_df \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

# Await the termination of the query
query.awaitTermination()

# Stop the Spark session
spark.stop()
