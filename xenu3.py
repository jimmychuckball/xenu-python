#!/usr/bin/env python3

import csv
import re
import ssl
import socket
import threading
import time
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


ssl._create_default_https_context = ssl._create_unverified_context

paused = False
quit_scan = False


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()


def command_listener():
    global paused, quit_scan

    while not quit_scan:
        cmd = input().strip().lower()

        if cmd == "p":
            paused = True
            print("[PAUSED] Type r + Enter to resume.")

        elif cmd == "r":
            paused = False
            print("[RESUMED]")

        elif cmd == "q":
            quit_scan = True
            print("[STOPPING] Saving current results...")


def wait_if_paused():
    while paused and not quit_scan:
        time.sleep(0.5)


def load_urls_from_txt(txt_file):
    with open(txt_file, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def clean_url(raw_url, scheme):
    if not raw_url.startswith(("http://", "https://")):
        return f"{scheme}://{raw_url.strip()}"
    return raw_url.strip()


def get_domain(url):
    return urlparse(url).netloc


def switch_to_http(url):
    return url.replace("https://", "http://", 1) if url.startswith("https://") else url


def extract_title(body):
    parser = TitleParser()
    parser.feed(body.decode("utf-8", errors="ignore"))
    return re.sub(r"\s+", " ", parser.title).strip()


def empty_result(url):
    return {
        "final_url": url,
        "status": "",
        "content_length": "",
        "title": "",
        "server": ""
    }


def request_url(url, timeout=10):
    headers = {"User-Agent": "Mozilla/5.0 URL-Metadata-Scanner/1.0"}

    context = ssl._create_unverified_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    request = Request(url, headers=headers)

    with urlopen(request, timeout=timeout, context=context) as response:
        body = response.read(1_000_000)

        content_length = response.headers.get("Content-Length")
        if content_length is None:
            content_length = len(body)

        return {
            "final_url": response.geturl(),
            "status": response.status,
            "content_length": content_length,
            "title": extract_title(body),
            "server": response.headers.get("Server", "")
        }


def fetch_url(url, timeout=10):
    try:
        return request_url(url, timeout)

    except HTTPError as e:
        return {
            "final_url": url,
            "status": e.code,
            "content_length": "",
            "title": "",
            "server": e.headers.get("Server", "") if e.headers else ""
        }

    except (ssl.SSLError, URLError, socket.timeout, Exception) as e:
        error_text = str(e).lower()

        if url.startswith("https://") and (
            "ssl" in error_text
            or "certificate" in error_text
            or "wrong version number" in error_text
            or "unknown protocol" in error_text
        ):
            try:
                return request_url(switch_to_http(url), timeout)
            except Exception:
                return empty_result(url)

        return empty_result(url)


def main():
    global quit_scan

    print("\n=== URL Metadata Scanner ===")
    print("Controls while scanning: p = pause, r = resume, q = quit\n")

    txt_file = input("Enter path to TXT file containing URLs/IPs: ").strip()

    try:
        urls = load_urls_from_txt(txt_file)
    except Exception as e:
        print(f"[-] Failed to read TXT file: {e}")
        return

    if not urls:
        print("[-] No URLs found.")
        return

    scheme = input("Use https or http? [https/http]: ").strip().lower()

    if scheme not in ("http", "https"):
        scheme = "https"

    output_csv = input("Enter output CSV filename: ").strip()

    if not output_csv:
        output_csv = "results.csv"

    if not output_csv.endswith(".csv"):
        output_csv += ".csv"

    listener = threading.Thread(target=command_listener, daemon=True)
    listener.start()

    fieldnames = [
        "input_url",
        "final_url",
        "domain",
        "status",
        "content_length",
        "title",
        "server"
    ]

    total = len(urls)

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for index, raw_url in enumerate(urls, start=1):
            wait_if_paused()

            if quit_scan:
                break

            url = clean_url(raw_url, scheme)

            print(f"[{index}/{total}] Scanning {url}")

            result = fetch_url(url)

            row = {
                "input_url": url,
                "final_url": result["final_url"],
                "domain": get_domain(result["final_url"]),
                "status": result["status"],
                "content_length": result["content_length"],
                "title": result["title"],
                "server": result["server"]
            }

            writer.writerow(row)
            csvfile.flush()

    quit_scan = True

    print(f"\n[+] Results saved to: {output_csv}")


if __name__ == "__main__":
    main()