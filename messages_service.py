from fastapi import FastAPI

app = FastAPI()


@app.get("/messages")
def messages():
    return "not implemented yet"
