#!/usr/bin/env python3
"""Build the complete offline-capable site using Python's standard library only.

Usage: python scripts/build.py [--site-url https://user.github.io/repository]
Content is plain UTF-8 JSON; static/ is copied verbatim; site/ is disposable output.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import math
import os
import posixpath
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site'

def load(name: str):
    with (ROOT / 'content' / name).open(encoding='utf-8') as f:
        return json.load(f)

def esc(value) -> str:
    return html.escape(str(value), quote=True)

def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')

def rel(target: str, current: str) -> str:
    return posixpath.relpath(target, posixpath.dirname(current) or '.')

def external(url: str) -> str:
    if urlparse(url).scheme != 'https':
        raise ValueError(f'Only HTTPS external URLs are allowed: {url}')
    return esc(url)

ICONS = {
 'arrow':'<path d="M4 12h16m-6-6 6 6-6 6"/>',
 'external':'<path d="M14 3h7v7M21 3 10 14M10 3H3v18h18v-7"/>',
 'search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
 'moon':'<path d="M20 15A9 9 0 0 1 9 4a9 9 0 1 0 11 11Z"/>',
 'globe':'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a19 19 0 0 1 0 18 19 19 0 0 1 0-18Z"/>',
 'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
 'download':'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
 'play':'<path d="m9 5 11 7-11 7Z"/>',
 'file':'<path d="M5 2h9l5 5v15H5ZM14 2v6h5M8 13h8M8 17h8"/>',
 'close':'<path d="m6 6 12 12M18 6 6 18"/>',
 'check':'<path d="m5 12 4 4L19 6"/>',
 'clock':'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
}
def icon(name: str) -> str:
    return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+ICONS[name]+'</svg>'

def text(value: str, lang: str = "en") -> str:
    """Escape all author text, then turn numeric citations into safe local links."""
    def cite(match):
        spec=match.group(1)
        nums=[]
        for part in spec.replace('\u2013','-').split(','):
            part=part.strip()
            if '-' in part:
                a,b=part.split('-'); nums.extend(range(int(a), int(b)+1))
            else: nums.append(int(part))
        label = 'Przypis' if lang == 'pl' else 'Reference'
        links=', '.join(f'<a href="#ref-{n}" aria-label="{label} {n}">{n}</a>' for n in nums)
        return f'<sup class="citations">[{links}]</sup>'
    return re.sub(r'\[([0-9]+(?:\s*[,\-\u2013]\s*[0-9]+)*)\]',cite,esc(value))

def short_number(v, lang, digits=2):
    if not isinstance(v,(int,float)): return esc(v)
    s=f'{v:.{digits}f}'
    return s.replace('.',',') if lang=='pl' else s

class Builder:
    def __init__(self, site_url: str | None = None):
        self.cfg=load('site.json')
        self.base=(site_url if site_url is not None else self.cfg['site_url']).rstrip('/')
        if self.base and (urlparse(self.base).scheme!='https' or not urlparse(self.base).netloc or urlparse(self.base).query or urlparse(self.base).fragment):
            raise ValueError('--site-url must be a full HTTPS URL without query or fragment')
        self.langs=self.cfg['published_languages']
        self.ui={l:load(f'ui/{l}.json') for l in self.langs}
        self.articles=load('articles.json'); self.byid={a['id']:a for a in self.articles}
        self.translations={l:load(f'articles/{l}.json') for l in self.langs}
        self.categories=load('categories.json'); self.cats={c['id']:c for c in self.categories}
        self.refs=load('references.json'); self.figures=load('figures.json')
        self.downloads=[d for d in load('downloads.json') if d.get('published',True)]
        self.dl={d['id']:d for d in self.downloads}
        self.pages=[]
        for lang in self.langs:
            if set(self.translations[lang]) != set(self.byid):
                raise ValueError(f'Incomplete article translation: {lang}')
            if set(self.ui[lang]) != set(self.ui[self.langs[0]]):
                raise ValueError(f'Incomplete UI translation: {lang}')
            for c in self.categories:
                for key in ['title','description']:
                    if not c.get(key,{}).get(lang): raise ValueError(f'Missing category translation: {lang}/{c["id"]}/{key}')
            for d in self.downloads:
                for key in ['title','description']:
                    if not d.get(key,{}).get(lang): raise ValueError(f'Missing download translation: {lang}/{d["id"]}/{key}')
        for a in self.articles:
            if a['category'] not in self.cats: raise ValueError(f'Unknown category: {a["id"]}')
            if a.get('video_id') and not re.fullmatch(r'[a-zA-Z0-9_-]{11}',a['video_id']): raise ValueError('Invalid video ID')
            if not (ROOT/'static'/a['image']).is_file(): raise ValueError(f'Missing image: {a["id"]}')
            for r in a['references']:
                if r not in self.refs: raise ValueError(f'Missing reference: {r}')
            for d in a['pdfs']:
                if d not in self.dl: raise ValueError(f'Missing download: {d}')
        for d in self.downloads:
            if d.get('path'):
                p=ROOT/'static'/d['path']
                if not p.is_file(): raise ValueError(f'Missing download: {p}')
                d['bytes']=p.stat().st_size;d['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
            elif d.get('url'):
                external(d['url'])
            else: raise ValueError(f'No download path or URL: {d["id"]}')
    def tr(self,lang,key):return esc(self.ui[lang][key])
    def article_path(self,lang,id):return f'{lang}/articles/{id}/index.html'
    def video(self,a):
        return 'https://www.youtube.com/watch?v='+a['video_id'] if a.get('video_id') else 'https://www.youtube.com/results?search_query='+quote_plus(a['video_query'])
    def minutes(self,a):
        words=' '.join([a['summary'],a['takeaway'],a['limitations']]+[p for s in a['sections'] for p in s['paragraphs']]).split()
        return max(2,math.ceil(len(words)/190))
    def write(self,path,body):
        p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body,encoding='utf-8')
    def render(self,lang,route,title,description,body,kind='page',article=None):
        current=f'{lang}/{route}'; t=lambda k:self.tr(lang,k); href=lambda p:esc(rel(p,current))
        home=f'{lang}/index.html'
        nav=''.join(f'<a href="{href(p)}"'+(' aria-current="page"' if (key==kind or key=='articles' and kind in ['home','article','topic']) else '')+f'>{t(key)}</a>' for key,p in [('articles',home+'#library'),('downloads',f'{lang}/downloads/index.html'),('about',f'{lang}/about/index.html')])
        language_links=''.join(f'<a href="{href(f"{l}/{route}")}" lang="{l}" hreflang="{l}" data-language="{l}"'+(' aria-current="true"' if l==lang else '')+f'><span>{esc(next(x["name"] for x in self.cfg["languages"] if x["code"]==l))}</span><small>{l.upper()}</small></a>' for l in self.langs)
        alts=''.join(f'<link rel="alternate" hreflang="{l}" href="{esc(self.base+"/"+l+"/"+route) if self.base else href(l+"/"+route)}">' for l in self.langs)
        alts+=f'<link rel="alternate" hreflang="x-default" href="{esc(self.base+"/"+self.cfg["default_language"]+"/"+route) if self.base else href(self.cfg["default_language"]+"/"+route)}">'
        meta=''
        if self.base:
            image=article['image'] if article else 'assets/img/channel-banner.webp'
            meta=f'<link rel="canonical" href="{esc(self.base+"/"+current)}"><meta property="og:url" content="{esc(self.base+"/"+current)}"><meta property="og:image" content="{esc(self.base+"/"+image)}">'
        schema={'@context':'https://schema.org','@type':'Article' if article else 'WebPage','headline' if article else 'name':title,'description':description,'inLanguage':lang}
        if article:
            schema.update({'author':{'@type':'Organization','name':'Armwrestling LAB'},'publisher':{'@type':'Organization','name':'Armwrestling LAB'},'datePublished':article['date'],'dateModified':article['modified']})
        if self.base: schema['url']=self.base+'/'+current
        cssver=hashlib.sha256((ROOT/'static/assets/site.css').read_bytes()).hexdigest()[:10]
        jsver=hashlib.sha256((ROOT/'static/assets/site.js').read_bytes()).hexdigest()[:10]
        brand=f'<a class="brand" href="{href(home)}" aria-label="Armwrestling LAB"><img src="{href("assets/img/logo.webp")}" width="44" height="44" alt=""><span>ARMWRESTLING <b>LAB<span class="brand-dot">.</span></b></span></a>'
        page=f'''<!doctype html>
<html lang="{lang}" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Armwrestling LAB</title><meta name="description" content="{esc(description)}"><meta name="color-scheme" content="light dark"><meta name="theme-color" content="#131415"><meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" type="image/png" href="{href('assets/favicon.png')}"><link rel="manifest" href="{href('site.webmanifest')}">{alts}{meta}<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:site_name" content="Armwrestling LAB"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta name="twitter:card" content="summary_large_image">
<script>try{{var th=localStorage.getItem('awl-theme');if(th==='dark'||th==='light')document.documentElement.dataset.theme=th}}catch(e){{}}</script><link rel="stylesheet" href="{href('assets/site.css')}?v={cssver}"><script defer src="{href('assets/site.js')}?v={jsver}"></script><script type="application/ld+json">{json_text(schema)}</script></head>
<body data-kind="{kind}"><a class="skip-link" href="#main">{t('skip')}</a><header class="site-header" id="top"><div class="shell header-inner">{brand}<nav class="desktop-nav" aria-label="{t('menu')}">{nav}</nav><div class="header-actions"><details class="language-picker"><summary>{icon('globe')}<span>{lang.upper()}</span><span class="chevron" aria-hidden="true"></span><span class="sr-only">{t('language')}</span></summary><nav class="language-list" aria-label="{t('read_in')}">{language_links}</nav></details><button class="icon-button theme-button" type="button" aria-label="{t('theme')}" title="{t('theme')}" hidden>{icon('moon')}</button><details class="mobile-menu"><summary aria-label="{t('menu')}">{icon('menu')}</summary><nav aria-label="{t('menu')}">{nav}</nav></details></div></div></header><main id="main">{body}</main>
<footer class="site-footer"><div class="shell"><div class="footer-main"><div>{brand}<p class="footer-tagline">{t('footer_tagline').replace(chr(10),'<br>')}</p><p>{t('footer_description')}</p></div><nav aria-label="{t('menu')}"><span class="eyebrow">EXPLORE / LAB</span>{nav}<a href="{href(f'{lang}/privacy/index.html')}">{t('privacy')}</a><a href="{external(self.cfg['channel_url'])}" target="_blank" rel="noopener noreferrer">YouTube {icon('external')}</a></nav><div class="footer-languages"><span class="eyebrow">{t('language')}</span>{language_links}<p>{t('education')}</p></div></div><div class="footer-bottom"><span>&copy; {esc(self.cfg['build_date'][:4])} Armwrestling LAB</span><span>{t('footer_note')}</span><a href="#top">{t('top')} &uarr;</a></div></div></footer>
<div class="toast" role="status" aria-live="polite" hidden></div><script type="application/json" id="ui-messages">{json_text({k:self.ui[lang][k] for k in ['results','copied','copy_failed','not_shared']})}</script></body></html>'''
        self.write(current,page);self.pages.append({'path':current,'lang':lang,'route':route})
    def card(self,lang,a,current,index=0):
        d=self.translations[lang][a['id']];t=lambda k:self.tr(lang,k);h=lambda p:esc(rel(p,current))
        search=' '.join([d['title'],d['summary'],d['takeaway'],d['limitations']]+[s['heading']+' '+' '.join(s['paragraphs']) for s in d['sections']])
        return f'''<article class="article-card" data-card data-category="{a['category']}" data-title="{esc(d['title'])}" data-order="{index}" data-search="{esc(search)}"><a class="card-image" href="{h(self.article_path(lang,a['id']))}" tabindex="-1" aria-hidden="true"><img src="{h(a['image'])}" alt="" width="1200" height="675" loading="lazy" decoding="async"></a><div class="card-body"><div class="card-kicker"><a href="{h(f"{lang}/topics/{a['category']}/index.html")}">{esc(self.cats[a['category']]['title'][lang])}</a><span>{self.minutes(d)} {t('minutes')}</span></div><h3><a href="{h(self.article_path(lang,a['id']))}">{esc(d['title'])}</a></h3><p>{esc(d['summary'])}</p><div class="card-bottom"><span>{len(a['references'])} {t('sources')}</span><a href="{h(self.article_path(lang,a['id']))}" aria-label="{esc(d['title'])}">{t('read_article')} {icon('arrow')}</a></div></div></article>'''
    def library(self,lang,current,cat=None):
        t=lambda k:self.tr(lang,k);h=lambda p:esc(rel(p,current)); scope='all' if not cat else cat
        filters=f'<a class="filter{ " active" if not cat else ""}" href="{h(lang+"/index.html")}#library"'+(' data-filter="all"' if not cat else '')+f'>{t("all_topics")}</a>'
        for c in self.categories:
            filters+=f'<a class="filter{ " active" if cat==c["id"] else ""}" href="{h(lang+"/topics/"+c["id"]+"/index.html")}"'+(f' data-filter="{c["id"]}"' if not cat else '')+f'>{esc(c["title"][lang])}</a>'
        articles=[a for a in self.articles if not cat or a['category']==cat]
        cards=''.join(self.card(lang,a,current,i) for i,a in enumerate(articles))
        header='' if cat else f'<div class="section-heading"><div><span class="eyebrow">01 / {t("articles")}</span><h2>{t("library_title")}</h2></div><p>{t("library_description")}</p></div>'
        return f'''<section class="library shell" id="library" data-library data-scope="{scope}">{header}<nav class="filters" aria-label="{t('all_topics')}">{filters}</nav><div class="search-row" hidden data-search-controls><div class="search-field"><label class="sr-only" for="article-search">{t('search')}</label>{icon('search')}<input id="article-search" type="search" placeholder="{t('search_placeholder')}" autocomplete="off" aria-describedby="search-hint"><button type="button" class="clear-search" aria-label="{t('clear')}" hidden>{icon('close')}</button></div><label class="sort-label">{t('sort')}<select id="article-sort"><option value="editorial">{t('editorial')}</option><option value="alpha">{t('alphabetical')}</option></select></label><span class="result-count" role="status" aria-live="polite">{len(articles)} {t('results')}</span></div><p class="search-hint" id="search-hint" data-search-controls hidden>{t('search_hint')}</p><div class="article-grid">{cards}</div><div class="empty-state" hidden data-empty><span class="empty-number">0</span><h3>{t('no_results')}</h3><button class="button secondary" data-reset type="button">{t('reset')}</button></div></section>'''
    def home(self,lang):
        t=lambda k:self.tr(lang,k);current=f'{lang}/index.html';h=lambda p:esc(rel(p,current));a=self.byid[self.cfg['featured_article']];d=self.translations[lang][a['id']]
        feature=f'<div class="hero-feature"><div class="feature-label"><span>{t("featured")}</span><span>01 / LAB</span></div><a href="{h(self.article_path(lang,a["id"]))}" class="feature-image" tabindex="-1" aria-hidden="true"><img src="{h(a["image"])}" width="1200" height="675" alt="" fetchpriority="high"></a><div class="feature-copy"><span class="eyebrow">{esc(self.cats[a["category"]]["title"][lang])}</span><h2><a href="{h(self.article_path(lang,a["id"]))}">{esc(d["title"])}</a></h2><a class="text-link" href="{h(self.article_path(lang,a["id"]))}">{t("read_article")}{icon("arrow")}</a></div></div>'
        stats=''.join(f'<div><strong>{count:02}</strong><span>{t(label)}</span></div>' for count,label in [(len(self.articles),'research_articles'),(len(self.langs),'available_languages'),(len(self.downloads),'source_reports')])
        body=f'''<section class="hero"><div class="shell hero-grid"><div class="hero-copy"><p class="eyebrow"><span class="red-dash"></span>{t('hero_eyebrow')}</p><h1>{t('hero_title')}<br><span>{t('hero_accent')}</span></h1><p class="hero-description">{t('hero_description')}</p><div class="hero-buttons"><a class="button primary" href="#library">{t('browse')}{icon('arrow')}</a><a class="text-link" href="{external(self.cfg['channel_url'])}" target="_blank" rel="noopener noreferrer">{t('youtube') if self.cfg.get('channel_url_is_search') else "YouTube"} {icon('external')}</a></div><div class="hero-stats">{stats}</div></div>{feature}</div></section>{self.library(lang,current)}<section class="download-banner shell"><div><span class="eyebrow">02 / LAB FILES</span><h2>{t('downloads_title')}</h2><p>{t('downloads_description')}</p></div><a class="button primary" href="{h(lang+'/downloads/index.html')}">{t('downloads')}{icon('download')}</a></section>'''
        self.render(lang,'index.html',self.ui[lang]['articles'],self.ui[lang]['hero_description'],body,'home')
    def category(self,lang,c):
        current=f'{lang}/topics/{c["id"]}/index.html';title=c['title'][lang];desc=c['description'][lang]
        body=f'<header class="page-header shell"><a class="back-link" href="{esc(rel(lang+"/index.html",current))}">&larr; {self.tr(lang,"articles")}</a><p class="eyebrow">TOPIC / {c["code"]}</p><h1>{esc(title)}</h1><p class="lead">{esc(desc)}</p></header>'+self.library(lang,current,c['id'])
        self.render(lang,f'topics/{c["id"]}/index.html',title,desc,body,'topic')
    def figure(self,lang,a,current):
        f=self.translations[lang][a['id']]['figure'];data=self.figures[a['figure']];labels=f['labels'];t=lambda k:self.tr(lang,k);num=lambda v,d=2:short_number(v,lang,d)
        content='';tab='';kind=data['kind'];heads=[];rows=[]
        if kind=='grouped':
            series=data.get('series',labels[2:4]);heads=[self.tr(lang,'figure')]+series
            content='<div class="chart-legend">'+''.join(f'<span><i class="swatch s{i}"></i>{esc(s)}</span>' for i,s in enumerate(series))+'</div>'
            for r in data['rows']:
                content+=f'<div class="bar-group"><strong>{esc(labels[r[0]])}</strong>'
                for i,v in enumerate(r[1:]):
                    content+=f'<div class="bar-row"><span class="sr-only">{esc(series[i])}</span><div class="bar-track"><span class="bar s{i}" style="width:{100*v/data["max"]:.2f}%"></span></div><b>{num(v,data["precision"])}</b></div>'
                content+='</div>';rows.append([labels[r[0]]]+r[1:])
            content+=f'<div class="axis-note">0 &mdash; {data["max"]} &middot; {esc(f.get("unit",""))}</div>'
        elif kind=='interval':
            heads=[t('figure'),t('estimate'),t('interval')]
            for r in data['rows']:
                idx,v,lo,hi=r;scale=lambda x:100*(x-data['min'])/(data['max']-data['min'])
                content+=f'<div class="interval-row"><div><strong>{esc(labels[idx])}</strong><span>{num(v)} <small>({num(lo)}&ndash;{num(hi)})</small></span></div><div class="interval-track"><span class="ci-line" style="left:{scale(lo):.2f}%;width:{scale(hi)-scale(lo):.2f}%"></span><span class="ci-dot" style="left:{scale(v):.2f}%"></span></div></div>'
                rows.append([labels[idx],v,f'{num(lo)} - {num(hi)}'])
            content+=f'<div class="interval-axis"><span>{num(data["min"],1)}</span><span>{esc(f.get("unit",""))}</span><span>{num(data["max"],1)}</span></div>'
        elif kind=='table':
            heads=labels;rows=data['rows']
            content=self.table(heads,rows,lang,f['title'],data.get('precision',2))
            if data.get('formula'):content+=f'<p class="formula">{esc(data["formula"])}</p>'
        elif kind=='concept':
            content='<div class="concept-grid">'+''.join(f'<div class="concept-item"><span class="concept-index">{i//2+1:02}</span><strong>{esc(labels[i])}</strong><p>{esc(labels[i+1])}</p></div>' for i in range(0,len(labels),2))+'</div>'
        elif kind=='numbers':
            content='<div class="number-grid">'+''.join(f'<div><strong>{num(v)}<small> {esc(f.get("unit",""))}</small></strong><span>{esc(labels[i])}</span></div>' for i,v in enumerate(data['values']))+'</div>'
            heads=[t('figure'),esc(f.get('unit',''))];rows=[[labels[i],v] for i,v in enumerate(data['values'])]
        if rows and kind!='table':tab=f'<details class="data-table"><summary>{t("show_data")}</summary>{self.table(heads,rows,lang,f["title"],data.get("precision",2))}</details>'
        source=''
        if data.get('source'):
            path=self.dl[data['source']]['path'];source+=f'<a href="{esc(rel(path,current))}" target="_blank" rel="noopener">{t("figure_source")}: PDF {", ".join(map(str,data.get("pages",[])))}</a>'
        if data.get('source_url'):source+=f'<a href="{external(data["source_url"])}" target="_blank" rel="noopener noreferrer">{t("read_research")} {icon("external")}</a>'
        exported=f'data/{lang}/{a["id"]}.json';self.write(exported,json.dumps({'article':a['id'],'language':lang,'figure':f,'data':data,'references':[self.refs[x] for x in a['references']]},ensure_ascii=False,indent=2)+'\n')
        source+=f'<a href="{esc(rel(exported,current))}" download>{t("figure_data")}</a>'
        tag={'reported':'reported','calculation':'calculation','editorial':'concept'}[data['origin']]
        return f'<figure class="evidence-figure" id="figure"><div class="figure-kicker"><span>{t("figure")} 01</span><span>{t(tag)}</span></div><h3>{esc(f["title"])}</h3><div class="figure-visual">{content}</div><figcaption>{esc(f["caption"])}</figcaption>{tab}<div class="figure-links">{source}</div></figure>'
    def table(self,heads,rows,lang,caption,digits=2):
        return '<div class="table-scroll" tabindex="0" role="region" aria-label="'+esc(caption)+'"><table><caption class="sr-only">'+esc(caption)+'</caption><thead><tr>'+''.join(f'<th scope="col">{esc(h)}</th>' for h in heads)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<{"th" if i==0 else "td"}'+(' scope="row"' if i==0 else '')+'>'+short_number(v,lang,digits)+f'</{"th" if i==0 else "td"}>' for i,v in enumerate(r))+'</tr>' for r in rows)+'</tbody></table></div>'
    def article(self,lang,a):
        d=self.translations[lang][a['id']];current=self.article_path(lang,a['id']);h=lambda p:esc(rel(p,current));t=lambda k:self.tr(lang,k)
        headings=''.join(f'<a href="#section-{i+1}"><span>{i+1:02}</span>{esc(s["heading"])}</a>' for i,s in enumerate(d['sections']))
        aside=f'<aside class="article-sidebar"><nav aria-label="{t("contents")}" class="toc"><span class="eyebrow">{t("contents")}</span>{headings}<a href="#references"><span>R</span>{t("references")}</a></nav><div class="sidebar-tools"><button type="button" class="quiet-button" data-print hidden>{t("print")}</button><button type="button" class="quiet-button" data-copy hidden>{t("copy_link")}</button></div><p class="sidebar-note">{t("education")}</p></aside>'
        mobile_toc=f'<details class="mobile-toc"><summary>{t("contents")}</summary><nav aria-label="{t("contents")}">{headings}<a href="#references"><span>R</span>{t("references")}</a></nav><div class="sidebar-tools"><button type="button" class="quiet-button" data-print hidden>{t("print")}</button><button type="button" class="quiet-button" data-copy hidden>{t("copy_link")}</button></div></details>'
        sections=''
        for i,s in enumerate(d['sections']):
            sections+=f'<section class="prose-section" id="section-{i+1}"><h2>{esc(s["heading"])}</h2>'+''.join(f'<p>{text(p,lang)}</p>' for p in s['paragraphs'])+'</section>'
            if i==1: sections+=self.figure(lang,a,current)
        refs=''
        for i,rid in enumerate(a['references'],1):
            r=self.refs[rid];link=external(r['url']) if r.get('url') else h(r['file'])
            refs+=f'<li id="ref-{i}"><span>{esc(r["authors"])} ({r["year"]}).</span> <a href="{link}" target="_blank" rel="noopener noreferrer">{esc(r["title"])}</a>. <span class="journal">{esc(r["journal"])}</span></li>'
        materials=''
        for did in a['pdfs']:
            file=self.dl[did];materials+=f'<a class="material-link" href="{h(file["path"])}" target="_blank" rel="noopener">{icon("file")}<span>{esc(file["title"][lang])}<small>{t("pdf_english")} &middot; {file["pages"]} {t("pages")}</small></span>{icon("external")}</a>'
        if materials:materials=f'<section class="article-materials" id="materials"><h2>{t("materials")}</h2>{materials}</section>'
        video_label=t('watch') if a.get('video_id') else t('find_video');video_note=t('video_note') if a.get('video_id') else t('unconfirmed_video')
        video=f'<div class="article-video"><a href="{external(self.video(a))}" target="_blank" rel="noopener noreferrer" class="video-cover" aria-label="{video_label}"><img src="{h(a["image"])}" alt="" width="1200" height="675"><span class="play-badge">{icon("play")}</span></a><a class="video-link" href="{external(self.video(a))}" target="_blank" rel="noopener noreferrer">{video_label}{icon("external")}</a><p>{video_note}</p></div>'
        body=f'''<article><header class="article-header shell"><nav class="breadcrumb" aria-label="{t('home')}"><a href="{h(lang+'/index.html')}">{t('articles')}</a><span>/</span><a href="{h(lang+'/topics/'+a['category']+'/index.html')}">{esc(self.cats[a['category']]['title'][lang])}</a></nav><div class="article-heading-grid"><div><span class="eyebrow">{t('article_label')} / {self.minutes(d)} {t('minutes')}</span><h1>{esc(d['title'])}</h1><p class="article-summary">{esc(d['summary'])}</p><div class="byline"><img src="{h('assets/img/logo.webp')}" width="32" height="32" alt=""><div><strong>{t('author')}</strong><span>{t('updated')} &middot; <time datetime="{a['date']}">{a['date']}</time></span></div></div></div>{video}</div></header><div class="article-layout shell"><div class="article-content">{mobile_toc}<div class="takeaway"><span class="eyebrow">{t('takeaway')}</span><p>{text(d['takeaway'],lang)}</p></div>{sections}<section class="limitations" id="limitations"><h2>{t('limitations')}</h2><p>{text(d['limitations'],lang)}</p></section>{materials}<section class="references" id="references"><h2>{t('references')}</h2><p class="source-note">{t('source_transcript')}</p><ol>{refs}</ol></section></div>{aside}</div></article>'''
        related=sorted([x for x in self.articles if x['id']!=a['id']],key=lambda x:x['category']!=a['category'])[:3]
        body+=f'<section class="related shell"><div class="section-heading"><h2>{t("related")}</h2><a class="text-link" href="{h(lang+"/index.html")}#library">{t("all_topics")}{icon("arrow")}</a></div><div class="article-grid">'+''.join(self.card(lang,x,current,i) for i,x in enumerate(related))+'</div></section>'
        self.render(lang,f'articles/{a["id"]}/index.html',d['title'],d['summary'],body,'article',a)
    def download_page(self,lang):
        t=lambda k:self.tr(lang,k);current=f'{lang}/downloads/index.html';h=lambda p:esc(rel(p,current))
        cards=''
        for d in self.downloads:
            url=h(d['path']) if d.get('path') else external(d['url']);size=f'{d["bytes"]/1024/1024:.2f} MB' if d.get('bytes') else ''
            details=f'<details class="checksum"><summary>{t("checksum")}</summary><code>{d["sha256"]}</code></details>' if d.get('sha256') else ''
            related=[a for a in self.articles if d['id'] in a['pdfs']]
            articlelink=f'<a class="download-article" href="{h(self.article_path(lang,related[0]["id"]))}">{t("read_article")} {icon("arrow")}</a>' if related else ''
            label=t('read_pdf') if d['type']=='report' else t('download_file')
            cards+=f'<article class="download-card" data-download-type="{esc(d["type"])}"><div class="download-top">{icon("file")}<span>{esc(d["language"].upper())} &middot; {esc(size)}'+(f' &middot; {d["pages"]} {t("pages")}' if d.get('pages') else '')+f'</span></div><h2>{esc(d["title"][lang])}</h2><p>{esc(d["description"][lang])}</p><div class="download-meta">{t("version")}: {esc(d["version"])}</div><div class="download-actions"><a class="button secondary small" href="{url}" target="_blank" rel="noopener noreferrer">{label}{icon("external")}</a><a class="icon-button" href="{url}" download aria-label="{t("download_file")}: {esc(d["title"][lang])}">{icon("download")}</a></div>{articlelink}{details}</article>'
        filters=''.join(f'<button class="filter{ " active" if typ=="all" else ""}" data-download-filter="{typ}" type="button" aria-pressed="{str(typ=="all").lower()}">{t(label)} <span>{len(self.downloads) if typ=="all" else sum(d["type"]==typ for d in self.downloads)}</span></button>' for typ,label in [('all','all_files'),('report','reports'),('software','software'),('model3d','models')])
        body=f'<header class="page-header shell"><p class="eyebrow">LAB / DOWNLOADS</p><h1>{t("downloads_title")}</h1><p class="lead">{t("downloads_description")}</p></header><section class="downloads-section shell" data-downloads><p class="notice">{t("files_note")}</p><div class="filters" data-download-controls hidden aria-label="{t("downloads")}">{filters}</div><div class="download-grid">{cards}</div><div class="empty-state" data-download-empty hidden><span class="empty-number">00</span><h2>{t("empty_files")}</h2><p>{t("tools_note")}</p></div><div class="files-explainer"><p>{t("file_note")}</p><p>{t("tools_note")}</p></div></section>'
        self.render(lang,'downloads/index.html',self.ui[lang]['downloads'],self.ui[lang]['downloads_description'],body,'downloads')
    def about(self,lang):
        t=lambda k:self.tr(lang,k);current=f'{lang}/about/index.html'
        methods=''.join(f'<div class="method"><span>{i:02}</span><h3>{t(f"approach_{i}_title")}</h3><p>{t(f"approach_{i}")}</p></div>' for i in range(1,4))
        languages=''.join(f'<span class="language-status'+(' published' if x['code'] in self.langs else '')+f'"><b lang="{x["code"]}">{esc(x["name"])}</b><small>{t("complete" if x["code"] in self.langs else "planned")}</small></span>' for x in self.cfg['languages'])
        body=f'<header class="page-header shell about-header"><p class="eyebrow">ABOUT / ARMWRESTLING LAB</p><h1>{t("about_title").replace(chr(10),"<br>")}</h1><p class="lead">{t("about_intro")}</p></header><div class="shell"><img class="channel-banner" src="{esc(rel("assets/img/channel-banner.webp",current))}" width="1920" height="1080" alt="Armwrestling LAB" loading="lazy"><section class="about-section"><h2>{t("approach_title")}</h2><div class="methods-grid">{methods}</div></section><section class="about-section prose-narrow"><h2>{t("editorial_title")}</h2><p>{t("editorial_text")}</p><h2>{t("corrections_title")}</h2><p>{t("corrections_text")}</p></section><section class="about-section" id="languages"><h2>{t("language_title")}</h2><p>{t("language_intro")}</p><div class="language-status-grid">{languages}</div></section></div>'
        self.render(lang,'about/index.html',self.ui[lang]['about'],self.ui[lang]['about_intro'],body,'about')
    def privacy(self,lang):
        t=lambda k:self.tr(lang,k)
        body=f'<header class="page-header shell"><p class="eyebrow">LAB / {t("privacy")}</p><h1>{t("privacy_title")}</h1><p class="lead">{t("privacy_intro")}</p></header><div class="shell"><div class="prose-narrow privacy-content">'+''.join(f'<section><h2>{t("privacy_"+k+"_title")}</h2><p>{t("privacy_"+k)}</p></section>' for k in ['storage','external','offline'])+'</div></div>'
        self.render(lang,'privacy/index.html',self.ui[lang]['privacy'],self.ui[lang]['privacy_intro'],body,'privacy')
    def root_pages(self):
        links=''.join(f'<a class="button primary" href="{l}/index.html" data-language="{l}">{esc(next(x["name"] for x in self.cfg["languages"] if x["code"]==l))} {icon("arrow")}</a>' for l in self.langs)
        self.write('index.html',f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Armwrestling LAB research articles in Polish and English."><title>Armwrestling LAB</title><link rel="icon" href="assets/favicon.png"><link rel="stylesheet" href="assets/site.css"></head><body><main class="language-landing"><img src="assets/img/logo.webp" width="100" height="100" alt="Armwrestling LAB"><p class="eyebrow">RESEARCH / TRAINING / ARMWRESTLING</p><h1>ARMWRESTLING <span>LAB.</span></h1><p>Choose your language. / Wybierz j\u0119zyk.</p><div class="landing-actions">{links}</div><p class="landing-note">{len(self.articles)} articles &middot; {len(self.downloads)} source PDFs &middot; No account required</p></main><script defer src="assets/site.js"></script></body></html>')
        # A self-contained error document also works when returned for a nested missing URL.
        base=self.base+'/' if self.base else './'
        links=' '.join(f'<a href="{esc(base+l+"/index.html")}">{esc(next(x["name"] for x in self.cfg["languages"] if x["code"]==l))}</a>' for l in self.langs)
        self.write('404.html',f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>404 | Armwrestling LAB</title><style>body{{margin:0;background:#151617;color:#f7f5f1;font:18px/1.6 system-ui,sans-serif}}main{{max-width:720px;margin:15vh auto;padding:30px}}strong{{color:#f24b50;font-size:100px}}h1{{font-size:42px;line-height:1.15}}a{{display:inline-block;margin:12px 12px 0 0;padding:12px 25px;color:white;border:1px solid #666;text-decoration:none}}a:focus-visible{{outline:3px solid #f24b50}}</style></head><body><main><strong>404</strong><h1>This page is out of reach.</h1><p lang="pl">Nie znaleziono strony. Wr\u00f3\u0107 do biblioteki artyku\u0142\u00f3w.</p><p>Return to the library:</p>{links}</main></body></html>')
        self.write('.nojekyll','')
        self.write('site.webmanifest',json.dumps({'name':'Armwrestling LAB','short_name':'AW LAB','start_url':'./index.html','scope':'./','display':'browser','background_color':'#f5f3ef','theme_color':'#151617','icons':[{'src':'assets/favicon.png','sizes':'64x64','type':'image/png'}]},indent=2))
        robots='User-agent: *\nAllow: /\n'
        if self.base:
            robots+='Sitemap: '+self.base+'/sitemap.xml\n'
            sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
            for page in self.pages:
                sitemap+='<url><loc>'+xml_escape(self.base+'/'+page['path'])+'</loc><lastmod>'+self.cfg['build_date']+'</lastmod>'
                sitemap+=''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{xml_escape(self.base+"/"+l+"/"+page["route"])}"/>' for l in self.langs)
                sitemap+='</url>'
            self.write('sitemap.xml',sitemap+'</urlset>\n')
        self.write('robots.txt',robots)
        self.write('build-info.json',json.dumps({'version':self.cfg['version'],'edition':self.cfg['build_date'],'languages':self.langs,'article_count':len(self.articles),'html_pages':len(self.pages)+2,'site_url':self.base,'offline_ready':True},indent=2))
    def build(self):
        if OUT.exists(): shutil.rmtree(OUT)
        shutil.copytree(ROOT/'static',OUT)
        for lang in self.langs:
            self.home(lang)
            for c in self.categories: self.category(lang,c)
            for a in self.articles: self.article(lang,a)
            self.download_page(lang);self.about(lang);self.privacy(lang)
        self.root_pages()
        print(f'Built {len(self.pages)+2} HTML pages; {len(self.articles)} articles x {len(self.langs)} languages; {len(self.downloads)} downloads.')
        print('Site:',OUT)
        print('Public URL:',self.base or '(unset: offline preview; pass --site-url for canonical URLs and sitemap)')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-url',default=None)
    args=parser.parse_args()
    try: Builder(args.site_url).build()
    except (ValueError,KeyError,FileNotFoundError,json.JSONDecodeError) as e:
        print(f'Build failed: {e}',file=sys.stderr);return 1
    return 0
if __name__=='__main__':sys.exit(main())
