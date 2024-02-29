from fastapi import FastAPI
from server.response import Response

app = FastAPI()


@app.get("/")
def read_root():
    return Response(message="Hello World", status=200)
