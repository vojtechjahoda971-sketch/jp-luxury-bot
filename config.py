# -*- coding: utf-8 -*-
"""
Konfigurace bota: sledované značky, kategorie (klíčová slova) a obecné nastavení.

Pro každou značku definujeme:
  - "jp": název značky japonsky (jak ho lidé zadávají do Mercari vyhledávání)
  - "color": barva Discord embedu (decimal, hex převedený na int)
  - "keywords": kombinace značka + kategorie -> každá kombinace je samostatný
    vyhledávací dotaz (kabelka / peněženka / doplněk), aby šlo přesněji filtrovat.
"""

CATEGORY_WORDS = {
    "kabelka": "バッグ",
    "peněženka": "財布",
    "doplněk": "アクセサリー",
}

BRANDS = {
    "Louis Vuitton": {"jp": "ルイヴィトン", "color": 0x8B5E3C},
    "Gucci": {"jp": "グッチ", "color": 0x006341},
    "Chanel": {"jp": "シャネル", "color": 0x111111},
}

# Kolik posledních (dle výpisu vyhledávání) položek se má z každého dotazu
# zkontrolovat na nové přírůstky. Mercari vrací primárně dle relevance, proto
# bereme rozumně velký vzorek, ne jen prvních pár kusů.
ITEMS_PER_QUERY = 60

# Kolik posledních cen si bot pamatuje na dotaz, aby dokázal poznat "slevu"
# (podprůměrnou cenu) -> ukládá se do state souboru.
PRICE_HISTORY_SIZE = 40

# Položka se označí jako "sleva", pokud je její cena nižší než tento poměr
# mediánu posledních zaznamenaných cen pro danou kombinaci značka+kategorie.
DISCOUNT_RATIO = 0.75

# Kolik ID naposledy viděných položek na dotaz se ukládá (proti opakovaným
# upozorněním). Mercari inzerát má stabilní ID, takže stačí množina.
SEEN_IDS_PER_QUERY = 500

# Minimální a maximální cena (v JPY), aby byla položka vůbec vyhodnocena a
# poslána jako upozornění.
# ~5 000 ¥ ≈ 30 €, ~17 000 ¥ ≈ 100 € (dle aktuálního kurzu se to trochu hýbe).
MIN_PRICE_JPY = 5000
MAX_PRICE_JPY = 17000

# Klíčová slova, která v japonském názvu inzerátu prozradí, že jde o repliku/
# padělek přiznaný samotným prodejcem -> takové položky se rovnou přeskočí.
# POZOR: toto NENÍ záruka pravosti, jen filtr na zjevně přiznané padělky.
# Nepoctivý prodejce padělku prostě tahle slova nepoužije - skutečné ověření
# (sériové číslo, datakód, řemeslné detaily) je potřeba udělat ručně před koupí.
FAKE_ITEM_KEYWORDS = [
    "レプリカ",      # replika
    "コピー品",      # kopie
    "スーパーコピー", # "super copy" (běžné označení pro padělky v JP bazarech)
    "非正規品",      # neoriginální/neautorizované zboží
    "偽物",          # padělek
    "フェイク",      # "fake"
]

CURRENCY_FROM = "JPY"
CURRENCY_TO = "EUR"
# Když se nepodaří stáhnout aktuální kurz, použije se tento záložní (přibližný).
FALLBACK_JPY_EUR_RATE = 0.0059

DISCORD_WEBHOOK_URL_ENV = "DISCORD_WEBHOOK_URL"

STATE_FILE = "state.json"
