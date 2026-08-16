import os
TICKER_MAP = {
    "Disney": "DIS", "Marvel": "DIS", "Pixar": "DIS",
    "Warner": "WBD", "Warner Bros": "WBD", "HBO": "WBD", "DC": "WBD",
    "Universal": "CMCSA", "Comcast": "CMCSA", "DreamWorks": "CMCSA",
    "Paramount": "PARA", "Netflix": "NFLX",
    "Sony": "SONY", "Sony Pictures": "SONY",
    "Lionsgate": "LGF.A", "IMAX": "IMAX", "AMC": "AMC",
    "Runway": "ADBE", "Pika": "NVDA", "Adobe": "ADBE", "Nvidia": "NVDA",
}
RSS_FEEDS = [
    "https://variety.com/feed/",
    "https://deadline.com/feed/",
    "https://www.hollywoodreporter.com/feed/",
    "https://www.thewrap.com/feed/",
]
CARD_SIZE = (1080, 1920)
FONT_BOLD = "assets/fonts/Pretendard-Bold.otf"
FONT_REGULAR = "assets/fonts/Pretendard-Regular.otf"
OUTPUT_BASE = "output"
GDRIVE_BACKGROUND_ID = os.getenv("GDRIVE_FOLDER_ID_BACKGROUND") or os.getenv("GDRIVE_FOLDER_ID_Background") or ""
GDRIVE_OUTPUT_ID = os.getenv("GDRIVE_FOLDER_ID_OUTPUT") or os.getenv("GDRIVE_FOLDER_ID_Output") or ""
