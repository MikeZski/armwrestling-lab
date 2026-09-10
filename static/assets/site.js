/* Progressive enhancement only. The site needs no API, fetch, framework or cookies. */
(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const messages = $('#ui-messages') ? JSON.parse($('#ui-messages').textContent) : {};
  const store = { get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } }, set(k,v) { try { localStorage.setItem(k,v); } catch (_) {} } };
  let toastTimer;
  function toast(message) { const el=$('.toast'); if(!el) return; el.textContent=message; el.hidden=false; clearTimeout(toastTimer); toastTimer=setTimeout(()=>{el.hidden=true;},5000); }
  const theme=$('.theme-button');
  if(theme){ theme.hidden=false; theme.setAttribute('aria-pressed',String(document.documentElement.dataset.theme==='dark')); theme.addEventListener('click',()=>{const value=document.documentElement.dataset.theme==='dark'?'light':'dark'; document.documentElement.dataset.theme=value; theme.setAttribute('aria-pressed',String(value==='dark')); store.set('awl-theme',value);}); }
  $$('[data-language]').forEach(a=>a.addEventListener('click',()=>store.set('awl-language',a.dataset.language)));
  $$('.header-actions details').forEach(el=>{ el.addEventListener('toggle',()=>{if(el.open) $$('.header-actions details').forEach(other=>{if(other!==el)other.open=false;});}); });
  document.addEventListener('click',e=>{ $$('.header-actions details[open]').forEach(el=>{if(!el.contains(e.target))el.open=false;}); });
  document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ $$('.header-actions details[open]').forEach(el=>{el.open=false;$('summary',el).focus();}); } });
  $$('[data-print]').forEach(button=>{button.hidden=false;button.addEventListener('click',()=>window.print());});
  $$('[data-copy]').forEach(button=>{button.hidden=false;button.addEventListener('click',async()=>{
    if(location.protocol==='file:'){toast(messages.not_shared);return;}
    try { if(!navigator.clipboard)throw new Error('Clipboard not available');await navigator.clipboard.writeText(location.href);toast(messages.copied); } catch(_){toast(messages.copy_failed);}
  });});
  function norm(value) { return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\u0142/g,'l').replace(/\u0141/g,'L').toLocaleLowerCase(document.documentElement.lang); }
  const library=$('[data-library]');
  if(library){
    $$('[data-search-controls]',library).forEach(el=>el.hidden=false);
    const input=$('#article-search',library), select=$('#article-sort',library), count=$('.result-count',library), empty=$('[data-empty]',library), clear=$('.clear-search',library), grid=$('.article-grid',library), filters=$$('[data-filter]',library);
    const cards=$$('[data-card]',grid);const index=new Map(cards.map(el=>[el,norm(el.dataset.search)]));let topic='all';
    function updateURL(){ try{const url=new URL(location.href);input.value.trim()?url.searchParams.set('q',input.value.trim()):url.searchParams.delete('q');topic!=='all'?url.searchParams.set('topic',topic):url.searchParams.delete('topic');select.value!=='editorial'?url.searchParams.set('sort',select.value):url.searchParams.delete('sort');history.replaceState(null,'',url);}catch(_){} }
    function apply(save=true){
      const words=norm(input.value.trim()).split(/\s+/).filter(Boolean);let n=0;
      cards.forEach(el=>{const matches=(topic==='all'||el.dataset.category===topic)&&words.every(word=>index.get(el).includes(word));el.hidden=!matches;if(matches)n++;});
      const order=[...cards].sort(select.value==='alpha'?(a,b)=>a.dataset.title.localeCompare(b.dataset.title,document.documentElement.lang,{sensitivity:'base'}):(a,b)=>Number(a.dataset.order)-Number(b.dataset.order));
      order.forEach(el=>grid.appendChild(el));count.textContent=n+' '+messages.results;empty.hidden=n!==0;clear.hidden=!input.value;filters.forEach(a=>{const active=a.dataset.filter===topic;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});if(save)updateURL();
    }
    function fromURL(){const params=new URL(location.href).searchParams;input.value=params.get('q')||'';const requested=params.get('topic')||'all';topic=filters.some(a=>a.dataset.filter===requested)?requested:'all';select.value=params.get('sort')==='alpha'?'alpha':'editorial';apply(false);}
    input.addEventListener('input',()=>apply());select.addEventListener('change',()=>apply());clear.addEventListener('click',()=>{input.value='';apply();input.focus();});
    filters.forEach(a=>a.addEventListener('click',e=>{if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();topic=a.dataset.filter;apply();}));
    $('[data-reset]',library).addEventListener('click',()=>{input.value='';topic='all';select.value='editorial';apply();input.focus();});
    window.addEventListener('popstate',fromURL);fromURL();
  }
  const downloads=$('[data-downloads]');
  if(downloads){
    $('[data-download-controls]',downloads).hidden=false;
    const controls=$$('[data-download-filter]',downloads),cards=$$('[data-download-type]',downloads),empty=$('[data-download-empty]',downloads);
    function filter(type,save=true){if(!controls.some(b=>b.dataset.downloadFilter===type))type='all';let count=0;cards.forEach(card=>{card.hidden=type!=='all'&&card.dataset.downloadType!==type;if(!card.hidden)count++;});empty.hidden=count>0;controls.forEach(button=>{const active=button.dataset.downloadFilter===type;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));});if(save){try{const u=new URL(location.href);type==='all'?u.searchParams.delete('type'):u.searchParams.set('type',type);history.replaceState(null,'',u);}catch(_){}}}
    controls.forEach(button=>button.addEventListener('click',()=>filter(button.dataset.downloadFilter)));
    filter(new URL(location.href).searchParams.get('type')||'all',false);
  }
  const sections=$$('.prose-section'),toc=$('.toc');
  if(toc&&'IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting){$$('a',toc).forEach(a=>{if(a.getAttribute('href')==='#'+entry.target.id)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});}});},{rootMargin:'-100px 0px -65% 0px'});sections.forEach(s=>observer.observe(s));}
})();
