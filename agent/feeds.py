# منابع خبری تحت رصد. نوع gnews یعنی موتور جمع‌کنندهٔ گوگل که خودش
# صدها رسانه رو پوشش می‌ده و نام منبع واقعی از تیتر استخراج می‌شه.
FEEDS = [
    {"name": "MINING.COM", "type": "rss",
     "url": "https://www.mining.com/feed/"},
    {"name": "Google News", "type": "gnews",
     "url": "https://news.google.com/rss/search?q=mining+OR+mine+OR+%22iron+ore%22+OR+%22open-pit%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News", "type": "gnews",
     "url": "https://news.google.com/rss/search?q=copper+OR+nickel+OR+lithium+OR+cobalt+OR+%22rare+earth%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News", "type": "gnews",
     "url": "https://news.google.com/rss/search?q=gold+price+OR+silver+price+OR+%22precious+metals%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "BBC Business", "type": "rss",
     "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {"name": "The Guardian", "type": "rss",
     "url": "https://www.theguardian.com/uk/business/rss"},
    {"name": "Al Jazeera", "type": "rss",
     "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "CNBC", "type": "rss",
     "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258"},
]

# فیلتر کلیدواژه‌ای: فقط اخبار مرتبط با زمین‌شناسی/معدن/فلزات نگه داشته می‌شوند.
KEYWORDS = [
    "copper", "gold", "silver", "lithium", "iron ore", "nickel", "cobalt", "zinc",
    "aluminum", "aluminium", "uranium", "rare earth", "rare-earth", "critical mineral",
    "battery metal", "graphite", "manganese", "tungsten", "tin", "palladium", "platinum",
    "mine", "mining", "miner", "deposit", "ore", "exploration", "drill", "geolog",
    "concentrate", "smelter", "refinery", "tailings", "open-pit", "underground",
    "LME", "BHP", "Rio Tinto", "Glencore", "Freeport", "Codelco", "Vale",
    "First Quantum", "Teck", "Newmont", "Barrick", "Albemarle", "SQM",
    "Grasberg", "Kamoa", "Simandou", "Escondida", "Cobre Panama", "Thacker Pass",
]
