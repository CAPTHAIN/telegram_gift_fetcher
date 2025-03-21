# 🎁 Telegram Gift Fetcher

**`telegram_gift_fetcher`** is a *lightweight Python library* to fetch Telegram user gifts using the Telegram API and Fragment.com.

---

## ✨ Features
- Fetch *standard* and *unique* gifts
- Get costs in **TON** and **stars**
- Reuse your Telegram(Telethon) client

## 🛠️ Setup
1. Install: `pip install telethon requests beautifulsoup4`
2. Get `api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org)

---

## 📝 Example

```python
from telethon import TelegramClient
from telegram_gift_fetcher import get_user_gifts
import asyncio

async def main():
    client = TelegramClient('session', 123456, 'your_api_hash')
    await client.start()
    gifts = await get_user_gifts(client, 'username')
    print(gifts)
    await client.disconnect()

asyncio.run(main())
```

---

```python
{
    "gifts": [
        # Standard gift (StarGift)
        {
            "type": "StarGift",
            "id": 123,
            "stars": 50,
            "convert_stars": 40,
            "sender_id": 456789,  # Or None if anonymous
            "received_date": 1698777600  # Unix timestamp
        },
        # Unique gift (StarGiftUnique)
        {
            "type": "StarGiftUnique",
            "id": 789,
            "title": "Golden Unicorn",
            "slug": "Golden-Unicorn-42",
            "num": 42,
            "collection_floor_price_in_ton": 2.5,  # Or None if unavailable
            "availability_issued": 100,
            "availability_total": 1000,
            "received_date": 1698864000  # Unix timestamp
        }
    ],
    "count_gifts": 2,  # Number of gifts in this response
    "total_cost": {
        "ton": 2.5,  # Total floor price for unique gifts
        "stars": 40  # Total convertible stars for standard gifts
    }
}
```

---

**`owner's telegram username: @vetalkaaa, for @replabs`**