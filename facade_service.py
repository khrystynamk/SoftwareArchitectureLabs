import httpx
import time

from message import Message
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder

app = FastAPI()


@app.post("/facade_service")
async def facade(request: Request) -> dict:
    body = await request.json()
    text = body.get("text")
    message = Message(text=text)
    serialized_message = jsonable_encoder(message)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8081/log",
                json=serialized_message,
                headers={"Content-Type": "application/json"},
            )

        if response.status_code == 200:
            return {
                "status": response.status_code,
                "uuid": message.mes_uuid,
                "text": message.text,
            }
        return {"status": response.status_code, "content": response.content}
    except httpx.RequestError as _:
        time.sleep(30)


@app.get("/facade_service")
async def facade() -> dict:
    logging_url = "http://localhost:8081/log"
    messages_url = "http://localhost:8082/messages"

    try:
        async with httpx.AsyncClient() as client:
            logging_request = client.get(logging_url)
            messages_request = client.get(messages_url)

            logging_response = await logging_request
            messages_response = await messages_request

        return {
            "logging_response": logging_response.json(),
            "messages_response": messages_response.json(),
        }
    except httpx.RequestError as _:
        time.sleep(30)
