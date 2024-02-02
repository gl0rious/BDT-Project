import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object SparkJob {
  def main(args: Array[String]): Unit = {
    // Create a Spark session
    val spark = SparkSession.builder
      .appName("RealTimeTopProducts")
      .config("hive.metastore.uris", "thrift://hive:9083")
      .enableHiveSupport()
      .getOrCreate()

    // Define the Kafka configuration
    val kafkaBootstrapServers = "kafka:9092"
    val kafkaTopic = "products-sold"

    // Define the schema for the Kafka message value
    val kafkaMessageSchema = StructType(
      StructField("id", IntegerType, true) ::
      StructField("name", StringType, true) ::
      StructField("quantity", IntegerType, true) ::
      StructField("timestamp", TimestampType, true) :: Nil
    )

    // Read data from Kafka topic
    val kafkaStreamDF = spark
      .readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", kafkaBootstrapServers)
      .option("subscribe", kafkaTopic)
      .load()

    // Parse the JSON value from the Kafka message
    val parsedDataDF = kafkaStreamDF
      .selectExpr("CAST(value AS STRING)")
      .select(from_json(col("value"), kafkaMessageSchema).alias("data"))
      .selectExpr("data.*")
      //.selectExpr("data.*", "current_timestamp() AS timestamp")

    // Perform windowed processing
    // val windowedDF = parsedDataDF
     // .withWatermark("timestamp", "1 seconds")
     // .groupBy(window(col("timestamp"), "1 seconds"), col("name"))
     // .agg(sum("quantity").alias("totalQuantity"))
     // .orderBy(col("totalQuantity").desc)
     // .limit(10)
     // .select( "name", "totalQuantity")

    // Define the query to output the top products in real-time
    //val query = windowedDF
    //  .writeStream
    //  .outputMode("complete")
    //  .format("console")
    //  .start()
    parsedDataDF.writeStream
      .outputMode("append")
      .format("hive")
      .table("retail_data")
      .start()

    // Await the termination of the query
    query.awaitTermination()

    // Stop the Spark session
    spark.stop()
  }
}
