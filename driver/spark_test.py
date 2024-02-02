from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, LongType
from pyspark.sql.functions import rand

# Create a Spark session
# spark = SparkSession.builder.appName("GenerateRetailData").enableHiveSupport().getOrCreate()
spark = SparkSession.builder \
    .appName("PySparkHiveExample") \
    .config("spark.sql.catalogImplementation", "hive") \
    .config("hive.metastore.uris", "thrift://hive:9083") \
    .enableHiveSupport() \
    .getOrCreate()
# Define the schema for the retail_data table
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("timestamp", LongType(), True)
])

# Generate random data
num_rows = 1000
random_data = spark.range(num_rows).selectExpr(
    "id",
    "concat('Product', cast(id as string)) as name",
    "cast(rand() * 100 as int) as quantity",
    "cast(current_timestamp() as long) as timestamp"
)

# Show the generated data
random_data.show()

# Save the random data to the retail_data table in Hive
random_data.write.mode("append").format("hive").saveAsTable("retail_data")

# Stop the Spark session
spark.stop()
