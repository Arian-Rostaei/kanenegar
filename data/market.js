/* نبض بازار — به ترتیب محبوبیت: طلا، نقره، سپس بقیه. فقط فلزهایی که قیمت دارند. */
window.MARKET_DATA = [
 {fa:"طلا",en:"Gold",sym:"Au",price:3882,unit:"دلار / اونس",chg:0,date:"2026-11-14",src:"gold-api",c:"#F5C84C",note:"🟢 زنده (به‌روزرسانی خودکار)"},
 {fa:"نقره",en:"Silver",sym:"Ag",price:50.07,unit:"دلار / اونس",chg:0,date:"2026-11-14",src:"gold-api",c:"#C9D3E0",note:"🟢 زنده (به‌روزرسانی خودکار)"},
 {fa:"مس",en:"Copper",sym:"Cu",price:13712,unit:"دلار / تن",chg:-1.18,date:"2026-11-12",src:"LME / Westmetall",c:"#E08D4F",note:"🟡 مرجع روزانه — سقف 2026: 14٬875"},
 {fa:"پلاتین",en:"Platinum",sym:"Pt",price:1520,unit:"دلار / اونس",chg:0,date:"2026-11-14",src:"gold-api",c:"#2DD4BF",note:"🟢 زنده (به‌روزرسانی خودکار)"},
 {fa:"پالادیم",en:"Palladium",sym:"Pd",price:991,unit:"دلار / اونس",chg:0,date:"2026-11-14",src:"gold-api",c:"#A78BFA",note:"🟢 زنده (به‌روزرسانی خودکار)"},
 {fa:"آلومینیوم",en:"Aluminum",sym:"Al",price:3135,unit:"دلار / تن",chg:0,date:"2026-11-14",src:"ارزیابی مرجع",c:"#57A6FF",note:"🟡 مرجع"},
 {fa:"نیکل",en:"Nickel",sym:"Ni",price:15000,unit:"دلار / تن",chg:0,date:"2026-11-14",src:"ارزیابی مرجع",c:"#3ECF8E",note:"🟡 مرجع"},
 {fa:"لیتیوم",en:"Lithium Carbonate",sym:"Li",price:13.9,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-04",src:"بازار چین",c:"#3ECF8E",note:"🟡 مرجع"},
 {fa:"سنگ‌آهن",en:"Iron Ore",sym:"Fe",price:90,unit:"دلار / تن",chg:0,date:"2026-11-14",src:"ارزیابی مرجع",c:"#57A6FF",note:"🟡 مرجع"},
 {fa:"روی",en:"Zinc",sym:"Zn",price:3000,unit:"دلار / تن",chg:0,date:"2026-11-14",src:"ارزیابی مرجع",c:"#57A6FF",note:"🟡 مرجع"},
 {fa:"قلع",en:"Tin",sym:"Sn",price:30000,unit:"دلار / تن",chg:0,date:"2026-11-14",src:"ارزیابی مرجع",c:"#57A6FF",note:"🟡 مرجع"},
 {fa:"کبالت",en:"Cobalt",sym:"Co",price:33,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع",c:"#3ECF8E",note:"🟡 مرجع"},
 {fa:"اورانیوم",en:"Uranium",sym:"U",price:85,unit:"دلار / پوند",chg:0,date:"2026-11-14",src:"ارزیابی مرجع",c:"#3ECF8E",note:"🟡 مرجع"},
 {fa:"منگنز",en:"Manganese",sym:"Mn",price:2.2,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#2DD4BF",note:"🟡 تخمینی"},
 {fa:"نئودیمیم-پرازئودیمیم",en:"NdPr",sym:"Nd",price:110,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-11",src:"کف قرارداد USA Rare Earth",c:"#A78BFA",note:"🟡 قراردادی"},
 {fa:"دیسپروسیم",en:"Dysprosium",sym:"Dy",price:575,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-11",src:"کف قرارداد USA Rare Earth",c:"#A78BFA",note:"🟡 قراردادی"},
 {fa:"تربیوم",en:"Terbium",sym:"Tb",price:2050,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-11",src:"کف قرارداد USA Rare Earth",c:"#A78BFA",note:"🟡 قراردادی"},
 {fa:"تنگستن",en:"Tungsten",sym:"W",price:45,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#2DD4BF",note:"🟡 تخمینی"},
 {fa:"مولیبدن",en:"Molybdenum",sym:"Mo",price:50,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#2DD4BF",note:"🟡 تخمینی"},
 {fa:"تیتانیوم",en:"Titanium",sym:"Ti",price:8,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#57A6FF",note:"🟡 تخمینی"},
 {fa:"منیزیم",en:"Magnesium",sym:"Mg",price:2.4,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#57A6FF",note:"🟡 تخمینی"},
 {fa:"ایندیم",en:"Indium",sym:"In",price:250,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#2DD4BF",note:"🟡 تخمینی"},
 {fa:"گالیم",en:"Gallium",sym:"Ga",price:300,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#2DD4BF",note:"🟡 تخمینی"},
 {fa:"ژرمانیم",en:"Germanium",sym:"Ge",price:1500,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#2DD4BF",note:"🟡 تخمینی"},
 {fa:"آنتیموان",en:"Antimony",sym:"Sb",price:15,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#2DD4BF",note:"🟡 تخمینی"},
 {fa:"رودیم",en:"Rhodium",sym:"Rh",price:150000,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#F5C84C",note:"🟡 تخمینی"},
 {fa:"ایریدیم",en:"Iridium",sym:"Ir",price:160000,unit:"دلار / کیلوگرم",chg:0,date:"2026-11-14",src:"ارزیابی مرجع (تخمینی)",c:"#F5C84C",note:"🟡 تخمینی"}
];
window.COPPER_POINTS = [
 {d:"2026-01-29",v:14527.5,label:"رکورد ژانویه",src:"Benchmark"},
 {d:"2026-08-14",v:14100,label:"بالای 14٬100",src:"MINING.COM"},
 {d:"2026-09-10",v:14875,label:"سقف 2026",src:"Fastmarkets"},
 {d:"2026-11-12",v:13712,label:"آخرین ثبت",src:"Westmetall"}
];
/* به‌روزرسانی زندهٔ طلا، نقره، پلاتین و پالادیم در مرورگر */
window.addEventListener("load", function () {
  var LIVE = {Au:"XAU", Ag:"XAG", Pt:"XPT", Pd:"XPD"};
  function findCard(sym){
    var all = Array.prototype.slice.call(document.querySelectorAll(".metal"));
    for (var i=0;i<all.length;i++){
      var s = all[i].querySelector(".metal-sym");
      if (s && s.textContent.trim() === sym) return all[i];
    }
    return null;
  }
  Object.keys(LIVE).forEach(function(sym){
    fetch("https://api.gold-api.com/price/" + LIVE[sym])
      .then(function(r){ return r.json(); })
      .then(function(j){
        if(!j || typeof j.price !== "number") return;
        var c = findCard(sym); if(!c) return;
        var p = c.querySelector(".metal-price");
        if(p) p.textContent = j.price.toLocaleString("fa-IR",{maximumFractionDigits:2});
        var u = c.querySelector(".metal-unit");
        if(u){ var base = u.textContent.split("·")[0]; u.textContent = base + "· لحظه‌ای"; }
        var ch = c.querySelector(".chg");
        if(ch){ ch.className="chg up"; ch.textContent="● زنده"; }
      })
      .catch(function(){});
  });
});
