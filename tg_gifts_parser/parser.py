from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from telethon import TelegramClient
from telethon.tl.custom.message import Message


GIFT_KEYWORDS = (
    "gift",
    "подар",
    "🎁",
    "premium",
    "subscription",
)


@dataclass(frozen=True)
class GiftEvent:
    message_id: int
    chat_id: int
    date: str
    sender_id: Optional[int]
    sender_username: Optional[str]
    text: str
    gift_type: str


class TelegramGiftParser:
    def __init__(self, client: TelegramClient, output_path: str, rate_limit_s: float) -> None:
        self._client = client
        self._output_path = Path(output_path)
        self._rate_limit_s = rate_limit_s
        self._last_seen_id: int | None = None

    async def run_once(self, chat: str, max_messages: int) -> list[GiftEvent]:
        messages = await self._fetch_messages(chat, max_messages)
        gifts: list[GiftEvent] = []
        for message in messages:
            gift = self._extract_gift(message)
            if gift:
                gifts.append(gift)
        if gifts:
            self._append_events(gifts)
        return gifts

    async def run_forever(self, chat: str, max_messages: int, poll_interval_s: float) -> None:
        while True:
            await self.run_once(chat, max_messages)
            await asyncio.sleep(poll_interval_s)

    async def _fetch_messages(self, chat: str, max_messages: int) -> Iterable[Message]:
        await asyncio.sleep(self._rate_limit_s)
        if self._last_seen_id is None:
            messages = await self._client.get_messages(chat, limit=max_messages)
        else:
            messages = await self._client.get_messages(chat, min_id=self._last_seen_id, limit=max_messages)
        if messages:
            self._last_seen_id = max(message.id for message in messages)
        return messages

    def _extract_gift(self, message: Message) -> GiftEvent | None:
        text = message.message or ""
        if not self._looks_like_gift(text):
            return None
        gift_type = self._classify_gift(text)
        sender = message.sender
        sender_id = getattr(sender, "id", None)
        sender_username = getattr(sender, "username", None)
        return GiftEvent(
            message_id=message.id,
            chat_id=message.peer_id.channel_id if hasattr(message.peer_id, "channel_id") else 0,
            date=self._format_date(message.date),
            sender_id=sender_id,
            sender_username=sender_username,
            text=text.strip(),
            gift_type=gift_type,
        )

    @staticmethod
    def _looks_like_gift(text: str) -> bool:
        lowered = text.lower()
        return any(keyword in lowered for keyword in GIFT_KEYWORDS)

    @staticmethod
    def _classify_gift(text: str) -> str:
        lowered = text.lower()
        if "premium" in lowered:
            return "telegram_premium"
        if "subscription" in lowered or "подпис" in lowered:
            return "subscription"
        if "🎁" in text:
            return "gift"
        return "unknown"

    @staticmethod
    def _format_date(date: datetime | None) -> str:
        if date is None:
            return datetime.now(timezone.utc).isoformat()
        if date.tzinfo is None:
            return date.replace(tzinfo=timezone.utc).isoformat()
        return date.isoformat()

    def _append_events(self, events: Iterable[GiftEvent]) -> None:
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        with self._output_path.open("a", encoding="utf-8") as handle:
            for event in events:
                handle.write(self._to_json(event))
                handle.write("\n")

    @staticmethod
    def _to_json(event: GiftEvent) -> str:
        escaped_text = event.text.replace("\\", "\\\\").replace('"', "\\\"")
        escaped_username = (
            "null"
            if event.sender_username is None
            else f'"{event.sender_username.replace("\\", "\\\\").replace("\"", "\\\"")}"'
        )
        return (
            "{"
            f"\"message_id\":{event.message_id},"
            f"\"chat_id\":{event.chat_id},"
            f"\"date\":\"{event.date}\","
            f"\"sender_id\":{event.sender_id if event.sender_id is not None else 'null'},"
            f"\"sender_username\":{escaped_username},"
            f"\"text\":\"{escaped_text}\","
            f"\"gift_type\":\"{event.gift_type}\""
            "}"
        )
