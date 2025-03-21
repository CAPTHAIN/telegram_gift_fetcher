import asyncio
from typing import Optional, Dict
from telethon import TelegramClient
from telethon.tl.types import InputUser
from .tl_objects import GetUserStarGifts
from .scraper import get_gift_collection_floor_price


async def _resolve_username(client: TelegramClient, username: str) -> Optional[tuple]:
    """
    Resolve a Telegram username to user ID and access hash.

    Args:
        client (TelegramClient): The Telegram client instance.
        username (str): The username to resolve.

    Returns:
        tuple or None: (user_id, access_hash) if resolved, None otherwise.
    """
    from telethon.tl.functions import contacts
    response = await client(contacts.ResolveUsernameRequest(username=username))
    if not response.users:
        print(f"No user found for username '{username}'")
        return None
    user = response.users[0]
    return user.id, user.access_hash


async def get_user_gifts(client: TelegramClient, username: str, offset: str = "", limit: int = 50) -> Dict:
    """
    Fetch gifts for a Telegram user using an existing client instance.

    Args:
        client (TelegramClient): An initialized and started TelegramClient instance.
        username (str): The target user's Telegram username.
        offset (str, optional): Offset for pagination. Defaults to "".
        limit (int, optional): Number of gifts to fetch. Defaults to 50.

    Returns:
        dict: Contains 'gifts' (list), 'count_gifts' (int), and 'total_cost' (dict with 'ton' and 'stars').
    """
    user_data = await _resolve_username(client, username)
    if user_data is None:
        return {'gifts': [], 'count_gifts': 0, 'total_cost': {'ton': 0.0, 'stars': 0}}
    user_id, access_hash = user_data
    user = InputUser(user_id=user_id, access_hash=access_hash)
    request = GetUserStarGifts(user_id=user, offset=offset, limit=limit)
    response = await client(request)

    filtered_gifts = []
    total_ton_cost = 0.0
    total_stars_cost = 0

    # Collect unique collection slugs for StarGiftUnique
    collection_slugs = set()
    for user_gift in response.gifts:
        gift = user_gift.gift
        if gift.CONSTRUCTOR_ID == 0x5c62d151:  # StarGiftUnique
            collection_slugs.add(gift.title.lower().replace(' ', ''))

    # Fetch floor prices concurrently
    floor_price_tasks = {
        slug: asyncio.to_thread(get_gift_collection_floor_price, slug)
        for slug in collection_slugs
    }
    floor_prices = await asyncio.gather(*floor_price_tasks.values())
    floor_price_dict = dict(zip(floor_price_tasks.keys(), floor_prices))

    # Process each gift
    for user_gift in response.gifts:
        gift = user_gift.gift
        received_date = int(user_gift.date.timestamp())  # Convert datetime to Unix timestamp
        if gift.CONSTRUCTOR_ID == 0x2cc73c8:  # StarGift
            sender_id = user_gift.from_id.user_id if user_gift.from_id is not None else None
            gift_data = {
                "type": "StarGift",
                "id": gift.id,
                "stars": gift.stars,
                "convert_stars": gift.convert_stars,
                "sender_id": sender_id,
                "received_date": received_date
            }
            total_stars_cost += gift.convert_stars
        elif gift.CONSTRUCTOR_ID == 0x5c62d151:  # StarGiftUnique
            collection_slug = gift.title.lower().replace(' ', '')
            floor_price = floor_price_dict.get(collection_slug)
            gift_data = {
                "type": "StarGiftUnique",
                "id": gift.id,
                "title": gift.title,
                "slug": gift.slug,
                "num": gift.num,
                "collection_floor_price_in_ton": floor_price,
                "availability_issued": gift.availability_issued,
                "availability_total": gift.availability_total,
                "received_date": received_date
            }
            if floor_price is not None:
                total_ton_cost += floor_price
        else:
            continue
        filtered_gifts.append(gift_data)

    return {
        "gifts": filtered_gifts,
        "count_gifts": len(filtered_gifts),
        "total_cost": {"ton": total_ton_cost, "stars": total_stars_cost}
    }
