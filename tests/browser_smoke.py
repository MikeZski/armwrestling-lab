#!/usr/bin/env python3
"""Optional browser regression checks. Not required to build or use the site.

pip install playwright beautifulsoup4
python -m playwright install chromium
python tests/browser_smoke.py --mode http

Use --mode isolate where the execution environment prohibits browser navigation.
Isolation inlines the *actual* local assets and uses page.set_content; it tests
rendering and interactions, NOT real browser navigation/transport or hosting.
The structural checker and test_site.py independently verify local targets/HTTP.
"""
from __future__ import annotations
import argparse
import base64
import functools
import json
import mimetypes
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

def inline_html(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    scripts = []
    for tag in soup.find_all('script', src=True):
        scripts.append((path.parent / tag['src'].split('?')[0]).read_text(encoding='utf-8'))
        tag.decompose()
    for tag in soup.find_all('link'):
        if 'stylesheet' in tag.get('rel', []):
            style = soup.new_tag('style')
            style.string = (path.parent / tag['href'].split('?')[0]).read_text(encoding='utf-8')
            tag.replace_with(style)
        elif 'manifest' in tag.get('rel', []) or 'icon' in tag.get('rel', []):
            tag.decompose()
    for img in soup.find_all('img'):
        f = (path.parent / img['src']).resolve()
        mime = mimetypes.guess_type(str(f))[0] or 'application/octet-stream'
        img['src'] = 'data:' + mime + ';base64,' + base64.b64encode(f.read_bytes()).decode()
        # Load off-screen images for screenshot/image-integrity checks as well.
        img['loading'] = 'eager'
    for code in scripts:
        script = soup.new_tag('script')
        script.string = code
        soup.body.append(script)
    return str(soup)

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['http', 'isolate'], default='http')
    parser.add_argument('--browser', help='Optional Chromium executable path')
    parser.add_argument('--report', default='docs/browser-test-report.json')
    args = parser.parse_args()
    server = None
    if args.mode == 'http':
        server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(SITE)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
    report = {'mode': args.mode, 'passed': False, 'layout_cases': [], 'functional_checks': [], 'errors': []}
    report['scope'] = ('Actual HTTP navigation to a local preview server.' if args.mode == 'http' else
        'Actual generated HTML/CSS/JS/images inlined in Chromium. Browser HTTP/file navigation is not covered.')
    def record(name, condition):
        report['functional_checks'].append({'name': name, 'passed': bool(condition)})
        if not condition:
            report['errors'].append(name)
    with sync_playwright() as p:
        options = {'headless': True}
        if args.browser:
            options['executable_path'] = args.browser
        browser = p.chromium.launch(**options)
        report['browser'] = browser.version
        context = browser.new_context()
        nojs_context = browser.new_context(java_script_enabled=False)
        def visit(route, width=1440, js=True):
            page = (context if js else nojs_context).new_page()
            page.set_viewport_size({'width': width, 'height': 900})
            page.set_default_timeout(5000)
            page.on('pageerror', lambda e: report['errors'].append(f'{route}: {e}'))
            if args.mode == 'http':
                page.goto(f'http://127.0.0.1:{server.server_port}/{route}', wait_until='load')
            else:
                page.set_content(inline_html(SITE / route), wait_until='load')
            return page
        for path in sorted(SITE.rglob('*.html')):
            route = path.relative_to(SITE).as_posix()
            page = visit(route, 320)
            for width in (320, 390, 1440):
                page.set_viewport_size({'width': width, 'height': 900})
                result = page.evaluate('''() => ({
                  viewport: innerWidth,
                  width: document.documentElement.scrollWidth,
                  h1: document.querySelectorAll('h1').length,
                  brokenImages: [...document.images].filter(i=>i.complete && i.naturalWidth===0).length
                })''')
                okay = result['width'] <= width + 1 and result['h1'] == 1 and not result['brokenImages']
                report['layout_cases'].append({'page': route, 'width': width, 'passed': okay, **result})
                if not okay:
                    report['errors'].append(f'Layout/image check failed: {route} at {width}: {result}')
            page.close()
            print('Layout:', route, flush=True)
        for lang in ('pl', 'en'):
            page = visit(f'{lang}/index.html')
            visible = lambda: page.locator('[data-card]:visible').count()
            record(f'{lang}: twelve articles initially visible', visible() == 12)
            page.locator('[data-filter="strength"]').click()
            record(f'{lang}: category filter', visible() == 3)
            page.locator('[data-filter="all"]').click()
            page.locator('#article-search').fill('zzzzNoMatchingResearch000')
            record(f'{lang}: search empty state', visible() == 0 and page.locator('[data-empty]').is_visible())
            page.locator('[data-reset]').click()
            record(f'{lang}: reset search and filters', visible() == 12)
            page.locator('#article-search').fill('kolagen' if lang == 'pl' else 'collagen')
            record(f'{lang}: full-text search', 0 < visible() < 12)
            page.locator('.clear-search').click()
            record(f'{lang}: clear search', visible() == 12)
            page.locator('#article-sort').select_option('alpha')
            sorted_ok = page.evaluate('''() => {let a=[...document.querySelectorAll('[data-card]')].map(x=>x.dataset.title);return a.every((x,i)=>!i||a[i-1].localeCompare(x,document.documentElement.lang,{sensitivity:'base'})<=0)}''')
            record(f'{lang}: alphabetical sorting', sorted_ok)
            page.locator('.theme-button').click()
            record(f'{lang}: dark theme', page.locator('html').get_attribute('data-theme') == 'dark')
            page.locator('.theme-button').click()
            record(f'{lang}: light theme', page.locator('html').get_attribute('data-theme') == 'light')
            page.locator('.language-picker summary').click()
            record(f'{lang}: language picker', page.locator('.language-picker').get_attribute('open') is not None)
            page.keyboard.press('Escape')
            record(f'{lang}: keyboard closes language picker', page.locator('.language-picker').get_attribute('open') is None)
            page.close()
            page = visit(f'{lang}/downloads/index.html', 390)
            record(f'{lang}: nine real downloads', page.locator('[data-download-type]:visible').count() == 9)
            page.locator('[data-download-filter="software"]').click()
            record(f'{lang}: honest software empty state', page.locator('[data-download-type]:visible').count() == 0 and page.locator('[data-download-empty]').is_visible())
            page.locator('[data-download-filter="model3d"]').click()
            record(f'{lang}: honest models empty state', page.locator('[data-download-type]:visible').count() == 0 and page.locator('[data-download-empty]').is_visible())
            page.locator('[data-download-filter="report"]').click()
            record(f'{lang}: PDF filter', page.locator('[data-download-type]:visible').count() == 9)
            page.locator('.checksum summary').first.click()
            record(f'{lang}: checksum disclosure', page.locator('.checksum code').first.is_visible())
            page.locator('.mobile-menu summary').click()
            record(f'{lang}: mobile menu', page.locator('.mobile-menu nav').is_visible())
            page.keyboard.press('Escape')
            page.close()
            page = visit(f'{lang}/articles/train-rfd/index.html', 390)
            page.locator('.mobile-toc summary').click()
            record(f'{lang}: mobile article contents', page.locator('.mobile-toc nav').is_visible())
            record(f'{lang}: mobile copy and print controls', page.locator('.mobile-toc [data-copy]').is_visible() and page.locator('.mobile-toc [data-print]').is_visible())
            record(f'{lang}: same-article language links', all('/train-rfd/' in (SITE / lang / 'articles/train-rfd' / (a.get_attribute('href') or '')).resolve().as_posix() for a in page.locator('.language-list a').all()))
            page.emulate_media(media='print')
            record(f'{lang}: print keeps references, hides navigation', not page.locator('.site-header').is_visible() and page.locator('.references').is_visible())
            page.close()
            page = visit(f'{lang}/index.html', js=False)
            record(f'{lang}: all articles available without JavaScript', page.locator('[data-card]:visible').count() == 12)
            record(f'{lang}: nonfunctional search hidden without JavaScript', not page.locator('#article-search').is_visible())
            page.close()
        browser.close()
    if server:
        server.shutdown()
    report['passed'] = not report['errors']
    output = ROOT / args.report
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ['layout_cases', 'functional_checks']}, indent=2))
    print(f"Layout cases: {len(report['layout_cases'])}; functional checks: {len(report['functional_checks'])}")
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
