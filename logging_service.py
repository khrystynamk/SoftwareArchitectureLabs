import hazelcast
import os
from fastapi import FastAPI, Response
from message import Message
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

node_addresses = os.getenv(
    "HZ_NODES", "127.0.0.1:5701,127.0.0.1:5702,127.0.0.1:5703"
).split(",")
SERVICE_IDX = int(os.getenv("LOG_SERVICE_INSTANCE"))
hz_node = node_addresses[SERVICE_IDX]

hazelcast_client = hazelcast.HazelcastClient(
    cluster_name=os.getenv("HZ_CLUSTER_NAME"),
    cluster_members=[hz_node],
)

messages_map = hazelcast_client.get_map("messages").blocking()


@app.get("/")
def list_messages():
    return "\n".join(messages_map.values())


@app.post("/")
async def logging(message: Message):
    mes_uuid = str(message.mes_uuid)
    mes_text = message.text
    if messages_map.contains_key(mes_uuid):
        return Response(
            media_type="application/json",
            status_code=400,
            content='{"error": "Message already exists"}',
        )
    messages_map.put(mes_uuid, mes_text)
    print(
        f"The following message has been added to Logging Instance {SERVICE_IDX}: {mes_text}"
    )
    return {"status": 200}
