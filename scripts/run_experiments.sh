#!/bin/bash
set -e

wait_for_hadoop() {
    while ! curl -s "http://localhost:9870" > /dev/null; do
        sleep 1
    done
    echo "Hadoop is up and running"
}

run_hadoop_cluster() {
    local config=$1
    echo "=== Running with ${config} configuration ==="

    cd "docker/${config}"
    docker compose down -v 2>/dev/null || true
    docker compose up -d
    echo "Waiting for Hadoop to initialize..."
    wait_for_hadoop

    cd ../../
    bash scripts/upload_data.sh
}

run_spark_jobs() {
    local config=$1
    echo "Running Spark job without optimization..."
    python3 spark_app/main.py --exp_name "${config}"

    echo "Running Spark job with optimization..."
    python3 spark_app/main.py --exp_name "${config}" --optimized
}

cleanup_cluster() {
    local config=$1
    cd "docker/${config}"
    docker compose down -v
    cd ../../
}

mkdir -p results

CONFIG_1NODE="hadoop-1node"
CONFIG_3NODE="hadoop-3node"

cleanup_all_clusters() {
    echo "Cleaning up all clusters..."
    cleanup_cluster "${CONFIG_1NODE}" || true
    cleanup_cluster "${CONFIG_3NODE}" || true
}

trap cleanup_all_clusters EXIT

echo "Starting experiments..."
bash scripts/download_data.sh

run_hadoop_cluster "${CONFIG_1NODE}"
run_spark_jobs "${CONFIG_1NODE}"
cleanup_cluster "${CONFIG_1NODE}"

run_hadoop_cluster "${CONFIG_3NODE}"
run_spark_jobs "${CONFIG_3NODE}"
cleanup_cluster "${CONFIG_3NODE}"

echo "All experiments completed! Results are in the 'results' directory."