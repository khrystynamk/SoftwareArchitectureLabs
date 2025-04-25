import hazelcast
import os

from fastapi import FastAPI, Response
from message import Message
from dotenv import load_dotenv
from prerequisites import register_service, deregister_service, get_key_value_item

app = FastAPI()
load_dotenv()

SERVICE_IDX = int(os.getenv("LOG_SERVICE_INSTANCE"))
PORT = os.getenv("PORT")
HOST = os.getenv("HOST")
register_service("logging-service", SERVICE_IDX, PORT, HOST)

cluster_name = get_key_value_item("hazelcast/cluster_name")
data = get_key_value_item("hazelcast/nodes")
node_addresses = data.decode()
hz_node = node_addresses.strip(",")[SERVICE_IDX]
hz_client = hazelcast.HazelcastClient(
    cluster_name=cluster_name.decode(),
    cluster_members=[hz_node],
)
messages_map = hz_client.get_map("messages").blocking()


@app.get("/")
def list_messages():
    return "\n".join(messages_map.values())


@app.post("/")
async def logging(message: Message):
    mes_uuid = str(message.mes_uuid)
    mes_text = message.text
    messages_map
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

@app.on_event("shutdown")
def shutdown_event():
    deregister_service(f"logging-service-{SERVICE_IDX}")