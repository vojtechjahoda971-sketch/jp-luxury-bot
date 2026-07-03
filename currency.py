# -*- coding: utf-8 -*-
"""
Získání aktuálního kurzu JPY -> EUR. Používá volné API frankfurter.app
(bez nutnosti API klíče). Pokud selže, použije se záložní kurz z config.py.
"""
import requests
from config import CURRENCY_FROM, CURRENCY_TO, FALLBACK_JPY_EUR_RATE


def get_jpy_eur_rate():
    try:
        resp = requests.get(
            "https://api.frankfurter.app/latest",
            params={"from": CURRENCY_FROM, "to": CURRENCY_TO},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        rate = data["rates"][CURRENCY_TO]
        return float(rate)
    except Exception:
        return FALLBACK_JPY_EUR_RATE


def jpy_to_eur(jpy_amount, rate):
    return round(jpy_amount * rate, 2)
