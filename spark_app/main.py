import sys
import time
import psutil
import logging
from pyspark.sql import SparkSession
from utils import setup_logging, optimize_spark_job
import argparse
import json
import os
from pyspark.sql import functions as F

def get_memory_usage():
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def main(args):
    setup_logging()
    logger = logging.getLogger(__name__)

    spark = SparkSession.builder.master("local") \
        .appName("SpotifyAnalysis") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

    logger.info("Starting data processing")
    start_time = time.time()
    initial_memory = get_memory_usage()

    try:
        hdfs_path = "hdfs://localhost:9000/data/spotify_dataset.csv"
        try:
            df = spark.read.csv(hdfs_path, header=True)
        except Exception as e:
            logger.error("Failed to read file from HDFS: {}".format(e))
            sys.exit(1)

        if args.optimized:
            logger.info("Applying optimizations...")
            df = optimize_spark_job(df)

        numerical_features = ['Tempo', 'Loudness (db)', 'Energy', 'Danceability', 'Positiveness', 'Speechiness']

        for col in numerical_features:
            df = df.withColumn(col, F.col(col).cast('double'))

        correlation_matrix = {}
        for i, col1 in enumerate(numerical_features):
            for col2 in numerical_features[i+1:]:
                corr_value = df.stat.corr(col1, col2)
                correlation_matrix["{}-{}".format(col1, col2)] = corr_value
        logger.info("Correlation matrix: {}".format(correlation_matrix))

        avg_energy = (
            df.groupBy('Genre')
            .agg(F.mean('Energy').alias('avg_energy'))
            .orderBy(F.desc('avg_energy'))
        )
        logger.info("Average energy by genre (top 5):")
        for row in avg_energy.limit(5).collect():
            logger.info(row)

        emotion_counts = (
            df.groupBy('emotion')
            .count()
            .orderBy(F.desc('count'))
        )
        logger.info("Emotion counts:")
        for row in emotion_counts.collect():
            logger.info(row)

        
        for col in ['Similar Song 1', 'Similarity Score 1']:
            df = df.withColumn(col, F.col(col).cast('double'))

        top_similar_songs = (
            df.select('Similar Song 1', 'Similarity Score 1')
            .orderBy(F.desc('Similarity Score 1'))
            .limit(5)
        )
        logger.info("Top 5 similar songs:")
        for row in top_similar_songs.collect():
            logger.info(row)

        end_time = time.time()
        final_memory = get_memory_usage()
    
        metrics = {
            "execution_time": end_time - start_time,
            "memory_usage_mb": final_memory - initial_memory,
            "optimized": args.optimized,
            "exp_name": args.exp_name,
        }
        os.makedirs('results', exist_ok=True)
        with open('results/execution_metrics_{}_opt_{}.json'.format(args.exp_name, args.optimized), 'w') as f:
            json.dump(metrics, f, indent=4)

        logger.info("Execution time: {} seconds".format(end_time - start_time))
        logger.info("Memory usage: {} MB".format(final_memory - initial_memory))

    finally:
        spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark app")
    parser.add_argument(
        "--exp_name",
        type=str,
        default="local",
        help="Name of the experiment"
    )
    parser.add_argument(
        "--optimized",
        action="store_true",
        help="Enable Spark optimizations"
    )
    args = parser.parse_args()
    main(args)
