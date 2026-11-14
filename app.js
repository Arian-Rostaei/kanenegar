/* ================= HELPERS ================= */
const $=s=>document.querySelector(s), $$=s=>Array.from(document.querySelectorAll(s));
function faChar(d){return String.fromCharCode(0x06F0+(+d));}
function faNum(v){
  const s=String(v); let out="";
  for(let i=0;i<s.length;i++){
    const ch=s[i];
    if(ch>="0"&&ch<="9"){
      const p=s[i-1]||"", pp=s[i-2]||"";
      const keep=/[A-Za-z]/.test(p)||(p==="-"&&/[A-Za-z]/.test(pp));
      out+=keep?ch:faChar(ch);
    } else out+=ch;
  }
  return out;
}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
const dateFmt=new Intl.DateTimeFormat("fa-IR",{year:"numeric",month:"long",day:"numeric"});
const dateShort=new Intl.DateTimeFormat("fa-IR",{month:"long",day:"numeric"});
function pdate(iso){try{return dateFmt.format(new Date(iso+"T12:00:00"));}catch(e){return iso;}}
function pdateShort(iso){try{return dateShort.format(new Date(iso+"T12:00:00"));}catch(e){return iso;}}
function wordCount(a){return (a.body||[]).reduce((n,b)=>n+((b&&b.x)?b.x.split(/\s+/).length:0),0)+(a.lede?a.lede.split(/\s+/).length:0);}
function readMin(a){return Math.max(2,Math.round(wordCount(a)/180));}
function hashStr(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
function mulberry(seed){let t=seed>>>0;return function(){t+=0x6D2B79F5;let r=Math.imul(t^t>>>15,1|t);r^=r+Math.imul(r^r>>>7,61|r);return((r^r>>>14)>>>0)/4294967296;};}
const byId=Object.fromEntries(ARTICLES.map(a=>[a.id,a]));
const sortedAll=[...ARTICLES].sort((a,b)=>String(b.date).localeCompare(String(a.date)));
const METALS=Array.isArray(window.MARKET_DATA)?window.MARKET_DATA:[];
const COPPER_POINTS=Array.isArray(window.COPPER_POINTS)?window.COPPER_POINTS:[];

/* ================= GENERATIVE MINERAL ART ================= */
function makeArt(a,uid){
  const rnd=mulberry(hashStr(a.id));
  const c=(CATS[a.cat]||{c:"#E08D4F"}).c;
  const id=a.id+"-"+uid;
  const W=640,H=360;
  let defs=`<defs>
    <linearGradient id="sky-${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B1020"/><stop offset=".55" stop-color="#0A0E16"/><stop offset="1" stop-color="#07090D"/></linearGradient>
    <radialGradient id="glow-${id}" cx=".7" cy=".25" r=".8"><stop offset="0" stop-color="${c}" stop-opacity=".5"/><stop offset=".5" stop-color="${c}" stop-opacity=".12"/><stop offset="1" stop-color="${c}" stop-opacity="0"/></radialGradient>
    <linearGradient id="ore-${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${c}"/><stop offset="1" stop-color="#1a1208"/></linearGradient>
    <linearGradient id="fade-${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient>
  </defs>`;
  let stars="";
  for(let i=0;i<26;i++){const x=rnd()*W,y=rnd()*H*0.5,r=rnd()*1.3+0.3;stars+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="#fff" opacity="${(rnd()*0.5+0.15).toFixed(2)}"/>`;}
  let scene="";
  const R=(n)=>rnd()*n;
  if(a.cat==="copper"){
    let pit="";const cx=W*0.5,cy=H*0.62;
    for(let i=0;i<8;i++){const rx=250-i*26, ry=95-i*10, yy=cy+i*13;const op=(0.85-i*0.07).toFixed(2);
      pit+=`<ellipse cx="${cx}" cy="${yy}" rx="${rx}" ry="${ry}" fill="none" stroke="${c}" stroke-opacity="${op}" stroke-width="${(3-i*0.2).toFixed(1)}"/>`;
      pit+=`<path d="M ${cx-rx} ${yy} A ${rx} ${ry} 0 0 0 ${cx+rx} ${yy}" fill="${c}" opacity="${(0.05+i*0.02).toFixed(2)}"/>`;}
    for(let i=0;i<7;i++){const ang=rnd()*Math.PI;const rr=60+R(160);const x=cx+Math.cos(ang)*rr,y=cy+40+Math.sin(ang)*rr*0.35;pit+=`<rect x="${x.toFixed(0)}" y="${y.toFixed(0)}" width="7" height="4" rx="1" fill="#FFD9A0" opacity=".8"/>`;}
    scene=`<path d="M0 ${H*0.55} L ${W*0.2} ${H*0.42} L ${W*0.4} ${H*0.5} L ${W*0.6} ${H*0.4} L ${W*0.8} ${H*0.52} L ${W} ${H*0.45} L ${W} ${H} L 0 ${H} Z" fill="#0E1420"/>${pit}<ellipse cx="${cx}" cy="${cy+95}" rx="70" ry="22" fill="${c}" opacity=".5"/>`;
  } else if(a.cat==="precious"){
    let cr="";
    for(let i=0;i<6;i++){const x=90+i*90+R(30), base=H*0.82, h=90+R(120), w=26+R(26);const tip=x+R(20)-10;
      cr+=`<polygon points="${x-w},${base} ${x-w*0.5},${base-h*0.7} ${tip},${base-h} ${x+w*0.6},${base-h*0.6} ${x+w},${base}" fill="url(#ore-${id})" opacity="${(0.75+rnd()*0.25).toFixed(2)}"/>`;
      cr+=`<polygon points="${x-w*0.5},${base-h*0.7} ${tip},${base-h} ${x},${base} ${x-w},${base}" fill="#fff" opacity=".12"/>`;
      cr+=`<line x1="${tip}" y1="${base-h}" x2="${x}" y2="${base}" stroke="#fff" stroke-opacity=".25" stroke-width="1"/>`;}
    for(let i=0;i<8;i++){const x=R(W),y=H*0.2+R(H*0.5);cr+=`<path d="M ${x} ${y-5} L ${x+1.5} ${y-1.5} L ${x+5} ${y} L ${x+1.5} ${y+1.5} L ${x} ${y+5} L ${x-1.5} ${y+1.5} L ${x-5} ${y} L ${x-1.5} ${y-1.5} Z" fill="#FFF3C4" opacity="${(0.4+rnd()*0.5).toFixed(2)}"/>`;}
    scene=`<rect x="0" y="${H*0.82}" width="${W}" height="${H*0.18}" fill="#0C0F16"/>${cr}`;
  } else if(a.cat==="battery"){
    let ponds="";
    for(let row=0;row<4;row++){const y=H*0.5+row*34, sc=1+row*0.35;
      for(let col=0;col<5;col++){const w=90*sc,h=26*sc,x=W*0.5+(col-2)*(w+10)-w/2;
        ponds+=`<rect x="${x.toFixed(0)}" y="${y}" width="${w.toFixed(0)}" height="${h.toFixed(0)}" rx="3" fill="${c}" opacity="${(0.12+row*0.08+rnd()*0.08).toFixed(2)}" stroke="${c}" stroke-opacity=".4"/>`;}}
    scene=`<circle cx="${W*0.75}" cy="${H*0.28}" r="34" fill="${c}" opacity=".5"/><circle cx="${W*0.75}" cy="${H*0.28}" r="20" fill="#EAFFF6" opacity=".7"/><path d="M0 ${H*0.5} L ${W} ${H*0.46} L ${W} ${H} L 0 ${H} Z" fill="#0B141A"/>${ponds}`;
  } else if(a.cat==="rare"){
    let hex="";
    for(let i=0;i<7;i++){const x=80+i*80+R(24), y=H*0.55+R(60), r=22+R(26), rot=R(30);
      let pts="";for(let k=0;k<6;k++){const ang=Math.PI/3*k+rot*Math.PI/180;pts+=`${(x+Math.cos(ang)*r).toFixed(1)},${(y+Math.sin(ang)*r*1.4).toFixed(1)} `;}
      hex+=`<polygon points="${pts.trim()}" fill="url(#ore-${id})" opacity="${(0.6+rnd()*0.4).toFixed(2)}" stroke="${c}" stroke-opacity=".7"/>`;
      hex+=`<polygon points="${pts.trim()}" fill="#fff" opacity=".07"/>`;}
    for(let i=0;i<10;i++){hex+=`<circle cx="${R(W).toFixed(0)}" cy="${(H*0.15+R(H*0.5)).toFixed(0)}" r="${(1+rnd()*2).toFixed(1)}" fill="${c}" opacity=".7"/>`;}
    scene=`<path d="M0 ${H*0.78} Q ${W*0.5} ${H*0.7} ${W} ${H*0.8} L ${W} ${H} L 0 ${H} Z" fill="#0D0A18"/>${hex}`;
  } else if(a.cat==="iron"){
    let layers="";const cols=["#16202E","#1B2A3C","#22344A","#2A3E58","#33506E"];
    for(let i=0;i<5;i++){const y=H*0.45+i*30;layers+=`<path d="M0 ${y} Q ${W*0.25} ${y-12+R(20)} ${W*0.5} ${y} T ${W} ${y-6} L ${W} ${y+30} L 0 ${y+30} Z" fill="${cols[i]}" opacity=".9"/>`;}
    layers+=`<path d="M0 ${H*0.62} Q ${W*0.3} ${H*0.56} ${W*0.55} ${H*0.64} T ${W} ${H*0.6}" fill="none" stroke="${c}" stroke-width="4" stroke-opacity=".8"/>`;
    layers+=`<g stroke="#9FB6D4" stroke-width="3" fill="none" opacity=".8"><path d="M ${W*0.78} ${H*0.45} v -70 h 60"/><path d="M ${W*0.78} ${H*0.45-70} l -26 26"/><path d="M ${W*0.78+40} ${H*0.45-70} v 34"/></g>`;
    layers+=`<path d="M ${W*0.6} ${H*0.86} h 130 l -18 22 h -96 Z" fill="#101826" stroke="${c}" stroke-opacity=".6"/>`;
    scene=`${layers}<rect x="0" y="${H*0.86}" width="${W}" height="${H*0.14}" fill="#0A1220" opacity=".7"/>`;
  } else if(a.cat==="geo"){
    let ridges=`<path d="M0 ${H*0.6} L ${W*0.18} ${H*0.34} L ${W*0.32} ${H*0.52} L ${W*0.5} ${H*0.26} L ${W*0.68} ${H*0.5} L ${W*0.84} ${H*0.36} L ${W} ${H*0.55} L ${W} ${H} L 0 ${H} Z" fill="#0F1A1E"/>`;
    ridges+=`<path d="M0 ${H*0.72} L ${W*0.22} ${H*0.5} L ${W*0.42} ${H*0.66} L ${W*0.62} ${H*0.46} L ${W*0.82} ${H*0.64} L ${W} ${H*0.56} L ${W} ${H} L 0 ${H} Z" fill="#13242A"/>`;
    for(let i=0;i<6;i++){const x=W*0.15+i*90+R(30);ridges+=`<line x1="${x}" y1="${H*0.95}" x2="${x+50+R(40)}" y2="${H*0.4+R(60)}" stroke="${c}" stroke-width="${(1.5+rnd()*2).toFixed(1)}" stroke-opacity="${(0.4+rnd()*0.4).toFixed(2)}"/>`;}
    ridges+=`<g stroke="#CFE8E2" stroke-width="2.5" fill="none" opacity=".85"><path d="M ${W*0.7} ${H*0.8} l 16 -70 l 16 70"/><path d="M ${W*0.7+6} ${H*0.8-30} h 20"/><path d="M ${W*0.7+16} ${H*0.8-70} v -14"/></g>`;
    for(let i=0;i<4;i++){ridges+=`<rect x="${W*0.12+i*26}" y="${H*0.86}" width="14" height="${26+R(20)}" rx="3" fill="${c}" opacity=".55"/>`;}
    scene=ridges;
  } else {
    let candles="";let px=40;let py=H*0.6;let curve=`M ${px} ${py}`;
    for(let i=0;i<16;i++){const x=40+i*36, o=py, cl=py+(rnd()-0.48)*70; py=Math.max(60,Math.min(H*0.85,cl));
      const hi=Math.min(o,py)-10-R(20), lo=Math.max(o,py)+10+R(20);const up=py<o;
      candles+=`<line x1="${x}" y1="${hi}" x2="${x}" y2="${lo}" stroke="${up?c:'#F0605D'}" stroke-width="1.5" opacity=".7"/>`;
      candles+=`<rect x="${x-7}" y="${Math.min(o,py)}" width="14" height="${Math.max(4,Math.abs(py-o))}" rx="2" fill="${up?c:'#F0605D'}" opacity=".8"/>`;
      curve+=` L ${x} ${py}`;}
    let grid="";for(let i=1;i<5;i++){grid+=`<line x1="0" y1="${H*i/5}" x2="${W}" y2="${H*i/5}" stroke="#fff" stroke-opacity=".05"/>`;}
    scene=`${grid}<path d="${curve}" fill="none" stroke="#F5C84C" stroke-width="2.5" stroke-opacity=".9"/>${candles}`;
  }
  return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid slice" role="img" aria-label="تصویرسازی ${esc((CATS[a.cat]||{fa:"خبر"}).fa)}">${defs}<rect width="${W}" height="${H}" fill="url(#sky-${id})"/><rect width="${W}" height="${H}" fill="url(#glow-${id})"/>${stars}${scene}<rect width="${W}" height="${H}" fill="url(#fade-${id})"/></svg>`;
}

/* ================= STATE ================= */
const state={q:"",cat:"all",sort:"new",savedOnly:false,layout:"grid"};
let saved=new Set();
try{saved=new Set(JSON.parse(localStorage.getItem("kanenegar-saved")||"[]"));}catch(e){saved=new Set();}
function persistSaved(){try{localStorage.setItem("kanenegar-saved",JSON.stringify([...saved]));}catch(e){}}
let currentArticle=null, lastFocus=null;

function toast(msg,opts={}){
  const box=$("#toasts");
  const el=document.createElement("div");
  el.className="toast";
  el.style.setProperty("--tc",opts.color||"var(--ok)");
  el.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 4v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V7Z"/><path d="m9 12 2 2 4-4"/></svg><span>${esc(msg)}</span>`;
  const dismiss=()=>{el.classList.add("out");setTimeout(()=>el.remove(),300);};
  if(opts.action){const b=document.createElement("button");b.textContent=opts.action.label;b.addEventListener("click",()=>{opts.action.fn();dismiss();});el.appendChild(b);}
  box.appendChild(el);
  setTimeout(dismiss,opts.duration||3600);
}
function updateSavedUI(){
  const n=saved.size, badge=$("#savedCount");
  badge.hidden=n===0; badge.textContent=faNum(n);
  $$(".save-btn").forEach(b=>{const on=saved.has(b.dataset.id);b.classList.toggle("saved",on);b.setAttribute("aria-pressed",on);b.querySelector("svg").setAttribute("fill",on?"currentColor":"none");});
  if(currentArticle){const on=saved.has(currentArticle.id);$("#rSave").classList.toggle("saved",on);$("#rSave svg").setAttribute("fill",on?"currentColor":"none");$("#rSave").style.color=on?"var(--gold)":"";}
}
function toggleSave(id,withUndo=true){
  if(!byId[id])return;
  if(saved.has(id)){saved.delete(id);persistSaved();updateSavedUI();
    if(withUndo)toast("نشان مقاله برداشته شد.",{color:"var(--warn)",action:{label:"بازگردانی",fn:()=>{saved.add(id);persistSaved();updateSavedUI();if(state.savedOnly)renderFeed();}}});
  }else{saved.add(id);persistSaved();updateSavedUI();toast("مقاله نشان‌گذاری شد و در «نشان‌شده‌ها» ذخیره شد.");}
  if(state.savedOnly)renderFeed();
}

/* ================= FEED ================= */
function filtered(){
  let list=[...ARTICLES];
  if(state.cat!=="all")list=list.filter(a=>a.cat===state.cat);
  if(state.savedOnly)list=list.filter(a=>saved.has(a.id));
  if(state.q.trim()){const q=state.q.trim().toLowerCase();
    list=list.filter(a=>{const hay=(a.title+" "+a.lede+" "+(a.tags||[]).join(" ")+" "+(a.src?a.src.name:"")+" "+(a.src?a.src.orig:"")+" "+(a.body||[]).map(b=>b.x).join(" ")).toLowerCase();return hay.includes(q);});}
  if(state.sort==="new")list.sort((a,b)=>String(b.date).localeCompare(String(a.date)));
  else if(state.sort==="old")list.sort((a,b)=>String(a.date).localeCompare(String(b.date)));
  else list.sort((a,b)=>readMin(b)-readMin(a));
  return list;
}
function cardHTML(a,i){
  const cat=CATS[a.cat]||{fa:"خبر",c:"#E08D4F"};
  return `<article class="card" data-id="${a.id}" style="--cc:${cat.c};transition-delay:${Math.min(i*45,360)}ms" tabindex="0" role="button" aria-label="خواندن مقاله: ${esc(faNum(a.title))}">
    <div class="card-art">${makeArt(a,"card")}
      <span class="card-cat chip" style="color:${cat.c};border-color:${cat.c}66;background:${cat.c}1f">${esc(cat.fa)}</span>
      <button class="save-btn" data-id="${a.id}" aria-pressed="false" title="نشان‌کردن مقاله" aria-label="نشان‌کردن مقاله"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3h12v18l-6-4-6 4Z"/></svg></button>
    </div>
    <div class="card-body">
      <h3 class="card-title">${esc(faNum(a.title))}</h3>
      <p class="card-lede">${esc(faNum(a.lede||""))}</p>
      <div class="card-foot">
        <span class="src-badge"><i></i>${esc(a.src?a.src.name:"")}</span>
        <span>${pdateShort(a.date)} · ${faNum(readMin(a))} دقیقه</span>
      </div>
    </div>
  </article>`;
}
let revealObs=null;
function renderFeed(){
  const list=filtered();
  const grid=$("#articleGrid");
  grid.classList.toggle("list",state.layout==="list");
  if(!list.length){
    grid.innerHTML=`<div class="empty">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/><path d="M8 11h6"/></svg>
      <h3>مقاله‌ای با این فیلترها پیدا نشد</h3>
      <p>عبارت جستجو یا دسته‌بندی را تغییر دهید، یا فیلتر «فقط نشان‌شده‌ها» را خاموش کنید.</p>
      <button class="btn btn-primary" id="resetFilters">پاک‌سازی همهٔ فیلترها</button>
    </div>`;
    $("#resetFilters").addEventListener("click",()=>{state.q="";state.cat="all";state.savedOnly=false;$("#searchInput").value="";$("#savedToggle").classList.remove("on");$("#savedToggle").setAttribute("aria-pressed","false");renderChips();renderFeed();});
  }else{grid.innerHTML=list.map(cardHTML).join("");}
  $("#resultCount").innerHTML=`نمایش <b>${faNum(list.length)}</b> مقاله از ${faNum(ARTICLES.length)} مقالهٔ ترجمه‌شده`;
  const parts=[];
  if(state.cat!=="all")parts.push("دسته: "+(CATS[state.cat]?CATS[state.cat].fa:state.cat));
  if(state.savedOnly)parts.push("فقط نشان‌شده‌ها");
  if(state.q.trim())parts.push("جستجو: «"+esc(state.q.trim())+"»");
  $("#activeFilter").textContent=parts.join(" · ");
  updateSavedUI();
  if(revealObs)revealObs.disconnect();
  revealObs=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("in");revealObs.unobserve(e.target);}});},{threshold:0.08});
  $$("#articleGrid .card").forEach(c=>revealObs.observe(c));
}
function renderChips(){
  const counts={};ARTICLES.forEach(a=>counts[a.cat]=(counts[a.cat]||0)+1);
  let html=`<button class="cat-chip ${state.cat==="all"?"on":""}" data-cat="all" style="--cc:var(--copper)"><span class="swatch"></span>همهٔ دسته‌ها <span class="cnt">${faNum(ARTICLES.length)}</span></button>`;
  for(const k in CATS){html+=`<button class="cat-chip ${state.cat===k?"on":""}" data-cat="${k}" style="--cc:${CATS[k].c}"><span class="swatch"></span>${esc(CATS[k].fa)} <span class="cnt">${faNum(counts[k]||0)}</span></button>`;}
  $("#catChips").innerHTML=html;
}

/* ================= HERO / TICKER / STATS / SOURCES ================= */
function renderHero(){
  if(!sortedAll.length){$("#heroFeature").innerHTML=`<div class="hero-content"><h1 class="hero-title">هنوز خبری منتشر نشده است</h1><p class="hero-lede">ایجنت به‌زودی نخستین اخبار را منتشر می‌کند.</p></div>`;return;}
  const f=sortedAll[0];const cat=CATS[f.cat]||{fa:"خبر",c:"#E08D4F"};
  $("#heroFeature").innerHTML=`<div class="hero-art">${makeArt(f,"hero")}</div>
    <div class="hero-content">
      <span class="chip" style="color:${cat.c};border-color:${cat.c}66;background:${cat.c}22">◆ گزارش ویژه · ${esc(cat.fa)}</span>
      <h1 class="hero-title">${esc(faNum(f.title))}</h1>
      <p class="hero-lede">${esc(faNum(f.lede||""))}</p>
      <div class="meta-row"><span>${esc(f.src?f.src.name:"")}</span><span class="dot"></span><span>${pdate(f.date)}</span><span class="dot"></span><span>${faNum(readMin(f))} دقیقه مطالعه</span></div>
      <div class="hero-cta">
        <button class="btn btn-primary" data-open="${f.id}">خواندن مقالهٔ کامل<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 6l-6 6 6 6"/></svg></button>
        ${f.src&&f.src.url?`<a class="btn btn-ghost" href="${esc(f.src.url)}" target="_blank" rel="noopener noreferrer">منبع اصلی<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 4h6v6"/><path d="M20 4 10 14"/><path d="M18 13v6H5V6h6"/></svg></a>`:""}
      </div>
    </div>`;
  $("#heroSide").innerHTML=sortedAll.slice(1,4).map(a=>{const c=(CATS[a.cat]||{c:"#E08D4F"}).c;
    return `<article class="side-card" data-open="${a.id}" style="--sc:${c}" tabindex="0" role="button">
      <span class="eyebrow" style="color:${c}">${esc((CATS[a.cat]||{fa:"خبر"}).fa)}</span>
      <h3>${esc(faNum(a.title))}</h3>
      <div class="meta-row"><span>${esc(a.src?a.src.name:"")}</span><span class="dot"></span><span>${pdateShort(a.date)}</span></div>
    </article>`;}).join("");
  const srcCount=new Set(ARTICLES.map(a=>a.src?a.src.name:"")).size;
  const stats=[
    [ARTICLES.length,"مقالهٔ ترجمه‌شده","rgba(224,141,79,.3)","#E08D4F"],
    [srcCount,"منبع معتبر رصدشده","rgba(87,166,255,.3)","#57A6FF"],
    [Object.keys(CATS).length,"دستهٔ تخصصی","rgba(62,207,142,.3)","#3ECF8E"],
    [ARTICLES.reduce((n,a)=>n+wordCount(a),0),"واژهٔ فارسی ترجمه‌شده","rgba(167,139,250,.3)","#A78BFA"]
  ];
  $("#heroStats").innerHTML=stats.map(s=>`<div class="stat" style="--stc:${s[2]};--stc2:${s[3]}"><b data-count="${s[0]}">${faChar(0)}</b><span>${s[1]}</span></div>`).join("");
  $("#lastScan").textContent=pdate(sortedAll[0].date);
}
function renderTicker(){
  if(!sortedAll.length){$("#tickerTrack").innerHTML="";return;}
  const items=sortedAll.slice(0,7).map(a=>`<span class="tick-item" data-open="${a.id}"><b>${esc((CATS[a.cat]||{fa:"خبر"}).fa)}</b>${esc(faNum(a.title))}<span class="tick-sep">◆</span></span>`).join("");
  $("#tickerTrack").innerHTML=items+items;
}
function renderSources(){
  const map={};ARTICLES.forEach(a=>{if(a.src){const n=a.src.name;map[n]=(map[n]||0)+1;}});
  const entries=Object.entries(map).sort((a,b)=>b[1]-a[1]);
  $("#srcList").innerHTML=entries.map(([n,c],i)=>{
    const first=ARTICLES.find(a=>a.src&&a.src.name===n);const u=first&&first.src.url?first.src.url.replace(/\/[^/]*$/,"/"):"#";
    return `<a class="src-item" href="${esc(u)}" target="_blank" rel="noopener noreferrer"><span class="n">${faNum(i+1)}</span><span>${esc(n)}</span><span class="cnt">${faNum(c)} مقاله</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 4h6v6"/><path d="M20 4 10 14"/><path d="M18 13v6H5V6h6"/></svg></a>`;}).join("");
}

/* ================= MARKET + CHART ================= */
function renderMarket(){
  if(!METALS.length){$("#marketGrid").innerHTML="";return;}
  $("#marketGrid").innerHTML=METALS.map(m=>{
    const up=m.chg>=0;
    const price=m.price.toLocaleString("fa-IR",{maximumFractionDigits:2});
    return `<div class="metal" style="--mc:${m.c}">
      <div class="metal-top"><div><div class="metal-name">${esc(m.fa)}</div><div class="metal-en lat">${esc(m.en)}</div></div><div class="metal-sym lat">${m.sym}</div></div>
      <div class="metal-price lat">${price}</div>
      <div class="metal-unit">${esc(m.unit)} · ${pdateShort(m.date)}</div>
      <span class="chg ${up?"up":"down"} lat">${up?"▲":"▼"} ${Math.abs(m.chg).toLocaleString("fa-IR",{minimumFractionDigits:2,maximumFractionDigits:2})}٪</span>
      <div class="metal-note">${esc(faNum(m.note||""))}<br><span style="opacity:.7">منبع: ${esc(m.src)}</span></div>
    </div>`;}).join("");
  if(COPPER_POINTS.length)renderCopperChart();
}
function renderCopperChart(){
  const wrap=$("#copperChartWrap");const old=wrap.querySelector("svg");if(old)old.remove();
  const W=900,H=300,padL=64,padR=30,padT=26,padB=52;
  const vals=COPPER_POINTS.map(p=>p.v);
  const min=Math.min(...vals)-1200,max=Math.max(...vals)+800;
  const t0=new Date(COPPER_POINTS[0].d).getTime(),t1=new Date(COPPER_POINTS[COPPER_POINTS.length-1].d).getTime()||t0+1;
  const X=d=>padL+((new Date(d).getTime()-t0)/(t1-t0||1))*(W-padL-padR);
  const Y=v=>padT+(max-v)/(max-min||1)*(H-padT-padB);
  let grid="";const step=Math.ceil((max-min)/4/500)*500;
  for(let v=Math.ceil(min/500)*500;v<=max;v+=step){
    grid+=`<line x1="${padL}" y1="${Y(v)}" x2="${W-padR}" y2="${Y(v)}" stroke="#fff" stroke-opacity=".07"/>`;
    grid+=`<text x="${padL-10}" y="${Y(v)+4}" text-anchor="end" fill="#69738A" font-size="11" font-family="Space Grotesk">${faNum(v.toLocaleString("en-US")).replace(/,/g,"٬")}</text>`;}
  const pts=COPPER_POINTS.map(p=>({x:X(p.d),y:Y(p.v),p}));
  const line=pts.map((q,i)=>(i?"L":"M")+q.x.toFixed(1)+" "+q.y.toFixed(1)).join(" ");
  const area=line+` L ${pts[pts.length-1].x.toFixed(1)} ${H-padB} L ${pts[0].x.toFixed(1)} ${H-padB} Z`;
  let dots="",labels="";
  pts.forEach((q)=>{dots+=`<circle cx="${q.x.toFixed(1)}" cy="${q.y.toFixed(1)}" r="6" fill="#0A0C10" stroke="#E08D4F" stroke-width="3"/>`;
    dots+=`<circle cx="${q.x.toFixed(1)}" cy="${q.y.toFixed(1)}" r="13" fill="#E08D4F" opacity=".12"/>`;
    labels+=`<text x="${q.x.toFixed(1)}" y="${H-padB+22}" text-anchor="middle" fill="#9AA4B4" font-size="11">${pdateShort(q.p.d)}</text>`;
    labels+=`<text x="${q.x.toFixed(1)}" y="${(q.y-16).toFixed(1)}" text-anchor="middle" fill="#EDEAE3" font-size="12" font-weight="700" font-family="Space Grotesk">${faNum(q.p.v.toLocaleString("en-US")).replace(/,/g,"٬")}</text>`;});
  const svg=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="نمودار قیمت مس">
    <defs><linearGradient id="cuArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E08D4F" stop-opacity=".35"/><stop offset="1" stop-color="#E08D4F" stop-opacity="0"/></linearGradient></defs>
    ${grid}<path d="${area}" fill="url(#cuArea)"/><path d="${line}" fill="none" stroke="#E08D4F" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>${dots}${labels}
  </svg>`;
  wrap.insertAdjacentHTML("afterbegin",svg);
  const tip=$("#chartTip");const svgEl=wrap.querySelector("svg");
  function showTip(i,cx,cy){const p=COPPER_POINTS[i];
    tip.innerHTML=`<b>${faNum(p.v.toLocaleString("en-US")).replace(/,/g,"٬")} دلار/تن</b><br>${pdate(p.d)} · ${esc(faNum(p.label||""))}<br><span style="color:var(--faint)">${esc(p.src||"")}</span>`;
    const rect=wrap.getBoundingClientRect();tip.style.left=(cx*rect.width/W)+"px";tip.style.top=(cy*rect.height/H)+"px";tip.style.opacity="1";}
  svgEl.addEventListener("mousemove",e=>{const rect=svgEl.getBoundingClientRect();const mx=(e.clientX-rect.left)/rect.width*W;
    let best=0,bd=1e9;pts.forEach((q,i)=>{const d=Math.abs(q.x-mx);if(d<bd){bd=d;best=i;}});showTip(best,pts[best].x,pts[best].y);});
  svgEl.addEventListener("mouseleave",()=>{tip.style.opacity="0";});
  svgEl.addEventListener("touchstart",e=>{const rect=svgEl.getBoundingClientRect();const t=e.touches[0];const mx=(t.clientX-rect.left)/rect.width*W;
    let best=0,bd=1e9;pts.forEach((q,i)=>{const d=Math.abs(q.x-mx);if(d<bd){bd=d;best=i;}});showTip(best,pts[best].x,pts[best].y);},{passive:true});
}

/* ================= READER ================= */
function bodyHTML(a){return (a.body||[]).map(b=>{
    if(!b)return "";
    if(b.t==="h")return `<h3>${esc(faNum(b.x))}</h3>`;
    if(b.t==="q")return `<blockquote>«${esc(faNum(b.x))}»<footer>— ${esc(faNum(b.by||""))}</footer></blockquote>`;
    return `<p>${esc(faNum(b.x))}</p>`;}).join("");}
function openArticle(id,push=true){
  const a=byId[id];if(!a)return;currentArticle=a;
  const cat=CATS[a.cat]||{fa:"خبر",c:"#E08D4F"};const reader=$("#reader");
  reader.style.setProperty("--cc",cat.c);
  $("#readerHero").innerHTML=makeArt(a,"reader");
  $("#readerCat").innerHTML=`<span class="chip" style="color:${cat.c};border-color:${cat.c}66;background:${cat.c}1f">${esc(cat.fa)}</span>`;
  $("#readerTitle").textContent=faNum(a.title);
  $("#readerLede").textContent=faNum(a.lede||"");
  $("#readerMeta").innerHTML=`<span>${esc(a.src?a.src.name:"")}</span><span class="dot" style="width:3px;height:3px;border-radius:50%;background:var(--faint)"></span><span>${pdate(a.date)}</span><span class="dot" style="width:3px;height:3px;border-radius:50%;background:var(--faint)"></span><span>${faNum(readMin(a))} دقیقه مطالعه</span><span class="dot" style="width:3px;height:3px;border-radius:50%;background:var(--faint)"></span><span>${faNum(wordCount(a))} واژه</span>`;
  $("#readerFacts").innerHTML=(a.facts||[]).map(f=>`<div class="fact"><b>${esc(faNum(f[0]))}</b><span>${esc(faNum(f[1]))}</span></div>`).join("");
  $("#readerProse").innerHTML=bodyHTML(a);
  $("#readerTags").innerHTML=(a.tags||[]).map(t=>`<span class="tag">#${esc(faNum(t))}</span>`).join("");
  $("#readerSource").innerHTML=a.src?`<div class="lbl">منبع اصلی خبر</div><h4>${esc(a.src.name)}</h4><div class="orig">${esc(a.src.orig||"")}</div>${a.src.url?`<a class="btn btn-primary" href="${esc(a.src.url)}" target="_blank" rel="noopener noreferrer">مطالعهٔ متن اصلی در منبع<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 4h6v6"/><path d="M20 4 10 14"/><path d="M18 13v6H5V6h6"/></svg></a>`:""}`:"";
  const idx=sortedAll.findIndex(x=>x.id===id);const prev=sortedAll[idx+1], next=sortedAll[idx-1];
  $("#readerNav").innerHTML=`<button data-open="${next?next.id:""}" ${next?"":"disabled"}><span class="dir">← مقالهٔ جدیدتر</span><span class="t">${next?esc(faNum(next.title)):"در ابتدای آرشیو هستید"}</span></button>
    <button data-open="${prev?prev.id:""}" ${prev?"":"disabled"}><span class="dir">مقالهٔ قدیمی‌تر →</span><span class="t">${prev?esc(faNum(prev.title)):"در انتهای آرشیو هستید"}</span></button>`;
  const rel=ARTICLES.filter(x=>x.cat===a.cat&&x.id!==a.id).slice(0,3);
  $("#readerRelated").innerHTML=rel.length?`<h3>مقالات مرتبط در دستهٔ ${esc(cat.fa)}</h3><div class="rel-grid">${rel.map(r=>`<div class="rel-card" data-open="${r.id}" style="--cc:${(CATS[r.cat]||{c:"#E08D4F"}).c}" tabindex="0" role="button"><div class="ra">${makeArt(r,"rel")}</div><div class="rb"><h4>${esc(faNum(r.title))}</h4><span>${pdateShort(r.date)}</span></div></div>`).join("")}</div>`:"";
  reader.classList.add("open");reader.setAttribute("aria-hidden","false");
  document.body.classList.add("locked");
  $("#readerScroll").scrollTop=0;$("#readerBar").style.width="0%";
  updateSavedUI();
  if(!reader.classList.contains("was-open")){lastFocus=document.activeElement;}
  reader.classList.add("was-open");
  setTimeout(()=>$("#readerClose").focus(),80);
  if(push){try{history.pushState({article:id},"","#m-"+id);}catch(e){}}
}
function closeReader(pop=false){
  const reader=$("#reader");if(!reader.classList.contains("open"))return;
  reader.classList.remove("open","was-open");reader.setAttribute("aria-hidden","true");
  document.body.classList.remove("locked");currentArticle=null;
  if(lastFocus&&lastFocus.focus)lastFocus.focus();
  if(!pop){try{history.pushState({},"",location.pathname+location.search);}catch(e){}}
}
function copyText(text,msg){const done=()=>toast(msg||"کپی شد.");
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(done).catch(()=>fallbackCopy(text,done));}
  else fallbackCopy(text,done);}
function fallbackCopy(text,done){const ta=document.createElement("textarea");ta.value=text;ta.style.position="fixed";ta.style.opacity="0";document.body.appendChild(ta);ta.select();
  try{document.execCommand("copy");done();}catch(e){toast("کپی ممکن نشد؛ متن را دستی انتخاب کنید.",{color:"var(--danger)"});}ta.remove();}
function articlePlainText(a){return faNum(a.title)+"\n\n"+faNum(a.lede||"")+"\n\n"+(a.body||[]).map(b=>b.t==="q"?`«${faNum(b.x)}» — ${faNum(b.by||"")}`:faNum(b.x)).join("\n\n")+"\n\nمنبع: "+(a.src?a.src.name+" — "+(a.src.orig||"")+"\n"+a.src.url:"");}
function articleLink(id){return location.origin+location.pathname+location.search+"#m-"+id;}
function exportArchive(){
  const payload={site:"کانه‌نگار",generated:new Date().toISOString(),articles:ARTICLES};
  const blob=new Blob([JSON.stringify(payload,null,2)],{type:"application/json;charset=utf-8"});
  const url=URL.createObjectURL(blob);const link=document.createElement("a");link.href=url;link.download="kanenegar-archive.json";document.body.appendChild(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1500);toast("آرشیو کامل مقالات (JSON) دانلود شد.");
}

/* ================= PARTICLES ================= */
function initDust(){
  const cv=$("#dust");if(!cv)return;const ctx=cv.getContext("2d");if(!ctx)return;
  const reduced=window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let w=0,h=0,dpr=1,parts=[],raf=0,running=false;
  function resize(){const rect=cv.parentElement.getBoundingClientRect();dpr=Math.min(window.devicePixelRatio||1,2);
    w=Math.max(1,rect.width);h=Math.max(1,rect.height);cv.width=w*dpr;cv.height=h*dpr;cv.style.width=w+"px";cv.style.height=h+"px";ctx.setTransform(dpr,0,0,dpr,0,0);
    const n=Math.min(80,Math.round(w*h/16000));parts=[];
    for(let i=0;i<n;i++){parts.push({x:Math.random()*w,y:Math.random()*h,r:Math.random()*1.8+0.4,vx:(Math.random()-0.5)*0.18,vy:-Math.random()*0.22-0.04,a:Math.random()*0.5+0.15,tw:Math.random()*Math.PI*2});}}
  function frame(){if(!running)return;ctx.clearRect(0,0,w,h);
    for(const p of parts){p.x+=p.vx;p.y+=p.vy;p.tw+=0.02;if(p.y<-4){p.y=h+4;p.x=Math.random()*w;}if(p.x<-4)p.x=w+4;if(p.x>w+4)p.x=-4;
      const al=p.a*(0.6+0.4*Math.sin(p.tw));ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=`rgba(242,179,61,${al.toFixed(3)})`;ctx.fill();}
    raf=requestAnimationFrame(frame);}
  function start(){if(running||reduced)return;running=true;raf=requestAnimationFrame(frame);}
  function stop(){running=false;cancelAnimationFrame(raf);}
  resize();
  if(reduced){ctx.clearRect(0,0,w,h);for(const p of parts){ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=`rgba(242,179,61,${p.a})`;ctx.fill();}}
  else start();
  let rt;window.addEventListener("resize",()=>{clearTimeout(rt);rt=setTimeout(()=>{resize();},180);});
  document.addEventListener("visibilitychange",()=>{if(document.hidden)stop();else start();});
}

/* ================= SCROLL / NAV / REVEAL ================= */
function initScroll(){
  const prog=$("#scrollProgress"),fab=$("#backTop");
  function onScroll(){const st=window.scrollY||document.documentElement.scrollTop;const max=document.documentElement.scrollHeight-window.innerHeight;
    prog.style.width=(max>0?(st/max*100):0)+"%";fab.classList.toggle("show",st>620);}
  window.addEventListener("scroll",onScroll,{passive:true});onScroll();
  fab.addEventListener("click",()=>window.scrollTo({top:0,behavior:"smooth"}));
  const secs=["hero","feed","market","about","newsletter"].map(id=>document.getElementById(id)).filter(Boolean);
  const navObs=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){const id=e.target.id==="hero"?"top":e.target.id;
    $$("[data-nav]").forEach(l=>l.classList.toggle("active",l.dataset.nav===id));}});},{rootMargin:"-45% 0px -50% 0px",threshold:0});
  secs.forEach(s=>navObs.observe(s));
  const ro=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("in");ro.unobserve(e.target);}});},{threshold:0.12});
  $$(".reveal").forEach(el=>ro.observe(el));
  const co=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){animateCounters();co.disconnect();}});},{threshold:0.3});
  const hs=$("#heroStats");if(hs)co.observe(hs);
}
function animateCounters(){
  $$("#heroStats b[data-count]").forEach(el=>{const target=+el.dataset.count;const dur=1100;const t0=performance.now();
    function step(t){const k=Math.min(1,(t-t0)/dur);const e=1-Math.pow(1-k,3);el.textContent=faNum(Math.round(target*e));if(k<1)requestAnimationFrame(step);}
    requestAnimationFrame(step);});
}

/* ================= EVENTS / INIT ================= */
function init(){
  renderHero();renderTicker();renderChips();renderFeed();renderSources();renderMarket();
  initDust();initScroll();updateSavedUI();
  document.addEventListener("click",e=>{
    const save=e.target.closest(".save-btn");if(save){e.stopPropagation();toggleSave(save.dataset.id);return;}
    const open=e.target.closest("[data-open]");if(open&&open.dataset.open){openArticle(open.dataset.open);return;}
    const card=e.target.closest(".card");if(card){openArticle(card.dataset.id);return;}
    if(e.target.closest("[data-close]")){closeReader();return;}
  });
  document.addEventListener("keydown",e=>{
    if((e.key==="Enter"||e.key===" ")&&e.target.matches(".card,.side-card,.rel-card")){e.preventDefault();openArticle(e.target.dataset.id||e.target.dataset.open);return;}
    if(e.key==="Escape"){closeReader();$("#mobileNav").classList.remove("open");$("#menuToggle").setAttribute("aria-expanded","false");return;}
    if(e.key==="/"&&!/input|textarea|select/i.test(document.activeElement.tagName)){e.preventDefault();$("#searchInput").focus();$("#feed").scrollIntoView({behavior:"smooth"});}
  });
  let st;
  $("#searchInput").addEventListener("input",e=>{clearTimeout(st);st=setTimeout(()=>{state.q=e.target.value;renderFeed();},130);});
  $("#sortSelect").addEventListener("change",e=>{state.sort=e.target.value;renderFeed();});
  $("#savedToggle").addEventListener("click",()=>{state.savedOnly=!state.savedOnly;$("#savedToggle").classList.toggle("on",state.savedOnly);$("#savedToggle").setAttribute("aria-pressed",state.savedOnly);renderFeed();});
  $("#gridBtn").addEventListener("click",()=>{state.layout="grid";$("#gridBtn").classList.add("on");$("#listBtn").classList.remove("on");renderFeed();});
  $("#listBtn").addEventListener("click",()=>{state.layout="list";$("#listBtn").classList.add("on");$("#gridBtn").classList.remove("on");renderFeed();});
  $("#catChips").addEventListener("click",e=>{const c=e.target.closest(".cat-chip");if(!c)return;state.cat=c.dataset.cat;renderChips();renderFeed();});
  $("#searchJump").addEventListener("click",()=>{$("#feed").scrollIntoView({behavior:"smooth"});setTimeout(()=>$("#searchInput").focus(),450);});
  $("#savedJump").addEventListener("click",()=>{state.savedOnly=true;$("#savedToggle").classList.add("on");$("#savedToggle").setAttribute("aria-pressed","true");renderFeed();$("#feed").scrollIntoView({behavior:"smooth"});});
  $("#exportBtn").addEventListener("click",exportArchive);
  $("#footExport").addEventListener("click",exportArchive);
  $("#footSaved").addEventListener("click",()=>{$("#savedJump").click();});
  $("#footSources").addEventListener("click",()=>$("#about").scrollIntoView({behavior:"smooth"}));
  $("#rSave").addEventListener("click",()=>{if(currentArticle)toggleSave(currentArticle.id);});
  $("#rCopyLink").addEventListener("click",()=>{if(currentArticle)copyText(articleLink(currentArticle.id),"پیوند مقاله کپی شد.");});
  $("#rCopyText").addEventListener("click",()=>{if(currentArticle)copyText(articlePlainText(currentArticle),"متن کامل مقاله کپی شد.");});
  $("#rShare").addEventListener("click",async()=>{if(!currentArticle)return;
    const data={title:faNum(currentArticle.title),text:faNum(currentArticle.lede||""),url:articleLink(currentArticle.id)};
    if(navigator.share){try{await navigator.share(data);}catch(e){}}else copyText(data.url,"پیوند مقاله برای هم‌رسانی کپی شد.");});
  $("#readerScroll").addEventListener("scroll",()=>{const el=$("#readerScroll");const max=el.scrollHeight-el.clientHeight;
    $("#readerBar").style.width=(max>0?(el.scrollTop/max*100):0)+"%";},{passive:true});
  $("#reader").addEventListener("keydown",e=>{if(e.key!=="Tab")return;
    const f=$$("#reader button, #reader a[href], #reader [tabindex]:not([tabindex='-1'])").filter(el=>!el.disabled&&el.offsetParent!==null);
    if(!f.length)return;const first=f[0],last=f[f.length-1];
    if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
    else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
  $("#menuToggle").addEventListener("click",()=>{const n=$("#mobileNav");const open=n.classList.toggle("open");$("#menuToggle").setAttribute("aria-expanded",open);});
  $$("#mobileNav a").forEach(a=>a.addEventListener("click",()=>{$("#mobileNav").classList.remove("open");$("#menuToggle").setAttribute("aria-expanded","false");}));
  $("#nlForm").addEventListener("submit",e=>{e.preventDefault();
    const email=$("#nlEmail").value.trim();const msg=$("#nlMsg");
    const ok=/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
    if(!ok){msg.className="nl-msg err";msg.textContent="لطفاً یک ایمیل معتبر وارد کنید.";return;}
    try{const list=JSON.parse(localStorage.getItem("kanenegar-newsletter")||"[]");if(!list.includes(email))list.push(email);localStorage.setItem("kanenegar-newsletter",JSON.stringify(list));}catch(err){}
    msg.className="nl-msg ok";msg.textContent="✓ ایمیل شما ثبت شد! در این نسخهٔ مستقل، اشتراک به‌صورت محلی در مرورگر شما نگهداری می‌شود.";
    $("#nlEmail").value="";toast("ایمیل شما در خبرنامهٔ کانه‌نگار ثبت شد.");});
  function handleHash(){const h=location.hash;if(h.startsWith("#m-")){const id=h.slice(3);if(byId[id])openArticle(id,false);}}
  window.addEventListener("hashchange",()=>{const h=location.hash;if(h.startsWith("#m-"))handleHash();else closeReader(true);});
  window.addEventListener("popstate",()=>{const h=location.hash;if(h.startsWith("#m-"))handleHash();else closeReader(true);});
  handleHash();
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
