import logging
from pyspark.sql import DataFrame

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('spark_app.log'),
            logging.StreamHandler()
        ]
    )

    logging.getLogger("org.apache.spark").setLevel(logging.ERROR)
    logging.getLogger("org.apache.hadoop").setLevel(logging.ERROR)

def optimize_spark_job(df) -> DataFrame:
    logger = logging.getLogger(__name__)

    optimal_partitions = max(df.rdd.getNumPartitions() * 2, 8)
    logger.info(f"Repartitioning to {optimal_partitions} partitions")
    optimized_df = df.repartition(optimal_partitions)

    optimized_df.cache()
    optimized_df.count()
    
    logger.info("Applied optimizations: repartitioning and caching")
    return optimized_df
