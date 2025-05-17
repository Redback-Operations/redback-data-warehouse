---
sidebar_position: 4
---

# Blob Storage using MinIO + Kafka + Airflow Integration

:::INFO

Document Creation: 17 May, 2025. Authors: Preeth Ramadoss, Peter Huang.

This documentation outlines the integration of **MinIO**, **Apache Kafka**, and **Apache Airflow** for real-time blob metadata processing in our Data Warehousing pipeline. All steps, configurations, and errors have been included to ensure reproducibility.

---

## Overview

We built a pipeline that:

--> Stores blobs in **MinIO** object storage.

--> Uses **Airflow** to fetch all blobs dynamically from the bucket.

--> Publishes file metadata previews to **Kafka**.

--> **Displays messages in **Kafdrop UI**.

---

## Docker Compose Setup

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,PLAINTEXT_HOST://0.0.0.0:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  kafdrop:
    image: obsidiandynamics/kafdrop
    ports:
      - "9002:9000"
    environment:
      KAFKA_BROKER_CONNECT: kafka:9092
      JVM_OPTS: "-Xms32M -Xmx64M"
    depends_on:
      - kafka

  minio:
    image: quay.io/minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  airflow-webserver:
    build: .
    image: custom-airflow:latest
    command: webserver
    ports:
      - "8888:8080"
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
    volumes:
      - ./dags:/opt/airflow/dags
      - airflow-db-volume:/opt/airflow
    user: "${AIRFLOW_UID:-50000}"
    depends_on:
      - airflow-scheduler
      - kafka
      - minio

  airflow-scheduler:
    build: .
    image: custom-airflow:latest
    command: scheduler
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
    volumes:
      - ./dags:/opt/airflow/dags
      - airflow-db-volume:/opt/airflow
    user: "${AIRFLOW_UID:-50000}"

  airflow-init:
    build: .
    image: custom-airflow:latest
    entrypoint: /bin/bash -c "airflow db migrate && airflow users create --username airflow --firstname admin --lastname user --role Admin --email admin@example.com --password airflow"
    environment:
      AIRFLOW__CORE__EXECUTOR: SequentialExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db
    volumes:
      - ./dags:/opt/airflow/dags
      - airflow-db-volume:/opt/airflow
    user: "${AIRFLOW_UID:-50000}"

volumes:
  airflow-db-volume:
  minio_data:
```

---

## Airflow DAG: test\_minio\_dag.py

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from minio import Minio
from kafka import KafkaProducer
import json

# Configs
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "project4bucket"
KAFKA_BROKER = "kafka:9092"
TOPIC_NAME = "project4-events"

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    dag_id="test_minio_dag",
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval="@once",
    catchup=False,
)

def read_all_blobs_and_publish():
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    objects = list(client.list_objects(BUCKET_NAME, recursive=True))
    if not objects:
        raise Exception("No objects found in bucket.")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    for obj in objects:
        response = client.get_object(BUCKET_NAME, obj.object_name)
        content = response.read(200)
        response.close()
        response.release_conn()

        preview = content.decode('utf-8', errors='ignore')
        event = {
            "bucket": BUCKET_NAME,
            "filename": obj.object_name,
            "timestamp": str(datetime.utcnow()),
            "preview": preview
        }

        result = producer.send(TOPIC_NAME, event).get(timeout=10)
        print(f" Kafka message sent: {event}")
        print(f"   ↳ Topic: {result.topic}, Partition: {result.partition}, Offset: {result.offset}")

    producer.flush()

process_all = PythonOperator(
    task_id="read_all_and_publish",
    python_callable=read_all_blobs_and_publish,
    dag=dag,
)
```

---

## Kafka Consumer Code (Testing)

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'project4-events',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening to topic 'project4-events'...")
for msg in consumer:
    print("Received:", msg.value)
```

---

## Screenshots & Output

* **MinIO Bucket Objects**
  ![MinIO](./Blob-Storage-Setup/results/Screenshot 2025-05-17 161432.png)

* **Airflow DAG Running**
  ![Airflow DAG](./Blob-Storage-Setup/results/Screenshot 2025-05-17 161534.png)

* **Kafka Messages in Kafdrop**
  ![Kafdrop](./Blob-Storage-Setup/results/Screenshot 2025-05-17 161608.png)

* **Docker Compose Setup**
  ![Docker PS](./Blob-Storage-Setup/results/Screenshot 2025-05-17 161728.png)

---

## Notes & Issues Faced

* Initial DAG failed due to missing `minio` and `kafka` Python packages.
* Kafka listener failed until `KAFKA_ADVERTISED_LISTENERS` and `KAFKA_LISTENER_SECURITY_PROTOCOL_MAP` were correctly defined.
* Ensured topics appear in **Kafdrop** by using `docker exec` to manually create the topic:

```
docker exec -it airflow_storage_setup-kafka-1 /usr/bin/kafka-topics --create   --bootstrap-server localhost:9092   --topic project4-events   --partitions 1   --replication-factor 1
```

---

## Conclusion

Successfully implemented a blob metadata publishing pipeline with:

* Dynamic MinIO file detection
* Kafka event streaming
* Airflow orchestration
* Kafdrop UI for message inspection

This system ensures our data warehouse ingests metadata from MinIO efficiently and provides visibility into data movement using Kafka.

**Setup Completed**.

---
