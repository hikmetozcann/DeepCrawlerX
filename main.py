import argparse
import json
import os
import signal
import sys
from crawler import DeepCrawler

crawler = None

def signal_handler(sig, frame):
    print("Program durduruluyor, veriler kaydediliyor...")
    crawler.save_data()  # Toplanan verileri kaydet
    sys.exit(0)

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="DeepCrawlerX")
    parser.add_argument("url", help="Base URL to crawl")
    parser.add_argument(
        "--config",
        default=os.path.join("config", "settings.json"),
        help="Path to configuration file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = load_config(args.config)

    crawler = DeepCrawler(args.url, config)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        crawler.scrape_url(args.url)
    finally:
        crawler.save_data()
