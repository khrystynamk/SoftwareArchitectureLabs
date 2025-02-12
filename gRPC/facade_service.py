import grpc
import httpx
import time
import uuid
import os
import facade_logging_service_pb2_grpc
import facade_logging_service_pb2

from dotenv import load_dotenv
from fastapi import FastAPI, Request

app = FastAPI()
load_dotenv("../.env")

CHANNEL = os.getenv("CHANNEL")
LOGGING_URL = os.getenv("LOGGING_URL")
MESSAGES_URL = os.getenv("MESSAGES_URL")
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY"))


def get_logging_service_stub():
    channel = grpc.insecure_channel(CHANNEL)
    return facade_logging_service_pb2_grpc.LoggingStub(channel)


async def send_retry_request(request_func, *args, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return await request_func(*args, **kwargs)
        except grpc.RpcError as err:
            if attempt < MAX_RETRIES:
                print(
                    f"Request attempt {attempt} failed: {str(err)}. Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
            else:
                raise grpc.RpcError(
                    status_code=400, detail=f"Maximum number of retries reached."
                )


async def log_message(text: str) -> dict:
    stub = get_logging_service_stub()
    mes_uuid = str(uuid.uuid4())
    request_message = facade_logging_service_pb2.LogMessageRequest(
        uuid=mes_uuid, text=text
    )
    response = stub.LogMessage(request_message)

    return {"status": response.status}


@app.post("/facade_service")
async def post_facade(request: Request) -> dict:
    body = await request.json()
    text = body.get("text")
    return await send_retry_request(log_message, text)


async def fetch_messages() -> dict:
    async with httpx.AsyncClient() as client:
        messages_request = client.get(MESSAGES_URL)
        messages_response = await messages_request

    stub = get_logging_service_stub()
    request = facade_logging_service_pb2.GetMessagesRequest()
    response = stub.GetMessages(request)

    return {
        "logging_response": list(response.messages),
        "messages_response": messages_response.json(),
    }


@app.get("/facade_service")
async def get_facade() -> dict:
    return await send_retry_request(fetch_messages)
