from fastapi import FastAPI, Request
from server.response import Response
from server.model.embedding import Embedding
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pinecone.Index(os.getenv("PINECONE_INDEX"))


@app.get("/")
def read_root():
    return Response(message="Hello World", status=200)


@app.post("/api/get-sentiment")
async def get_embedding(request: Request):
    """
    Get the sentiment of the text

    Args:
    ----
        request (Request): request object

    Returns:
    ----
        dict: dictionary containing the response
    """

    data = await request.json()
    embedding = Embedding().encode(data["text"]).tolist()
    response = index.query(vector=embedding, top_k=3, namespace="sentiment", include_metadata=True)

    if response:
        return Response(message="success", status=200, data=response.to_dict())
    return Response(message="failed", status=500, data=response)
