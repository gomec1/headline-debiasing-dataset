import json
import random
from pathlib import Path


INPUT_FILE = Path("gdelt_us_media_headlines_by_outlet_100_each.json")


def ask_sample_size(total_records):
    while True:
        raw_value = input(f"Wie viele News moechtest du zufaellig auswaehlen? (max. {total_records}): ").strip()

        try:
            sample_size = int(raw_value)
        except ValueError:
            print("Bitte gib eine ganze Zahl ein, z.B. 50.")
            continue

        if sample_size <= 0:
            print("Bitte gib eine Zahl groesser als 0 ein.")
            continue

        if sample_size > total_records:
            print(f"Es gibt nur {total_records} News im JSON. Bitte waehle maximal {total_records}.")
            continue

        return sample_size


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"JSON-Datei nicht gefunden: {INPUT_FILE}")

    with INPUT_FILE.open(encoding="utf-8") as f:
        news = json.load(f)

    if not news:
        print("Die JSON-Datei enthaelt keine News.")
        return

    print(f"Verfuegbare News im JSON: {len(news)}")

    sample_size = ask_sample_size(len(news))
    selected_news = random.sample(news, sample_size)

    print("\n" + "=" * 80)
    print(f"ZUFALLSAUSWAHL: {sample_size} NEWS")
    print("=" * 80)

    for index, item in enumerate(selected_news, start=1):
        print(f"\n{index}. {item.get('headline', '')}")
        print(f"   ID: {item.get('id', '')}")
        print(f"   Outlet: {item.get('outlet', '')}")
        print(f"   Bias: {item.get('bias_category', '')}")
        print(f"   Datum: {item.get('article_date', '')}")
        print(f"   URL: {item.get('url', '')}")

    print("\n" + "=" * 80)
    print("NUR TITEL ZUM KOPIEREN")
    print("=" * 80)

    for item in selected_news:
        print(item.get("headline", ""))


if __name__ == "__main__":
    main()
