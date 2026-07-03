# -*- coding: utf-8 -*-
"""
Hlavní skript bota.

Pro každou sledovanou značku a kategorii (kabelka/peněženka/doplněk) provede
vyhledávání na Mercari Japan (přes knihovnu `mercapi`), zjistí nové položky
(dle ID, které ještě nejsou v state.json), vyhodnotí, zda je cena
podprůměrná (sleva), a pošle upozornění na Discord webhook.

Spouští se opakovaně (viz .github/workflows/monitor.yml, cron každých 15 min),
NENÍ to nekonečná smyčka - jeden běh = jedna kontrola všech dotazů.
"""
import asyncio
import os
import statistics
import sys
import time

from mercapi import Mercapi

from config import (
    BRANDS,
    CATEGORY_WORDS,
    ITEMS_PER_QUERY,
    DISCOUNT_RATIO,
    DISCORD_WEBHOOK_URL_ENV,
)
from currency import get_jpy_eur_rate, jpy_to_eur
from discord_notify import build_embed, send_alerts
from state_store import (
    load_state,
    save_state,
    get_seen_ids,
    add_seen_ids,
    get_price_history,
    add_price,
)


def normalize_item(raw_item):
    """Bezpečně vytáhne potřebná pole z objektu vráceného knihovnou mercapi.

    Knihovna mercapi mapuje odpověď Mercari API na vlastní třídy; přesné
    názvy některých volitelných polí se mohou mezi verzemi mírně lišit,
    proto se přistupuje defenzivně přes getattr/try-except.
    """
    item_id = getattr(raw_item, "id", None) or getattr(raw_item, "id_", None)
    if not item_id:
        return None

    name = getattr(raw_item, "name", "") or "(bez názvu)"
    price = getattr(raw_item, "price", None)
    if price is None:
        return None

    thumbnail = None
    thumbnails = getattr(raw_item, "thumbnails", None)
    if thumbnails:
        try:
            thumbnail = thumbnails[0]
        except (IndexError, TypeError):
            thumbnail = None

    condition = None
    cond_obj = getattr(raw_item, "item_condition", None)
    if cond_obj is not None:
        condition = getattr(cond_obj, "name", None) or str(cond_obj)

    created = getattr(raw_item, "created", None)

    return {
        "id": item_id,
        "name": name,
        "price": price,
        "thumbnail": thumbnail,
        "condition": condition,
        "created": created,
        "url": f"https://jp.mercari.com/item/{item_id}",
    }


async def fetch_query(mercapi_client, query):
    try:
        results = await mercapi_client.search(query)
    except Exception as exc:
        print(f"[warn] Vyhledávání selhalo pro '{query}': {exc}")
        return []

    items = []
    for raw in getattr(results, "items", [])[:ITEMS_PER_QUERY]:
        norm = normalize_item(raw)
        if norm:
            items.append(norm)
    return items


async def run():
    webhook_url = os.environ.get(DISCORD_WEBHOOK_URL_ENV)
    if not webhook_url:
        print(f"[fatal] Chybí proměnná prostředí {DISCORD_WEBHOOK_URL_ENV}.")
        sys.exit(1)

    state = load_state()
    rate = get_jpy_eur_rate()
    print(f"[info] Kurz JPY->EUR: {rate}")

    mercapi_client = Mercapi()
    now = int(time.time())
    total_new = 0

    for brand_name, brand_cfg in BRANDS.items():
        brand_embeds = []
        for category_label, category_jp in CATEGORY_WORDS.items():
            query_text = f"{brand_cfg['jp']} {category_jp}"
            query_key = f"{brand_name}|{category_label}"

            items = await fetch_query(mercapi_client, query_text)
            seen_ids = get_seen_ids(state, query_key)
            new_items = [it for it in items if it["id"] not in seen_ids]

            # Historii cen aktualizujeme ze VŠECH vidčenách položek (i starých),
            # aby medián odrážel běžné tržní ceny, ne jen nové přírůstky.
            for it in items:
                add_price(state, query_key, it["price"])

            if new_items:
                history = get_price_history(state, query_key)
                median_price = statistics.median(history) if len(history) >= 5 else None

                for it in new_items:
                    is_discount = bool(
                        median_price and it["price"] < median_price * DISCOUNT_RATIO
                    )
                    age_seconds = (now - it["created"]) if it.get("created") else None
                    price_eur = jpy_to_eur(it["price"], rate)
                    embed = build_embed(
                        item=it,
                        brand_name=brand_name,
                        category_label=category_label,
                        price_eur=price_eur,
                        is_discount=is_discount,
                        age_seconds=age_seconds,
                        color=brand_cfg["color"],
                    )
                    brand_embeds.append(embed)

                add_seen_ids(state, query_key, [it["id"] for it in new_items])
                total_new += len(new_items)

            # Krátká pauza mezi dotazy, abychom nebyli agresivní vůči Mercari.
            await asyncio.sleep(1.5)

        if brand_embeds:
            send_alerts(webhook_url, brand_name, brand_embeds)

    save_state(state)
    print(f"[info] Hotovo. Nových položek celkem: {total_new}")


if __name__ == "__main__":
    asyncio.run(run())
