from fastapi import FastAPI, Request
from server.response import Response
from server.model.embedding import Embedding
from pinecone import Pinecone
from dotenv import load_dotenv
import os
from datetime import datetime
import motor.motor_asyncio

load_dotenv()
app = FastAPI()
pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pinecone.Index(os.getenv("PINECONE_INDEX"))

DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DB_URL = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}"

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = client.airlinesentiment
comment_collection = database.get_collection("comments")


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
    matches = index.query(
        vector=embedding, top_k=11, namespace="sentiment", include_metadata=True
    ).to_dict()

    sentiments = {}
    for match in matches["matches"]:
        sentiment = match["metadata"]["airline_sentiment"]
        if sentiment in sentiments:
            sentiments[sentiment] += 1
        else:
            sentiments[sentiment] = 1

    current_timestamp = datetime.now().timestamp()
    sentiment = max(sentiments, key=sentiments.get)
    comment_collection.insert_one(
        {"text": data["text"], "sentiment": sentiment, "timestamp": current_timestamp}
    )

    return Response(message="success", status=200, data={"sentiment": sentiment})
