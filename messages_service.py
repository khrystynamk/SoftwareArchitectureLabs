import time
import os
import json

from fastapi import FastAPI
from threading import Thread
from dotenv import load_dotenv
from confluent_kafka import Consumer
from prerequisites import register_service, deregister_service, get_key_value_item

app = FastAPI()
load_dotenv()

SERVICE_IDX = int(os.getenv("MES_SERVICE_INSTANCE"))
PORT = os.getenv("PORT")
HOST = os.getenv("HOST")
register_service("messages-service", SERVICE_IDX, PORT, HOST)
messages = []

topic = get_key_value_item("kafka/topic")
data = get_key_value_item("kafka/nodes")
node_addresses = data.decode()

consumer = Consumer(
    {
        "bootstrap.servers": node_addresses,
        "group.id": f"message-group-{time.time()}",
        "auto.offset.reset": "earliest",
    }
)
consumer.subscribe([topic.decode()])


def consume_messages():
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        value = msg.value()
        decoded = json.loads(value.decode("utf-8"))
        text = decoded.get("text")
        print(f"Service instance {SERVICE_IDX} received a message: {text}")
        messages.append(text)


Thread(target=consume_messages, daemon=True).start()

@app.get("/")
def send_message():
    print("Messages:", messages)
    return messages

@app.on_event("shutdown")
def shutdown_event():
    deregister_service(f"messages-service-{SERVICE_IDX}")
