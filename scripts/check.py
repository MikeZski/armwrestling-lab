#!/usr/bin/env python3
"""Offline structural audit of generated HTML and source content. No dependencies."""
from __future__ import annotations
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[1]
class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.links=[];self.ids=set();self.duplicate_ids=[];self.lang=None;self.h1=0;self.has_title=False;self.images=[];self.citations=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html':self.lang=a.get('lang')
        if tag=='h1':self.h1+=1
        if tag=='title':self.has_title=True
        if tag=='img':self.images.append(a)
        if a.get('id'):
            if a['id'] in self.ids:self.duplicate_ids.append(a['id'])
            self.ids.add(a['id'])
        for key in ['href','src']:
            if a.get(key):self.links.append((tag,key,a[key]))

def audit(site:Path):
    errors=[];warnings=[];docs={};local_links=0;external_links=set()
    def error(s):errors.append(s)
    for p in site.rglob('*.html'):
        d=Document();d.feed(p.read_text(encoding='utf-8'));docs[p.resolve()]=d
        name=p.relative_to(site).as_posix()
        if not d.lang:error(f'{name}: no lang attribute')
        if d.h1!=1:error(f'{name}: expected 1 h1, got {d.h1}')
        if not d.has_title:error(f'{name}: no title')
        if d.duplicate_ids:error(f'{name}: duplicate IDs: {d.duplicate_ids}')
        for img in d.images:
            if 'alt' not in img:error(f'{name}: image without alt')
            if not img.get('width') or not img.get('height'):error(f'{name}: image without intrinsic dimensions')
    for p,d in docs.items():
        for tag,key,link in d.links:
            url=urlsplit(link)
            if url.scheme in ['https','http']:
                if url.scheme!='https':error(f'{p.name}: insecure URL {link}')
                external_links.add(link);continue
            if url.scheme in ['mailto','tel','data']:continue
            if url.scheme:error(f'{p.name}: unsupported URL {link}');continue
            if link.startswith('//'):error(f'{p.name}: protocol-relative URL {link}');continue
            if url.path.startswith('/'):error(f'{p.name}: root-relative link breaks repo deployments: {link}');continue
            target=(p.parent/unquote(url.path)).resolve() if url.path else p
            if target.is_dir():target=target/'index.html'
            local_links+=1
            if not target.is_relative_to(site.resolve()):error(f'{p.name}: link escapes site: {link}');continue
            if not target.is_file():error(f'{p.relative_to(site)}: missing {link}');continue
            if url.fragment and target.suffix=='.html' and url.fragment not in docs.get(target,Document()).ids:
                error(f'{p.relative_to(site)}: missing fragment {link}')
    cfg=json.loads((ROOT/'content/site.json').read_text(encoding='utf-8'));meta=json.loads((ROOT/'content/articles.json').read_text(encoding='utf-8'));refs=json.loads((ROOT/'content/references.json').read_text(encoding='utf-8'))
    for lang in cfg['published_languages']:
        articles=json.loads((ROOT/f'content/articles/{lang}.json').read_text(encoding='utf-8'))
        for a in meta:
            d=articles[a['id']]
            if len(d['sections'])<3:error(f'{lang}/{a["id"]}: too few sections')
            if not d.get('figure',{}).get('caption'):error(f'{lang}/{a["id"]}: missing figure provenance')
            for m in re.findall(r'\[([\d,\-\u2013 ]+)\]',json.dumps(d,ensure_ascii=False)):
                for n in re.findall(r'\d+',m):
                    if not 1<=int(n)<=len(a['references']):error(f'{lang}/{a["id"]}: out-of-range citation [{m}]')
            for r in a['references']:
                if r not in refs:error(f'{lang}/{a["id"]}: missing reference {r}')
            for required in ['index.html',f'articles/{a["id"]}/index.html']:
                if not (site/lang/required).is_file():error(f'Missing page: {lang}/{required}')
    for a in meta:
        if not a.get('video_id'):warnings.append(f'{a["id"]}: labelled YouTube search link, exact video ID not supplied/confirmed.')
    report={'passed':not errors,'html_pages':len(docs),'article_editions':len(meta)*len(cfg['published_languages']),'local_links_checked':local_links,'unique_external_urls':len(external_links),'external_network_checked':False,'errors':errors,'warnings':warnings}
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--site',default=str(ROOT/'site'));ap.add_argument('--report');args=ap.parse_args();report=audit(Path(args.site).resolve())
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if args.report:Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
