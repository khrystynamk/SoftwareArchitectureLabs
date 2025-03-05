from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def messages():
    return "not implemented yet"
