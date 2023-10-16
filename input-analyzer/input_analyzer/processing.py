import itertools

import polars as pl

from input_analyzer.utils import (
    PatternCheat,
    MatchRequest,
    ResponseCheat,
    SuspiciousAction,
)

CHEAT_PATTERNS = [
    PatternCheat(consecutive_frames=15, change_frame=2, suspicion="medium"),
    PatternCheat(consecutive_frames=20, change_frame=2, suspicion="high"),
    PatternCheat(consecutive_frames=25, change_frame=3, suspicion="medium"),
    PatternCheat(consecutive_frames=30, change_frame=3, suspicion="high"),
    PatternCheat(consecutive_frames=60, change_frame=4, suspicion="medium"),
    PatternCheat(consecutive_frames=80, change_frame=4, suspicion="high"),
]


def create_dataframe(match: MatchRequest) -> list[pl.DataFrame]:
    df = pl.DataFrame(itertools.chain(*match.playerActions))
    df_player_actions = (
        df.with_columns(
            up=(pl.col("action") & 1) != 0,
            down=(pl.col("action") & 2) != 0,
            left=(pl.col("action") & 4) != 0,
            right=(pl.col("action") & 8) != 0,
            kick=(pl.col("action") & 16) != 0,
        )
    )

    return df_player_actions


def get_kick_streaks(df: pl.DataFrame) -> pl.DataFrame:
    df_actions_player_list = df.partition_by("player")
    df_streaks_player = pl.DataFrame()

    for df_action in df_actions_player_list:
        df_streak = df_action.with_columns(
            diff_previous=(
                (pl.col("kick") != pl.col("kick").shift(1)).fill_null(True).cumsum()
            )
        ).to_pandas()

        df_streak["kick_streak"] = df_streak.groupby("diff_previous").cumcount() + 1
        df_streaks_player = df_streaks_player.vstack(pl.from_pandas(df_streak))

    return df_streaks_player


def get_suspicious_actions_match(
    df: pl.DataFrame, pattern: PatternCheat
) -> list[SuspiciousAction]:
    df_streaks_player_list = df.partition_by("player")
    df_macro_players = pl.DataFrame()

    for df_kick in df_streaks_player_list:
        df_streak = (
            df_kick.with_columns(
                fast_kick=pl.col("kick_streak") <= pattern.change_frame
            )
            .with_columns(
                diff_previous=(
                    (pl.col("fast_kick") != pl.col("fast_kick").shift(1))
                    .fill_null(True)
                    .cumsum()
                )
            )
            .to_pandas()
        )

        df_streak["fast_kick_streak"] = (
            df_streak.groupby("diff_previous").cumcount() + 1
        )
        df_macro_players = df_macro_players.vstack(pl.from_pandas(df_streak))

    suspicious_df = df_macro_players.filter(
        (pl.col("fast_kick_streak") == pattern.consecutive_frames)
        & (pl.col("fast_kick"))
    )

    if suspicious_df.height == 0:
        return []

    suspicious_list = [
        SuspiciousAction.model_validate(
            {
                "recMs": row["recMs"],
                "frame": row["frame"],
                "player": row["player"],
                "pattern": pattern,
            }
        )
        for row in suspicious_df.to_dicts()
    ]

    return suspicious_list


def get_response(match: MatchRequest) -> ResponseCheat:
    match_df = create_dataframe(match)
    suspicious_actions: list[SuspiciousAction] = []

    df_streaks = get_kick_streaks(match_df)
    for pattern in CHEAT_PATTERNS:
        suspicious_actions.extend(get_suspicious_actions_match(df_streaks, pattern))

    return ResponseCheat(suspicions=suspicious_actions)
