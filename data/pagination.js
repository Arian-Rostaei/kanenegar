/* ۱) پاک‌سازی نمایشی: خبرهایی که تیترشان فارسی نیست یا بدنهٔ خالی دارند حذف می‌شوند
      (باقی‌ماندهٔ اجراهای قبل از خود-بازبینی). این کار قبل از رندر app.js انجام می‌شود. */
(function(){
  var A = window.ARTICLES_DATA;
  if (Array.isArray(A)) {
    for (var i = A.length - 1; i >= 0; i--) {
      var a = A[i] || {};
      var t = a.title || "";
      var fa = (t.match(/[\u0600-\u06FF]/g) || []).length;
      var la = (t.match(/[A-Za-z]/g) || []).length;
      var bodyOk = Array.isArray(a.body) && a.body.length > 0;
      if (fa === 0 || fa < la || !bodyOk) A.splice(i, 1);
    }
  }
})();

/* ۲) نمایش درست اعداد: توکن‌های ترکیبی مثل 3Q26 لاتین می‌مانند؛ اعداد خالص فارسی می‌شوند. */
window.faNum = function (v) {
  var s = String(v), out = "";
  for (var i = 0; i < s.length; i++) {
    var ch = s[i];
    if (ch >= "0" && ch <= "9") {
      var a = i, b = i;
      while (a > 0 && /[A-Za-z0-9]/.test(s[a - 1])) a--;
      while (b < s.length - 1 && /[A-Za-z0-9]/.test(s[b + 1])) b++;
      var token = s.slice(a, b + 1);
      out += /[A-Za-z]/.test(token) ? ch : "۰۱۲۴۵۶۷۸۹"[+ch];
    } else out += ch;
  }
  return out;
};

/* ۳) صفحه‌بندی: ۱۵ خبر اول + دکمهٔ قدیمی‌تر | ۳ منبع اول + دکمهٔ بقیه */
(function(){
  var FEED_STEP = 15;
  var SRC_LIMIT = 3;
  var feedLimit = FEED_STEP;
  var srcExpanded = false;

  function ensureBtn(anchor, id){
    var b = document.getElementById(id);
    if(!b){
      b = document.createElement("button");
      b.id = id;
      b.className = "btn btn-ghost";
      b.style.cssText = "margin:18px auto;display:block;";
      anchor.parentNode.insertBefore(b, anchor.nextSibling);
    }
    return b;
  }

  function applyFeed(){
    var grid = document.getElementById("articleGrid");
    if(!grid) return;
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".card"));
    var btn = ensureBtn(grid, "feedMore");
    if(!cards.length){ btn.style.display="none"; return; }
    cards.forEach(function(c,i){ c.style.display = (i < feedLimit) ? "" : "none"; });
    if(cards.length <= feedLimit){
      btn.style.display = "none";
    } else {
      btn.style.display = "block";
      btn.textContent = "دیدن اخبار قدیمی‌تر ↓ (" + (cards.length - feedLimit) + " خبر مانده)";
      btn.onclick = function(){ feedLimit += FEED_STEP; applyFeed(); };
    }
  }

  function applySources(){
    var list = document.getElementById("srcList");
    if(!list) return;
    var items = Array.prototype.slice.call(list.children);
    var btn = ensureBtn(list, "srcMore");
    if(items.length <= SRC_LIMIT){ btn.style.display="none"; }
    items.forEach(function(el,i){ el.style.display = (srcExpanded || i < SRC_LIMIT) ? "" : "none"; });
    if(items.length > SRC_LIMIT){
      btn.style.display = "block";
      btn.textContent = srcExpanded
        ? "نمایش کمتر ↑"
        : "دیدن بقیهٔ منابع ↓ (" + (items.length - SRC_LIMIT) + " منبع دیگر)";
      btn.onclick = function(){ srcExpanded = !srcExpanded; applySources(); };
    }
  }

  function hook(){
    var grid = document.getElementById("articleGrid");
    var list = document.getElementById("srcList");
    if(grid){
      new MutationObserver(function(){ feedLimit = FEED_STEP; applyFeed(); })
        .observe(grid, {childList:true});
    }
    if(list){
      new MutationObserver(function(){ applySources(); })
        .observe(list, {childList:true});
    }
    applyFeed();
    applySources();
  }

  if(document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", function(){ setTimeout(hook, 0); });
  } else {
    setTimeout(hook, 0);
  }
})();
