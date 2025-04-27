import httpx
import time
import os
import json
import random
import socket

from message import Message
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from confluent_kafka import Producer
from prerequisites import (
    register_service,
    deregister_service,
    discover_service,
    get_key_value_item,
)

app = FastAPI()
load_dotenv()

MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY"))
SERVICE_IDX = os.getenv("FACADE_INSTANCE")
PORT = os.getenv("PORT")
HOST = os.getenv("HOST")
register_service("facade-service", SERVICE_IDX, PORT, HOST)
data = get_key_value_item("kafka/nodes")
node_addresses = data.decode()
producer = Producer(
    {
        "bootstrap.servers": node_addresses,
        "client.id": socket.gethostname(),
    }
)


async def send_request_to_service(service_urls, request_func, *args, **kwargs):
    random.shuffle(service_urls)

    for attempt in range(1, MAX_RETRIES + 1):
        if not service_urls:
            raise HTTPException(
                status_code=503, detail="All service instances are unavailable."
            )

        service_url = service_urls.pop(0)
        try:
            async with httpx.AsyncClient() as client:
                response = await request_func(client, service_url, *args, **kwargs)
                return response
        except httpx.HTTPError:
            print(f"Attempt {attempt}: Failed to reach {service_url}, retrying...")
            time.sleep(RETRY_DELAY)
    raise HTTPException(status_code=503, detail="All retry attempts failed.")


async def post_request(client: httpx.AsyncClient, url: str, json_data: dict):
    response = await client.post(
        f"{url}/", json=json_data, headers={"Content-Type": "application/json"}
    )
    return response


async def get_request(client: httpx.AsyncClient, url: str):
    response = await client.get(f"{url}/")
    return response.json()


@app.post("/facade_service")
async def post_facade(request: Request):
    body = await request.json()
    message = Message(text=body.get("text"))
    serialized_message = jsonable_encoder(message)

    service_instances = discover_service("logging-service")
    response = await send_request_to_service(
        service_instances, post_request, serialized_message
    )
    message_bytes = json.dumps(serialized_message).encode("utf-8")

    try:
        topic = get_key_value_item("kafka/topic")
        topic = topic.decode()
        producer.produce(topic, message_bytes)
        producer.flush()  # ensure the message is sent
        return {
            "kafka_status": "Message produced successfully",
            "topic": topic,
            "logging_status": response.status_code,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to produce message: {str(e)}"
        )


@app.get("/facade_service")
async def get_facade():
    logging_service_instances = discover_service("logging-service")
    print("Discovered logging-service instances:", logging_service_instances)
    response_logging = await send_request_to_service(
        logging_service_instances, get_request
    )

    messages_service_instances = discover_service("messages-service")
    print("Discovered logging-service instances:", messages_service_instances)
    response_messages = await send_request_to_service(
        messages_service_instances, get_request
    )

    return {
        "logging_response": response_logging,
        "messages_response": response_messages,
    }


@app.on_event("shutdown")
def shutdown_event():
    deregister_service(f"facade-service-{SERVICE_IDX}")
