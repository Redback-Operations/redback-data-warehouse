#!/bin/sh

echo "Initializing Restic repository if not exists..."
if ! restic snapshots > /dev/null 2>&1; then
  restic init
fi

while true; do
  echo "Starting Restic backup..."
  restic backup\
  /data-lakehouse_minio-data\
  /data-lakehouse_minio-config \
  /fileuploadservice_dremio-data \
  /dp-postgres-data \
  /dp-es-data \
  /dp-logstash-data
  echo "Backup completed. Sleeping for 4 minutes..."
  #find /localbackup -type f -delete
  echo "Sleeping for 4 minutes..."
  sleep 240
done
