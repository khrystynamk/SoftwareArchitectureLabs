from fastapi import FastAPI

app = FastAPI()


@app.get("/messages")
async def messages():
    return "not implemented yet"
