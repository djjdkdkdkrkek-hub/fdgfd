# Telegram Gifts Parser

Fast, stable Telegram gifts parser that polls a chat/channel and stores matching gift messages in JSONL.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables:

```bash
export TG_API_ID="123456"
export TG_API_HASH="your_api_hash"
export TG_CHAT="@channel_or_chat"
```

Optional:

- `TG_SESSION` (default: `tg_gifts`)
- `TG_OUTPUT` (default: `gifts.jsonl`)
- `TG_POLL_INTERVAL` (default: `20` seconds)
- `TG_MAX_MESSAGES` (default: `100`)
- `TG_RATE_LIMIT` (default: `1.0` seconds)

3. Run the parser:

```bash
python -m tg_gifts_parser.main
```

## Output

Each gift message is appended to `gifts.jsonl` as a JSON line with:

- `message_id`
- `chat_id`
- `date`
- `sender_id`
- `sender_username`
- `text`
- `gift_type`

## Notes

- The parser detects gifts by keywords and emojis (e.g. "gift", "подар", "🎁").
- It uses rate limiting and polling to stay stable under load.
