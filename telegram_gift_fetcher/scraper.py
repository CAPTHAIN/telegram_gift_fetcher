from typing import Optional
import time
import requests
from bs4 import BeautifulSoup

# In-memory cache for gift collections
collections_cache = {}

def get_gift_collection_floor_price(collection_slug: str) -> Optional[float]:
    """
    Fetch the floor price of a gift collection from Fragment.com, with caching.

    Args:
        collection_slug (str): The slug of the gift collection.

    Returns:
        float or None: The floor price in TON, or None if not found.
    """
    current_time = int(time.time())  # Current Unix timestamp in seconds
    cache_entry = collections_cache.get(collection_slug)

    # Check if the collection is cached and the data is less than 1 hour old
    if cache_entry and (current_time - cache_entry['last_update_at']) < 3600:
        return cache_entry['floor_price']

    # Fetch new price if not in cache or cache is stale
    try:
        url = f"https://fragment.com/gifts/{collection_slug}?sort=price_asc&filter=sale"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        container = soup.select_one('.tm-catalog-grid.js-autoscroll-body')
        if not container:
            print("Gift collection's container not found.")
            floor_price = None
        else:
            first_gift = container.find('a', class_='tm-grid-item')
            if not first_gift:
                print("No gift collection's items found in the container.")
                floor_price = None
            else:
                price_tag = first_gift.select_one('.tm-grid-item-values .tm-value')
                floor_price = float(price_tag.text.strip().replace(',', '')) if price_tag else None

        # Update the cache with the new price and timestamp
        collections_cache[collection_slug] = {
            'floor_price': floor_price,
            'last_update_at': current_time
        }
        return floor_price

    except Exception as e:
        print(f'Error getting gift collection floor price: {e}')
        # Cache the failure as None to avoid repeated failed requests
        collections_cache[collection_slug] = {
            'floor_price': None,
            'last_update_at': current_time
        }
        return None
