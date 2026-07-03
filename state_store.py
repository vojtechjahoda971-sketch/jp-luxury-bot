# -*- coding: utf-8 -*-
"""
Jednoduché perzistentní úložiště stavu v JSON souboru.

Struktura:
{
  "seen": {
      "<query_key>": ["m123...", "m456...", ...]   # naposledy viděná ID
  },
  "prices": {
      "<query_key>": [12000, 15000, ...]           # historie cen pro detekci slev
  }
}
"""
import json
import os
from config import STATE_FILE, SEEN_IDS_PER_QUERY, PRICE_HISTORY_SIZE


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"seen": {}, "prices": {}}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("seen", {})
            data.setdefault("prices", {})
            return data
    except (json.JSONDecodeError, OSError):
        # Poškozený nebo prázdný soubor -> začneme s čistým stavem místo pádu bota.
        return {"seen": {}, "prices": {}}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_seen_ids(state, query_key):
    return set(state["seen"].get(query_key, []))


def add_seen_ids(state, query_key, new_ids):
    current = state["seen"].get(query_key, [])
    current.extend(new_ids)
    # Ořízneme na posledních N, ať soubor neroste donekonečna.
    state["seen"][query_key] = current[-SEEN_IDS_PER_QUERY:]


def get_price_history(state, query_key):
    return state["prices"].get(query_key, [])


def add_price(state, query_key, price):
    history = state["prices"].get(query_key, [])
    history.append(price)
    state["prices"][query_key] = history[-PRICE_HISTORY_SIZE:]
