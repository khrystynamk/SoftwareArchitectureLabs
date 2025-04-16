#!/bin/bash

BASE_PATH="$(pwd)"
HAZELCAST_PATH="$BASE_PATH/hazelcast-5.5.0"
HAZELCAST_CONFIG_PATH="$BASE_PATH/hazelcast.xml"

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

    # facade
    uvicorn facade_service:app --host 127.0.0.1 --port 8000 &

    # config
    uvicorn config_server:app --host 127.0.0.1 --port 8001 &

    # logging
    SERVICE_INSTANCE=0 uvicorn logging_service:app --host 127.0.0.1 --port 8081 &
    SERVICE_INSTANCE=1 uvicorn logging_service:app --host 127.0.0.1 --port 8082 &
    SERVICE_INSTANCE=2 uvicorn logging_service:app --host 127.0.0.1 --port 8083 &

    # messages
    uvicorn messages_service:app --host 127.0.0.1 --port 8084 &
}

trap "echo 'Shutting down...'; stop_hazelcast_nodes; exit 0" SIGINT SIGTERM

start_hazelcast_nodes

start_services

wait
