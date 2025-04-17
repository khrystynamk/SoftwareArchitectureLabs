import time
import os
import json

from fastapi import FastAPI
from threading import Thread
from dotenv import load_dotenv
from confluent_kafka import Consumer

app = FastAPI()
load_dotenv()
KAFKA_SERVERS = os.getenv("KAFKA_SERVERS")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "messages")
SERVICE_IDX = int(os.getenv("MES_SERVICE_INSTANCE"))

messages = []

consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_SERVERS,
        "group.id": f"message-group-{time.time()}",
        "auto.offset.reset": "earliest",
    }
)

consumer.subscribe([KAFKA_TOPIC])


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
