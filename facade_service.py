import httpx
import time
import os

from message import Message
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder

app = FastAPI()
load_dotenv()

LOGGING_URL = os.getenv("LOGGING_URL")
MESSAGES_URL = os.getenv("MESSAGES_URL")
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY"))


async def send_retry_request(request_func, *args, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient() as client:
                return await request_func(client, *args, **kwargs)
        except httpx.RequestError as err:
            if attempt < MAX_RETRIES:
                print(
                    f"Request attempt {attempt} failed: {str(err)}. Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                raise httpx.RequestError(message="All retry attempts failed.")


async def post_request(
    client: httpx.AsyncClient, url: str, json_data: dict
) -> httpx.Response:
    return await client.post(
        url, json=json_data, headers={"Content-Type": "application/json"}
    )


@app.post("/facade_service")
async def post_facade(request: Request) -> dict:
    body = await request.json()
    text = body.get("text")
    message = Message(text=text)
    serialized_message = jsonable_encoder(message)

    response = await send_retry_request(post_request, LOGGING_URL, serialized_message)
    return {
        "status": response.status_code
    }


async def get_requests(client: httpx.AsyncClient) -> dict:
    logging_request = client.get(LOGGING_URL)
    messages_request = client.get(MESSAGES_URL)
    logging_response = await logging_request
    messages_response = await messages_request

    return {
        "logging_response": logging_response.json(),
        "messages_response": messages_response.json(),
    }


@app.get("/facade_service")
async def get_facade() -> dict:
    return await send_retry_request(get_requests)
