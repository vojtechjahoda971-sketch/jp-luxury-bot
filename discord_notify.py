# -*- coding: utf-8 -*-
"""
Odesílání upozornění na Discord webhook. Zprávy jsou seskupené podle značky
a modelu (query), každá položka jako jeden embed. Discord dovoluje max.
10 embedů na jednu zprávu webhooku, proto se dělí na dávky.
"""
import time
import requests

MAX_EMBEDS_PER_MESSAGE = 10


def _format_age(seconds_listed):
    if seconds_listed is None:
        return "neznámo"
    minutes = int(seconds_listed // 60)
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} h"
    days = hours // 24
    return f"{days} d"


def build_embed(item, brand_name, category_label, price_eur, is_discount, age_seconds, color):
    condition = item.get("condition") or "neuvedeno"
    title = item["name"][:250]
    fields = [
        {"name": "Cena", "value": f"¥{item['price']:,} (~€{price_eur:,.2f})", "inline": True},
        {"name": "Stav", "value": condition, "inline": True},
        {"name": "V nabídce", "value": _format_age(age_seconds), "inline": True},
        {"name": "Kategorie", "value": category_label, "inline": True},
    ]
    embed = {
        "title": f"{'🔥 SLEVA — ' if is_discount else ''}{title}",
        "url": item["url"],
        "color": color,
        "fields": fields,
        "footer": {"text": f"{brand_name} · Mercari Japan"},
    }
    if item.get("thumbnail"):
        embed["thumbnail"] = {"url": item["thumbnail"]}
    return embed


def send_alerts(webhook_url, brand_name, embeds):
    """Pošle embedy na webhook v dávkách po MAX_EMBEDS_PER_MESSAGE."""
    if not embeds:
        return
    for i in range(0, len(embeds), MAX_EMBEDS_PER_MESSAGE):
        batch = embeds[i:i + MAX_EMBEDS_PER_MESSAGE]
        payload = {
            "username": "JP Luxury Watcher",
            "content": f"**{brand_name}** — {len(batch)} nová nabídka/y" if i == 0 else None,
            "embeds": batch,
        }
        resp = requests.post(webhook_url, json=payload, timeout=15)
        if resp.status_code == 429:
            # Rate limit -> počkej dle Discordu a zkus znovu.
            retry_after = resp.json().get("retry_after", 1.5)
            time.sleep(float(retry_after) + 0.5)
            requests.post(webhook_url, json=payload, timeout=15)
        elif resp.status_code >= 300:
            print(f"[discord] Chyba při odesílání ({resp.status_code}): {resp.text[:300]}")
        time.sleep(0.5)  # šetrné tempo vůči Discord rate limitům
