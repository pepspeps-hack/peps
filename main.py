import yaml
import os
import time
import datetime
from pyVinted.vinted import Vinted
from google.oauth2 import service_account
from googleapiclient.discovery import build

import json

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def load_cache():
    if os.path.exists("cache.json"):
        with open("cache.json", "r") as f:
            return set(json.load(f))
    return set()

def save_cache(cache):
    with open("cache.json", "w") as f:
        json.dump(list(cache), f)

import yaml
from pyVinted import Vinted

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def search_vinted(config):
    v = Vinted(domain="nl", proxy=config.get("proxy"))
    v.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    time.sleep(5)
    items = v.search(
        f'https://www.vinted.nl/catalog?search_text={config["search_term"]}&price_from={config["min_price"]}&price_to={config["max_price"]}&currency=EUR',
        50,
        1
    )
    return items

import openai

def get_retail_price(item, config):
    if "OR_API_KEY" not in config or not config["OR_API_KEY"]:
        print("OR_API_KEY not found in config, using dummy value for retail price.")
        return float(item.price.amount) * 2

    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=config["OR_API_KEY"],
    )

    prompt = f"Wat is de adviesprijs (nieuwprijs) voor een {item.brand_title} {item.title} in goede staat?"

    try:
        completion = client.chat.completions.create(
            model="google/gemini-flash-1.5",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides retail prices for items."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        response_text = completion.choices[0].message.content
        # Extract number from the response
        price_str = ''.join(filter(str.isdigit, response_text))
        if price_str:
            return float(price_str)
        else:
            print(f"Could not parse retail price from OpenRouter response: {response_text}")
            return float(item.price.amount) * 2
    except Exception as e:
        print(f"Error calling OpenRouter: {e}")
        return float(item.price.amount) * 2

def calculate_profit(item, config):
    retail_price = get_retail_price(item, config)
    cost_total = float(item.price.amount) + float(item.service_fee.amount)
    profit_eur = retail_price - cost_total
    if cost_total > 0:
        profit_pct = (profit_eur / cost_total) * 100
    else:
        profit_pct = 0
    return profit_pct, retail_price

def save_to_google_sheets(config, items_with_profit):
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    )
    service = build("sheets", "v4", credentials=creds).spreadsheets()

    rows = []
    now_iso = datetime.datetime.now().isoformat()
    for item, profit_pct, retail_price in items_with_profit:
        rows.append([
            now_iso,
            item.id,
            item.url,
            item.title,
            float(item.price.amount),
            float(item.service_fee.amount),
            retail_price,
            round(profit_pct, 2)
        ])

    service.values().append(
        spreadsheetId=config["sheet_id"],
        range="Deals!A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()
    print(f"Saved {len(rows)} new deals to Google Sheets.")

if __name__ == "__main__":
    config = load_config()
    cache = load_cache()

    search_response = search_vinted(config)

    new_items = [item for item in search_response.items if item.id not in cache]
    print(f"Found {len(new_items)} new items.")

    items_with_profit = []
    for item in new_items:
        profit_pct, retail_price = calculate_profit(item, config)
        if profit_pct >= config["min_profit_pct"]:
            items_with_profit.append((item, profit_pct, retail_price))
            print(f"Found a good deal: {item.title} (profit: {profit_pct:.2f}%)")

    if items_with_profit:
        save_to_google_sheets(config, items_with_profit)
        for item, _, _ in items_with_profit:
            cache.add(item.id)

    save_cache(cache)

    print(f"\nFound {len(items_with_profit)} items with a profit margin of at least {config['min_profit_pct']}%.")
