import grpc
import httpx
import facade_logging_service_pb2_grpc
import facade_logging_service_pb2
from fastapi import FastAPI, Request

app = FastAPI()


def get_grpc_channel():
    return grpc.insecure_channel("localhost:8081")


def get_logging_service_stub(channel):
    return facade_logging_service_pb2_grpc.LoggingStub(channel)


@app.post("/facade_service")
async def facade(request: Request) -> dict:
    body = await request.json()
    text = body.get("text")

    channel = get_grpc_channel()
    stub = get_logging_service_stub(channel)

    request_message = facade_logging_service_pb2.PutMessageRequest(text=text)

    try:
        response = stub.PutMessage(request_message)

        if response.status == 200:
            return {
                "status": response.status,
                "uuid": response.uuid,
                "text": response.text,
            }
        return {"status": response.status, "content": response.text}

    except grpc.RpcError as err:
        return {"error_code": err.code(), "error_details": err.details()}


@app.get("/facade_service")
async def facade() -> dict:
    messages_url = "http://localhost:8082/messages"
    channel = get_grpc_channel()
    stub = get_logging_service_stub(channel)

    request = facade_logging_service_pb2.GetMessagesRequest()

    try:
        async with httpx.AsyncClient() as client:
            messages_request = client.get(messages_url)
            messages_response = await messages_request

        response = stub.GetMessages(request)
        messages_list = list(response.messages)
        return {
            "logging_response": messages_list,
            "messages_response": messages_response.json(),
        }
    except grpc.RpcError as err:
        return {"error_code": err.code(), "error_details": err.details()}
