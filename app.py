from fastapi import FastAPI
from server.response import Response
from server.model.embedding import Embedding

app = FastAPI()


@app.get("/")
def read_root():
    embedding = Embedding()
    print(embedding.encode("Hello World"))
    return Response(message="Hello World", status=200)
