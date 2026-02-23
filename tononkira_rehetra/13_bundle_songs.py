import os
import json
from tqdm import tqdm

def bundle_songs(output_dir, bundle_path):
    print("======================================================================")
    print("🚀 BUNDLE TURBO : Regroupement des 14 000 chansons")
    print(f"   Source : {output_dir}")
    print(f"   Cible  : {bundle_path}")
    print("======================================================================")

    if not os.path.exists(output_dir):
        print(f"❌ Erreur : Dossier {output_dir} introuvable.")
        return

    all_songs = []
    artists = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
    
    for artist in tqdm(artists, desc="Lecture des chansons"):
        artist_path = os.path.join(output_dir, artist)
        for song_file in os.listdir(artist_path):
            if song_file.endswith(".txt"):
                path = os.path.join(artist_path, song_file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            all_songs.append({
                                "artist": artist,
                                "title": song_file.replace(".txt", ""),
                                "content": content
                            })
                except:
                    continue

    with open(bundle_path, 'w', encoding='utf-8') as f:
        json.dump(all_songs, f, ensure_ascii=False)
        
    print(f"\n✅ Bundle terminé ! {len(all_songs)} chansons regroupées dans un seul fichier.")
    print(f"📍 Taille du fichier : {os.path.getsize(bundle_path) / (1024*1024):.2f} MB")
    print("======================================================================")

if __name__ == "__main__":
    bundle_songs("output", "songs_bundle.json")
