import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from input_analyzer.processing import get_response
from input_analyzer.utils import RecordingRequest, ResponseCheat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/recording")
def detect_cheaters(recording: RecordingRequest) -> ResponseCheat:
    resp = get_response(recording)
    return resp


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
