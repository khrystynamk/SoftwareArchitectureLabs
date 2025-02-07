from fastapi import FastAPI, Response
from message import Message

app = FastAPI()
all_messages = {}


@app.get("/log")
def list_messages():
    return all_messages.values()


@app.post("/log")
async def logging(message: Message) -> dict:
    mes_uuid = message.mes_uuid
    mes_text = message.text
    if mes_text in all_messages.values():
        return Response(
            media_type="application/json",
            status_code=403,
            content="message has been already added and exists",
        )
    all_messages[mes_uuid] = mes_text
    return Response(media_type="application/json", status_code=200)
