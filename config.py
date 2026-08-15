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
]
CARD_SIZE = (1080, 1920)
FONT_BOLD = "assets/fonts/Pretendard-Bold.otf"
FONT_REGULAR = "assets/fonts/Pretendard-Regular.otf"
OUTPUT_BASE = "output"
# Drive IDs - .env에서 덮어쓸 수 있음
GDRIVE_BACKGROUND_ID = os.getenv("GDRIVE_FOLDER_ID_Background", "1k1E6QdvCn4aQoXOd0tyEq0-XGZCaQwT_")
GDRIVE_OUTPUT_ID = os.getenv("GDRIVE_FOLDER_ID_Output", "1OOy2sqj7NKUdM2oOrP6PIpS8PE7YW161")
