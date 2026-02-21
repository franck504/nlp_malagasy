#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper pour les paroles de chansons malgaches depuis tononkira.serasera.org
À exécuter sur Google Colab
"""

import requests
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import shutil


class TononkiraArtistScraper:
    def __init__(self, output_dir="tononkira_raw_texts", delay=2, reset_output=True):
        self.output_dir = Path(output_dir)
        if reset_output and self.output_dir.exists():
           shutil.rmtree(self.output_dir)
           print(f"🧹 Dossier supprimé : {self.output_dir}")

        self.output_dir.mkdir(exist_ok=True)

        self.delay = delay
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Malagasy Lyrics Research Bot)"
        }

        self.stats = {
            "artists": 0,
            "songs": 0,
            "saved": 0,
            "failed": 0
        }

    # ===============================
    # 🌐 HTTP
    # ===============================
    def fetch_page(self, url):
        try:
            print(f"📥 {url}")
            r = requests.get(url, headers=self.headers, timeout=15)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"❌ Erreur : {e}")
            self.stats["failed"] += 1
            return None

    # ===============================
    # 📄 PAGINATION
    # ===============================
    def get_last_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        last = soup.find("a", attrs={"aria-label": "Farany"})

        if not last:
            return 1

        href = last.get("href", "")
        qs = parse_qs(urlparse(href).query)
        return int(qs.get("page", [1])[0])

    # ===============================
    # 🎵 LIENS DES CHANSONS
    # ===============================
    def extract_song_links(self, html):
        soup = BeautifulSoup(html, "html.parser")
        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("https://tononkira.serasera.org/hira/"):
                links.add(href)

        return list(links)

    # ===============================
    # 🎼 EXTRACTION DES PAROLES
    # ===============================
    def extract_lyrics(self, html):
        soup = BeautifulSoup(html, "html.parser")

        source_div = soup.find(
            "div",
            class_="print my-3 fst-italic",
            string=lambda x: x and "Nalaina tao amin'ny tononkira.serasera.org" in x
        )

        if not source_div:
            return ""

        lines = []

        for elem in source_div.next_siblings:
            if getattr(elem, "name", None) in ["div", "h5", "form"]:
                break

            if isinstance(elem, str):
                t = elem.strip()
                if t:
                    lines.append(t)

            elif elem.name == "br":
                lines.append("\n")

            else:
                t = elem.get_text(strip=True)
                if t:
                    lines.append(t)

        text = "\n".join(lines)
        text = text.replace("\n\n\n", "\n\n").strip()

        return text

    # ===============================
    # 💾 SAUVEGARDE
    # ===============================
    def save_lyrics(self, lyrics, song_url):
        parsed = urlparse(song_url)
        path = parsed.path.strip("/").replace("/", "_")

        filename = f"tononkira_{path}.txt"
        filepath = self.output_dir / filename

        counter = 1
        while filepath.exists():
            filepath = self.output_dir / f"tononkira_{path}_{counter}.txt"
            counter += 1

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(lyrics)

        self.stats["saved"] += 1
        print(f"💾 Sauvé : {filepath.name}")

    # ===============================
    # 🚀 PIPELINE COMPLET PAR ARTISTE
    # ===============================
    def scrape_artist(self, artiste):
        print("\n" + "=" * 70)
        print(f"🎤 ARTISTE : {artiste}")
        print("=" * 70)

        base_url = f"https://tononkira.serasera.org/mpihira/{artiste}/hira"
        html = self.fetch_page(base_url)

        if not html:
            return

        last_page = self.get_last_page(html)
        print(f"📄 Pages détectées : {last_page}")

        song_urls = set()

        for page in range(1, last_page + 1):
            page_url = f"{base_url}?page={page}"
            page_html = self.fetch_page(page_url)

            if not page_html:
                continue

            links = self.extract_song_links(page_html)
            song_urls.update(links)

            time.sleep(self.delay)

        print(f"🎵 {len(song_urls)} chansons trouvées")

        for song_url in song_urls:
            html = self.fetch_page(song_url)
            if not html:
                continue

            lyrics = self.extract_lyrics(html)
            if len(lyrics) > 100:
                self.save_lyrics(lyrics, song_url)
                self.stats["songs"] += 1

            time.sleep(self.delay)

        self.stats["artists"] += 1

    # ===============================
    # 📊 STATS
    # ===============================
    def print_stats(self):
        print("\n" + "=" * 70)
        print("📊 STATISTIQUES FINALES")
        print("=" * 70)
        for k, v in self.stats.items():
            print(f"{k:10s} : {v}")
        print("=" * 70)


# ===============================
# ▶️ MAIN
# ===============================
def run():
    artistes = [
        "mahaleo",
        "ambondrona",
        "rebika",
        "vola-sy-noro",
        "voahangy",
        "henri-ratsimbazafy",
        "lola-lahy",
        "bessa-sy-lola",
        "bodo",
        "poopy",
        "levelo",
        "zandry-gasy",
        "farakely",
    ]

    scraper = TononkiraArtistScraper(
        output_dir="tononkira_raw_texts",
        delay=2,
        reset_output=True
    )

    for artiste in artistes:
        scraper.scrape_artist(artiste)

    scraper.print_stats()


if __name__ == "__main__":
    run()
