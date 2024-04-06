import json
import unicodedata
from functools import lru_cache


@lru_cache()
def get_kw_data():
    with open("data/papers/j-stage.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    KEYWORDS = list(set(keyword for d in data for keyword in d["keywords"]))
    KEYWORDS_NORMED = [
        unicodedata.normalize("NFKC", keyword.lower()) for keyword in KEYWORDS
    ]

    return (
        KEYWORDS,
        KEYWORDS_NORMED,
    )


KEYWORDS, KEYWORDS_NORMED = get_kw_data()
