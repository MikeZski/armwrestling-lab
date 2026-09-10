# Agent handoff / Instrukcja wdrożenia

## Cel

Opublikuj istniejący projekt Armwrestling LAB na koncie GitHub wskazanym przez właściciela. **Nie przepisuj strony do Reacta, Next.js ani innego frameworka.** Nie potrzebuje backendu, bazy danych ani płatnego serwisu. Zostaw strukturę i polsko-angielskie artykuły.

## Co publikować

Do repozytorium dodaj zawartość folderu `armwrestling-lab`, nie sam ZIP i nie tylko `site/`. Katalogi `.github`, `content`, `static`, `scripts`, `tests` oraz pliki dokumentacji muszą być w **głównym katalogu repozytorium**. `site/` to gotowy podgląd i wynik generatora; workflow przebuduje go podczas publikacji.

Na hosting GitHub Pages workflow wysyła wyłącznie `site/`. Nigdy nie ustawiaj artefaktu Pages na cały katalog repozytorium.

## Procedura

1. Odczytaj `README.md`, `content/site.json` oraz `docs/EDITORIAL_NOTES.md`.
2. Uruchom lokalnie poniższe polecenia. Wymagany Python 3.10+, brak pakietów do instalowania.

```sh
python scripts/build.py
python scripts/check.py
python -m unittest discover -s tests -p "test_*.py" -v
```

3. Utwórz repozytorium na koncie wskazanym przez użytkownika i gałąź `main`. Nie zgaduj nazwy konta ani widoczności repozytorium. Nie nadpisuj istniejącego repozytorium bez sprawdzenia jego zawartości. Zachowaj nazwę repozytorium, jeżeli użytkownik ją podał.
4. Dodaj pliki, zrób commit i push. Nie dodawaj oryginalnego wejściowego ZIP-a, katalogów cache ani sekretów.
5. W repozytorium ustaw **Settings → Pages → Build and deployment → Source: GitHub Actions**. Zapisany workflow to `.github/workflows/pages.yml`.
6. Gdy ustawienie Pages nastąpiło po pierwszym pushu, uruchom ponownie workflow przez **Actions → Publish Armwrestling LAB → Run workflow**. `configure-pages` wymaga włączonej usługi Pages.
7. Workflow pobierze rzeczywisty adres z `actions/configure-pages`, przekaże go do generatora, zbuduje sitemapę, kanoniczne URL-e i `hreflang`, wykona testy, a następnie opublikuje artefakt.
8. Odczytaj URL ze środowiska `github-pages`. Sprawdź w realnej przeglądarce stronę startową, obie wersje językowe, artykuł, przełącznik języka, kategorię, wyszukiwanie, mobilne menu, PDF, sitemapę i nieistniejący URL. Dopiero wtedy zgłoś właścicielowi adres publikacji.

## Nie blokuj wdrożenia z powodu nieznanych identyfikatorów wideo

Istniejące, wyraźnie opisane linki do wyszukiwania są celowe. Gdy właściciel poda adres kanału, wpisz go jako `channel_url` w `content/site.json` i ustaw `channel_url_is_search: false`. Dopasowane ID wideo wpisuj do `video_id` w `content/articles.json` (11 znaków, bez całego URL-a). Brakujące ID mają wartość `null`. Nie zgaduj ich ani nie zastępuj filmami innego twórcy.

Po zmianie danych uruchom generator i walidator, a następnie commit/push.

## Pliki do pobrania

Obecne małe PDF-y leżą w `static/downloads/reports/` i są kopiowane do `site/downloads/reports/`. Nowe programy i modele 3D dodaje się do `content/downloads.json`. Lokalne pliki używają pola `path`; większe archiwa w GitHub Releases pola `url`. Strona nie jest panelem uploadu: aktualizacja katalogu plików jest zmianą w repozytorium.

## Przeprowadzka na inny serwer

```sh
python scripts/build.py --site-url https://adres-serwera.pl
python scripts/check.py
```

Prześlij **zawartość** `site/` do katalogu publicznego. Zachowaj podkatalogi i nazwy plików. Nie jest potrzebne przepisywanie tras do jednego `index.html`. Włącz HTTPS, ustaw `index.html` jako dokument indeksowy i opcjonalnie skonfiguruj odpowiedź 404 na wygenerowany `404.html`.

## Kryteria akceptacji

Pełne artykuły są widoczne bez logowania. Każdy ma bibliografię i podpisaną ilustrację. Działają wszystkie linki lokalne i 9 pobrań. Nie ma pustych tłumaczeń, fałszywych plików, formularzy bez backendu ani zależności od CDN. Publiczny URL uwzględnia nazwę repozytorium. Do obsługi zwykłego ruchu nie są potrzebne tokeny API.

Ograniczenia wykonanych testów są opisane w `docs/QA.md`. Nie traktuj dołączonych raportów jako dowodu publikacji na koncie właściciela: to należy wykonać w tym wdrożeniu.
