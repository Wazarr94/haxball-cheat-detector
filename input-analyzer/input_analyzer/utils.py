from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

Suspicion = Literal["low", "medium", "high"]


@dataclass
class PatternCheat:
    consecutive_frames: int
    change_frame: int
    suspicion: Suspicion


class PlayerActionRequest(BaseModel):
    frame: int
    player: str
    action: int


class MatchRequest(BaseModel):
    gameTicks: int
    playerActions: list[list[PlayerActionRequest]]


class RecordingRequest(BaseModel):
    matches: list[MatchRequest]
    loading: bool
    error: bool


class SuspiciousAction(BaseModel):
    frame: int
    player: str
    pattern: PatternCheat


class ResponseCheat(BaseModel):
    suspicions: list[SuspiciousAction | None]
