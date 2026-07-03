# -*- coding: utf-8 -*-
"""
Překlad japonského názvu položky do angličtiny přes volné MyMemory API
(bez nutnosti API klíče, vhodné pro krátké texty jako názvy inzerátů).

Pokud překlad selže (výpadek, limit, apod.), vrátí se None a bot použije
jako titulek zprávy původní japonský název - nic tím nespadne.
"""
import requests

MYMEMORY_URL = "https://api.mymemory.translated.net/get"
MAX_INPUT_LEN = 500  # MyMemory má limit na délku dotazu


def translate_ja_to_en(text):
    if not text:
        return None
    snippet = text[:MAX_INPUT_LEN]
    try:
        resp = requests.get(
            MYMEMORY_URL,
            params={"q": snippet, "langpair": "ja|en"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        translated = data.get("responseData", {}).get("translatedText")
        if translated and translated.strip().lower() != snippet.strip().lower():
            return translated.strip()
        return None
    except Exception:
        return None
