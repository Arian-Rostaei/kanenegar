# منابع خبری تحت رصد — خوراک‌های آر‌اس‌اس. هر فید خراب به‌تنهایی نادیده گرفته می‌شود.
# برای افزودن منبع جدید کافی است یک آیتم به این فهرست اضافه کنید.
FEEDS = [
    {"name": "MINING.COM",              "url": "https://www.mining.com/feed/",                        "lang": "en"},
    {"name": "MINING.COM - Markets",    "url": "https://www.mining.com/category/markets/feed/",       "lang": "en"},
    {"name": "Mining Weekly",           "url": "https://www.miningweekly.com/page/latest-news-rss",   "lang": "en"},
    {"name": "Kitco News",              "url": "https://www.kitco.com/rss/news.xml",                  "lang": "en"},
    {"name": "Northern Miner",          "url": "https://www.northernminer.com/feed/",                 "lang": "en"},
    {"name": "USGS Newsroom",           "url": "https://www.usgs.gov/news/rss.xml",                   "lang": "en"},
    {"name": "S&P Global - Metals",     "url": "https://www.spglobal.com/market-intelligence/en/news-insights/research.rss", "lang": "en"},
]

# فیلتر کلیدواژه‌ای: فقط اخبار مرتبط با زمین‌شناسی/معدن/فلزات نگه داشته می‌شوند.
# حداقل یک کلیدواژه باید در عنوان یا خلاصه دیده شود.
KEYWORDS = [
    # فلزات
    "copper", "gold", "silver", "lithium", "iron ore", "nickel", "cobalt", "zinc", "lead",
    "aluminum", "aluminium", "uranium", "rare earth", "rare-earth", "critical mineral",
    "battery metal", "graphite", "manganese", "tungsten", "tin", "palladium", "platinum",
    # معدن و زمین‌شناسی
    "mine", "mining", "miner", "deposit", "ore", "exploration", "drill", "geolog",
    "concentrate", "smelter", "refinery", "tailings", "open-pit", "underground",
    # بازار و شرکت‌های بزرگ
    "LME", "BHP", "Rio Tinto", "Glencore", "Freeport", "Codelco", "Vale", "Anglo American",
    "First Quantum", "Teck", "Newmont", "Barrick", "Albemarle", "SQM", "Pilbara",
    # پروژه‌های شاخص
    "Grasberg", "Kamoa", "Simandou", "Escondida", "Cobre Panama", "Thacker Pass", "Reko Diq",
]
