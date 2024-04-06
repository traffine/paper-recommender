import json
import unicodedata

with open("data/papers/j-stage.json", "r", encoding="utf-8") as file:
    data = json.load(file)

keywords = list(set(keyword for d in data for keyword in d["keywords"]))

file_name = "data/dictionary/userdic.csv"
with open(file_name, "w", encoding="utf-8") as file:
    for keyword in keywords:
        file.write(
            '"'
            + unicodedata.normalize("NFKC", keyword.lower())
            + '"'
            + ",,,10,名詞,一般,*,*,*,*,,,,"
            + "\n"
        )
