from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    session_name: str
    chat: str
    output_path: str
    poll_interval_s: float
    max_messages: int
    rate_limit_s: float


def load_settings() -> Settings:
    api_id_raw = os.environ.get("TG_API_ID", "")
    api_hash = os.environ.get("TG_API_HASH", "")
    session_name = os.environ.get("TG_SESSION", "tg_gifts")
    chat = os.environ.get("TG_CHAT", "")
    output_path = os.environ.get("TG_OUTPUT", "gifts.jsonl")
    poll_interval_s = float(os.environ.get("TG_POLL_INTERVAL", "20"))
    max_messages = int(os.environ.get("TG_MAX_MESSAGES", "100"))
    rate_limit_s = float(os.environ.get("TG_RATE_LIMIT", "1.0"))

    if not api_id_raw:
        raise ValueError("TG_API_ID is required")
    if not api_hash:
        raise ValueError("TG_API_HASH is required")
    if not chat:
        raise ValueError("TG_CHAT is required")

    return Settings(
        api_id=int(api_id_raw),
        api_hash=api_hash,
        session_name=session_name,
        chat=chat,
        output_path=output_path,
        poll_interval_s=poll_interval_s,
        max_messages=max_messages,
        rate_limit_s=rate_limit_s,
    )
