import os
import requests
from tqdm import tqdm

def download_wikipedia_dump(output_path):
    # URL du dump officiel de Wikipédia Malagasy (les articles actuels)
    url = "https://dumps.wikimedia.org/mgwiki/latest/mgwiki-latest-pages-articles.xml.bz2"
    
    print("======================================================================")
    print("🌍 TÉLÉCHARGEMENT DE WIKIPÉDIA MALAGASY")
    print(f"   Source : {url}")
    print("======================================================================")

    if os.path.exists(output_path):
        print(f"ℹ️ Le fichier {output_path} existe déjà. Saut de l'étape.")
        return

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f, tqdm(
        desc="Téléchargement",
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

    print(f"\n✅ Téléchargement terminé : {output_path}")
    print("⚠️ Prochaine étape : Extraire le texte avec 'wikiextractor'.")
    print("======================================================================")

if __name__ == "__main__":
    # On sauvegarde dans le dossier parent (bible/wiki) pour ne pas polluer 'tononkira_rehetra'
    output_file = "../mgwiki-latest-pages-articles.xml.bz2"
    download_wikipedia_dump(output_file)
