import httpx
import time
import os
import random

from message import Message
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder

app = FastAPI()
load_dotenv(dotenv_path="./.env")

CONFIG_SERVER_URL = os.getenv("CONFIG_SERVER_URL")
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY"))


async def fetch_service_instances(service_name: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CONFIG_SERVER_URL}/{service_name}")
        if response.status_code == 200:
            return response.json()["instances"]
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch {service_name} instances."
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
                return await request_func(client, service_url, *args, **kwargs)
        except httpx.RequestError:
            print(f"Attempt {attempt}: Failed to reach {service_url}, retrying...")
            time.sleep(RETRY_DELAY)
    raise HTTPException(status_code=503, detail="All retry attempts failed.")


async def post_request(client: httpx.AsyncClient, url: str, json_data: dict):
    return await client.post(
        f"{url}/", json=json_data, headers={"Content-Type": "application/json"}
    )


async def get_request(client: httpx.AsyncClient, url: str):
    response = await client.get(f"{url}/")
    return response.json()


@app.post("/facade_service")
async def post_facade(request: Request):
    body = await request.json()
    message = Message(text=body.get("text"))
    serialized_message = jsonable_encoder(message)

    service_instances = await fetch_service_instances("logging-service")
    response = await send_request_to_service(
        service_instances, post_request, serialized_message
    )

    return {"status": response.status_code}


@app.get("/facade_service")
async def get_facade():
    logging_service_instances = await fetch_service_instances("logging-service")
    response_logging = await send_request_to_service(
        logging_service_instances, get_request
    )

    messages_service_instances = await fetch_service_instances("messages-service")
    response_messages = await send_request_to_service(
        messages_service_instances, get_request
    )

    return {
        "logging_response": response_logging,
        "messages_response": response_messages,
    }
