/* نبض بازار — فقط فلزهایی که قیمتشون واقعاً به‌روز می‌شه.
   لایهٔ ۱: قیمت ساعتی که ایجنت سمت سرور ذخیره کرده (prices-live.js)
   لایهٔ ۲: قیمت لحظه‌ای مستقیم در مرورگر (gold-api)
   نمودار تاریخی: market-history.js (ساعتی توسط ایجنت) */
window.MARKET_DATA = [
 {fa:"طلا",en:"Gold",sym:"Au",price:0,unit:"دلار / اونس",chg:0,date:"",src:"—",c:"#F5C84C",note:"🟡 در حال دریافت قیمت…"},
 {fa:"نقره",en:"Silver",sym:"Ag",price:0,unit:"دلار / اونس",chg:0,date:"",src:"—",c:"#C9D3E0",note:"🟡 در حال دریافت قیمت…"},
 {fa:"پلاتین",en:"Platinum",sym:"Pt",price:0,unit:"دلار / اونس",chg:0,date:"",src:"—",c:"#2DD4BF",note:"🟡 در حال دریافت قیمت…"},
 {fa:"پالادیم",en:"Palladium",sym:"Pd",price:0,unit:"دلار / اونس",chg:0,date:"",src:"—",c:"#A78BFA",note:"🟡 در حال دریافت قیمت…"}
];
window.COPPER_POINTS = [];

window.addEventListener("load", function () {
  /* پاک‌سازی: کارت خالی مس و متن‌های قدیمی پنهان/اصلاح می‌شن */
  var cc = document.querySelector(".chart-card");
  if (cc && !(window.COPPER_POINTS || []).length) cc.style.display = "none";
  var mn = document.querySelector(".market-note span");
  if (mn) mn.textContent = "طلا، نقره، پلاتین و پالادیم به‌صورت ساعتی (توسط ایجنت) و در صورت اتصال مرورگر به‌صورت لحظه‌ای به‌روز می‌شوند و نمودار تاریخی دارند. فلزهایی که منبع قیمت زندهٔ رایگان ندارند حذف شده‌اند تا هیچ عدد کهنه‌ای به‌جای قیمت روز نمایش داده نشود.";
  var ss = document.querySelector(".market .sec-sub");
  if (ss) ss.textContent = "فقط فلزاتی که قیمت‌شان به‌طور خودکار به‌روز می‌شود. روی هر کارت کلیک کن تا نمودار روزانه/ماهانه/سالانه و قیمت‌های قبلی باز شود.";

  function findCard(sym){
    var all = Array.prototype.slice.call(document.querySelectorAll(".metal"));
    for (var i=0;i<all.length;i++){
      var s = all[i].querySelector(".metal-sym");
      if (s && s.textContent.trim() === sym) return all[i];
    }
    return null;
  }
  function setPrice(sym, price, badgeText, badgeClass, noteHTML){
    var c = findCard(sym); if(!c) return;
    var p = c.querySelector(".metal-price");
    if(p) p.textContent = Number(price).toLocaleString("fa-IR",{maximumFractionDigits:2});
    var ch = c.querySelector(".chg");
    if(ch){ ch.className = "chg " + badgeClass; ch.textContent = badgeText; }
    var n = c.querySelector(".metal-note");
    if(n && noteHTML) n.innerHTML = noteHTML;
  }

  /* لایهٔ ۱: قیمت ساعتیِ ذخیره‌شده توسط ایجنت */
  var hs = document.createElement("script");
  hs.src = "data/prices-live.js";
  hs.onload = function(){
    var lp = window.LIVE_PRICES || {};
    Object.keys(lp).forEach(function(sym){
      setPrice(sym, lp[sym].price, "🟡 ساعتی", "up",
        "🟡 به‌روزرسانی خودکار · " + lp[sym].ts + "<br><span style='opacity:.7'>منبع: " + lp[sym].src + "</span>");
    });
  };
  document.head.appendChild(hs);

  /* لایهٔ ۲: تلاش برای قیمت لحظه‌ای مستقیم */
  var LIVE = {Au:"XAU", Ag:"XAG", Pt:"XPT", Pd:"XPD"};
  Object.keys(LIVE).forEach(function(sym){
    fetch("https://api.gold-api.com/price/" + LIVE[sym])
      .then(function(r){ if(!r.ok) throw new Error("http "+r.status); return r.json(); })
      .then(function(j){
        if(!j || typeof j.price !== "number") return;
        setPrice(sym, j.price, "● زنده", "up",
          "🟢 لحظه‌ای (همین حالا از بازار)<br><span style='opacity:.7'>منبع: gold-api.com</span>");
      })
      .catch(function(){});
  });

  /* ===== مودال نمودار تاریخی ===== */
  var modal = document.getElementById("mmodal");
  if(!modal) return;
  var body = document.getElementById("mmBody");
  var titleEl = document.getElementById("mmTitle");
  var current = null, currentRange = 30;
  function fa(n){ return Number(n).toLocaleString("fa-IR",{maximumFractionDigits:2}); }
  function sliceByRange(hist, days){
    var n = Math.min(days, hist.t.length);
    return { t: hist.t.slice(hist.t.length-n), p: hist.p.slice(hist.p.length-n) };
  }
  function drawChart(hist, unit){
    var s = sliceByRange(hist, currentRange);
    if(!s.t.length){ body.innerHTML = '<p style="color:var(--muted)">داده‌ای برای نمایش نیست.</p>'; return; }
    var W=920,H=320,padL=70,padR=20,padT=20,padB=44;
    var min=Math.min.apply(null,s.p), max=Math.max.apply(null,s.p);
    var span=(max-min)||1; min-=span*0.08; max+=span*0.08;
    var X=function(i){return padL + i*(W-padL-padR)/Math.max(1,s.p.length-1);};
    var Y=function(v){return padT + (max-v)/(max-min)*(H-padT-padB);};
    var path=s.p.map(function(v,i){return (i?"L":"M")+X(i).toFixed(1)+" "+Y(v).toFixed(1);}).join(" ");
    var area=path+" L "+X(s.p.length-1).toFixed(1)+" "+(H-padB)+" L "+X(0).toFixed(1)+" "+(H-padB)+" Z";
    var grid="";
    for(var g=0; g<=4; g++){
      var v=min+(max-min)*g/4, y=Y(v);
      grid+='<line x1="'+padL+'" y1="'+y+'" x2="'+(W-padR)+'" y2="'+y+'" stroke="#fff" stroke-opacity=".07"/>'+
            '<text x="'+(padL-8)+'" y="'+(y+4)+'" text-anchor="end" fill="#69738A" font-size="11">'+fa(v)+'</text>';
    }
    var last=s.p[s.p.length-1], first=s.p[0];
    var chg=(last-first)/first*100;
    var svg='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto">'+
      '<defs><linearGradient id="mg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E08D4F" stop-opacity=".35"/><stop offset="1" stop-color="#E08D4F" stop-opacity="0"/></linearGradient></defs>'+
      grid+'<path d="'+area+'" fill="url(#mg)"/><path d="'+path+'" fill="none" stroke="#E08D4F" stroke-width="3" stroke-linecap="round"/>'+
      '<text x="'+X(0)+'" y="'+(H-14)+'" fill="#9AA4B4" font-size="11">'+s.t[0]+'</text>'+
      '<text x="'+X(s.t.length-1)+'" y="'+(H-14)+'" text-anchor="end" fill="#9AA4B4" font-size="11">'+s.t[s.t.length-1]+'</text>'+
      '</svg>';
    var stats='<div class="mmodal-stats">'+
      '<div class="mstat"><b>'+fa(first)+'</b><span>اول بازه</span></div>'+
      '<div class="mstat"><b>'+fa(last)+'</b><span>آخرین</span></div>'+
      '<div class="mstat"><b>'+fa(Math.min.apply(null,s.p))+'</b><span>کف بازه</span></div>'+
      '<div class="mstat"><b style="color:'+(chg>=0?"var(--ok)":"var(--danger)")+'">'+(chg>=0?"+":"")+fa(chg)+'٪</b><span>تغییر بازه</span></div>'+
      '</div>';
    var rows="";
    for(var r=s.t.length-1; r>=Math.max(0,s.t.length-10); r--){
      rows+='<tr><td>'+s.t[r]+'</td><td class="lat">'+fa(s.p[r])+'</td><td>'+unit+'</td></tr>';
    }
    var table='<table class="mtable"><thead><tr><th>تاریخ</th><th>قیمت</th><th>واحد</th></tr></thead><tbody>'+rows+'</tbody></table>';
    body.innerHTML = stats + svg + '<h4 style="margin-top:18px;font-size:.9rem">قیمت‌های قبلی (۱۰ روز اخیر)</h4>' + table;
  }
  function openModal(meta){
    current = meta; currentRange = 30;
    titleEl.textContent = "نمودار قیمت " + meta.fa + " (" + meta.en + ")";
    modal.classList.add("open"); modal.setAttribute("aria-hidden","false");
    document.body.classList.add("locked");
    var hist = (window.MARKET_HISTORY||{})[meta.sym];
    if(!hist || !hist.t || !hist.t.length){
      body.innerHTML = '<div style="text-align:center;padding:40px 10px;color:var(--muted)">'+
        '<p style="font-size:1rem;margin-bottom:8px">برای <b>'+meta.fa+'</b> هنوز دادهٔ تاریخی ذخیره نشده.</p>'+
        '<p style="font-size:.8rem">قیمت فعلی: <b class="lat">'+fa(meta.price)+'</b> '+meta.unit+' — با هر اجرای ساعتی، تاریخچه بزرگ‌تر می‌شود.</p></div>';
      return;
    }
    drawChart(hist, meta.unit);
  }
  function closeModal(){
    modal.classList.remove("open"); modal.setAttribute("aria-hidden","true");
    document.body.classList.remove("locked");
  }
  document.getElementById("mmRanges").addEventListener("click", function(e){
    var b=e.target.closest("button"); if(!b||!current) return;
    currentRange=+b.dataset.range;
    Array.prototype.forEach.call(this.children,function(x){x.classList.remove("on");});
    b.classList.add("on");
    var hist=(window.MARKET_HISTORY||{})[current.sym];
    if(hist) drawChart(hist, current.unit);
  });
  modal.addEventListener("click", function(e){ if(e.target.closest("[data-mclose]")) closeModal(); });
  document.addEventListener("keydown", function(e){ if(e.key==="Escape" && modal.classList.contains("open")) closeModal(); });
  document.getElementById("marketGrid").addEventListener("click", function(e){
    var card=e.target.closest(".metal"); if(!card) return;
    var symEl=card.querySelector(".metal-sym"); if(!symEl) return;
    var sym=symEl.textContent.trim(); var meta=null;
    (window.MARKET_DATA||[]).forEach(function(m){ if(m.sym===sym) meta=m; });
    if(meta) openModal(meta);
  });
});
