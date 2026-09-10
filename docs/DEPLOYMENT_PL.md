# Publikacja i hosting

## GitHub Pages

Projekt zawiera gotowe workflow dla gałęzi `main`. Struktura repozytorium musi zaczynać się od `.github/`, `content/`, `scripts/`, `static/` itd., bez dodatkowego folderu otaczającego cały projekt.

Przykładowe polecenia po utworzeniu pustego repozytorium (zastąp WLASCIWE_KONTO i REPO; to przykłady, nie skonfigurowane konto):

```sh
git init
git add .
git commit -m "Launch Armwrestling LAB"
git branch -M main
git remote add origin https://github.com/WLASCIWE_KONTO/REPO.git
git push -u origin main
```

Ustaw **Settings → Pages → Source: GitHub Actions**, a następnie uruchom `Publish Armwrestling LAB`. Repozytorium i plan konta muszą obsługiwać GitHub Pages. Publiczne repozytoria są obsługiwane w GitHub Free; dostępność dla repozytoriów prywatnych zależy od planu. [Dokumentacja GitHub](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

Nie są wymagane własne sekrety do publikacji: workflow korzysta z tokenu zadania i jawnych uprawnień `contents: read`, `pages: write`, `id-token: write`. W organizacji administrator może wymagać zatwierdzania środowiska `github-pages`.

Adres przykładowy projektu: `https://WLASCIWE_KONTO.github.io/REPO/`. Generator nie zakłada, że strona jest w głównym katalogu domeny. Wszystkie lokalne linki są względne. Publiczny URL potrzebny do SEO pochodzi z konfiguracji Pages, a nie ze zgadywanej nazwy konta.

## Pliki na GitHubie

Obecne 9 PDF-ów można trzymać w repozytorium razem ze stroną. Dla większych instalatorów lub paczek modeli zastosuj GitHub Releases i bezpośredni adres zasobu w `content/downloads.json`.

GitHub blokuje w zwykłym repozytorium pliki większe niż 100 MiB; limit pojedynczego pliku dodawanego przez przeglądarkę wynosi 25 MiB. Limity plików wydania należy sprawdzić dla aktualnego planu, zamiast zakładać stały limit. [Duże pliki i wydania](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

GitHub Pages przewiduje maksymalnie 1 GB opublikowanej strony oraz miękki limit transferu 100 GB miesięcznie. To kolejny powód, by nie dodawać dużych, często pobieranych binariów do katalogu strony. [Limity Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits). Informacje sprawdzone podczas przygotowania wydania 2026-09-09; przed dużą rozbudową sprawdź je ponownie.

Nie publikuj samych wskaźników Git LFS jako plików do pobrania. W tym projekcie LFS nie jest potrzebny ani skonfigurowany.

## Własna domena na Pages

Skonfiguruj domenę w Settings → Pages i rekordy DNS zgodnie z dokumentacją dostawcy. Po zmianie domeny uruchom workflow ponownie, aby wygenerować prawidłowe kanoniczne adresy i sitemapę. Nie dodano fikcyjnego pliku `CNAME`, ponieważ domena nie została podana.

## Zwykły serwer

```sh
python scripts/build.py --site-url https://twoja-domena.pl/lab
python scripts/check.py
```

Prześlij zawartość `site/` do katalogu `/lab` serwera. Dla publikacji w głównym katalogu użyj URL-a bez `/lab`. HTML, CSS, JavaScript, WebP, PNG, JSON i PDF są zwykłymi plikami. Serwer nie wykonuje kodu Pythona. Włącz HTTPS i serwowanie UTF-8. Nie ustawiaj globalnego przekierowania wszystkich ścieżek na stronę główną.

Opcjonalnie ustaw cache dla grafik/PDF-ów, ale nie wymuszaj długiego cache dla HTML-a. CSS i JS mają hash zawartości w parametrze URL, aktualizowany przez generator.

## Po publikacji

Otwórz obie wersje językowe, wejdź w artykuł i zmień język na tej samej podstronie. Przetestuj wyszukiwanie, filtry, widok telefonu, PDF-y oraz nieistniejący adres. Sprawdź `robots.txt`, `sitemap.xml`, kanoniczny URL w kodzie strony i panel Actions. Raport z takiego sprawdzenia dotyczy faktycznego wdrożenia; raporty w paczce dotyczą przygotowanych plików.

## Najczęstsze problemy

**Brak CSS po publikacji:** sprawdź, czy w artefakcie są `assets/` oraz oba foldery językowe. Nie publikuj pojedynczego HTML-a.

**Workflow zgłasza brak Pages:** najpierw włącz Source: GitHub Actions w ustawieniach repozytorium, potem uruchom workflow ponownie.

**Zmiana tekstu nie pojawia się:** zmień `content/`, nie `site/`; uruchom generator i push. Poczekaj na zakończenie wdrożenia.

**Lokalnie nie ma sitemap.xml:** to celowe przy pustym `site_url`. Podaj rzeczywisty publiczny URL lub użyj workflow Pages.

**Film nie otwiera się bezpośrednio:** pięć niepotwierdzonych identyfikatorów ma celowe, opisane wyszukiwanie; lista znajduje się w notatkach redakcyjnych.
