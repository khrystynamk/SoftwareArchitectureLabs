#!/bin/bash

BASE_PATH="$(pwd)"
HAZELCAST_PATH="$BASE_PATH/hazelcast-5.5.0"
HAZELCAST_CONFIG_PATH="$BASE_PATH/hazelcast-5.5.0/config/hazelcast.xml"

start_hazelcast_nodes() {
    echo "Starting Hazelcast nodes..."
    cd "$HAZELCAST_PATH"
    bin/hz start -c "$HAZELCAST_CONFIG_PATH" &
    bin/hz start -c "$HAZELCAST_CONFIG_PATH" &
    bin/hz start -c "$HAZELCAST_CONFIG_PATH" &

    sleep 5
}

stop_hazelcast_nodes() {
    echo "Stopping Hazelcast nodes..."
    pkill -f "hazelcast"
}

start_services() {
    cd "$BASE_PATH"
    echo "Starting the services..."

    python3 prerequisites.py
    # facade
    FACADE_INSTANCE=0 PORT=8000 python3 -m uvicorn facade_service:app --host 127.0.0.1 --port 8000 &

    # # logging
    LOG_SERVICE_INSTANCE=0 PORT=8081 python3 -m uvicorn logging_service:app --host 127.0.0.1 --port 8081 &
    LOG_SERVICE_INSTANCE=1 PORT=8082 python3 -m uvicorn logging_service:app --host 127.0.0.1 --port 8082 &
    LOG_SERVICE_INSTANCE=2 PORT=8083 python3 -m uvicorn logging_service:app --host 127.0.0.1 --port 8083 &

    # messages
    MES_SERVICE_INSTANCE=0 PORT=8101 python3 -m uvicorn messages_service:app --host 127.0.0.1 --port 8101 &
    MES_SERVICE_INSTANCE=1 PORT=8102 python3 -m uvicorn messages_service:app --host 127.0.0.1 --port 8102 &
}

trap "echo 'Shutting down...'; stop_hazelcast_nodes; exit 0" SIGINT SIGTERM

start_hazelcast_nodes

start_services

wait
