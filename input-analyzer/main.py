import json

import uvicorn
from brotli import decompress
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from input_analyzer.processing import get_response
from input_analyzer.utils import MatchRequest, ResponseCheat


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/recording")
async def detect_cheaters(match_request: Request) -> ResponseCheat:
    body = await match_request.body()
    match_bytes = decompress(body)
    match_json = json.loads(match_bytes.decode("utf-8"))
    match_analysis = MatchRequest.model_validate(match_json)
    resp = get_response(match_analysis)
    return resp


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
