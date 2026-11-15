/* صفحه‌بندی سبک: ۴۰ خبر اول + دکمهٔ قدیمی‌تر | ۵ منبع اول + دکمهٔ بقیه */
(function(){
  var FEED_STEP = 40;
  var SRC_LIMIT = 5;
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
