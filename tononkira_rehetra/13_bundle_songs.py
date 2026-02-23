import os
import json
from tqdm import tqdm

def bundle_songs(output_dir, bundle_path):
    print("======================================================================")
    print("🚀 BUNDLE TURBO 2.0 : Regroupement optimisé")
    print(f"   Source : {output_dir}")
    print(f"   Cible  : {bundle_path}")
    print("======================================================================")

    if not os.path.exists(output_dir):
        print(f"❌ Erreur : Dossier {output_dir} introuvable.")
        return

    # Charger le bundle existant pour pouvoir reprendre (Resume)
    all_songs = []
    processed_artists = set()
    if os.path.exists(bundle_path):
        try:
            with open(bundle_path, 'r', encoding='utf-8') as f:
                all_songs = json.load(f)
                processed_artists = {s["artist"] for s in all_songs}
                print(f"ℹ️ Reprise : {len(processed_artists)} artistes déjà traités ({len(all_songs)} chansons).")
        except:
            print("⚠️ Impossible de lire le bundle existant, on repart à zéro.")

    try:
        # scandir est plus rapide que listdir pour les métadonnées
        with os.scandir(output_dir) as it:
            artists = [entry.name for entry in it if entry.is_dir()]
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du dossier output : {e}")
        return

    count_new = 0
    artists_to_process = [a for a in artists if a not in processed_artists]
    
    if not artists_to_process:
        print("✅ Tout est déjà traité !")
        return

    try:
        # On sauvegarde toutes les X chansons pour ne rien perdre
        save_every = 50 
        
        for artist in tqdm(artists_to_process, desc="Lecture des nouvelles chansons"):
            artist_path = os.path.join(output_dir, artist)
            try:
                with os.scandir(artist_path) as it_songs:
                    for entry in it_songs:
                        if entry.is_file() and entry.name.endswith(".txt"):
                            with open(entry.path, 'r', encoding='utf-8') as f:
                                # On nettoie un peu le contenu
                                content = f.read().strip()
                                if content:
                                    all_songs.append({
                                        "artist": artist,
                                        "title": entry.name.replace(".txt", ""),
                                        "content": content
                                    })
                                    count_new += 1
            except:
                continue

            # Sauvegarde régulière
            if count_new > save_every:
                with open(bundle_path, 'w', encoding='utf-8') as f:
                    json.dump(all_songs, f, ensure_ascii=False)
                count_new = 0 # reset compteur de sauvegarde

    except KeyboardInterrupt:
        print("\n🛑 Interruption détectée ! Sauvegarde en cours...")
    finally:
        # Sauvegarde finale
        with open(bundle_path, 'w', encoding='utf-8') as f:
            json.dump(all_songs, f, ensure_ascii=False)
        
    print(f"\n✅ Terminé ! Total : {len(all_songs)} chansons dans {bundle_path}")
    print(f"📍 Taille finale : {os.path.getsize(bundle_path) / (1024*1024):.2f} MB")
    print("======================================================================")

if __name__ == "__main__":
    bundle_songs("output", "songs_bundle.json")
