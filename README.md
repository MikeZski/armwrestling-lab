# Armwrestling LAB

**Gotowa statyczna strona: 12 artykułów, pełne wersje PL i EN, 9 PDF-ów.**

## Otwórz bez instalacji

1. Rozpakuj **cały** ZIP. Nie otwieraj pojedynczego HTML-a wewnątrz podglądu archiwum.
2. Otwórz `START.html` i wybierz Polski lub English.
3. Przeglądaj artykuły, wyszukuj, zmieniaj kategorię i otwieraj PDF-y. Wszystko to działa z rozpakowanego folderu. Filmy i zewnętrzne publikacje wymagają internetu.

Nie trzeba instalować Node.js, pakietów npm, Pythona ani bazy danych, aby obejrzeć gotową stronę. Na Windows możesz też otworzyć `START_WINDOWS.bat`. Gdy przeglądarka firmowa blokuje pliki lokalne, skorzystaj z opcjonalnego podglądu HTTP poniżej.

## Co jest gotowe

- 24 pełne wersje artykułów, bibliografie z odnośnikami, 12 autorskich zestawień danych lub schematów i eksport danych wykresów do JSON.
- Pięć kategorii: siła i RFD; ścięgna i biomechanika; trening i regeneracja; żywienie i skład ciała; sport pod lupą.
- Wyszukiwanie w pełnej treści, filtrowanie, sortowanie, przełącznik języka zachowujący aktualny artykuł, jasny/ciemny wygląd, menu mobilne, spis treści, druk artykułu i kopiowanie linku.
- Sekcja pobierania: 9 rzeczywistych PDF-ów, rozmiary, sumy SHA-256, wersje i kategorie programów/modeli 3D gotowe na przyszłe pliki.
- Strony kategorii, opis redakcji i zasad opracowania, prywatność, strona 404, metadane SEO, opcjonalna mapa witryny, konfiguracja GitHub Pages.
- 44 pliki HTML. Treść pozostaje dostępna bez JavaScriptu; wyszukiwanie i przyciski dodatkowe są progresywnym rozszerzeniem.

To **nie jest makieta** ani aplikacja wymagająca zewnętrznego API. W katalogu `site/` znajduje się gotowa strona do publikacji.

## Przekaż agentowi kodującemu

Daj agentowi cały folder oraz plik **`AGENT_HANDOFF.md`**. Instrukcja zawiera gotowe polecenia, właściwą strukturę repozytorium i kontrolę po publikacji.

Na GitHubie publikowany jest wyłącznie katalog `site/`. Workflow sam buduje go z danych źródłowych i pobiera prawidłowy adres GitHub Pages. Nie trzeba wpisywać nazwy repozytorium w linkach strony.

## Edycja i ponowne budowanie

Potrzebny jest Python **3.10 lub nowszy**; workflow korzysta z 3.12. Nie ma zależności do instalowania.

```sh
python scripts/build.py
python scripts/check.py
python -m unittest discover -s tests -p "test_*.py" -v
```

Na macOS/Linux polecenie może nazywać się `python3`. Na Windows można użyć `py -3`.

Opcjonalny lokalny serwer:

```sh
python preview.py
```

Otwiera podgląd na `http://127.0.0.1:8080/`. Zakończ Ctrl+C. Zajęty port: `python preview.py --port 8081`.

Budowanie dla innego hostingu:

```sh
python scripts/build.py --site-url https://twoja-domena.pl
```

Następnie prześlij **zawartość `site/`** do katalogu publicznego serwera. Obsługiwany jest także adres z podkatalogiem, np. `https://twoja-domena.pl/lab`. Strona nie wymaga SPA fallbacku, PHP ani Pythona na serwerze.

## Gdzie są pliki

```text
START.html                   lokalny ekran startowy
AGENT_HANDOFF.md              instrukcja dla agenta
content/articles/{pl,en}.json teksty artykułów i podpisy wykresów
content/articles.json        adresy wideo, kategorie, referencje i miniatury
content/references.json      baza publikacji
content/figures.json         liczby i pochodzenie zestawień
content/downloads.json       katalog plików do pobrania
content/ui/{pl,en}.json      teksty interfejsu
content/site.json            języki, adres kanału i konfiguracja
static/                      grafiki, CSS, JS i PDF-y
scripts/                     generator i kontrola linków
site/                        GOTOWA STRONA; generowana ponownie
sources/                     wybrane transkrypcje i manifest pochodzenia
tests/                       testy; przeglądarkowe są opcjonalne
docs/                        przewodniki, raporty QA i podglądy
.github/workflows/           publikacja i walidacja na GitHubie
```

Nie edytuj ręcznie plików w `site/`: następne budowanie je zastąpi. Edytuj `content/` lub `static/`, potem uruchom generator.

## Ważne decyzje redakcyjne

**Języki:** opublikowane są PL i EN. Architektura przewiduje wszystkie 13 wskazanych języków, ale pozostałe 11 nie ma fikcyjnych wersji tekstu ani nieaktywnych pozycji w przełączniku. Instrukcja rozszerzenia: `docs/TRANSLATIONS.md`.

**YouTube:** 7 artykułów ma dopasowane bezpośrednie adresy filmów. Przy pozostałych 5 są jawnie opisane odnośniki do wyszukiwania kanału i tematu. Główny odnośnik YouTube również prowadzi do wyszukiwania, ponieważ w archiwum nie było potwierdzonego adresu kanału. Wystarczy uzupełnić `video_id` i `channel_url`; nie trzeba zmieniać szablonów.

**Pliki:** PDF-y zachowują oryginalny język angielski. Nie dodano przykładowych programów ani pustych modeli 3D. Zasady dodawania rzeczywistych plików: `docs/CONTENT_GUIDE.md`.

**Opracowanie:** teksty są syntezą materiałów, nie dosłownym zapisem wypowiedzi. Dane raportowane, przykłady obliczeniowe i schematy są rozdzielone. Materiał ma charakter edukacyjny, nie jest indywidualnym zaleceniem leczenia. Szczegóły i lista pominiętych materiałów: `docs/EDITORIAL_NOTES.md`.

## Dokumentacja

- `docs/DEPLOYMENT_PL.md` — GitHub Pages i przeprowadzka na inny serwer.
- `docs/CONTENT_GUIDE.md` — artykuły, pliki, referencje i wykresy.
- `docs/TRANSLATIONS.md` — dodawanie kompletnych wersji językowych.
- `docs/QA.md` — zakres testów i ograniczenia weryfikacji.
- `CREDITS_AND_RIGHTS.md` — pochodzenie materiałów.
