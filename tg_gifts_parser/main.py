import asyncio

from telethon import TelegramClient

from tg_gifts_parser.config import load_settings
from tg_gifts_parser.parser import TelegramGiftParser


async def _run() -> None:
    settings = load_settings()
    async with TelegramClient(settings.session_name, settings.api_id, settings.api_hash) as client:
        parser = TelegramGiftParser(client, settings.output_path, settings.rate_limit_s)
        await parser.run_forever(settings.chat, settings.max_messages, settings.poll_interval_s)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
