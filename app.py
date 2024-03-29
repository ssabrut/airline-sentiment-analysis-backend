from fastapi import FastAPI, Request
from server.response import Response
from pinecone import Pinecone
from dotenv import load_dotenv
import os
from datetime import datetime
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

load_dotenv()
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pinecone.Index(os.getenv("PINECONE_INDEX"))

DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

DB_URL = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}"
API_URL = "https://api-inference.huggingface.co/models/intfloat/e5-small-v2"

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

    comments = []
    data = await request.json()

    async for comment in comment_collection.find():
        comments.append(comment["text"])

    payload = {
        "inputs": {
            "source_sentence": data["text"],
            "sentences": comments,
        },
    }

    time.sleep(30)
    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
        json=payload,
    )

    matches = index.query(
        vector=response.json()[:384],
        top_k=5,
        namespace="sentiment",
        include_metadata=True,
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
