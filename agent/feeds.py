# منابع خبری: جهانی + آسیایی/آسیای شرقی. نوع gnews یعنی موتور گوگل که
# نام رسانهٔ واقعی از انتهای تیتر استخراج می‌شود.
FEEDS = [
    {"name": "MINING.COM", "type": "rss", "url": "https://www.mining.com/feed/"},
    {"name": "Google News", "type": "gnews", "url": "https://news.google.com/rss/search?q=mining+OR+mine+OR+%22iron+ore%22+OR+%22open-pit%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News", "type": "gnews", "url": "https://news.google.com/rss/search?q=copper+OR+nickel+OR+lithium+OR+cobalt+OR+%22rare+earth%22&hl=en-US&gl=US&ceid=US:en"},
    {"name": "Google News", "type": "gnews", "url": "https://news.google.com/rss/search?q=gold+price+OR+silver+price+OR+%22precious+metals%22&hl=en-US&gl=US&ceid=US:en"},
    # --- آسیا و آسیای شرقی ---
    {"name": "Google News", "type": "gnews", "url": "https://news.google.com/rss/search?q=(mining+OR+metals+OR+copper+OR+gold)+when:2d&hl=en-SG&gl=SG&ceid=SG:en"},
    {"name": "Google News", "type": "gnews", "url": "https://news.google.com/rss/search?q=(mining+OR+%22rare+earth%22+OR+lithium)+when:2d&hl=en-AU&gl=AU&ceid=AU:en"},
    {"name": "Nikkei Asia", "type": "rss", "url": "https://asia.nikkei.com/rss/feed/nar"},
    {"name": "SCMP", "type": "rss", "url": "https://www.scmp.com/rss/2/feed"},
    {"name": "Yonhap", "type": "rss", "url": "https://en.yna.co.kr/RSS/news.xml"},
    {"name": "China Daily", "type": "rss", "url": "http://www.chinadaily.com.cn/rss/business_rss.xml"},
    {"name": "Asia Times", "type": "rss", "url": "https://asiatimes.com/feed/"},
    # --- جهانی ---
    {"name": "BBC Business", "type": "rss", "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {"name": "The Guardian", "type": "rss", "url": "https://www.theguardian.com/uk/business/rss"},
    {"name": "Al Jazeera", "type": "rss", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "CNBC", "type": "rss", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258"},
]

KEYWORDS = [
    "copper", "gold", "silver", "lithium", "iron ore", "nickel", "cobalt", "zinc",
    "aluminum", "aluminium", "uranium", "rare earth", "rare-earth", "critical mineral",
    "battery metal", "graphite", "manganese", "tungsten", "tin", "palladium", "platinum",
    "mine", "mining", "miner", "deposit", "ore", "exploration", "drill", "geolog",
    "concentrate", "smelter", "refinery", "tailings", "open-pit", "underground",
    "LME", "BHP", "Rio Tinto", "Glencore", "Freeport", "Codelco", "Vale",
    "First Quantum", "Teck", "Newmont", "Barrick", "Albemarle", "SQM",
    "Grasberg", "Kamoa", "Simandou", "Escondida", "Cobre Panama", "Thacker Pass",
    "China", "Chinese", "Japan", "Japanese", "Korea", "Indonesia", "India",
]
