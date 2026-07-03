# JP Luxury Watcher

Bot, který sleduje japonský Mercari (největší japonský bazar s použitým
zbožím) pro vybrané luxusní značky a nové nabídky posílá jako upozornění
na Discord — seskupené podle značky, s cenou v JPY i EUR, stavem zboží,
dobou v nabídce a přímým odkazem.

Sledované značky: Louis Vuitton, Gucci, Chanel, Coach, Céline, Hermès,
Cartier, Vivienne Westwood, Porter (lze upravit v `config.py`).

Kontrola probíhá každých 15 minut, zdarma, bez nutnosti vlastního serveru —
běží na GitHub Actions.

## Jak to funguje

- `main.py` projede pro každou značku 3 dotazy (kabelka / peněženka / doplněk)
  na Mercari přes knihovnu [mercapi](https://github.com/take-kun/mercapi).
- Nové položky (dle ID, které bot ještě neviděl) pošle na Discord webhook.
- Cena se označí jako 🔥 **sleva**, pokud je nižší než 75 % mediánu posledních
  zaznamenaných cen pro danou kombinaci značka+kategorie.
- Stav (co už bot viděl, historie cen) se ukládá do `state.json`, který si
  GitHub Actions po každém běhu sám commitne zpět do repozitáře.

## Nasazení (nejjednodušší varianta — GitHub Actions, zdarma)

**1. Vytvoř si Discord webhook**
   V Discordu: Nastavení kanálu → Integrace → Webhooky → Nový webhook →
   zkopíruj URL.

**2. Vytvoř si GitHub účet a nový repozitář** (pokud ho ještě nemáš)
   Může být klidně soukromý (private).

**3. Nahraj do repozitáře tyto soubory**
   Buď přes web (Add file → Upload files) — nahraj celý obsah této složky
   se zachováním struktury (hlavně `.github/workflows/monitor.yml` musí
   zůstat v této cestě), nebo přes git:
   ```
   git init
   git add .
   git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/TVOJE_JMENO/TVUJ_REPO.git
   git push -u origin main
   ```

**4. Přidej webhook URL jako "Secret"**
   V repozitáři: Settings → Secrets and variables → Actions → New repository
   secret → Name: `DISCORD_WEBHOOK_URL` → Value: (URL z kroku 1).

**5. Hotovo**
   Workflow se spustí automaticky každých 15 minut. Manuální test:
   záložka **Actions** → **JP Luxury Watcher** → **Run workflow**.

## Úpravy

- **Přidat/odebrat značku nebo kategorii** → uprav `BRANDS` / `CATEGORY_WORDS`
  v `config.py`.
- **Změnit citlivost slevy** → `DISCOUNT_RATIO` v `config.py` (0.75 = upozorní
  při ceně pod 75 % mediánu).
- **Změnit frekvenci kontrol** → uprav `cron` v
  `.github/workflows/monitor.yml` (GitHub cron min. interval je cca 5 minut,
  ale při vysoké zátěži GitHubu se skutečné spuštění může o pár minut
  zpozdit — to je omezení platformy, ne bota).

## Důležité poznámky

- `mercapi` je **neoficiální** knihovna reverzně inženýrovaná z Mercari
  webu/appky. Mercari čas od času mění zabezpečení API, což může knihovnu
  dočasně rozbít — pokud bot přestane fungovat, zkontroluj repozitář
  [take-kun/mercapi](https://github.com/take-kun/mercapi), jestli nevyšla
  nová verze (`pip install -U mercapi`).
- Automatizované dotazování cizí služby může být v rozporu s obchodními
  podmínkami Mercari. Nastav si přiměřenou frekvenci (15 min je bezpečný
  kompromis) a používej bota jen pro osobní účel (sledování nabídek), ne
  pro hromadné stahování dat.
- Pole jako "stav zboží" nebo "vytvořeno" nemusí být u každé položky
  k dispozici — bot to ošetřuje a v takovém případě zobrazí "neuvedeno" /
  "neznámo" místo pádu.

## Rozšíření na další tržiště (Yahoo Auctions Japan, Rakuma, 2nd Street…)

Aktuálně bot pokrývá jen Mercari Japan (nejrelevantnější a nejlikvidnější
trh pro tento typ zboží). Přidání dalšího tržiště znamená napsat obdobnou
funkci jako `fetch_query()` v `main.py`, která vrátí seznam položek ve
stejném formátu (`id`, `name`, `price`, `url`, `condition`, `created`,
`thumbnail`) — zbytek pipeline (dedup, sleva, Discord) je znovupoužitelný.
Napiš, pokud chceš pomoct s konkrétním tržištěm.
