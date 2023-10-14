import itertools

import polars as pl

from input_analyzer.utils import (
    PatternCheat,
    RecordingRequest,
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


def create_dataframes(request: RecordingRequest) -> list[pl.DataFrame]:
    list_df = []
    for match in request.matches:
        df = pl.DataFrame(itertools.chain(*match.playerActions))
        df_player_actions = (
            df.with_columns(
                up=(pl.col("action") & 1) != 0,
                down=(pl.col("action") & 2) != 0,
                left=(pl.col("action") & 4) != 0,
                right=(pl.col("action") & 8) != 0,
                kick=(pl.col("action") & 16) != 0,
            )
            .with_columns(
                game_time_m=(pl.col("frame") / 60 / 60)
                .cast(int)
                .cast(str)
                .str.zfill(2),
                game_time_s=(pl.col("frame") / 60 % 60)
                .cast(int)
                .cast(str)
                .str.zfill(2),
            )
            .with_columns(
                game_time=pl.format(
                    "{}:{}", pl.col("game_time_m"), pl.col("game_time_s")
                )
            )
            .drop("game_time_m", "game_time_s")
            .select("game_time", pl.exclude("game_time"))
        )

        list_df.append(df_player_actions)

    return list_df


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


def get_suspicious_actions(
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
                "frame": row["frame"],
                "player": row["player"],
                "pattern": pattern,
            }
        )
        for row in suspicious_df.to_dicts()
    ]

    return suspicious_list


def get_response(request: RecordingRequest) -> ResponseCheat:
    list_df = create_dataframes(request)
    list_suspicious: list[list[SuspiciousAction]] = []

    for df in list_df:
        match_suspicious: list[SuspiciousAction] = []
        df_streaks_player = get_kick_streaks(df)
        for pattern in CHEAT_PATTERNS:
            match_suspicious.extend(get_suspicious_actions(df_streaks_player, pattern))

        list_suspicious.append(match_suspicious)

    return ResponseCheat(matches=list_suspicious)
