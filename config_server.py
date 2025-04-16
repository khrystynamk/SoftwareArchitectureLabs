import os
from fastapi import FastAPI, HTTPException

app = FastAPI()

SERVICES = {
    "logging-service": os.getenv("LOGGING_SERVICES", "").split(","),
    "messages-service": [os.getenv("MESSAGES_URL", "")],
}

@app.get("/{service_name}")
def get_service_instances(service_name: str):
    if service_name in SERVICES:
        instances = SERVICES[service_name]
        if not instances or instances == [""]:
            raise HTTPException(status_code=404, detail=f"No instances found for {service_name}")
        return {"instances": instances}
    raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
