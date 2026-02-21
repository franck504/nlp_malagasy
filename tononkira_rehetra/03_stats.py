#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 : Statistiques et vérification du scraping
Analyse le dossier output/ et affiche un rapport détaillé.
"""

import argparse
from pathlib import Path


def analyze_output(output_dir="output"):
    """Analyse le dossier de sortie et affiche les statistiques."""

    output_path = Path(output_dir)

    if not output_path.exists():
        print(f"❌ Dossier {output_dir} introuvable !")
        print("💡 Exécutez d'abord : python3 02_scrape_lyrics.py")
        return

    print("=" * 70)
    print("📊 STATISTIQUES DU SCRAPING")
    print(f"   Dossier : {output_path.resolve()}")
    print("=" * 70)

    # Collecter les stats par artiste
    artist_stats = []
    total_files = 0
    total_size = 0
    empty_dirs = []
    small_files = []

    for artist_dir in sorted(output_path.iterdir()):
        if not artist_dir.is_dir():
            continue

        txt_files = list(artist_dir.glob("*.txt"))
        count = len(txt_files)
        size = sum(f.stat().st_size for f in txt_files)

        artist_stats.append({
            "name": artist_dir.name,
            "count": count,
            "size": size
        })

        total_files += count
        total_size += size

        if count == 0:
            empty_dirs.append(artist_dir.name)

        # Détecter les fichiers très petits (< 100 octets)
        for f in txt_files:
            if f.stat().st_size < 100:
                small_files.append(f"{artist_dir.name}/{f.name}")

    # Tri par nombre de chansons
    artist_stats.sort(key=lambda x: x["count"], reverse=True)

    # Affichage
    print(f"\n📁 Nombre d'artistes : {len(artist_stats)}")
    print(f"🎵 Nombre de chansons : {total_files:,}")
    print(f"💾 Taille totale      : {total_size / 1024 / 1024:.2f} MB")

    if total_files > 0:
        print(f"📄 Taille moyenne     : {total_size / total_files / 1024:.2f} KB / chanson")

    # Top 20
    print(f"\n🏆 Top 20 artistes par nombre de chansons :")
    print(f"{'#':>4}  {'Artiste':<40} {'Chansons':>10} {'Taille':>10}")
    print("-" * 70)
    for i, a in enumerate(artist_stats[:20], 1):
        size_str = f"{a['size'] / 1024:.1f} KB"
        print(f"{i:4d}. {a['name']:<40} {a['count']:>10} {size_str:>10}")

    # Distribution
    print(f"\n📈 Distribution :")
    ranges = [
        (100, "100+"),
        (50, "50-99"),
        (20, "20-49"),
        (10, "10-19"),
        (5, "5-9"),
        (1, "1-4"),
    ]
    for min_count, label in ranges:
        if label.endswith("+"):
            n = sum(1 for a in artist_stats if a["count"] >= min_count)
        else:
            low, high = map(int, label.split("-"))
            n = sum(1 for a in artist_stats if low <= a["count"] <= high)
        bar = "█" * (n // 2)
        print(f"  {label:>8} chansons : {n:4d} artistes {bar}")

    zero = sum(1 for a in artist_stats if a["count"] == 0)
    print(f"  {'0':>8} chansons : {zero:4d} artistes (dossiers vides)")

    # Alertes
    if empty_dirs:
        print(f"\n⚠️  {len(empty_dirs)} dossiers artiste vides :")
        for d in empty_dirs[:10]:
            print(f"    - {d}")
        if len(empty_dirs) > 10:
            print(f"    ... et {len(empty_dirs) - 10} autres")

    if small_files:
        print(f"\n⚠️  {len(small_files)} fichiers très petits (< 100 octets) :")
        for f in small_files[:10]:
            print(f"    - {f}")
        if len(small_files) > 10:
            print(f"    ... et {len(small_files) - 10} autres")

    print("\n" + "=" * 70)
    print("✅ Analyse terminée !")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Phase 3 : Statistiques du scraping tononkira"
    )
    parser.add_argument(
        "--output", type=str, default="output",
        help="Dossier de sortie à analyser (défaut: output/)"
    )
    args = parser.parse_args()

    analyze_output(output_dir=args.output)
